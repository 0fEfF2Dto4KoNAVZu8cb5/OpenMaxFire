"""Guarded physical J3 firmware-flashing workflow.

The resident MaxFire loader is a separate binary protocol from the normal
ASCII service protocol.  This module is deliberately narrow: it accepts only
the exact authenticated factory Downloader images in :mod:`firmware_catalog`,
never sends the application's ``CW0FC4`` reset command, and requires a manual
power cycle plus structured safety interlocks.

Physical execution is experimental until it is exercised on an externally
recoverable spare PIC/controller.  The code nevertheless fails closed at every
boundary that can be checked by software: current identity, image SHA-256,
image delivery layout, fixed 9,600-baud loader transport, per-block replies,
target application identity, and unchanged data EEPROM.
"""

from __future__ import annotations

import json
import hashlib
import math
import os
import time
import uuid
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Callable, Mapping, TextIO

from .audit import AuditTrail
from .backup import build_eeprom_backup, save_json_document
from .client import MaxFireClient, StoveIdentity
from .errors import SafetyInterlockError, UnsupportedControllerError, VerificationError
from .firmware import (
    LOADER_CHECKSUM_ACCEPTED_RESPONSE,
    LOADER_CHECKSUM_REJECTED_RESPONSE,
    LOADER_COMPLETE_REQUEST,
    LOADER_COMPLETE_RESPONSE,
    LOADER_IDENTIFY_REQUEST,
    LOADER_IDENTIFY_RESPONSE,
    LOADER_WRITE_FAILED_RESPONSE,
    LOADER_WRITE_VERIFIED_RESPONSE,
    FirmwareImage,
    FirmwareVariant,
    build_program_blocks,
)
from .firmware_catalog import FIRMWARE_CORPUS, FirmwareCorpusEntry
from .loader import (
    LoaderAttemptOutcome,
    LoaderAttemptReceipt,
    LoaderBlockReceipt,
    LoaderPlan,
    LoaderState,
    build_loader_plan,
    execute_loader_plan,
    LoaderPolicy,
)
from .profiles import ControllerProfile, PROFILES_BY_KEY, select_profile
from .protocol import AddressedResponse, ProtocolError, TelemetryResponse
from .transport import Transport


LOADER_BAUDRATE = 9600
# Loader receive() seeds TMR1H with 0x0B and permits three Fosc/4 overflows.
# At the photographed 10.000 MHz oscillator this is about 78 ms.  Host probes
# therefore need a much shorter read timeout than normal register traffic.
LOADER_BOOT_WINDOW_ESTIMATE_SECONDS = 0.078
RECOVERY_MARKER_FILENAME = "RECOVERY_REQUIRED.txt"
FLASH_STATE_FILENAME = "state.json"
RECOVERY_MANIFEST_FILENAME = "recovery-manifest.json"
RECOVERY_DELEGATION_FILENAME = "RECOVERY_DELEGATED_TO.json"
UNSUPPORTED_FIRMWARE_MESSAGE = (
    "firmware 2.73 is not preserved or supported; contact "
    "contact@openmaxfire.com and see https://github.com/OpenMaxFire/OpenMaxFire"
)


@dataclass(frozen=True, slots=True)
class ApprovedFirmware:
    """One exact factory image approved for the J3 resident loader."""

    entry: FirmwareCorpusEntry
    target_profile_key: str
    application_baudrate: int
    block_count: int
    wire_sha256: str

    @property
    def firmware_version(self) -> str:
        return self.entry.firmware_version

    @property
    def target_profile(self) -> ControllerProfile:
        return PROFILES_BY_KEY[self.target_profile_key]

    def to_dict(self) -> dict[str, object]:
        return {
            "firmware_version": self.firmware_version,
            "filename": self.entry.filename,
            "sha256": self.entry.sha256,
            "variant": self.entry.variant.value,
            "target_profile_key": self.target_profile_key,
            "loader_baudrate": LOADER_BAUDRATE,
            "application_baudrate": self.application_baudrate,
            "block_count": self.block_count,
            "wire_sha256": self.wire_sha256,
        }


_TARGET_PROFILE_BY_VERSION = {
    "2.06": "fw206-format05",
    "2.70": "fw270-format07",
    "2.71": "fw271-format07",
}

_ALLOWED_FORWARD_TRANSITIONS = {
    ("2.02", "2.06"),
    ("2.06", "2.70"),
    ("2.70", "2.71"),
}

_WIRE_AUTHENTICATION_BY_VERSION = {
    "2.06": (476, "2f0dbb4a61f8a290e081336845ba91faea76fe2602630a75092f90697baccc1e"),
    "2.70": (481, "aefae97af8eab83c4f7587fe1bdce3d601a66a6ea9c8d528dd37bd520f4a36c1"),
    "2.71": (486, "cf117ab66472e6ed13e455164e6708fa93a6a45889a7afe2cad654cd7c4ce759"),
}

APPROVED_FIRMWARE: Mapping[str, ApprovedFirmware] = {
    entry.sha256: ApprovedFirmware(
        entry,
        _TARGET_PROFILE_BY_VERSION[entry.firmware_version],
        PROFILES_BY_KEY[_TARGET_PROFILE_BY_VERSION[entry.firmware_version]].baudrates[0],
        _WIRE_AUTHENTICATION_BY_VERSION[entry.firmware_version][0],
        _WIRE_AUTHENTICATION_BY_VERSION[entry.firmware_version][1],
    )
    for entry in FIRMWARE_CORPUS
    if entry.firmware_version in _TARGET_PROFILE_BY_VERSION
    and entry.variant in (FirmwareVariant.DOWNLOADER, FirmwareVariant.EMBEDDED)
}


def _looks_like_273(image: FirmwareImage) -> bool:
    normalized = image.filename.casefold().replace("_", "").replace("-", "")
    return image.firmware_version == "2.73" or "0273" in normalized or "2.73" in normalized


def approve_live_firmware(image: FirmwareImage) -> ApprovedFirmware:
    """Authenticate an exact vendor J3 image or fail without a bypass."""

    if _looks_like_273(image):
        raise UnsupportedControllerError(UNSUPPORTED_FIRMWARE_MESSAGE)
    approved = APPROVED_FIRMWARE.get(image.sha256)
    if approved is None:
        raise VerificationError(
            "firmware SHA-256 is not in the authenticated J3 allowlist; unknown, "
            "modified, PICkit, and unpreserved images are blocked"
        )
    entry = approved.entry
    mismatches: list[str] = []
    if image.filename != entry.filename:
        mismatches.append("filename")
    if image.firmware_version != entry.firmware_version:
        mismatches.append("firmware version")
    if image.variant is not entry.variant:
        mismatches.append("delivery variant")
    if len(image.program_words) != entry.program_words:
        mismatches.append("program-word count")
    if image.configuration_word != entry.configuration_word:
        mismatches.append("configuration word")
    if mismatches:
        raise VerificationError(
            "authenticated firmware metadata mismatch: " + ", ".join(mismatches)
        )
    blocks = build_program_blocks(image)
    if len(blocks) != approved.block_count or _loader_frames_sha256(blocks) != approved.wire_sha256:
        raise VerificationError("authenticated firmware loader-frame sequence mismatch")
    return approved


def _loader_frames_sha256(blocks) -> str:
    digest = hashlib.sha256()
    for block in blocks:
        frame = block.frame
        digest.update(len(frame).to_bytes(2, "big"))
        digest.update(frame)
    return digest.hexdigest()


@dataclass(frozen=True, slots=True)
class FlashSafetyInterlocks:
    """Human-observable prerequisites that software cannot infer from J3."""

    stove_cold_and_off: bool = False
    igniters_physically_unplugged: bool = False
    correct_5v_ttl_wiring: bool = False
    j3_pin3_disconnected: bool = False
    adapter_vcc_disconnected: bool = False
    pickit_recovery_tested_on_spare: bool = False
    computer_power_stable: bool = False
    stove_power_stable: bool = False
    calibration_plan_ready: bool = False
    downgrade_stale_flash_accepted: bool = False
    recovery_target_matches_backup: bool = False

    def missing(
        self,
        *,
        calibration_required: bool,
        downgrade: bool,
        recovery_mode: bool = False,
    ) -> tuple[str, ...]:
        requirements = {
            "stove is cold and OFF": self.stove_cold_and_off,
            "both igniters are physically unplugged": self.igniters_physically_unplugged,
            "J3 uses the verified 5 V TTL ground/TX/RX wiring": self.correct_5v_ttl_wiring,
            "J3 pin 3 is disconnected": self.j3_pin3_disconnected,
            "adapter VCC is disconnected": self.adapter_vcc_disconnected,
            "PICkit recovery was tested on a spare PIC/controller": (
                self.pickit_recovery_tested_on_spare
            ),
            "computer power is stable and the lid will remain open": (
                self.computer_power_stable
            ),
            "stove AC power will remain stable during programming": (
                self.stove_power_stable
            ),
        }
        if calibration_required:
            requirements["post-flash calibration/Format plan is ready"] = (
                self.calibration_plan_ready
            )
        if downgrade:
            requirements["sparse-downgrade stale Flash risk is accepted"] = (
                self.downgrade_stale_flash_accepted
            )
        if recovery_mode:
            requirements["physical recovery target matches the saved backup"] = (
                self.recovery_target_matches_backup
            )
        return tuple(label for label, satisfied in requirements.items() if not satisfied)

    def validate(
        self,
        *,
        calibration_required: bool,
        downgrade: bool,
        recovery_mode: bool = False,
    ) -> None:
        missing = self.missing(
            calibration_required=calibration_required,
            downgrade=downgrade,
            recovery_mode=recovery_mode,
        )
        if missing:
            raise SafetyInterlockError(
                "live flashing prerequisites are not satisfied: " + "; ".join(missing)
            )

    def to_dict(self) -> dict[str, bool]:
        return {
            "stove_cold_and_off": self.stove_cold_and_off,
            "igniters_physically_unplugged": self.igniters_physically_unplugged,
            "correct_5v_ttl_wiring": self.correct_5v_ttl_wiring,
            "j3_pin3_disconnected": self.j3_pin3_disconnected,
            "adapter_vcc_disconnected": self.adapter_vcc_disconnected,
            "pickit_recovery_tested_on_spare": self.pickit_recovery_tested_on_spare,
            "computer_power_stable": self.computer_power_stable,
            "stove_power_stable": self.stove_power_stable,
            "calibration_plan_ready": self.calibration_plan_ready,
            "downgrade_stale_flash_accepted": self.downgrade_stale_flash_accepted,
            "recovery_target_matches_backup": self.recovery_target_matches_backup,
        }


def _version_key(version: str) -> tuple[int, int]:
    major, minor = version.split(".", 1)
    return int(major), int(minor)


@dataclass(frozen=True, slots=True)
class LiveLoaderPolicy:
    """Outcome-specific retry limits for the physical loader.

    Checksum rejection proves no write began. A timeout before ``E7`` is still
    ambiguous because a reply can be lost, so only the identical row is ever
    replayed. A timeout after an observed ``E7`` receives one cautious replay.
    ``E5`` already includes the PIC loader's two internal row-write attempts:
    one host retry is allowed, while a second ``E5`` anywhere in the session
    aborts as a likely systemic power/contact/PIC problem. Unexpected bytes and
    transport errors are never retried blindly.
    """

    identify_attempts: int = 1500
    checksum_retries: int = 2
    pre_accept_timeout_retries: int = 2
    post_accept_timeout_retries: int = 1
    write_failure_retries: int = 1
    max_block_transmissions: int = 4
    retry_delay: float = 0.020
    probe_timeout: float = 0.020
    response_timeout: float = 0.50

    def __post_init__(self) -> None:
        if (
            isinstance(self.identify_attempts, bool)
            or not isinstance(self.identify_attempts, int)
            or not 1 <= self.identify_attempts <= 5000
        ):
            raise ValueError("identify_attempts must be between 1 and 5000")
        retry_fields = {
            "checksum_retries": self.checksum_retries,
            "pre_accept_timeout_retries": self.pre_accept_timeout_retries,
            "post_accept_timeout_retries": self.post_accept_timeout_retries,
            "write_failure_retries": self.write_failure_retries,
        }
        for name, value in retry_fields.items():
            if (
                isinstance(value, bool)
                or not isinstance(value, int)
                or not 0 <= value <= 3
            ):
                raise ValueError(f"{name} must be between 0 and 3")
        if (
            isinstance(self.max_block_transmissions, bool)
            or not isinstance(self.max_block_transmissions, int)
            or not 1 <= self.max_block_transmissions <= 5
        ):
            raise ValueError("max_block_transmissions must be between 1 and 5")
        if (
            not isinstance(self.retry_delay, (int, float))
            or not math.isfinite(self.retry_delay)
            or self.retry_delay < 0
            or self.retry_delay > 5
        ):
            raise ValueError("retry_delay must be between 0 and 5 seconds")
        if (
            not isinstance(self.probe_timeout, (int, float))
            or not math.isfinite(self.probe_timeout)
            or not 0.001 <= self.probe_timeout <= 0.050
        ):
            raise ValueError("probe_timeout must be between 0.001 and 0.050 seconds")
        if (
            not isinstance(self.response_timeout, (int, float))
            or not math.isfinite(self.response_timeout)
            or not 0.05 <= self.response_timeout <= 5
        ):
            raise ValueError("response_timeout must be between 0.05 and 5 seconds")


class FlashJournal:
    """Crash-resistant state journal separate from the byte-exact audit."""

    SCHEMA = "openmaxfire.flash-journal.v1"

    def __init__(
        self,
        path: str | Path,
        *,
        metadata: Mapping[str, object],
    ):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._stream: TextIO = self.path.open("x", encoding="utf-8", newline="\n")
        self._sequence = 0
        self.record("session", metadata=dict(metadata))

    def record(self, event: str, **fields: object) -> None:
        if not event:
            raise ValueError("journal event name cannot be empty")
        self._sequence += 1
        document = {
            **fields,
            "schema": self.SCHEMA,
            "sequence": self._sequence,
            "created_utc": datetime.now(timezone.utc).isoformat(),
            "monotonic_ns": time.monotonic_ns(),
            "event": event,
        }
        self._stream.write(json.dumps(document, sort_keys=True) + "\n")
        self._stream.flush()
        os.fsync(self._stream.fileno())

    def close(self) -> None:
        if not self._stream.closed:
            self._stream.close()


class FlashSessionStatus(str, Enum):
    """Durable, operator-facing state of one physical flash attempt."""

    INITIALIZING = "initializing"
    PREPARED = "prepared"
    REHEARSAL_ARMED = "rehearsal_armed"
    REHEARSAL_FAILED = "rehearsal_failed_no_flash_written"
    REHEARSAL_COMPLETE = "rehearsal_complete_no_flash_written"
    PROGRAMMING = "programming_recovery_required_until_verified"
    RECOVERY_REQUIRED = "recovery_required"
    VERIFYING = "verifying_recovery_still_available"
    CALIBRATION_REQUIRED = "programming_verified_calibration_required"
    COMPLETE = "complete_verified"
    ABORTED_SAFE = "aborted_before_programming"
    FAILED_SAFE = "failed_before_programming"


def _fsync_directory(path: Path) -> None:
    """Best-effort directory durability on platforms that support it."""

    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
    try:
        descriptor = os.open(path, flags)
    except OSError:
        return
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _atomic_write_bytes(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    try:
        with temporary.open("xb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        _fsync_directory(path.parent)
    finally:
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass


def _atomic_write_json(path: Path, document: Mapping[str, object]) -> None:
    encoded = (json.dumps(dict(document), indent=2, sort_keys=True) + "\n").encode(
        "utf-8"
    )
    _atomic_write_bytes(path, encoded)


def _exclusive_write_json(path: Path, document: Mapping[str, object]) -> None:
    """Create one small coordination record without replacing a peer's file."""

    encoded = (json.dumps(dict(document), indent=2, sort_keys=True) + "\n").encode(
        "utf-8"
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    try:
        with os.fdopen(descriptor, "wb", closefd=True) as stream:
            descriptor = -1
            stream.write(encoded)
            stream.flush()
            os.fsync(stream.fileno())
    finally:
        if descriptor >= 0:
            os.close(descriptor)
    _fsync_directory(path.parent)


class FlashSessionState:
    """Atomically updated state plus a conspicuous recovery marker.

    The marker is created *before* the first possible ``E3`` transmission and
    is removed only after target identity and unchanged EEPROM are verified.
    A killed process therefore leaves a self-contained recovery instruction
    beside the exact firmware copy and pre-flash backup.
    """

    SCHEMA = "openmaxfire.flash-session-state.v1"

    def __init__(self, directory: str | Path, *, metadata: Mapping[str, object]):
        self.directory = Path(directory)
        self.path = self.directory / FLASH_STATE_FILENAME
        self.marker_path = self.directory / RECOVERY_MARKER_FILENAME
        self._sequence = 0
        self._metadata = dict(metadata)
        self.transition(
            FlashSessionStatus.INITIALIZING,
            message="session created; no firmware block has been sent",
            recovery_required=False,
        )

    def transition(
        self,
        status: FlashSessionStatus,
        *,
        message: str,
        recovery_required: bool,
        **fields: object,
    ) -> Mapping[str, object]:
        if not isinstance(status, FlashSessionStatus):
            raise TypeError("status must be a FlashSessionStatus")
        if not isinstance(message, str) or not message.strip():
            raise ValueError("flash-session state message cannot be empty")
        self._sequence += 1
        document: dict[str, object] = {
            **fields,
            "schema": self.SCHEMA,
            "sequence": self._sequence,
            "updated_utc": datetime.now(timezone.utc).isoformat(),
            "status": status.value,
            "recovery_required": recovery_required,
            "message": message.strip(),
            "metadata": dict(self._metadata),
        }
        if recovery_required:
            marker = (
                "OPENMAXFIRE RECOVERY REQUIRED\n\n"
                "Do not operate the stove or reconnect the igniters. Do not delete or "
                "edit this directory. Start a new flash session with "
                f"--recover-from-session {self.directory} so the exact preserved image "
                "is replayed from block zero. J3 pin 3 and adapter VCC must remain "
                "disconnected.\n"
            ).encode("utf-8")
            _atomic_write_bytes(self.marker_path, marker)
        _atomic_write_json(self.path, document)
        if not recovery_required and self.marker_path.exists():
            self.marker_path.unlink()
            _fsync_directory(self.directory)
        return document


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def preserve_recovery_bundle(
    source_image: str | Path,
    image: FirmwareImage,
    preparation: Mapping[str, object],
    *,
    session_dir: str | Path,
) -> Mapping[str, object]:
    """Preserve the exact approved HEX and hash-bound preflight artifacts."""

    source = Path(source_image)
    directory = Path(session_dir)
    preparation_path = directory / "preparation.json"
    backup_path = directory / "eeprom-before.json"
    if not preparation_path.is_file() or not backup_path.is_file():
        raise VerificationError("recovery bundle requires preparation and EEPROM backup")
    rescue = directory / "rescue"
    rescue.mkdir(parents=False, exist_ok=False)
    raw = source.read_bytes()
    if hashlib.sha256(raw).hexdigest() != image.sha256:
        raise VerificationError("firmware file changed after it was authenticated")
    destination = rescue / image.filename
    if destination.exists():
        raise FileExistsError(destination)
    _atomic_write_bytes(destination, raw)
    if _file_sha256(destination) != image.sha256:
        raise VerificationError("preserved recovery image failed its SHA-256 readback")

    manifest: dict[str, object] = {
        "schema": "openmaxfire.recovery-manifest.v1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "firmware_filename": image.filename,
        "firmware_sha256": image.sha256,
        "firmware_size": len(raw),
        "preparation_sha256": _file_sha256(preparation_path),
        "eeprom_backup_sha256": _file_sha256(backup_path),
        "current_profile": preparation.get("current_profile", {}).get("key")
        if isinstance(preparation.get("current_profile"), Mapping)
        else None,
        "target_profile": preparation.get("approved_firmware", {}).get(
            "target_profile_key"
        )
        if isinstance(preparation.get("approved_firmware"), Mapping)
        else None,
        "replay_rule": "exact image from block zero; arbitrary checkpoint resume forbidden",
    }
    _atomic_write_json(rescue / RECOVERY_MANIFEST_FILENAME, manifest)
    return manifest


def load_recovery_bundle(
    session_dir: str | Path,
    *,
    supplied_image: str | Path | None = None,
) -> tuple[FirmwareImage, Mapping[str, object], Mapping[str, object], Mapping[str, object]]:
    """Authenticate a self-contained prior session for exact-image replay."""

    directory = Path(session_dir)
    rescue = directory / "rescue"
    delegation_path = directory / RECOVERY_DELEGATION_FILENAME
    if delegation_path.exists():
        try:
            delegation = json.loads(delegation_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            delegation = {}
        successor = (
            delegation.get("recovery_session")
            if isinstance(delegation, Mapping)
            else None
        )
        detail = f"; use {successor}" if isinstance(successor, str) else ""
        raise VerificationError(
            "recovery responsibility was already delegated to a newer session"
            + detail
        )
    marker_path = directory / RECOVERY_MARKER_FILENAME
    state_path = directory / FLASH_STATE_FILENAME
    try:
        state = json.loads(state_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise VerificationError(
            "recovery source has no readable durable flash state"
        ) from exc
    if (
        not marker_path.is_file()
        or not isinstance(state, Mapping)
        or state.get("schema") != FlashSessionState.SCHEMA
        or state.get("recovery_required") is not True
    ):
        raise VerificationError(
            "recovery source is not marked as an unresolved interrupted session"
        )
    manifest_path = rescue / RECOVERY_MANIFEST_FILENAME
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise VerificationError(
            "recovery session has no readable authenticated recovery manifest"
        ) from exc
    if not isinstance(manifest, Mapping) or manifest.get("schema") != (
        "openmaxfire.recovery-manifest.v1"
    ):
        raise VerificationError("recovery manifest schema is not recognized")
    filename = manifest.get("firmware_filename")
    expected_sha = manifest.get("firmware_sha256")
    if (
        not isinstance(filename, str)
        or Path(filename).name != filename
        or not isinstance(expected_sha, str)
    ):
        raise VerificationError("recovery manifest firmware identity is invalid")
    state_metadata = state.get("metadata")
    if (
        not isinstance(state_metadata, Mapping)
        or state_metadata.get("image_sha256") != expected_sha
    ):
        raise VerificationError(
            "recovery state and manifest identify different firmware images"
        )
    image_path = rescue / filename
    preparation_path = directory / "preparation.json"
    backup_path = directory / "eeprom-before.json"
    checks = (
        (image_path, expected_sha, "firmware"),
        (preparation_path, manifest.get("preparation_sha256"), "preparation"),
        (backup_path, manifest.get("eeprom_backup_sha256"), "EEPROM backup"),
    )
    for path, expected, label in checks:
        if not isinstance(expected, str) or not path.is_file():
            raise VerificationError(f"recovery {label} artifact is missing")
        if _file_sha256(path) != expected:
            raise VerificationError(f"recovery {label} artifact SHA-256 mismatch")
    expected_size = manifest.get("firmware_size")
    if (
        isinstance(expected_size, bool)
        or not isinstance(expected_size, int)
        or expected_size < 1
        or image_path.stat().st_size != expected_size
    ):
        raise VerificationError("recovery firmware size does not match its manifest")
    image = FirmwareImage.load(image_path)
    approved = approve_live_firmware(image)
    if image.sha256 != expected_sha:
        raise VerificationError("recovery image does not match its manifest")
    if supplied_image is not None:
        supplied = FirmwareImage.load(supplied_image)
        approve_live_firmware(supplied)
        if supplied.sha256 != image.sha256:
            raise VerificationError(
                "supplied recovery image differs from the exact session image"
            )
    try:
        preparation = json.loads(preparation_path.read_text(encoding="utf-8"))
        backup = json.loads(backup_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise VerificationError("recovery JSON artifact is malformed") from exc
    if not isinstance(preparation, Mapping) or not isinstance(backup, Mapping):
        raise VerificationError("recovery artifacts must be JSON objects")
    approved_document = preparation.get("approved_firmware")
    plan_document = preparation.get("loader_plan")
    current_document = preparation.get("current_profile")
    if (
        not isinstance(approved_document, Mapping)
        or approved_document.get("sha256") != image.sha256
        or approved_document.get("filename") != image.filename
        or approved_document.get("target_profile_key") != approved.target_profile_key
        or approved_document.get("wire_sha256") != approved.wire_sha256
        or approved_document.get("block_count") != approved.block_count
        or not isinstance(plan_document, Mapping)
        or plan_document.get("image_sha256") != image.sha256
        or plan_document.get("profile_key") != manifest.get("current_profile")
        or not isinstance(current_document, Mapping)
        or current_document.get("key") != manifest.get("current_profile")
        or manifest.get("target_profile") != approved.target_profile_key
    ):
        raise VerificationError(
            "recovery preparation, manifest, and approved firmware do not agree"
        )
    backup_identity = _backup_identity(backup)
    backup_profile = select_profile(backup_identity)
    backup_eeprom = _backup_eeprom(backup)
    if (
        backup_profile is None
        or backup_profile.key != manifest.get("current_profile")
        or preparation.get("current_identity") != backup_identity.to_dict()
        or preparation.get("eeprom_before_sha256") != _eeprom_sha256(backup_eeprom)
    ):
        raise VerificationError(
            "recovery preparation and EEPROM backup identify different controllers"
        )
    return image, preparation, backup, manifest


def delegate_recovery_source(
    source_session: str | Path,
    recovery_session: str | Path,
    *,
    image_sha256: str,
) -> Mapping[str, object]:
    """Atomically hand unresolved recovery responsibility to a new session.

    The new session must already contain its own recovery marker and exact
    rescue bundle. A failed recovery is then continued from that newer session,
    while the old bundle cannot be replayed again accidentally.
    """

    source = Path(source_session)
    successor = Path(recovery_session)
    successor_marker = successor / RECOVERY_MARKER_FILENAME
    successor_manifest = successor / "rescue" / RECOVERY_MANIFEST_FILENAME
    if not successor_marker.is_file() or not successor_manifest.is_file():
        raise VerificationError(
            "new recovery session is not self-contained; source was not delegated"
        )
    marker = source / RECOVERY_MARKER_FILENAME
    if not marker.is_file():
        raise VerificationError("recovery source marker disappeared before delegation")
    document: dict[str, object] = {
        "schema": "openmaxfire.recovery-delegation.v1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "image_sha256": image_sha256,
        "recovery_session": str(successor.resolve()),
        "rule": "continue any unresolved recovery from the delegated session",
    }
    _exclusive_write_json(source / RECOVERY_DELEGATION_FILENAME, document)
    marker.unlink()
    _fsync_directory(source)
    return document


@dataclass(frozen=True, slots=True)
class FlashPreparation:
    approved: ApprovedFirmware
    current_identity: StoveIdentity
    current_profile: ControllerProfile
    loader_plan: LoaderPlan
    eeprom_before: Mapping[int, int]
    eeprom_backup: Mapping[str, object]
    data_format_migration_required: bool
    calibration_required: bool
    downgrade: bool
    identity_confirmations: int = 0
    eeprom_confirmation_reads: int = 0
    recovery_mode: bool = False

    def to_dict(self) -> dict[str, object]:
        return {
            "schema": "openmaxfire.flash-preparation.v1",
            "approved_firmware": self.approved.to_dict(),
            "current_identity": self.current_identity.to_dict(),
            "current_profile": self.current_profile.to_dict(),
            "loader_plan": self.loader_plan.to_dict(),
            "data_format_migration_required": self.data_format_migration_required,
            "calibration_required": self.calibration_required,
            "downgrade": self.downgrade,
            "identity_confirmations": self.identity_confirmations,
            "eeprom_confirmation_reads": self.eeprom_confirmation_reads,
            "recovery_mode": self.recovery_mode,
            "eeprom_before_sha256": _eeprom_sha256(self.eeprom_before),
            "safety_boundary": (
                "manual AC power cycle only; no CW0FC4 software reset is sent"
            ),
        }


def _confirm_identity(
    client: MaxFireClient,
    *,
    request_delay: float,
    confirmations: int,
) -> StoveIdentity:
    if not 2 <= confirmations <= 5:
        raise ValueError("identity confirmations must be between 2 and 5")
    identities = tuple(
        client.identify(request_delay=request_delay) for _ in range(confirmations)
    )
    if any(item != identities[0] for item in identities[1:]):
        raise VerificationError(
            "controller identity was not stable across repeated reads"
        )
    return identities[0]


def _confirm_eeprom(
    client: MaxFireClient,
    *,
    request_delay: float,
    reads: int,
    baseline: Mapping[int, int] | None = None,
) -> Mapping[int, int]:
    if not 2 <= reads <= 3:
        raise ValueError("EEPROM confirmation reads must be between 2 and 3")
    first = (
        client.read_eeprom(request_delay=request_delay)
        if baseline is None
        else baseline
    )
    snapshots = (first,) + tuple(
        client.read_eeprom(request_delay=request_delay)
        for _ in range(reads - 1)
    )
    for index, snapshot in enumerate(snapshots[1:], start=2):
        changed = [
            address
            for address in range(0x100)
            if snapshot.get(address) != first.get(address)
        ]
        if changed:
            raise VerificationError(
                f"EEPROM was not stable across read 1 and read {index}; first "
                f"difference A{changed[0]:02X}"
            )
    return first


def prepare_live_flash(
    client: MaxFireClient,
    image: FirmwareImage,
    *,
    port: str,
    current_baudrate: int,
    interlocks: FlashSafetyInterlocks,
    request_delay: float = 0.05,
    backup_path: str | Path | None = None,
    identity_confirmations: int = 3,
    eeprom_confirmation_reads: int = 2,
) -> FlashPreparation:
    """Identify and back up a normally running controller before loader entry."""

    approved = approve_live_firmware(image)
    identity = _confirm_identity(
        client,
        request_delay=request_delay,
        confirmations=identity_confirmations,
    )
    profile = select_profile(identity)
    if profile is None:
        if identity.firmware_version == "2.73":
            raise UnsupportedControllerError(UNSUPPORTED_FIRMWARE_MESSAGE)
        raise UnsupportedControllerError(
            "controller firmware/data-format identity is not an exact preserved profile"
        )
    if current_baudrate not in profile.baudrates:
        raise VerificationError(
            f"controller {profile.key} is cataloged at {profile.baudrates}, not "
            f"{current_baudrate} baud"
        )
    eeprom = client.read_eeprom(request_delay=request_delay)
    backup = build_eeprom_backup(
        identity,
        eeprom,
        port=port,
        baudrate=current_baudrate,
    )
    # Persist the raw, complete read before any semantic gate can reject the
    # session.  A checksum or format mismatch blocks programming, but the
    # evidence that was safely read should not be discarded with the error.
    if backup_path is not None:
        save_json_document(backup, backup_path)
    _confirm_eeprom(
        client,
        request_delay=request_delay,
        reads=eeprom_confirmation_reads,
        baseline=eeprom,
    )
    if backup["checksum"]["matches"] is not True:  # type: ignore[index]
        raise VerificationError(
            "pre-flash EEPROM checksum is missing or invalid; raw backup was read but "
            "programming is blocked"
        )
    individualization = backup["individualization"]
    if not isinstance(individualization, Mapping) or not individualization.get(
        "controller_and_eeprom_format_match"
    ):
        raise VerificationError(
            "controller and EEPROM data formats do not match before flashing"
        )
    plan = build_loader_plan(image, profile, live_executable=True)
    if not plan.simulator_executable:
        raise VerificationError(
            "; ".join(plan.compatibility.blockers) or "firmware plan is not executable"
        )
    migration = approved.target_profile.data_format != profile.data_format
    calibration = approved.firmware_version != profile.firmware_version
    downgrade = _version_key(approved.firmware_version) < _version_key(
        profile.firmware_version
    )
    validate_live_transition(profile.firmware_version, approved.firmware_version)
    interlocks.validate(
        calibration_required=calibration,
        downgrade=downgrade,
        recovery_mode=False,
    )
    return FlashPreparation(
        approved=approved,
        current_identity=identity,
        current_profile=profile,
        loader_plan=plan,
        eeprom_before=eeprom,
        eeprom_backup=backup,
        data_format_migration_required=migration,
        calibration_required=calibration,
        downgrade=downgrade,
        identity_confirmations=identity_confirmations,
        eeprom_confirmation_reads=eeprom_confirmation_reads,
    )


def _backup_identity(document: Mapping[str, object]) -> StoveIdentity:
    identity = document.get("controller_identity")
    if not isinstance(identity, Mapping):
        raise VerificationError("recovery backup has no controller identity")
    registers = identity.get("registers")
    if not isinstance(registers, Mapping):
        raise VerificationError("recovery backup has no identity registers")

    def value(name: str) -> int:
        raw = registers.get(name)
        if not isinstance(raw, str):
            raise VerificationError(f"recovery backup identity is missing {name}")
        try:
            parsed = int(raw, 16)
        except ValueError as exc:
            raise VerificationError(
                f"recovery backup identity {name} is not hexadecimal"
            ) from exc
        if not 0 <= parsed <= 0xFF:
            raise VerificationError(f"recovery backup identity {name} is not a byte")
        return parsed

    return StoveIdentity(
        probe=value("CR00"),
        data_format=value("CR08"),
        firmware_major=value("CR0B"),
        firmware_minor=value("CR0C"),
        reserved=value("CR0D"),
        version_readback=value("CR0E"),
    )


def _backup_eeprom(document: Mapping[str, object]) -> dict[int, int]:
    raw_hex = document.get("raw_hex")
    if not isinstance(raw_hex, str):
        raise VerificationError("recovery backup has no raw EEPROM image")
    try:
        raw = bytes.fromhex(raw_hex)
    except ValueError as exc:
        raise VerificationError("recovery backup raw EEPROM is not hexadecimal") from exc
    if len(raw) != 0x100:
        raise VerificationError("recovery backup must contain exactly 256 EEPROM bytes")
    encoded = document.get("eeprom")
    if not isinstance(encoded, Mapping):
        raise VerificationError("recovery backup has no addressed EEPROM map")
    for address, value in enumerate(raw):
        key = f"A{address:02X}"
        if encoded.get(key) != f"{value:02X}":
            raise VerificationError(f"recovery backup raw/addressed mismatch at {key}")
    return dict(enumerate(raw))


def prepare_recovery_flash(
    image: FirmwareImage,
    backup: Mapping[str, object],
    *,
    port: str,
    current_baudrate: int,
    interlocks: FlashSafetyInterlocks,
) -> FlashPreparation:
    """Rebuild preflight from a prior durable backup when the app cannot boot."""

    if backup.get("schema") != "openmaxfire.eeprom-backup.v1":
        raise VerificationError("recovery backup schema is not recognized")
    approved = approve_live_firmware(image)
    identity = _backup_identity(backup)
    profile = select_profile(identity)
    if profile is None:
        if identity.firmware_version == "2.73":
            raise UnsupportedControllerError(UNSUPPORTED_FIRMWARE_MESSAGE)
        raise UnsupportedControllerError(
            "recovery backup identity is not an exact preserved profile"
        )
    if current_baudrate not in profile.baudrates:
        raise VerificationError(
            f"recovery backup profile {profile.key} is cataloged at {profile.baudrates}, "
            f"not {current_baudrate} baud"
        )
    eeprom = _backup_eeprom(backup)
    canonical = build_eeprom_backup(
        identity,
        eeprom,
        port=port,
        baudrate=current_baudrate,
    )
    if canonical["checksum"]["matches"] is not True:  # type: ignore[index]
        raise VerificationError("recovery backup EEPROM checksum is invalid")
    individualization = canonical["individualization"]
    if not isinstance(individualization, Mapping) or not individualization.get(
        "controller_and_eeprom_format_match"
    ):
        raise VerificationError(
            "recovery backup controller and EEPROM data formats do not match"
        )
    plan = build_loader_plan(image, profile, live_executable=True)
    migration = approved.target_profile.data_format != profile.data_format
    calibration = approved.firmware_version != profile.firmware_version
    downgrade = _version_key(approved.firmware_version) < _version_key(
        profile.firmware_version
    )
    validate_live_transition(profile.firmware_version, approved.firmware_version)
    interlocks.validate(
        calibration_required=calibration,
        downgrade=downgrade,
        recovery_mode=True,
    )
    return FlashPreparation(
        approved=approved,
        current_identity=identity,
        current_profile=profile,
        loader_plan=plan,
        eeprom_before=eeprom,
        eeprom_backup=canonical,
        data_format_migration_required=migration,
        calibration_required=calibration,
        downgrade=downgrade,
        recovery_mode=True,
    )


def validate_live_transition(current: str, target: str) -> None:
    if current == target:
        raise VerificationError(
            "same-version J3 rewrites are blocked; exact replay is available only from "
            "a bound recovery session"
        )
    if _version_key(target) < _version_key(current):
        raise VerificationError(
            "J3 downgrades are blocked because sparse images can leave stale newer "
            "program words; use externally verified PICkit recovery instead"
        )
    if (current, target) not in _ALLOWED_FORWARD_TRANSITIONS:
        raise VerificationError(
            f"forward transition {current} to {target} skips an unvalidated vendor "
            "generation; use the preserved sequential upgrade path"
        )


def qualify_flash_preparation(preparation: FlashPreparation):
    """Run the exact authenticated plan through the strict simulator first."""

    from .simulator import SimulatedLoaderTransport

    result = execute_loader_plan(
        SimulatedLoaderTransport(),
        preparation.loader_plan,
        authorize=True,
        policy=LoaderPolicy(max_retries=0, transmit_terminal_block_attempt=False),
    )
    if not result.successful:
        raise VerificationError(
            "offline whole-image loader qualification failed: " + result.message
        )
    return result


@dataclass(frozen=True, slots=True)
class LoaderRehearsalResult:
    loader_identified: bool
    completion_sent: bool
    completion_acknowledged: bool
    identify_attempts: int
    message: str

    @property
    def successful(self) -> bool:
        return (
            self.loader_identified
            and self.completion_sent
            and self.completion_acknowledged
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "schema": "openmaxfire.loader-rehearsal-result.v1",
            "loader_identified": self.loader_identified,
            "completion_sent": self.completion_sent,
            "completion_acknowledged": self.completion_acknowledged,
            "identify_attempts": self.identify_attempts,
            "successful": self.successful,
            "program_blocks_sent": 0,
            "flash_write_commands_sent": 0,
            "message": self.message,
            "protocol": "EA/EB then ED/E4; no E3 frame",
        }


def execute_loader_rehearsal(
    transport: Transport,
    preparation: FlashPreparation,
    *,
    interlocks: FlashSafetyInterlocks,
    policy: LiveLoaderPolicy | None = None,
    audit: AuditTrail | None = None,
    journal: FlashJournal | None = None,
) -> LoaderRehearsalResult:
    """Enter and leave the loader without transmitting a program block."""

    if preparation.recovery_mode:
        raise SafetyInterlockError(
            "loader rehearsal is unavailable in recovery mode because the saved "
            "application may already be incomplete"
        )
    selected = policy or LiveLoaderPolicy()
    approved = APPROVED_FIRMWARE.get(preparation.loader_plan.image_sha256)
    if approved is None or preparation.approved != approved:
        raise VerificationError("rehearsal preparation is not canonical")
    interlocks.validate(
        calibration_required=preparation.calibration_required,
        downgrade=preparation.downgrade,
        recovery_mode=False,
    )
    _require_loader_baud(transport)
    if journal is not None:
        journal.record(
            "loader_rehearsal_start",
            loader_baudrate=LOADER_BAUDRATE,
            program_blocks_allowed=False,
        )
    _set_transport_timeout(transport, selected.probe_timeout)
    identified = False
    attempts_used = 0
    for attempt in range(1, selected.identify_attempts + 1):
        attempts_used = attempt
        buffered = _drain_available(transport, audit)
        if _contains_only_identify_responses(buffered):
            identified = True
            break
        _record_write(transport, LOADER_IDENTIFY_REQUEST, audit)
        if _record_read(transport, audit) == LOADER_IDENTIFY_RESPONSE:
            identified = True
            break
        if selected.retry_delay:
            time.sleep(selected.retry_delay)
    _set_transport_timeout(transport, selected.response_timeout)
    if not identified:
        result = LoaderRehearsalResult(
            False,
            False,
            False,
            attempts_used,
            "loader did not answer EA with EB; no E3 frame was sent",
        )
    else:
        tail = _drain_available(transport, audit)
        if tail and not _contains_only_identify_responses(tail):
            result = LoaderRehearsalResult(
                True,
                False,
                False,
                attempts_used,
                "unexpected bytes followed loader identify; no E3 frame was sent",
            )
            if journal is not None:
                journal.record(
                    "loader_rehearsal_unexpected_identify_tail",
                    data_hex=tail.hex(" ").upper(),
                )
                journal.record("loader_rehearsal_result", **result.to_dict())
            return result
        _record_write(transport, LOADER_COMPLETE_REQUEST, audit)
        response = _record_read(transport, audit)
        acknowledged = response == LOADER_COMPLETE_RESPONSE
        result = LoaderRehearsalResult(
            True,
            True,
            acknowledged,
            attempts_used,
            (
                "non-writing EA/EB and ED/E4 rehearsal completed"
                if acknowledged
                else "loader rehearsal ED was not acknowledged; no E3 frame was sent"
            ),
        )
    if journal is not None:
        journal.record("loader_rehearsal_result", **result.to_dict())
    return result


@dataclass(frozen=True, slots=True)
class ApplicationUnchangedVerification:
    identity: StoveIdentity
    identity_confirmations: int
    eeprom_confirmation_reads: int
    eeprom_sha256: str

    def to_dict(self) -> dict[str, object]:
        return {
            "schema": "openmaxfire.application-unchanged-verification.v1",
            "identity": self.identity.to_dict(),
            "identity_confirmations": self.identity_confirmations,
            "eeprom_confirmation_reads": self.eeprom_confirmation_reads,
            "eeprom_sha256": self.eeprom_sha256,
            "identity_unchanged": True,
            "eeprom_unchanged": True,
            "successful": True,
        }


@dataclass(frozen=True, slots=True)
class ApplicationReadinessEvidence:
    """Passive proof that the application UART has finished starting.

    The controller emits periodic ``T`` and ``DW`` frames without a host
    request.  Waiting for one of those frames keeps the host TX line silent
    while the application initializes its two-byte PIC USART receive FIFO.
    """

    frame_kind: str
    raw: bytes
    ignored_frames: int
    serial_timeouts: int

    def to_dict(self) -> dict[str, object]:
        return {
            "schema": "openmaxfire.application-readiness.v1",
            "ready": True,
            "evidence": "passive_periodic_telemetry",
            "frame_kind": self.frame_kind,
            "raw_hex": self.raw.hex(" ").upper(),
            "raw_ascii": self.raw.decode("ascii"),
            "ignored_frames": self.ignored_frames,
            "serial_timeouts": self.serial_timeouts,
            "host_transmissions": 0,
        }


def wait_for_application_ready(
    client: MaxFireClient,
    *,
    timeout: float = 30.0,
) -> ApplicationReadinessEvidence:
    """Wait for unsolicited application telemetry without transmitting.

    A fixed delay followed by an immediate ``CR00`` can reach firmware 2.02
    after its USART receiver is enabled but before its receive interrupt is
    servicing bytes.  Four request bytes can overrun the PIC's two-byte FIFO
    and leave reception disabled until reset.  Only an unsolicited ``T`` or
    periodic ``DW`` frame is accepted as readiness evidence here.
    """

    if (
        not isinstance(timeout, (int, float))
        or not math.isfinite(timeout)
        or timeout <= 0
    ):
        raise ValueError("application readiness timeout must be greater than zero")

    deadline = time.monotonic() + float(timeout)
    ignored_frames = 0
    serial_timeouts = 0
    while time.monotonic() < deadline:
        try:
            frame = client.receive_response()
        except TimeoutError:
            serial_timeouts += 1
            continue
        except ProtocolError:
            # A baud transition or retained loader byte can leave one bounded
            # malformed fragment ahead of the first application line.
            ignored_frames += 1
            continue

        if isinstance(frame, TelemetryResponse):
            return ApplicationReadinessEvidence(
                "T", frame.raw, ignored_frames, serial_timeouts
            )
        if (
            isinstance(frame, AddressedResponse)
            and frame.unit == "D"
            and frame.opcode == "W"
        ):
            return ApplicationReadinessEvidence(
                "DW", frame.raw, ignored_frames, serial_timeouts
            )
        ignored_frames += 1

    raise TimeoutError(
        "application emitted no valid periodic telemetry within "
        f"{float(timeout):g} seconds; no CR00 or other application request was "
        "transmitted"
    )


def verify_application_unchanged(
    client: MaxFireClient,
    preparation: FlashPreparation,
    *,
    port: str,
    baudrate: int,
    request_delay: float = 0.05,
    identity_confirmations: int = 3,
    eeprom_confirmation_reads: int = 2,
) -> tuple[
    ApplicationUnchangedVerification,
    Mapping[int, int],
    Mapping[str, object],
]:
    """Prove that a non-writing loader rehearsal returned to the same app."""

    identity = _confirm_identity(
        client,
        request_delay=request_delay,
        confirmations=identity_confirmations,
    )
    if identity != preparation.current_identity:
        raise VerificationError(
            "application identity changed during the non-writing loader rehearsal"
        )
    eeprom = _confirm_eeprom(
        client,
        request_delay=request_delay,
        reads=eeprom_confirmation_reads,
    )
    changed = tuple(
        address
        for address in range(0x100)
        if eeprom[address] != preparation.eeprom_before[address]
    )
    if changed:
        raise VerificationError(
            f"EEPROM changed during loader rehearsal at A{changed[0]:02X}"
        )
    backup = build_eeprom_backup(identity, eeprom, port=port, baudrate=baudrate)
    verification = ApplicationUnchangedVerification(
        identity,
        identity_confirmations,
        eeprom_confirmation_reads,
        _eeprom_sha256(eeprom),
    )
    return verification, eeprom, backup


@dataclass(frozen=True, slots=True)
class LiveLoaderResult:
    state: LoaderState
    image_sha256: str
    blocks_total: int
    blocks_completed: int
    retries: int
    block_receipts: tuple[LoaderBlockReceipt, ...]
    loader_identified: bool
    pic_side_blocks_verified: bool
    completion_sent: bool
    completion_acknowledged: bool
    message: str
    write_failure_events: int = 0
    anomalies: tuple[str, ...] = ()
    diagnostic_errors: tuple[str, ...] = ()
    failure_outcome: LoaderAttemptOutcome | None = None
    recovery_required: bool = False

    @property
    def successful(self) -> bool:
        return (
            self.state is LoaderState.COMPLETE
            and self.loader_identified
            and self.pic_side_blocks_verified
            and self.completion_sent
            and self.completion_acknowledged
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "schema": "openmaxfire.live-loader-result.v2",
            "state": self.state.value,
            "image_sha256": self.image_sha256,
            "blocks_total": self.blocks_total,
            "blocks_completed": self.blocks_completed,
            "retries": self.retries,
            "loader_identified": self.loader_identified,
            "pic_side_blocks_verified": self.pic_side_blocks_verified,
            "completion_sent": self.completion_sent,
            "completion_acknowledged": self.completion_acknowledged,
            "write_failure_events": self.write_failure_events,
            "anomalies": list(self.anomalies),
            "diagnostic_errors": list(self.diagnostic_errors),
            "diagnostics_complete": not self.diagnostic_errors,
            "failure_outcome": (
                self.failure_outcome.value if self.failure_outcome is not None else None
            ),
            "recovery_required": self.recovery_required,
            "successful": self.successful,
            "block_receipts": [item.to_dict() for item in self.block_receipts],
            "message": self.message,
            "evidence_boundary": (
                "E4 proves the resident PIC loader read back each submitted block; "
                "J3 cannot perform an independent whole-program-memory readback"
            ),
        }


ProgressCallback = Callable[[int, int, LoaderBlockReceipt], None]


@dataclass(frozen=True, slots=True)
class LiveAttemptEvent:
    block_number: int
    blocks_total: int
    word_address: int
    receipt: LoaderAttemptReceipt
    will_retry: bool
    decision: str

    def to_dict(self) -> dict[str, object]:
        return {
            "block_number": self.block_number,
            "blocks_total": self.blocks_total,
            "word_address": f"0x{self.word_address:04X}",
            "attempt": self.receipt.to_dict(),
            "will_retry": self.will_retry,
            "decision": self.decision,
        }


AttemptCallback = Callable[[LiveAttemptEvent], None]


def _remember_diagnostic_error(
    errors: list[str], label: str, exc: BaseException
) -> None:
    message = f"{label}: {type(exc).__name__}: {exc}"
    if message not in errors and len(errors) < 20:
        errors.append(message)


def _record_write(
    transport: Transport,
    data: bytes,
    audit: AuditTrail | None,
    diagnostic_errors: list[str] | None = None,
) -> None:
    if audit is not None:
        try:
            audit.record("tx", data)
        except (OSError, RuntimeError, ValueError) as exc:
            if diagnostic_errors is None:
                raise
            _remember_diagnostic_error(diagnostic_errors, "traffic audit write", exc)
    transport.write(data)


def _record_read(
    transport: Transport,
    audit: AuditTrail | None,
    diagnostic_errors: list[str] | None = None,
) -> bytes:
    data = transport.read(1)
    if audit is not None:
        try:
            audit.record("rx", data)
        except (OSError, RuntimeError, ValueError) as exc:
            if diagnostic_errors is None:
                raise
            _remember_diagnostic_error(diagnostic_errors, "traffic audit read", exc)
    return data


def _drain_available(
    transport: Transport,
    audit: AuditTrail | None,
    diagnostic_errors: list[str] | None = None,
) -> bytes:
    reader = getattr(transport, "read_available", None)
    if reader is None:
        return b""
    data = bytes(reader())
    if data and audit is not None:
        try:
            audit.record("rx", data)
        except (OSError, RuntimeError, ValueError) as exc:
            if diagnostic_errors is None:
                raise
            _remember_diagnostic_error(diagnostic_errors, "traffic audit drain", exc)
    return data


def _contains_only_identify_responses(data: bytes) -> bool:
    """Accept delayed EB bytes only when no unrelated byte is interleaved."""

    return bool(data) and all(value == LOADER_IDENTIFY_RESPONSE[0] for value in data)


def _journal_record(
    journal: FlashJournal | None,
    diagnostic_errors: list[str],
    event: str,
    **fields: object,
) -> None:
    if journal is None:
        return
    try:
        journal.record(event, **fields)
    except (OSError, RuntimeError, ValueError) as exc:
        _remember_diagnostic_error(diagnostic_errors, "flash journal", exc)


def _notify_attempt(
    callback: AttemptCallback | None,
    event: LiveAttemptEvent,
    diagnostic_errors: list[str],
) -> None:
    if callback is None:
        return
    try:
        callback(event)
    except Exception as exc:
        _remember_diagnostic_error(diagnostic_errors, "attempt callback", exc)


def _notify_progress(
    callback: ProgressCallback | None,
    current: int,
    total: int,
    receipt: LoaderBlockReceipt,
    diagnostic_errors: list[str],
) -> None:
    if callback is None:
        return
    try:
        callback(current, total, receipt)
    except Exception as exc:
        _remember_diagnostic_error(diagnostic_errors, "progress callback", exc)


def _require_loader_baud(transport: Transport) -> None:
    settings = getattr(transport, "settings", None)
    baudrate = getattr(settings, "baudrate", None)
    if baudrate is not None and baudrate != LOADER_BAUDRATE:
        raise SafetyInterlockError(
            f"resident loader must be opened at {LOADER_BAUDRATE} baud, not {baudrate}"
        )


def _set_transport_timeout(transport: Transport, timeout: float) -> None:
    setter = getattr(transport, "set_timeout", None)
    if setter is not None:
        setter(timeout)


def _classify_block_attempt(
    transport: Transport,
    audit: AuditTrail | None,
    diagnostic_errors: list[str] | None = None,
) -> tuple[LoaderAttemptOutcome, tuple[bytes, ...]]:
    first = _record_read(transport, audit, diagnostic_errors)
    responses = [first]
    if first == LOADER_CHECKSUM_REJECTED_RESPONSE:
        return LoaderAttemptOutcome.CHECKSUM_REJECTED, tuple(responses)
    if first == LOADER_CHECKSUM_ACCEPTED_RESPONSE:
        second = _record_read(transport, audit, diagnostic_errors)
        responses.append(second)
        if second == LOADER_WRITE_VERIFIED_RESPONSE:
            return LoaderAttemptOutcome.ACKNOWLEDGED, tuple(responses)
        if second == LOADER_WRITE_FAILED_RESPONSE:
            return LoaderAttemptOutcome.WRITE_VERIFICATION_FAILED, tuple(responses)
        if not second:
            return LoaderAttemptOutcome.POST_ACCEPT_TIMEOUT, tuple(responses)
        return LoaderAttemptOutcome.UNEXPECTED_RESPONSE, tuple(responses)
    if not first:
        return LoaderAttemptOutcome.PRE_ACCEPT_TIMEOUT, tuple(responses)
    return LoaderAttemptOutcome.UNEXPECTED_RESPONSE, tuple(responses)


def _retry_decision(
    outcome: LoaderAttemptOutcome,
    *,
    outcome_counts: Counter[LoaderAttemptOutcome],
    write_failure_events: int,
    transmissions: int,
    policy: LiveLoaderPolicy,
) -> tuple[bool, str]:
    if outcome is LoaderAttemptOutcome.ACKNOWLEDGED:
        return False, "PIC loader returned E7 then E4"
    if outcome is LoaderAttemptOutcome.TRANSPORT_ERROR:
        return False, "transport error is not retried"
    if outcome is LoaderAttemptOutcome.UNEXPECTED_RESPONSE:
        return False, "unexpected bytes are not retried because framing may be lost"
    if transmissions >= policy.max_block_transmissions:
        return False, "per-block transmission ceiling reached"
    if outcome is LoaderAttemptOutcome.CHECKSUM_REJECTED:
        allowed = outcome_counts[outcome] <= policy.checksum_retries
        return allowed, (
            "E8 proves no write began; resend the identical authenticated block"
            if allowed
            else "E8 checksum-retry budget exhausted"
        )
    if outcome is LoaderAttemptOutcome.PRE_ACCEPT_TIMEOUT:
        allowed = outcome_counts[outcome] <= policy.pre_accept_timeout_retries
        return allowed, (
            "no E7 was received; cautiously resend the identical block"
            if allowed
            else "pre-E7 timeout budget exhausted"
        )
    if outcome is LoaderAttemptOutcome.POST_ACCEPT_TIMEOUT:
        allowed = outcome_counts[outcome] <= policy.post_accept_timeout_retries
        return allowed, (
            "E7 was received but final verification was lost; allow one idempotent replay"
            if allowed
            else "post-E7 timeout budget exhausted"
        )
    if outcome is LoaderAttemptOutcome.WRITE_VERIFICATION_FAILED:
        allowed = (
            write_failure_events == 1
            and outcome_counts[outcome] <= policy.write_failure_retries
        )
        return allowed, (
            "first E5 in session; allow one identical host retry"
            if allowed
            else "second E5 indicates a likely systemic write/power/contact failure"
        )
    return False, "outcome has no safe retry policy"


def execute_live_loader_plan(
    transport: Transport,
    preparation: FlashPreparation,
    *,
    interlocks: FlashSafetyInterlocks,
    policy: LiveLoaderPolicy | None = None,
    audit: AuditTrail | None = None,
    journal: FlashJournal | None = None,
    progress: ProgressCallback | None = None,
    attempt_callback: AttemptCallback | None = None,
) -> LiveLoaderResult:
    """Execute the authenticated plan on an already-open 9,600-baud port.

    The caller must arm this by manually removing and restoring AC power.  No
    normal-protocol reset or bootloader-entry write exists in this function.
    """

    selected = policy or LiveLoaderPolicy()
    plan = preparation.loader_plan
    approved = APPROVED_FIRMWARE.get(plan.image_sha256)
    if approved is None or preparation.approved != approved:
        raise VerificationError("preparation does not reference a canonical approved image")
    # Re-check the immutable values that cross the preflight/loader boundary.
    if plan.image_sha256 != approved.entry.sha256:
        raise VerificationError("loader plan image hash changed after preflight")
    if plan.firmware_version != approved.firmware_version:
        raise VerificationError("loader plan target version changed after preflight")
    if not plan.live_executable or not plan.simulator_executable or not plan.blocks:
        raise VerificationError("loader plan has no executable authenticated blocks")
    if (
        len(plan.blocks) != approved.block_count
        or _loader_frames_sha256(plan.blocks) != approved.wire_sha256
    ):
        raise VerificationError("loader plan frame sequence is not the authenticated image")
    current = select_profile(preparation.current_identity)
    if (
        current is None
        or current.key != preparation.current_profile.key
        or plan.profile_key != preparation.current_profile.key
    ):
        raise VerificationError("controller identity/profile changed after preflight")
    interlocks.validate(
        calibration_required=preparation.calibration_required,
        downgrade=preparation.downgrade,
        recovery_mode=preparation.recovery_mode,
    )
    _require_loader_baud(transport)

    diagnostic_errors: list[str] = []
    anomalies: list[str] = []
    _journal_record(
        journal,
        diagnostic_errors,
        "loader_start",
        image_sha256=plan.image_sha256,
        block_count=len(plan.blocks),
        loader_baudrate=LOADER_BAUDRATE,
        boot_window_estimate_seconds=LOADER_BOOT_WINDOW_ESTIMATE_SECONDS,
        probe_timeout=selected.probe_timeout,
        response_timeout=selected.response_timeout,
        retry_policy={
            "checksum_retries": selected.checksum_retries,
            "pre_accept_timeout_retries": selected.pre_accept_timeout_retries,
            "post_accept_timeout_retries": selected.post_accept_timeout_retries,
            "write_failure_retries": selected.write_failure_retries,
            "max_block_transmissions": selected.max_block_transmissions,
            "second_e5_aborts_session": True,
        },
    )

    loader_identified = False
    identify_attempts_used = 0
    identify_transport_failed = False
    _set_transport_timeout(transport, selected.probe_timeout)
    for attempt in range(1, selected.identify_attempts + 1):
        identify_attempts_used = attempt
        try:
            discarded = _drain_available(transport, audit, diagnostic_errors)
        except (OSError, TimeoutError, ValueError) as exc:
            _remember_diagnostic_error(diagnostic_errors, "loader identify transport", exc)
            identify_transport_failed = True
            break
        if _contains_only_identify_responses(discarded):
            loader_identified = True
            _journal_record(
                journal,
                diagnostic_errors,
                "loader_identified",
                attempt=attempt,
                source="late_buffered_response",
                discarded_hex=discarded.hex(" ").upper(),
            )
            break
        try:
            _record_write(
                transport, LOADER_IDENTIFY_REQUEST, audit, diagnostic_errors
            )
            response = _record_read(transport, audit, diagnostic_errors)
        except (OSError, TimeoutError, ValueError) as exc:
            _remember_diagnostic_error(diagnostic_errors, "loader identify transport", exc)
            identify_transport_failed = True
            break
        if response == LOADER_IDENTIFY_RESPONSE:
            loader_identified = True
            _journal_record(
                journal,
                diagnostic_errors,
                "loader_identified",
                attempt=attempt,
                discarded_hex=discarded.hex(" ").upper(),
            )
            break
        if response or discarded:
            _journal_record(
                journal,
                diagnostic_errors,
                "loader_probe_miss",
                attempt=attempt,
                response_hex=response.hex(" ").upper(),
                discarded_hex=discarded.hex(" ").upper(),
            )
        if selected.retry_delay:
            time.sleep(selected.retry_delay)
    _set_transport_timeout(transport, selected.response_timeout)
    if loader_identified:
        try:
            identify_tail = _drain_available(transport, audit, diagnostic_errors)
        except (OSError, TimeoutError, ValueError) as exc:
            identify_tail = b""
            identify_transport_failed = True
            loader_identified = False
            _remember_diagnostic_error(
                diagnostic_errors, "loader identify tail transport", exc
            )
        if identify_tail:
            clean_tail = _contains_only_identify_responses(identify_tail)
            _journal_record(
                journal,
                diagnostic_errors,
                "loader_identify_tail",
                data_hex=identify_tail.hex(" ").upper(),
                accepted=clean_tail,
            )
            if not clean_tail:
                loader_identified = False
    if not loader_identified:
        _journal_record(
            journal,
            diagnostic_errors,
            "loader_identify_failed",
            attempts=identify_attempts_used,
            transport_failed=identify_transport_failed,
        )
        return LiveLoaderResult(
            state=LoaderState.FAILED,
            image_sha256=plan.image_sha256,
            blocks_total=len(plan.blocks),
            blocks_completed=0,
            retries=max(0, identify_attempts_used - 1),
            block_receipts=(),
            loader_identified=False,
            pic_side_blocks_verified=False,
            completion_sent=False,
            completion_acknowledged=False,
            message=(
                "loader identify transport failed; no program block was sent"
                if identify_transport_failed
                else "loader did not answer EA with a clean EB response; no program block was sent"
            ),
            diagnostic_errors=tuple(diagnostic_errors),
            failure_outcome=(
                LoaderAttemptOutcome.TRANSPORT_ERROR
                if identify_transport_failed
                else LoaderAttemptOutcome.PRE_ACCEPT_TIMEOUT
            ),
            recovery_required=preparation.recovery_mode,
        )

    receipts: list[LoaderBlockReceipt] = []
    completed = 0
    retries = 0
    write_failure_events = 0
    for block_index, block in enumerate(plan.blocks):
        attempts: list[LoaderAttemptReceipt] = []
        acknowledged = False
        outcome_counts: Counter[LoaderAttemptOutcome] = Counter()
        final_outcome = LoaderAttemptOutcome.UNEXPECTED_RESPONSE
        for attempt in range(1, selected.max_block_transmissions + 1):
            if attempt > 1:
                if selected.retry_delay:
                    time.sleep(selected.retry_delay)
                try:
                    late = _drain_available(transport, audit, diagnostic_errors)
                except (OSError, TimeoutError, ValueError) as exc:
                    _remember_diagnostic_error(
                        diagnostic_errors, "loader retry drain transport", exc
                    )
                    previous = attempts[-1]
                    attempts[-1] = LoaderAttemptReceipt(
                        previous.attempt,
                        previous.responses,
                        LoaderAttemptOutcome.TRANSPORT_ERROR,
                    )
                    final_outcome = LoaderAttemptOutcome.TRANSPORT_ERROR
                    event = LiveAttemptEvent(
                        block_index + 1,
                        len(plan.blocks),
                        block.word_address,
                        attempts[-1],
                        False,
                        "transport failed while checking for a delayed reply; block was not resent",
                    )
                    _journal_record(
                        journal,
                        diagnostic_errors,
                        "block_retry_aborted",
                        **event.to_dict(),
                    )
                    _notify_attempt(attempt_callback, event, diagnostic_errors)
                    break
                if late:
                    anomalies.append(
                        f"late loader bytes before block 0x{block.word_address:04X} "
                        f"attempt {attempt}: {late.hex(' ').upper()}"
                    )
                    _journal_record(
                        journal,
                        diagnostic_errors,
                        "late_loader_bytes",
                        block_index=block_index,
                        word_address=f"0x{block.word_address:04X}",
                        data_hex=late.hex(" ").upper(),
                    )
                    # Match a delayed reply to the exact phase observed on the
                    # prior attempt. E4 is valid only after E7 was consumed;
                    # E7/E4 is valid only when neither byte was consumed.
                    previous = attempts[-1]
                    delayed_acknowledgement = (
                        previous.outcome is LoaderAttemptOutcome.POST_ACCEPT_TIMEOUT
                        and late == LOADER_WRITE_VERIFIED_RESPONSE
                    ) or (
                        previous.outcome is LoaderAttemptOutcome.PRE_ACCEPT_TIMEOUT
                        and late
                        == LOADER_CHECKSUM_ACCEPTED_RESPONSE
                        + LOADER_WRITE_VERIFIED_RESPONSE
                    )
                    if delayed_acknowledgement:
                        attempts[-1] = LoaderAttemptReceipt(
                            previous.attempt,
                            previous.responses + (late,),
                            LoaderAttemptOutcome.ACKNOWLEDGED,
                        )
                        acknowledged = True
                        final_outcome = LoaderAttemptOutcome.ACKNOWLEDGED
                        break
                    attempts[-1] = LoaderAttemptReceipt(
                        previous.attempt,
                        previous.responses + (late,),
                        LoaderAttemptOutcome.UNEXPECTED_RESPONSE,
                    )
                    final_outcome = LoaderAttemptOutcome.UNEXPECTED_RESPONSE
                    break
            try:
                _record_write(transport, block.frame, audit, diagnostic_errors)
                outcome, responses = _classify_block_attempt(
                    transport, audit, diagnostic_errors
                )
            except (OSError, TimeoutError, ValueError) as exc:
                _remember_diagnostic_error(
                    diagnostic_errors, "loader block transport", exc
                )
                outcome = LoaderAttemptOutcome.TRANSPORT_ERROR
                responses = ()
            receipt_attempt = LoaderAttemptReceipt(attempt, responses, outcome)
            attempts.append(receipt_attempt)
            outcome_counts[outcome] += 1
            if outcome is LoaderAttemptOutcome.WRITE_VERIFICATION_FAILED:
                write_failure_events += 1
                anomalies.append(
                    f"E5 at block {block_index + 1}/{len(plan.blocks)} "
                    f"word 0x{block.word_address:04X} attempt {attempt}"
                )
            if outcome is LoaderAttemptOutcome.ACKNOWLEDGED:
                acknowledged = True
                final_outcome = outcome
                will_retry = False
                decision = "PIC loader returned E7 then E4"
            else:
                will_retry, decision = _retry_decision(
                    outcome,
                    outcome_counts=outcome_counts,
                    write_failure_events=write_failure_events,
                    transmissions=attempt,
                    policy=selected,
                )
                final_outcome = outcome
            event = LiveAttemptEvent(
                block_index + 1,
                len(plan.blocks),
                block.word_address,
                receipt_attempt,
                will_retry,
                decision,
            )
            _journal_record(
                journal,
                diagnostic_errors,
                "block_attempt",
                **event.to_dict(),
            )
            _notify_attempt(attempt_callback, event, diagnostic_errors)
            if acknowledged or not will_retry:
                break

        retries += max(0, len(attempts) - 1)
        receipt = LoaderBlockReceipt(
            block.word_address,
            len(block.data),
            len(attempts),
            acknowledged,
            final_outcome,
            tuple(attempts),
        )
        receipts.append(receipt)
        _notify_progress(
            progress,
            block_index + 1,
            len(plan.blocks),
            receipt,
            diagnostic_errors,
        )
        if not acknowledged:
            _journal_record(
                journal,
                diagnostic_errors,
                "programming_failed",
                block_index=block_index,
                word_address=f"0x{block.word_address:04X}",
                outcome=final_outcome.value,
                completed_blocks=completed,
                exact_replay_from_block_zero_required=True,
            )
            return LiveLoaderResult(
                state=LoaderState.FAILED,
                image_sha256=plan.image_sha256,
                blocks_total=len(plan.blocks),
                blocks_completed=completed,
                retries=retries,
                block_receipts=tuple(receipts),
                loader_identified=True,
                pic_side_blocks_verified=False,
                completion_sent=False,
                completion_acknowledged=False,
                message=(
                    f"block 0x{block.word_address:04X} failed after "
                    f"{len(attempts)} bounded attempts ({final_outcome.value}); "
                    "do not operate the stove; replay the session's exact image from block zero"
                ),
                write_failure_events=write_failure_events,
                anomalies=tuple(anomalies),
                diagnostic_errors=tuple(diagnostic_errors),
                failure_outcome=final_outcome,
                recovery_required=True,
            )
        completed += 1

    completion_sent = False
    completion_transport_failed = False
    try:
        _record_write(
            transport, LOADER_COMPLETE_REQUEST, audit, diagnostic_errors
        )
        completion_sent = True
        completion_response = _record_read(transport, audit, diagnostic_errors)
    except (OSError, TimeoutError, ValueError) as exc:
        _remember_diagnostic_error(diagnostic_errors, "loader completion transport", exc)
        completion_transport_failed = True
        completion_response = b""
    completion_acknowledged = completion_response == LOADER_COMPLETE_RESPONSE
    _journal_record(
        journal,
        diagnostic_errors,
        "completion_response",
        response_hex=completion_response.hex(" ").upper(),
        sent=completion_sent,
        acknowledged=completion_acknowledged,
    )
    return LiveLoaderResult(
        state=LoaderState.COMPLETE if completion_acknowledged else LoaderState.FAILED,
        image_sha256=plan.image_sha256,
        blocks_total=len(plan.blocks),
        blocks_completed=completed,
        retries=retries,
        block_receipts=tuple(receipts),
        loader_identified=True,
        pic_side_blocks_verified=True,
        completion_sent=completion_sent,
        completion_acknowledged=completion_acknowledged,
        message=(
            "all blocks received E7/E4 and loader completion received E4"
            if completion_acknowledged
            else (
                "all blocks received E7/E4, but ED acknowledgement was absent; "
                "verify the target application before probing the loader again"
            )
        ),
        write_failure_events=write_failure_events,
        anomalies=tuple(anomalies),
        diagnostic_errors=tuple(diagnostic_errors),
        failure_outcome=(
            None
            if completion_acknowledged
            else (
                LoaderAttemptOutcome.TRANSPORT_ERROR
                if completion_transport_failed
                else (
                    LoaderAttemptOutcome.PRE_ACCEPT_TIMEOUT
                    if not completion_response
                    else LoaderAttemptOutcome.UNEXPECTED_RESPONSE
                )
            )
        ),
        recovery_required=not completion_acknowledged,
    )


def recover_live_loader_completion(
    transport: Transport,
    result: LiveLoaderResult,
    *,
    audit: AuditTrail | None = None,
    journal: FlashJournal | None = None,
    identify_attempts: int = 3,
    probe_timeout: float = 0.020,
) -> bool:
    """Retry only the final handoff after application reconnect already failed.

    This is legal only when every block previously received its PIC-side E4.
    If the target application is already running, it will not answer ``EA`` and
    no second ``ED`` is sent.
    """

    if not result.pic_side_blocks_verified or result.blocks_completed != result.blocks_total:
        raise SafetyInterlockError(
            "completion recovery requires E4 verification for every program block"
        )
    if result.completion_acknowledged:
        return True
    if not 1 <= identify_attempts <= 10:
        raise ValueError("identify_attempts must be between 1 and 10")
    if (
        not isinstance(probe_timeout, (int, float))
        or not math.isfinite(probe_timeout)
        or not 0.001 <= probe_timeout <= 0.050
    ):
        raise ValueError("probe_timeout must be between 0.001 and 0.050 seconds")
    _require_loader_baud(transport)
    _set_transport_timeout(transport, float(probe_timeout))
    diagnostic_errors: list[str] = []
    for attempt in range(1, identify_attempts + 1):
        try:
            _drain_available(transport, audit, diagnostic_errors)
            _record_write(
                transport, LOADER_IDENTIFY_REQUEST, audit, diagnostic_errors
            )
            response = _record_read(transport, audit, diagnostic_errors)
        except (OSError, TimeoutError, ValueError):
            return False
        if response == LOADER_IDENTIFY_RESPONSE:
            try:
                _record_write(
                    transport, LOADER_COMPLETE_REQUEST, audit, diagnostic_errors
                )
                done = _record_read(transport, audit, diagnostic_errors)
            except (OSError, TimeoutError, ValueError):
                return False
            acknowledged = done == LOADER_COMPLETE_RESPONSE
            _journal_record(
                journal,
                diagnostic_errors,
                "completion_recovery",
                loader_identified=True,
                identify_attempt=attempt,
                response_hex=done.hex(" ").upper(),
                acknowledged=acknowledged,
            )
            return acknowledged
    _journal_record(
        journal,
        diagnostic_errors,
        "completion_recovery",
        loader_identified=False,
        identify_attempts=identify_attempts,
        acknowledged=False,
    )
    return False


def _eeprom_sha256(values: Mapping[int, int]) -> str:
    return hashlib.sha256(bytes(values[address] for address in range(0x100))).hexdigest()


@dataclass(frozen=True, slots=True)
class PostFlashVerification:
    identity: StoveIdentity
    target_profile_matched: bool
    eeprom_unchanged: bool
    eeprom_before_sha256: str
    eeprom_after_sha256: str
    changed_eeprom_addresses: tuple[int, ...]
    calibration_required: bool
    identity_confirmations: int = 3
    eeprom_confirmation_reads: int = 2

    @property
    def programming_verified(self) -> bool:
        return self.target_profile_matched and self.eeprom_unchanged

    @property
    def ready_for_operation(self) -> bool:
        return self.programming_verified and not self.calibration_required

    def to_dict(self) -> dict[str, object]:
        return {
            "schema": "openmaxfire.post-flash-verification.v2",
            "identity": self.identity.to_dict(),
            "target_profile_matched": self.target_profile_matched,
            "eeprom_unchanged": self.eeprom_unchanged,
            "eeprom_before_sha256": self.eeprom_before_sha256,
            "eeprom_after_sha256": self.eeprom_after_sha256,
            "changed_eeprom_addresses": [f"A{item:02X}" for item in self.changed_eeprom_addresses],
            "calibration_required": self.calibration_required,
            "identity_confirmations": self.identity_confirmations,
            "eeprom_confirmation_reads": self.eeprom_confirmation_reads,
            "programming_verified": self.programming_verified,
            "ready_for_operation": self.ready_for_operation,
        }


def verify_post_flash(
    client: MaxFireClient,
    preparation: FlashPreparation,
    *,
    request_delay: float = 0.05,
    identity_confirmations: int = 3,
    eeprom_confirmation_reads: int = 2,
) -> tuple[PostFlashVerification, Mapping[int, int], Mapping[str, object]]:
    """Verify target identity and byte-identical EEPROM after application handoff."""

    identity = _confirm_identity(
        client,
        request_delay=request_delay,
        confirmations=identity_confirmations,
    )
    if identity.firmware_version == "2.73":
        raise UnsupportedControllerError(UNSUPPORTED_FIRMWARE_MESSAGE)
    profile = select_profile(identity)
    target_matched = (
        profile is not None and profile.key == preparation.approved.target_profile_key
    )
    if not target_matched:
        actual = profile.key if profile is not None else identity.firmware_version
        raise VerificationError(
            f"post-flash application identity {actual!r} does not match target "
            f"{preparation.approved.target_profile_key}"
        )
    after = _confirm_eeprom(
        client,
        request_delay=request_delay,
        reads=eeprom_confirmation_reads,
    )
    changed = tuple(
        address
        for address in range(0x100)
        if preparation.eeprom_before[address] != after[address]
    )
    verification = PostFlashVerification(
        identity,
        True,
        not changed,
        _eeprom_sha256(preparation.eeprom_before),
        _eeprom_sha256(after),
        changed,
        preparation.calibration_required,
        identity_confirmations,
        eeprom_confirmation_reads,
    )
    backup = build_eeprom_backup(
        identity,
        after,
        port=str(preparation.eeprom_backup["connection"]["port"]),  # type: ignore[index]
        baudrate=preparation.approved.application_baudrate,
    )
    if changed:
        raise VerificationError(
            f"post-flash EEPROM changed at {len(changed)} address(es), beginning A{changed[0]:02X}"
        )
    return verification, after, backup


def live_flashing_supported() -> bool:
    """Return whether the guarded experimental executor is present."""

    return True


__all__ = [
    "APPROVED_FIRMWARE",
    "FLASH_STATE_FILENAME",
    "LOADER_BAUDRATE",
    "LOADER_BOOT_WINDOW_ESTIMATE_SECONDS",
    "RECOVERY_DELEGATION_FILENAME",
    "RECOVERY_MANIFEST_FILENAME",
    "RECOVERY_MARKER_FILENAME",
    "UNSUPPORTED_FIRMWARE_MESSAGE",
    "ApplicationUnchangedVerification",
    "ApprovedFirmware",
    "FlashJournal",
    "FlashPreparation",
    "FlashSessionState",
    "FlashSessionStatus",
    "FlashSafetyInterlocks",
    "LiveAttemptEvent",
    "LiveLoaderPolicy",
    "LiveLoaderResult",
    "LoaderRehearsalResult",
    "PostFlashVerification",
    "approve_live_firmware",
    "delegate_recovery_source",
    "execute_loader_rehearsal",
    "execute_live_loader_plan",
    "load_recovery_bundle",
    "live_flashing_supported",
    "prepare_live_flash",
    "prepare_recovery_flash",
    "preserve_recovery_bundle",
    "qualify_flash_preparation",
    "recover_live_loader_completion",
    "verify_application_unchanged",
    "verify_post_flash",
    "validate_live_transition",
]
