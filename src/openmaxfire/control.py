"""Typed normal-control planning and outcome models.

Plans are deliberately separate from transmission.  No known controller profile
marks normal control as physically validated, so generated operations remain
non-executable until live state/result semantics are established.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .audit import AuditSpan
from .models import StoveSnapshot
from .profiles import Capability, CapabilityState, ControllerProfile
from .protocol import REMOTE_BUTTON_REGISTER, RemoteButton
from .transactions import TransactionOperation


class ControlAction(str, Enum):
    OFF = "off"
    ON = "on"
    UP = "up"
    DOWN = "down"
    SET_LEVEL = "set_level"


class ControlOutcome(str, Enum):
    ALREADY_SATISFIED = "already_satisfied"
    SENT = "sent"
    ACCEPTED = "accepted"
    VERIFIED = "verified"
    REJECTED = "rejected"
    TIMED_OUT = "timed_out"
    INDETERMINATE = "indeterminate"


@dataclass(frozen=True, slots=True)
class ControlPlan:
    profile_key: str
    action: ControlAction
    target_level: int | None
    operations: tuple[TransactionOperation, ...]
    already_satisfied: bool
    executable: bool
    blockers: tuple[str, ...]
    verification: str

    def to_dict(self) -> dict[str, object]:
        return {
            "schema": "openmaxfire.control-plan.v1",
            "profile_key": self.profile_key,
            "action": self.action.value,
            "target_level": self.target_level,
            "operations": [operation.to_dict() for operation in self.operations],
            "already_satisfied": self.already_satisfied,
            "executable": self.executable,
            "blockers": list(self.blockers),
            "verification": self.verification,
        }


@dataclass(frozen=True, slots=True)
class ControlResult:
    action: ControlAction
    outcome: ControlOutcome
    requests: tuple[bytes, ...]
    before: StoveSnapshot | None
    after: StoveSnapshot | None
    message: str = ""
    audit_span: AuditSpan | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "schema": "openmaxfire.control-result.v1",
            "action": self.action.value,
            "outcome": self.outcome.value,
            "requests_hex": [request.hex(" ").upper() for request in self.requests],
            "before": self.before.to_dict() if self.before else None,
            "after": self.after.to_dict() if self.after else None,
            "message": self.message,
            "audit_span": self.audit_span.to_dict() if self.audit_span else None,
        }


def _operation(button: RemoteButton) -> TransactionOperation:
    return TransactionOperation(
        op="write",
        unit="C",
        address=REMOTE_BUTTON_REGISTER,
        value=int(button),
        verify=False,
    )


def plan_control(
    action: ControlAction | str,
    profile: ControllerProfile,
    snapshot: StoveSnapshot | None = None,
    *,
    target_level: int | None = None,
) -> ControlPlan:
    """Create an idempotence-aware offline normal-control plan."""

    action = ControlAction(action)
    if action is ControlAction.SET_LEVEL:
        if isinstance(target_level, bool) or not isinstance(target_level, int):
            raise ValueError("set_level requires an integer target_level")
        if not 1 <= target_level <= 8:
            raise ValueError("target_level must be between 1 and 8")
    elif target_level is not None:
        raise ValueError("target_level is valid only with set_level")

    already = False
    operations: list[TransactionOperation] = []
    verification = "observe a fresh operating-state transition"
    if action is ControlAction.OFF:
        already = bool(snapshot and snapshot.operating_state and snapshot.operating_state.phase == "off")
        if not already:
            operations.append(_operation(RemoteButton.OFF))
        verification = "observe the controller enter the Off family"
    elif action is ControlAction.ON:
        already = bool(
            snapshot
            and snapshot.operating_state
            and snapshot.operating_state.phase
            in ("prefill", "started", "starting", "ignited", "operating", "ramping")
        )
        if not already:
            operations.append(_operation(RemoteButton.ON))
        verification = "observe startup, operating, or ramping state"
    elif action is ControlAction.UP:
        operations.append(_operation(RemoteButton.UP))
        verification = "observe target heat level increase"
    elif action is ControlAction.DOWN:
        operations.append(_operation(RemoteButton.DOWN))
        verification = "observe target heat level decrease"
    else:
        current = snapshot.target_heat_level if snapshot else None
        if current is None:
            raise ValueError("set_level requires a snapshot with a known target heat level")
        already = current == target_level
        button = RemoteButton.UP if target_level > current else RemoteButton.DOWN
        operations.extend(_operation(button) for _ in range(abs(target_level - current)))
        verification = f"observe target heat level {target_level}"

    blockers: list[str] = []
    state = profile.capabilities.state(Capability.NORMAL_CONTROL)
    if state is not CapabilityState.AVAILABLE and operations:
        blockers.append(f"normal control capability is {state.value}")
    if snapshot is not None and not snapshot.fresh and operations:
        blockers.append("controller snapshot is stale")
    if snapshot is not None and snapshot.profile_key not in (None, profile.key):
        blockers.append("snapshot profile does not match requested controller profile")
    return ControlPlan(
        profile_key=profile.key,
        action=action,
        target_level=target_level,
        operations=tuple(operations),
        already_satisfied=already,
        executable=not blockers,
        blockers=tuple(blockers),
        verification=verification,
    )
