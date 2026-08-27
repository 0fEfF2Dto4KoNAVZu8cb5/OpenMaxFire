"""Offline firmware-loader planning and simulator-only execution.

This module models the binary protocol reconstructed from the preserved
BixCheck clients. It intentionally has no serial-port constructor and never
sends the normal-protocol ``CW0FC4`` bootloader-entry write. The executor
accepts only :class:`SimulatedLoaderTransport`, keeping physical flashing
unreachable while framing, retry, row-write, handoff, and failure behavior are
tested.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .audit import AuditSpan, AuditTrail
from .errors import CapabilityUnavailableError
from .firmware import (
    LOADER_CHECKSUM_ACCEPTED_RESPONSE,
    LOADER_CHECKSUM_REJECTED_RESPONSE,
    LOADER_COMPLETE_REQUEST,
    LOADER_COMPLETE_RESPONSE,
    LOADER_IDENTIFY_REQUEST,
    LOADER_IDENTIFY_RESPONSE,
    LOADER_WRITE_FAILED_RESPONSE,
    LOADER_WRITE_VERIFIED_RESPONSE,
    FirmwareCompatibility,
    FirmwareImage,
    ProgramBlock,
    assess_firmware_compatibility,
    build_program_blocks,
    loader_effective_word_address,
)
from .profiles import ControllerProfile
from .transport import Transport


class LoaderState(str, Enum):
    PLANNED = "planned"
    IDENTIFYING = "identifying"
    PROGRAMMING = "programming"
    COMPLETING = "completing"
    RECONNECTING = "reconnecting"
    COMPLETE = "complete"
    FAILED = "failed"
    BLOCKED = "blocked"


class LoaderAttemptOutcome(str, Enum):
    ACKNOWLEDGED = "acknowledged"
    CHECKSUM_REJECTED = "checksum_rejected_e8"
    WRITE_VERIFICATION_FAILED = "write_verification_failed_e5"
    TIMEOUT = "timeout"
    UNEXPECTED_RESPONSE = "unexpected_response"
    TERMINAL_TRANSMISSION_UNREAD = "terminal_transmission_unread"


@dataclass(frozen=True, slots=True)
class LoaderPolicy:
    """Bound simulation while preserving BixCheck's block-loop behavior.

    BixCheck accepts responses from one initial block transmission plus 29
    retries. Its control flow then transmits a 31st frame but aborts before
    accepting that response. The default therefore uses ``max_retries=29``
    and keeps the terminal transmission enabled. Identify remains bounded in
    simulation by the same accepted-attempt budget; BixCheck's real identify
    UI loop is operator-cancellable rather than limited to 30 probes.
    """

    max_retries: int = 29
    transmit_terminal_block_attempt: bool = True

    def __post_init__(self) -> None:
        if (
            isinstance(self.max_retries, bool)
            or not isinstance(self.max_retries, int)
            or not 0 <= self.max_retries <= 999
        ):
            raise ValueError("max_retries must be an integer between 0 and 999")
        if not isinstance(self.transmit_terminal_block_attempt, bool):
            raise TypeError("transmit_terminal_block_attempt must be a boolean")

    @property
    def max_accepted_attempts(self) -> int:
        return self.max_retries + 1


@dataclass(frozen=True, slots=True)
class LoaderPlan:
    profile_key: str
    image_filename: str
    image_sha256: str
    firmware_version: str | None
    compatibility: FirmwareCompatibility
    blocks: tuple[ProgramBlock, ...]
    live_executable: bool = False

    @property
    def simulator_executable(self) -> bool:
        return self.compatibility.valid_for_offline_planning and bool(self.blocks)

    @property
    def program_word_count(self) -> int:
        """Number of source words sent on the reconstructed wire protocol."""

        return sum(len(block.data) // 2 for block in self.blocks)

    @property
    def effective_program_word_count(self) -> int:
        return len(_effective_words_from_blocks(self.blocks))

    @property
    def relocated_word_count(self) -> int:
        return sum(
            1
            for address in _words_from_blocks(self.blocks)
            if loader_effective_word_address(address) not in (None, address)
        )

    @property
    def protected_skipped_word_count(self) -> int:
        return sum(
            1
            for address in _words_from_blocks(self.blocks)
            if loader_effective_word_address(address) is None
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "schema": "openmaxfire.loader-plan.v2",
            "profile_key": self.profile_key,
            "image_filename": self.image_filename,
            "image_sha256": self.image_sha256,
            "firmware_version": self.firmware_version,
            "block_count": len(self.blocks),
            "program_word_count": self.program_word_count,
            "effective_program_word_count": self.effective_program_word_count,
            "relocated_word_count": self.relocated_word_count,
            "protected_skipped_word_count": self.protected_skipped_word_count,
            "simulator_executable": self.simulator_executable,
            "live_executable": self.live_executable,
            "compatibility": self.compatibility.to_dict(),
            "blocks": [block.to_dict() for block in self.blocks],
            "safety_boundary": (
                "offline plan only; bootloader entry and physical serial execution are absent"
            ),
        }


@dataclass(frozen=True, slots=True)
class LoaderAttemptReceipt:
    attempt: int
    responses: tuple[bytes, ...]
    outcome: LoaderAttemptOutcome
    accepted_for_decision: bool = True

    def to_dict(self) -> dict[str, object]:
        return {
            "attempt": self.attempt,
            "responses_hex": [item.hex(" ").upper() for item in self.responses],
            "outcome": self.outcome.value,
            "accepted_for_decision": self.accepted_for_decision,
        }


@dataclass(frozen=True, slots=True)
class LoaderBlockReceipt:
    word_address: int
    byte_count: int
    attempts: int
    acknowledged: bool
    outcome: LoaderAttemptOutcome
    attempt_receipts: tuple[LoaderAttemptReceipt, ...] = ()

    @property
    def transmissions(self) -> int:
        return len(self.attempt_receipts) or self.attempts

    @property
    def accepted_attempts(self) -> int:
        if not self.attempt_receipts:
            return self.attempts
        return sum(item.accepted_for_decision for item in self.attempt_receipts)

    def to_dict(self) -> dict[str, object]:
        return {
            "word_address": f"0x{self.word_address:04X}",
            "byte_count": self.byte_count,
            "attempts": self.attempts,
            "transmissions": self.transmissions,
            "accepted_attempts": self.accepted_attempts,
            "acknowledged": self.acknowledged,
            "outcome": self.outcome.value,
            "attempt_receipts": [item.to_dict() for item in self.attempt_receipts],
        }


@dataclass(frozen=True, slots=True)
class LoaderResult:
    state: LoaderState
    image_sha256: str
    blocks_total: int
    blocks_completed: int
    retries: int
    memory_verified: bool
    block_receipts: tuple[LoaderBlockReceipt, ...]
    message: str
    audit_span: AuditSpan | None = None
    pic_side_blocks_verified: bool = False
    application_handoff: bool = False
    application_reconnected: bool = False

    @property
    def successful(self) -> bool:
        return (
            self.state is LoaderState.COMPLETE
            and self.memory_verified
            and self.pic_side_blocks_verified
            and self.application_handoff
            and self.application_reconnected
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "schema": "openmaxfire.loader-result.v2",
            "state": self.state.value,
            "image_sha256": self.image_sha256,
            "blocks_total": self.blocks_total,
            "blocks_completed": self.blocks_completed,
            "retries": self.retries,
            "memory_verified": self.memory_verified,
            "pic_side_blocks_verified": self.pic_side_blocks_verified,
            "application_handoff": self.application_handoff,
            "application_reconnected": self.application_reconnected,
            "successful": self.successful,
            "block_receipts": [item.to_dict() for item in self.block_receipts],
            "message": self.message,
            "audit_span": self.audit_span.to_dict() if self.audit_span else None,
            "evidence_boundary": (
                "simulator execution only; reconnect is an in-memory lifecycle transition"
            ),
        }


def build_loader_plan(
    image: FirmwareImage,
    profile: ControllerProfile,
    *,
    max_words: int = 16,
) -> LoaderPlan:
    compatibility = assess_firmware_compatibility(image, profile)
    return LoaderPlan(
        profile_key=profile.key,
        image_filename=image.filename,
        image_sha256=image.sha256,
        firmware_version=image.firmware_version,
        compatibility=compatibility,
        blocks=build_program_blocks(image, max_words=max_words),
    )


def _record_write(
    transport: Transport,
    request: bytes,
    audit: AuditTrail | None,
) -> None:
    if audit is not None:
        audit.record("tx", request)
    transport.write(request)


def _record_read(
    transport: Transport,
    audit: AuditTrail | None,
) -> bytes:
    chunk = transport.read(1)
    if audit is not None:
        audit.record("rx", chunk)
    return chunk


def _single_response_exchange(
    transport: Transport,
    request: bytes,
    expected: bytes,
    *,
    max_attempts: int,
    audit: AuditTrail | None,
) -> tuple[bool, tuple[LoaderAttemptReceipt, ...]]:
    receipts: list[LoaderAttemptReceipt] = []
    for attempt in range(1, max_attempts + 1):
        _record_write(transport, request, audit)
        response = _record_read(transport, audit)
        acknowledged = response == expected
        receipts.append(
            LoaderAttemptReceipt(
                attempt,
                (response,),
                (
                    LoaderAttemptOutcome.ACKNOWLEDGED
                    if acknowledged
                    else (
                        LoaderAttemptOutcome.TIMEOUT
                        if not response
                        else LoaderAttemptOutcome.UNEXPECTED_RESPONSE
                    )
                ),
            )
        )
        if acknowledged:
            return True, tuple(receipts)
    return False, tuple(receipts)


def _block_exchange(
    transport: Transport,
    block: ProgramBlock,
    policy: LoaderPolicy,
    audit: AuditTrail | None,
) -> tuple[bool, tuple[LoaderAttemptReceipt, ...]]:
    receipts: list[LoaderAttemptReceipt] = []
    for attempt in range(1, policy.max_accepted_attempts + 1):
        _record_write(transport, block.frame, audit)
        first = _record_read(transport, audit)
        responses = [first]
        if first == LOADER_CHECKSUM_REJECTED_RESPONSE:
            outcome = LoaderAttemptOutcome.CHECKSUM_REJECTED
        elif first == LOADER_CHECKSUM_ACCEPTED_RESPONSE:
            second = _record_read(transport, audit)
            responses.append(second)
            if second == LOADER_WRITE_VERIFIED_RESPONSE:
                outcome = LoaderAttemptOutcome.ACKNOWLEDGED
            elif second == LOADER_WRITE_FAILED_RESPONSE:
                outcome = LoaderAttemptOutcome.WRITE_VERIFICATION_FAILED
            elif not second:
                outcome = LoaderAttemptOutcome.TIMEOUT
            else:
                outcome = LoaderAttemptOutcome.UNEXPECTED_RESPONSE
        elif not first:
            outcome = LoaderAttemptOutcome.TIMEOUT
        else:
            outcome = LoaderAttemptOutcome.UNEXPECTED_RESPONSE
        receipts.append(LoaderAttemptReceipt(attempt, tuple(responses), outcome))
        if outcome is LoaderAttemptOutcome.ACKNOWLEDGED:
            return True, tuple(receipts)

    if policy.transmit_terminal_block_attempt:
        terminal_attempt = policy.max_accepted_attempts + 1
        _record_write(transport, block.frame, audit)
        receipts.append(
            LoaderAttemptReceipt(
                terminal_attempt,
                (),
                LoaderAttemptOutcome.TERMINAL_TRANSMISSION_UNREAD,
                accepted_for_decision=False,
            )
        )
    return False, tuple(receipts)


def execute_loader_plan(
    transport: Transport,
    plan: LoaderPlan,
    *,
    authorize: bool = False,
    policy: LoaderPolicy | None = None,
    audit: AuditTrail | None = None,
) -> LoaderResult:
    """Execute a reconstructed loader plan against the simulator only."""

    from .simulator import SimulatedLoaderTransport

    if not authorize:
        raise PermissionError("simulated firmware programming was not authorized")
    if not isinstance(transport, SimulatedLoaderTransport):
        raise CapabilityUnavailableError(
            "physical firmware-loader execution is unvalidated and blocked"
        )
    selected_policy = policy or LoaderPolicy()
    checkpoint = audit.checkpoint() if audit is not None else 0
    if not plan.simulator_executable:
        return LoaderResult(
            LoaderState.BLOCKED,
            plan.image_sha256,
            len(plan.blocks),
            0,
            0,
            False,
            (),
            "; ".join(plan.compatibility.blockers) or "loader plan is not executable",
            audit.span(checkpoint) if audit is not None else None,
        )

    receipts: list[LoaderBlockReceipt] = []
    total_retries = 0
    completed = 0
    state = LoaderState.IDENTIFYING
    try:
        acknowledged, identify_receipts = _single_response_exchange(
            transport,
            LOADER_IDENTIFY_REQUEST,
            LOADER_IDENTIFY_RESPONSE,
            max_attempts=selected_policy.max_accepted_attempts,
            audit=audit,
        )
        total_retries += max(0, len(identify_receipts) - 1)
        if not acknowledged:
            return _loader_failure(
                plan,
                completed,
                total_retries,
                receipts,
                "loader identify timed out within the simulator safety bound",
                audit,
                checkpoint,
            )

        state = LoaderState.PROGRAMMING
        for block in plan.blocks:
            acknowledged, attempt_receipts = _block_exchange(
                transport, block, selected_policy, audit
            )
            accepted_attempts = sum(
                item.accepted_for_decision for item in attempt_receipts
            )
            total_retries += max(0, accepted_attempts - 1)
            final_decision = next(
                (
                    item.outcome
                    for item in reversed(attempt_receipts)
                    if item.accepted_for_decision
                ),
                LoaderAttemptOutcome.UNEXPECTED_RESPONSE,
            )
            receipt = LoaderBlockReceipt(
                block.word_address,
                len(block.data),
                len(attempt_receipts),
                acknowledged,
                final_decision,
                attempt_receipts,
            )
            receipts.append(receipt)
            if not acknowledged:
                return _loader_failure(
                    plan,
                    completed,
                    total_retries,
                    receipts,
                    (
                        f"block 0x{block.word_address:04X} failed after "
                        f"{receipt.accepted_attempts} accepted attempts "
                        f"({final_decision.value})"
                    ),
                    audit,
                    checkpoint,
                )
            completed += 1

        state = LoaderState.COMPLETING
        acknowledged, _ = _single_response_exchange(
            transport,
            LOADER_COMPLETE_REQUEST,
            LOADER_COMPLETE_RESPONSE,
            max_attempts=1,
            audit=audit,
        )
        if not acknowledged:
            return _loader_failure(
                plan,
                completed,
                total_retries,
                receipts,
                "completion acknowledgement failed; BixCheck does not resend ED",
                audit,
                checkpoint,
                pic_side_blocks_verified=True,
            )

        expected_words = _effective_words_from_blocks(plan.blocks)
        protected_only_addresses = {
            address
            for address in _words_from_blocks(plan.blocks)
            if loader_effective_word_address(address) is None
            and address not in expected_words
        }
        memory_verified = (
            all(
                transport.flash_words.get(address, 0x3FFF) == value
                for address, value in expected_words.items()
            )
            and all(
                transport.flash_words.get(address, 0x3FFF)
                == transport.initial_flash_words.get(address, 0x3FFF)
                for address in protected_only_addresses
            )
            and transport.preserved_neighbors_verified
        )
        application_handoff = transport.application_running
        state = LoaderState.RECONNECTING
        application_reconnected = transport.reconnect_application()
        complete = memory_verified and application_handoff and application_reconnected
        state = LoaderState.COMPLETE if complete else LoaderState.FAILED
        return LoaderResult(
            state,
            plan.image_sha256,
            len(plan.blocks),
            completed,
            total_retries,
            memory_verified,
            tuple(receipts),
            (
                "simulated loader completed, preserved row neighbors, handed off, and reconnected"
                if complete
                else "simulated programming completed but memory, handoff, or reconnect verification failed"
            ),
            audit.span(checkpoint) if audit is not None else None,
            pic_side_blocks_verified=True,
            application_handoff=application_handoff,
            application_reconnected=application_reconnected,
        )
    except Exception as exc:
        return _loader_failure(
            plan,
            completed,
            total_retries,
            receipts,
            f"{state.value} failed: {exc}",
            audit,
            checkpoint,
            pic_side_blocks_verified=completed == len(plan.blocks),
            application_handoff=transport.application_running,
            application_reconnected=transport.application_reconnected,
        )


def _words_from_blocks(blocks: tuple[ProgramBlock, ...]) -> dict[int, int]:
    words: dict[int, int] = {}
    for block in blocks:
        for offset in range(0, len(block.data), 2):
            words[block.word_address + offset // 2] = (
                block.data[offset] | (block.data[offset + 1] << 8)
            )
    return words


def _effective_words_from_blocks(
    blocks: tuple[ProgramBlock, ...],
) -> dict[int, int]:
    words: dict[int, int] = {}
    for source_address, value in _words_from_blocks(blocks).items():
        target_address = loader_effective_word_address(source_address)
        if target_address is not None:
            words[target_address] = value
    return words


def _loader_failure(
    plan: LoaderPlan,
    completed: int,
    retries: int,
    receipts: list[LoaderBlockReceipt],
    message: str,
    audit: AuditTrail | None,
    checkpoint: int,
    *,
    pic_side_blocks_verified: bool = False,
    application_handoff: bool = False,
    application_reconnected: bool = False,
) -> LoaderResult:
    return LoaderResult(
        LoaderState.FAILED,
        plan.image_sha256,
        len(plan.blocks),
        completed,
        retries,
        False,
        tuple(receipts),
        message,
        audit.span(checkpoint) if audit is not None else None,
        pic_side_blocks_verified=pic_side_blocks_verified,
        application_handoff=application_handoff,
        application_reconnected=application_reconnected,
    )


def loader_simulation_supported() -> bool:
    return True


def live_loader_supported() -> bool:
    return False


__all__ = [
    "LoaderAttemptOutcome",
    "LoaderAttemptReceipt",
    "LoaderBlockReceipt",
    "LoaderPlan",
    "LoaderPolicy",
    "LoaderResult",
    "LoaderState",
    "build_loader_plan",
    "execute_loader_plan",
    "live_loader_supported",
    "loader_simulation_supported",
]
