"""Validated, fail-fast register transaction plans.

Transactions intentionally cover only the reconstructed A/C/D ASCII register
protocol.  Firmware-loader traffic remains a separate state machine and cannot
be smuggled into a register plan through the keyed ``CW0FC4`` request.
"""

from __future__ import annotations

import json
import math
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

from .client import MaxFireClient
from .protocol import ADDRESSED_UNITS, encode_read_register


TRANSACTION_SCHEMA = "openmaxfire.transaction.v1"
LOADER_ENTRY = ("C", 0x0F, 0xC4)


def _reject_unknown_keys(
    document: Mapping[object, object],
    allowed: frozenset[str],
    context: str,
) -> None:
    unknown = sorted(str(key) for key in document if key not in allowed)
    if unknown:
        raise ValueError(f"{context} contains unknown field(s): {', '.join(unknown)}")


def _byte(value: object, field: str) -> int:
    if isinstance(value, bool):
        raise ValueError(f"{field} must be a byte, not a boolean")
    if isinstance(value, int):
        parsed = value
    elif isinstance(value, str):
        try:
            parsed = int(value, 0)
        except ValueError as exc:
            raise ValueError(f"{field} must be an integer or 0x-prefixed byte") from exc
    else:
        raise ValueError(f"{field} must be an integer or 0x-prefixed byte")
    if not 0 <= parsed <= 0xFF:
        raise ValueError(f"{field} must be between 0x00 and 0xFF")
    return parsed


def _unit(value: object) -> str:
    if not isinstance(value, str) or value not in ADDRESSED_UNITS:
        raise ValueError("unit must be one of A, C, or D")
    return value


def _seconds(value: object) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("delay seconds must be a finite nonnegative number")
    parsed = float(value)
    if not math.isfinite(parsed) or parsed < 0:
        raise ValueError("delay seconds must be a finite nonnegative number")
    return parsed


@dataclass(frozen=True, slots=True)
class TransactionOperation:
    op: str
    unit: str | None = None
    address: int | None = None
    value: int | None = None
    verify: bool = False
    settle_delay: float = 0.0
    seconds: float = 0.0

    def to_dict(self) -> dict[str, object]:
        if self.op == "delay":
            return {"op": "delay", "seconds": self.seconds}
        result: dict[str, object] = {
            "op": self.op,
            "unit": self.unit,
            "address": f"0x{self.address:02X}",
        }
        if self.op == "write":
            result.update(
                {
                    "value": f"0x{self.value:02X}",
                    "verify": self.verify,
                    "settle_delay": self.settle_delay,
                }
            )
        return result


@dataclass(frozen=True, slots=True)
class TransactionPlan:
    operations: tuple[TransactionOperation, ...]
    description: str = ""

    @property
    def has_writes(self) -> bool:
        return any(operation.op == "write" for operation in self.operations)

    def to_dict(self) -> dict[str, object]:
        return {
            "schema": TRANSACTION_SCHEMA,
            "description": self.description,
            "operations": [operation.to_dict() for operation in self.operations],
        }


def _operation(document: object, index: int) -> TransactionOperation:
    if not isinstance(document, Mapping):
        raise ValueError(f"operation {index} must be a JSON object")
    op = document.get("op")
    if op == "delay":
        _reject_unknown_keys(document, frozenset(("op", "seconds")), f"operation {index}")
        return TransactionOperation(op="delay", seconds=_seconds(document.get("seconds")))
    if op not in ("read", "write"):
        raise ValueError(f"operation {index} has unsupported op {op!r}")
    allowed = (
        frozenset(("op", "unit", "address"))
        if op == "read"
        else frozenset(
            ("op", "unit", "address", "value", "verify", "settle_delay")
        )
    )
    _reject_unknown_keys(document, allowed, f"operation {index}")
    unit = _unit(document.get("unit", "C"))
    address = _byte(document.get("address"), f"operation {index} address")
    if op == "read":
        return TransactionOperation(op="read", unit=unit, address=address)

    value = _byte(document.get("value"), f"operation {index} value")
    if (unit, address, value) == LOADER_ENTRY:
        raise ValueError(
            "CW0FC4 enters the firmware loader and is forbidden in register transactions"
        )
    verify = document.get("verify", False)
    if not isinstance(verify, bool):
        raise ValueError(f"operation {index} verify must be true or false")
    settle_delay = _seconds(document.get("settle_delay", 0.0))
    return TransactionOperation(
        op="write",
        unit=unit,
        address=address,
        value=value,
        verify=verify,
        settle_delay=settle_delay,
    )


def parse_transaction_plan(document: object) -> TransactionPlan:
    if not isinstance(document, Mapping):
        raise ValueError("transaction document must be a JSON object")
    _reject_unknown_keys(
        document,
        frozenset(("schema", "description", "operations")),
        "transaction",
    )
    if document.get("schema") != TRANSACTION_SCHEMA:
        raise ValueError(f"transaction schema must be {TRANSACTION_SCHEMA!r}")
    description = document.get("description", "")
    if not isinstance(description, str):
        raise ValueError("transaction description must be a string")
    operations_document = document.get("operations")
    if not isinstance(operations_document, Sequence) or isinstance(
        operations_document, (str, bytes, bytearray)
    ):
        raise ValueError("transaction operations must be a JSON array")
    if not operations_document:
        raise ValueError("transaction must contain at least one operation")
    operations = tuple(
        _operation(operation, index)
        for index, operation in enumerate(operations_document, start=1)
    )
    return TransactionPlan(operations=operations, description=description)


def load_transaction_plan(path: str | Path) -> TransactionPlan:
    with Path(path).open("r", encoding="utf-8") as stream:
        return parse_transaction_plan(json.load(stream))


def execute_transaction(
    client: MaxFireClient,
    plan: TransactionPlan,
    *,
    allow_writes: bool = False,
) -> dict[str, object]:
    """Execute a validated plan in order and stop on failed verification."""

    if plan.has_writes and not allow_writes:
        raise PermissionError("transaction contains writes but writes were not authorized")
    results: list[dict[str, object]] = []
    success = True
    failure: str | None = None
    started = time.monotonic()
    for index, operation in enumerate(plan.operations, start=1):
        if operation.op == "delay":
            time.sleep(operation.seconds)
            results.append(
                {"index": index, "op": "delay", "seconds": operation.seconds}
            )
            continue

        assert operation.unit is not None and operation.address is not None
        if operation.op == "read":
            response = client.query_register(operation.address, unit=operation.unit)
            results.append(
                {
                    "index": index,
                    "op": "read",
                    "unit": operation.unit,
                    "address": f"0x{operation.address:02X}",
                    "value": f"0x{response.value:02X}",
                    "request_hex": encode_read_register(
                        operation.address, unit=operation.unit
                    ).hex(" ").upper(),
                    "response_hex": response.raw.hex(" ").upper(),
                }
            )
            continue

        assert operation.value is not None
        if operation.verify:
            receipt = client.write_register_verified(
                operation.address,
                operation.value,
                unit=operation.unit,
                settle_delay=operation.settle_delay,
            )
        else:
            receipt = client.write_register(
                operation.address,
                operation.value,
                unit=operation.unit,
            )
        result: dict[str, object] = {
            "index": index,
            "op": "write",
            "unit": operation.unit,
            "address": f"0x{operation.address:02X}",
            "value": f"0x{operation.value:02X}",
            "request_hex": receipt.request.hex(" ").upper(),
            "verification_requested": operation.verify,
            "verified": receipt.verified,
        }
        if receipt.response is not None:
            result["readback_request_hex"] = encode_read_register(
                operation.address, unit=operation.unit
            ).hex(" ").upper()
            result["readback_hex"] = receipt.response.hex(" ").upper()
        results.append(result)
        if operation.verify and not receipt.verified:
            success = False
            failure = f"operation {index} readback did not match requested value"
            break

    return {
        "schema": "openmaxfire.transaction-result.v1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "description": plan.description,
        "success": success,
        "failure": failure,
        "elapsed_seconds": time.monotonic() - started,
        "operations_planned": len(plan.operations),
        "operations_completed": len(results),
        "results": results,
    }
