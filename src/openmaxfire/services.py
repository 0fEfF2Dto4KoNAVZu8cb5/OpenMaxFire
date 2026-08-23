"""Controller-aware service workflows above the register client.

Read-only workflows are usable with real sessions.  State-changing executors
currently accept only the explicit simulator backend and therefore cannot be
used to bypass the evidence gates published by controller profiles.
"""

from __future__ import annotations

import hashlib
import math
import time
from dataclasses import dataclass, replace
from enum import Enum
from typing import Callable, Iterable, Mapping

from .audit import AuditSpan
from .checkout import (
    CheckoutKind,
    CheckoutOutcome,
    CheckoutReport,
    CheckoutResult,
    checkout_test,
    plan_checkout_test,
)
from .configuration import ConfigurationImage, ConfigurationPlan
from .control import ControlAction, ControlOutcome, ControlResult, plan_control
from .errors import (
    CapabilityUnavailableError,
    SafetyInterlockError,
    VerificationError,
)
from .session import ControllerSession
from .transactions import TransactionPlan, execute_transaction


READ_ONLY_CHECKOUT_TESTS: tuple[int, ...] = (
    1, 2, 3, 4, 5, 6, 7, 8, 11, 12, 13, 14, 16, 33, 34, 36, 37
)


class ReadOnlyCheckoutRunner:
    """Evaluate only non-writing BixCheck tests from fresh controller reads."""

    def __init__(self, session: ControllerSession):
        self.session = session
        self._configuration: ConfigurationImage | None = None

    def _configuration_image(self, *, refresh: bool = False) -> ConfigurationImage:
        if refresh or self._configuration is None:
            self._configuration = self.session.read_configuration_image()
        return self._configuration

    def run_test(
        self,
        number: int,
        *,
        timeout_seconds: float = 0.0,
        poll_interval: float = 0.10,
    ) -> CheckoutResult:
        checkpoint = (
            self.session.audit.checkpoint() if self.session.audit is not None else 0
        )
        result = self._run_test(
            number,
            timeout_seconds=timeout_seconds,
            poll_interval=poll_interval,
        )
        return replace(result, audit_span=_audit_span(self.session, checkpoint))

    def _run_test(
        self,
        number: int,
        *,
        timeout_seconds: float = 0.0,
        poll_interval: float = 0.10,
    ) -> CheckoutResult:
        """Poll one test until it passes or its bounded read-only window ends."""

        if not math.isfinite(timeout_seconds) or timeout_seconds < 0:
            raise ValueError("timeout_seconds must be finite and nonnegative")
        if not math.isfinite(poll_interval) or poll_interval < 0:
            raise ValueError("poll_interval must be finite and nonnegative")
        test = checkout_test(number)
        if test.kind in (CheckoutKind.ACTUATOR, CheckoutKind.MANUAL):
            return CheckoutResult(
                test_number=number,
                outcome=CheckoutOutcome.NOT_RUN,
                observations={"kind": test.kind.value},
                message="test requires state-changing output or operator observation",
            )
        if number == 1:
            try:
                probe = self.session.read_register(0x00)
            except Exception as exc:
                return CheckoutResult(number, CheckoutOutcome.INDETERMINATE, {}, str(exc))
            return CheckoutResult(
                number,
                CheckoutOutcome.PASS if probe == 0 else CheckoutOutcome.FAIL,
                {"CR00": f"{probe:02X}"},
                "controller communication probe",
            )
        if number == 2:
            try:
                image = self._configuration_image(refresh=True)
                validation = image.validate(self.session.profile)
            except Exception as exc:
                return CheckoutResult(number, CheckoutOutcome.INDETERMINATE, {}, str(exc))
            return CheckoutResult(
                number,
                CheckoutOutcome.PASS if validation.valid else CheckoutOutcome.FAIL,
                {
                    "stored_checksum": f"{image.stored_checksum:04X}",
                    "calculated_checksum": f"{image.calculated_checksum:04X}",
                    "issues": [issue.message for issue in validation.issues],
                },
                "configuration checksum validation",
            )
        if number == 3:
            try:
                image = self._configuration_image()
            except Exception as exc:
                return CheckoutResult(number, CheckoutOutcome.INDETERMINATE, {}, str(exc))
            matches = image.data_format == self.session.identity.data_format
            return CheckoutResult(
                number,
                CheckoutOutcome.PASS if matches else CheckoutOutcome.FAIL,
                {
                    "controller_format": f"{self.session.identity.data_format:02X}",
                    "eeprom_format": f"{image.data_format:02X}",
                    "profile_key": self.session.profile.key,
                },
                "controller/EEPROM data-format comparison",
            )

        if not test.expectations:
            return CheckoutResult(
                number,
                CheckoutOutcome.NOT_RUN,
                {},
                "no machine-evaluable read-only predicate is established",
            )
        deadline = time.monotonic() + timeout_seconds
        last_values: dict[tuple[str, int], int] = {}
        errors: list[str] = []
        attempts = 0
        while True:
            attempts += 1
            values: dict[tuple[str, int], int] = {}
            errors.clear()
            for expectation in test.expectations:
                key = (expectation.unit, expectation.address)
                if key in values:
                    continue
                try:
                    values[key] = self.session.read_register(
                        expectation.address, unit=expectation.unit
                    )
                except Exception as exc:
                    errors.append(str(exc))
            last_values = values
            outcome = test.evaluate(values)
            if outcome is CheckoutOutcome.PASS:
                break
            if time.monotonic() >= deadline:
                outcome = (
                    CheckoutOutcome.INDETERMINATE
                    if errors or not values
                    else CheckoutOutcome.FAIL
                )
                break
            if poll_interval:
                time.sleep(poll_interval)
        observations = {
            f"{unit}R{address:02X}": f"{value:02X}"
            for (unit, address), value in sorted(last_values.items())
        }
        observations["attempts"] = attempts
        if errors:
            observations["errors"] = tuple(errors)
        return CheckoutResult(number, outcome, observations, test.instruction)

    def run_tests(
        self,
        numbers: Iterable[int],
        *,
        timeout_seconds: float = 0.0,
        poll_interval: float = 0.10,
    ) -> tuple[CheckoutResult, ...]:
        return tuple(
            self.run_test(
                number,
                timeout_seconds=timeout_seconds,
                poll_interval=poll_interval,
            )
            for number in numbers
        )

    def report(self, results: Iterable[CheckoutResult]) -> CheckoutReport:
        image = self._configuration_image()
        return CheckoutReport(
            profile_key=self.session.profile.key,
            configuration_checksum=f"{image.stored_checksum:04X}",
            configuration_backup_sha256=hashlib.sha256(image.raw).hexdigest(),
            results=tuple(results),
        )


class ConfigurationExecutionOutcome(str, Enum):
    NO_CHANGES = "no_changes"
    VERIFIED = "verified"
    FAILED = "failed"


@dataclass(frozen=True, slots=True)
class ConfigurationExecutionResult:
    outcome: ConfigurationExecutionOutcome
    profile_key: str
    prewrite_backup_sha256: str
    transaction: Mapping[str, object] | None
    observed: ConfigurationImage | None
    message: str = ""
    audit_span: AuditSpan | None = None

    @property
    def verified(self) -> bool:
        return self.outcome is ConfigurationExecutionOutcome.VERIFIED

    def to_dict(self) -> dict[str, object]:
        return {
            "schema": "openmaxfire.configuration-execution-result.v1",
            "outcome": self.outcome.value,
            "profile_key": self.profile_key,
            "prewrite_backup_sha256": self.prewrite_backup_sha256,
            "transaction": dict(self.transaction) if self.transaction else None,
            "observed_checksum": (
                f"{self.observed.stored_checksum:04X}"
                if self.observed is not None
                else None
            ),
            "verified": self.verified,
            "message": self.message,
            "audit_span": self.audit_span.to_dict() if self.audit_span else None,
            "evidence_boundary": "simulator execution only",
        }


def execute_configuration_plan(
    session: ControllerSession,
    plan: ConfigurationPlan,
    *,
    authorize: bool = False,
) -> ConfigurationExecutionResult:
    """Execute and fully verify a configuration plan on the simulator only."""

    checkpoint = session.audit.checkpoint() if session.audit is not None else 0
    if plan.profile_key != session.profile.key:
        raise VerificationError("configuration plan profile does not match session")
    before = session.read_configuration_image()
    backup_sha = hashlib.sha256(before.raw).hexdigest()
    if before != plan.current:
        raise VerificationError("controller configuration changed after the plan was built")
    if not plan.has_writes:
        return ConfigurationExecutionResult(
            ConfigurationExecutionOutcome.NO_CHANGES,
            session.profile.key,
            backup_sha,
            None,
            before,
            "configuration already matches target",
            _audit_span(session, checkpoint),
        )
    if not authorize:
        raise PermissionError("configuration writes were not explicitly authorized")
    if not session.simulated_backend:
        raise CapabilityUnavailableError(
            "physical configuration execution remains unvalidated and blocked"
        )
    try:
        transaction = execute_transaction(
            session.client,
            TransactionPlan(plan.operations, "simulated configuration apply"),
            allow_writes=True,
        )
        observed = session.read_configuration_image()
    except Exception as exc:
        return ConfigurationExecutionResult(
            ConfigurationExecutionOutcome.FAILED,
            session.profile.key,
            backup_sha,
            None,
            None,
            f"configuration execution interrupted: {exc}",
            _audit_span(session, checkpoint),
        )
    transaction_ok = bool(transaction.get("success"))
    verified = transaction_ok and observed == plan.target and observed.checksum_valid
    return ConfigurationExecutionResult(
        outcome=(
            ConfigurationExecutionOutcome.VERIFIED
            if verified
            else ConfigurationExecutionOutcome.FAILED
        ),
        profile_key=session.profile.key,
        prewrite_backup_sha256=backup_sha,
        transaction=transaction,
        observed=observed,
        message=(
            "complete A00-AFF image and checksum match"
            if verified
            else "post-write verification failed"
        ),
        audit_span=_audit_span(session, checkpoint),
    )


def execute_control(
    session: ControllerSession,
    action: ControlAction | str,
    *,
    target_level: int | None = None,
    authorize: bool = False,
    minimum_interval: float = 0.25,
) -> ControlResult:
    """Execute and verify normal control against the simulator only."""

    checkpoint = session.audit.checkpoint() if session.audit is not None else 0
    before = session.poll_snapshot()
    plan = plan_control(action, session.profile, before, target_level=target_level)
    if plan.already_satisfied:
        return ControlResult(
            action=plan.action,
            outcome=ControlOutcome.ALREADY_SATISFIED,
            requests=(),
            before=before,
            after=before,
            message="requested controller state is already satisfied",
            audit_span=_audit_span(session, checkpoint),
        )
    if not authorize:
        raise PermissionError("normal control was not explicitly authorized")
    if not session.simulated_backend:
        raise CapabilityUnavailableError(
            "high-level physical normal-control verification remains incomplete and blocked"
        )
    unsafe_blocker = any(
        "stale" in blocker or "profile" in blocker for blocker in plan.blockers
    )
    if plan.blockers and unsafe_blocker:
        raise SafetyInterlockError("; ".join(plan.blockers))
    if plan.action is not ControlAction.OFF and before.physical_inputs is not None:
        if before.physical_inputs.firebox_door_open:
            raise SafetyInterlockError("firebox door is open")
        if before.physical_inputs.ash_drawer_open:
            raise SafetyInterlockError("ash drawer is open")
    session.claim_control_window(minimum_interval)
    requests: list[bytes] = []
    try:
        for operation in plan.operations:
            assert operation.address is not None and operation.value is not None
            receipt = session.client.write_register(
                operation.address,
                operation.value,
                unit=operation.unit or "C",
            )
            requests.append(receipt.request)
        after = session.poll_snapshot()
    except Exception as exc:
        return ControlResult(
            action=plan.action,
            outcome=ControlOutcome.INDETERMINATE,
            requests=tuple(requests),
            before=before,
            after=None,
            message=f"control execution or verification was interrupted: {exc}",
            audit_span=_audit_span(session, checkpoint),
        )
    verified = _control_verified(plan.action, before, after, plan.target_level)
    return ControlResult(
        action=plan.action,
        outcome=(ControlOutcome.VERIFIED if verified else ControlOutcome.INDETERMINATE),
        requests=tuple(requests),
        before=before,
        after=after,
        message=plan.verification,
        audit_span=_audit_span(session, checkpoint),
    )


def _control_verified(
    action: ControlAction,
    before: object,
    after: object,
    target_level: int | None,
) -> bool:
    from .models import StoveSnapshot

    assert isinstance(before, StoveSnapshot) and isinstance(after, StoveSnapshot)
    state = after.operating_state
    if state is None or not after.fresh:
        return False
    if action is ControlAction.OFF:
        return state.phase == "off"
    if action is ControlAction.ON:
        return state.phase in (
            "prefill", "started", "starting", "ignited", "operating", "ramping"
        )
    if action is ControlAction.SET_LEVEL:
        return after.target_heat_level == target_level
    if before.target_heat_level is None or after.target_heat_level is None:
        return False
    if action is ControlAction.UP:
        return after.target_heat_level > before.target_heat_level
    return after.target_heat_level < before.target_heat_level


ObservationProvider = Callable[[int], bool | None]


def execute_simulated_checkout(
    session: ControllerSession,
    number: int,
    *,
    authorize: bool = False,
    observation_provider: ObservationProvider | None = None,
) -> CheckoutResult:
    """Exercise an actuator plan with unconditional cleanup in simulation."""

    checkpoint = session.audit.checkpoint() if session.audit is not None else 0
    test = checkout_test(number)
    if test.kind is not CheckoutKind.ACTUATOR:
        return ReadOnlyCheckoutRunner(session).run_test(number)
    if not authorize:
        raise PermissionError("Checkout actuator execution was not explicitly authorized")
    if not session.simulated_backend:
        raise CapabilityUnavailableError(
            "physical Checkout actuator execution remains unvalidated and blocked"
        )
    plan = plan_checkout_test(number, session.profile)
    if not plan.operations:
        raise CapabilityUnavailableError("complete Checkout action is not reconstructed")
    if not plan.cleanup:
        raise SafetyInterlockError("proven Checkout cleanup action is unavailable")
    observations: dict[str, object] = {"command_requests": [], "cleanup_requests": []}
    outcome = CheckoutOutcome.INDETERMINATE
    message = "simulated actuator observation is indeterminate"
    try:
        for operation in plan.operations:
            assert operation.address is not None and operation.value is not None
            receipt = session.client.write_register(
                operation.address, operation.value, unit=operation.unit or "C"
            )
            observations["command_requests"].append(receipt.request.hex().upper())
        if test.expectations:
            values = {
                (expectation.unit, expectation.address): session.read_register(
                    expectation.address, unit=expectation.unit
                )
                for expectation in test.expectations
            }
            outcome = test.evaluate(values)
            observations.update(
                {
                    f"{unit}R{address:02X}": f"{value:02X}"
                    for (unit, address), value in values.items()
                }
            )
            message = "simulated register predicate evaluated"
        elif observation_provider is not None:
            observed = observation_provider(number)
            outcome = (
                CheckoutOutcome.PASS
                if observed is True
                else CheckoutOutcome.FAIL
                if observed is False
                else CheckoutOutcome.INDETERMINATE
            )
            message = "simulated observation provider evaluated"
    except Exception as exc:
        outcome = CheckoutOutcome.INDETERMINATE
        message = f"actuator workflow failed: {exc}"
    finally:
        cleanup_errors: list[str] = []
        for operation in plan.cleanup:
            try:
                assert operation.address is not None and operation.value is not None
                receipt = session.client.write_register(
                    operation.address, operation.value, unit=operation.unit or "C"
                )
                observations["cleanup_requests"].append(receipt.request.hex().upper())
            except Exception as exc:
                cleanup_errors.append(str(exc))
        if cleanup_errors:
            outcome = CheckoutOutcome.INDETERMINATE
            observations["cleanup_errors"] = cleanup_errors
            message = "mandatory cleanup failed"
    return CheckoutResult(
        number,
        outcome,
        observations,
        message,
        _audit_span(session, checkpoint),
    )


def _audit_span(session: ControllerSession, checkpoint: int) -> AuditSpan | None:
    return session.audit.span(checkpoint) if session.audit is not None else None
