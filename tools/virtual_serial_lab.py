#!/usr/bin/env python3
"""Read-only-by-default virtual MaxFire endpoint for offline BixCheck research.

The lab creates a pseudo-terminal and parses the exact unterminated four-byte
read / six-byte write requests reconstructed from BixCheck.  It is deliberately
an ASCII register-protocol emulator, not a firmware-downloader emulator: binary
bootloader bytes are rejected.

Run from the repository root:

    python tools/virtual_serial_lab.py

Then connect a serial client to the printed PTY path at either 9600 or 19200
baud.  PTYs do not model physical timing or voltage levels.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import TextIO


try:
    from openmaxfire.protocol import (
        ADDRESSED_UNITS,
        ProtocolError,
        RegisterRequest,
        calculate_configuration_checksum,
        decode_register_request,
    )
except ModuleNotFoundError:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
    from openmaxfire.protocol import (  # type: ignore[no-redef]
        ADDRESSED_UNITS,
        ProtocolError,
        RegisterRequest,
        calculate_configuration_checksum,
        decode_register_request,
    )


@dataclass(frozen=True, slots=True)
class LabEvent:
    monotonic_seconds: float
    direction: str
    frame_hex: str
    frame_ascii: str
    outcome: str


class RequestStreamParser:
    """Split BixCheck's unterminated requests by opcode-defined length."""

    def __init__(self, max_buffer: int = 256):
        self.max_buffer = max_buffer
        self._buffer = bytearray()

    def feed(self, data: bytes | bytearray | memoryview) -> list[RegisterRequest]:
        self._buffer.extend(data)
        requests: list[RegisterRequest] = []
        while self._buffer:
            while self._buffer[:1] in (b"\r", b"\n"):
                del self._buffer[:1]
            if not self._buffer:
                break
            if chr(self._buffer[0]) not in ADDRESSED_UNITS:
                rejected = self._buffer[0]
                self._buffer.clear()
                raise ProtocolError(
                    f"non-register byte 0x{rejected:02X}; downloader traffic is not supported"
                )
            if len(self._buffer) < 2:
                break
            opcode = chr(self._buffer[1])
            if opcode == "R":
                length = 4
            elif opcode == "W":
                length = 6
            else:
                self._buffer.clear()
                raise ProtocolError(f"unsupported request opcode: {opcode!r}")
            if len(self._buffer) < length:
                break
            frame = bytes(self._buffer[:length])
            del self._buffer[:length]
            requests.append(decode_register_request(frame))
        if len(self._buffer) > self.max_buffer:
            self._buffer.clear()
            raise ProtocolError("request buffer limit exceeded")
        return requests

    @property
    def pending(self) -> bytes:
        return bytes(self._buffer)


def default_registers() -> dict[tuple[str, int], int]:
    """Synthetic, conspicuously non-live identity used by the virtual endpoint."""

    registers: dict[tuple[str, int], int] = {
        ("C", 0x08): 0x07,
        ("C", 0x0B): 0x02,
        ("C", 0x0C): 0x71,
        ("C", 0x0D): 0x00,
        ("C", 0x0E): 0x00,
        ("A", 0x00): 0x00,
        ("A", 0x01): 0x00,
        ("A", 0x02): 0x07,
    }
    fields = (
        (0x03, b"00005215"),
        (0x0B, b"20051201"),
        (0x13, b"VIRTUAL-MAXFIRE!"),
    )
    for start, value in fields:
        for offset, byte in enumerate(value):
            registers[("A", start + offset)] = byte
    eeprom = {
        address: registers.get(("A", address), 0) for address in range(0x100)
    }
    checksum = calculate_configuration_checksum(7, eeprom)
    registers[("A", 0x00)] = checksum >> 8
    registers[("A", 0x01)] = checksum & 0xFF
    return registers


class VirtualStove:
    """Deterministic register model; writes are blocked unless explicitly enabled."""

    def __init__(
        self,
        registers: dict[tuple[str, int], int] | None = None,
        *,
        allow_writes: bool = False,
    ):
        self.registers = default_registers() if registers is None else dict(registers)
        self.allow_writes = allow_writes

    def transact(self, request: RegisterRequest) -> tuple[bytes, str]:
        if request.opcode == "R":
            value = self.registers.get((request.unit, request.address), 0)
            return (
                f"{request.unit}R{request.address:02X}{value:02X}\n".encode("ascii"),
                "synthetic read",
            )
        assert request.value is not None
        if not self.allow_writes:
            return b"IWRITE-BLOCKED\n", "write blocked"
        self.registers[(request.unit, request.address)] = request.value
        return (
            f"{request.unit}W{request.address:02X}{request.value:02X}\n".encode("ascii"),
            "synthetic write accepted",
        )


def parse_override(text: str) -> tuple[tuple[str, int], int]:
    try:
        key, value_text = text.split("=", 1)
        unit, address_text = key.split(":", 1)
        address = int(address_text, 16)
        value = int(value_text, 16)
    except (ValueError, TypeError) as exc:
        raise argparse.ArgumentTypeError("use UNIT:XX=YY, for example C:08=07") from exc
    if unit not in ADDRESSED_UNITS or not 0 <= address <= 0xFF or not 0 <= value <= 0xFF:
        raise argparse.ArgumentTypeError("override must use A/C/D and byte-sized hex values")
    return (unit, address), value


def event(direction: str, frame: bytes, outcome: str) -> LabEvent:
    return LabEvent(
        monotonic_seconds=time.monotonic(),
        direction=direction,
        frame_hex=frame.hex(" ").upper(),
        frame_ascii="".join(chr(value) if 0x20 <= value <= 0x7E else "." for value in frame),
        outcome=outcome,
    )


def emit(item: LabEvent, log: TextIO | None) -> None:
    print(
        f"{item.monotonic_seconds:12.6f} {item.direction:>3} "
        f"{item.frame_hex:<24} {item.frame_ascii!r} {item.outcome}",
        flush=True,
    )
    if log is not None:
        log.write(json.dumps(asdict(item), sort_keys=True) + "\n")
        log.flush()


def request_bytes(request: RegisterRequest) -> bytes:
    if request.value is None:
        return f"{request.unit}{request.opcode}{request.address:02X}".encode("ascii")
    return f"{request.unit}{request.opcode}{request.address:02X}{request.value:02X}".encode(
        "ascii"
    )


def run_demo(stove: VirtualStove) -> int:
    parser = RequestStreamParser()
    samples = (b"CR", b"08CR0B", b"CW0E14")
    for chunk in samples:
        print(f"chunk: {chunk!r}")
        for request in parser.feed(chunk):
            response, outcome = stove.transact(request)
            print(f"  {request!r} -> {response!r} ({outcome})")
    return 0


def run_pty(stove: VirtualStove, log: TextIO | None) -> int:
    """Run the optional POSIX PTY endpoint.

    Imports remain local so the protocol model and its tests are importable on
    Windows even though Windows does not provide Unix pseudo-terminals.
    """

    try:
        import pty
        import select
        import signal
        import termios
        import tty
    except ImportError as exc:
        raise RuntimeError(
            "the PTY virtual endpoint requires Linux or macOS; use --demo on Windows"
        ) from exc

    master, slave = pty.openpty()
    tty.setraw(slave, when=termios.TCSANOW)
    slave_name = os.ttyname(slave)
    print(f"Virtual MaxFire serial endpoint: {slave_name}", flush=True)
    print(
        "Mode: " + ("LAB WRITES ENABLED" if stove.allow_writes else "READ ONLY (writes blocked)"),
        flush=True,
    )
    print("Only ASCII register traffic is accepted; Ctrl-C stops the lab.", flush=True)
    stop = False

    def stop_handler(_signum: int, _frame: object) -> None:
        nonlocal stop
        stop = True

    previous_int = signal.signal(signal.SIGINT, stop_handler)
    previous_term = signal.signal(signal.SIGTERM, stop_handler)
    parser = RequestStreamParser()
    try:
        while not stop:
            readable, _, _ = select.select([master], [], [], 0.25)
            if not readable:
                continue
            try:
                chunk = os.read(master, 256)
            except OSError:
                break
            if not chunk:
                break
            emit(event("RX", chunk, "received"), log)
            try:
                requests = parser.feed(chunk)
            except ProtocolError as exc:
                response = f"IERROR:{exc}\n".encode("ascii", errors="replace")
                os.write(master, response)
                emit(event("TX", response, "parser rejection"), log)
                continue
            for request in requests:
                response, outcome = stove.transact(request)
                os.write(master, response)
                emit(event("REQ", request_bytes(request), outcome), log)
                emit(event("TX", response, outcome), log)
    finally:
        signal.signal(signal.SIGINT, previous_int)
        signal.signal(signal.SIGTERM, previous_term)
        os.close(master)
        os.close(slave)
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--allow-writes",
        action="store_true",
        help="allow writes inside the synthetic model (never affects a real stove)",
    )
    parser.add_argument(
        "--register",
        action="append",
        default=[],
        type=parse_override,
        metavar="UNIT:XX=YY",
        help="override a synthetic register; may be repeated",
    )
    parser.add_argument("--jsonl-log", type=Path, help="optional event log path")
    parser.add_argument("--demo", action="store_true", help="run a finite parser demo")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    registers = default_registers()
    registers.update(dict(args.register))
    stove = VirtualStove(registers, allow_writes=args.allow_writes)
    if args.demo:
        return run_demo(stove)
    if args.jsonl_log:
        args.jsonl_log.parent.mkdir(parents=True, exist_ok=True)
        with args.jsonl_log.open("a", encoding="utf-8") as log:
            return run_pty(stove, log)
    return run_pty(stove, None)


if __name__ == "__main__":
    raise SystemExit(main())
