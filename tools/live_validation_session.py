#!/usr/bin/env python3
"""Guided, evidence-preserving live validation for an installed MaxFire controller.

The default workflow is read-only.  Remote front-panel commands are available
only behind separate command-line and interactive gates.  Configuration writes,
factory Checkout actuators, raw traffic, and firmware-loader traffic are
deliberately absent.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Mapping, Sequence

import openmaxfire
from openmaxfire import AuditTrail, ControllerSession, RemoteButton
from openmaxfire.discovery import DetectionStatus, detect_controller
from openmaxfire.errors import OpenMaxFireError, UnsupportedControllerError
from openmaxfire.transport import RecordingTransport, SerialTransport


SCHEMA = "openmaxfire.live-validation.v1"
CONTROL_PHRASE = "I ACCEPT STATE-CHANGING STOVE CONTROL"
START_PHRASE = "START THE STOVE"


class SessionAborted(RuntimeError):
    """The operator intentionally stopped or declined a required condition."""


@dataclass(frozen=True, slots=True)
class Interaction:
    key: str
    title: str
    instruction: str
    address: int
    expected: int | None = None
    mask: int = 0xFF
    minimum: int | None = None
    maximum: int | None = None


INTERACTIONS: tuple[Interaction, ...] = (
    Interaction(
        "buttons-released",
        "Front-panel buttons released",
        "Release every front-panel button.",
        0x01,
        expected=0x00,
    ),
    Interaction(
        "button-off",
        "Physical OFF button",
        "Press and HOLD only the physical OFF button while taking the samples.",
        0x01,
        expected=0x01,
    ),
    Interaction(
        "button-up",
        "Physical UP button",
        "Press and HOLD only the physical UP button while taking the samples.",
        0x01,
        expected=0x04,
    ),
    Interaction(
        "button-down",
        "Physical DOWN button",
        "Press and HOLD only the physical DOWN button while taking the samples.",
        0x01,
        expected=0x08,
    ),
    Interaction(
        "buttons-restored",
        "Front-panel buttons restored",
        "Release every front-panel button.",
        0x01,
        expected=0x00,
    ),
    Interaction(
        "firebox-closed",
        "Firebox door closed",
        "Fully close and latch the firebox door.",
        0x02,
        expected=0x00,
        mask=0x20,
    ),
    Interaction(
        "firebox-open",
        "Firebox door open",
        "Open the firebox door. Do not leave it open after this test.",
        0x02,
        expected=0x20,
        mask=0x20,
    ),
    Interaction(
        "firebox-restored",
        "Firebox door restored",
        "Fully close and latch the firebox door again.",
        0x02,
        expected=0x00,
        mask=0x20,
    ),
    Interaction(
        "drawer-closed",
        "Ash drawer closed",
        "Fully close and latch the ash drawer.",
        0x02,
        expected=0x00,
        mask=0x40,
    ),
    Interaction(
        "drawer-open",
        "Ash drawer open",
        "Open the ash drawer. Do not leave it open after this test.",
        0x02,
        expected=0x40,
        mask=0x40,
    ),
    Interaction(
        "drawer-restored",
        "Ash drawer restored",
        "Fully close and latch the ash drawer again.",
        0x02,
        expected=0x00,
        mask=0x40,
    ),
    Interaction(
        "thermostat-closed",
        "Thermostat contact closed",
        (
            "Close the already-installed thermostat contact. If this would require "
            "moving wiring while powered, skip this test."
        ),
        0x06,
        expected=0x00,
        mask=0x04,
    ),
    Interaction(
        "thermostat-open",
        "Thermostat contact open",
        (
            "Open the already-installed thermostat contact. If this would require "
            "moving wiring while powered, skip this test."
        ),
        0x06,
        expected=0x04,
        mask=0x04,
    ),
    Interaction(
        "thermostat-restored",
        "Thermostat contact restored",
        "Restore the thermostat contact to its normal safe condition.",
        0x06,
    ),
    Interaction(
        "fuel-wood",
        "Fuel selector Wood / Fuel B",
        "Move the fuel selector to Wood / Fuel B.",
        0x02,
        expected=0x00,
        mask=0x04,
    ),
    Interaction(
        "fuel-corn",
        "Fuel selector Corn / Fuel A",
        "Move the fuel selector to Corn / Fuel A.",
        0x02,
        expected=0x04,
        mask=0x04,
    ),
    Interaction(
        "fuel-restored",
        "Fuel selector restored",
        "Restore the fuel selector to the fuel actually installed in the stove.",
        0x02,
    ),
    Interaction(
        "fan-pot-low",
        "Fan trim low",
        "Turn the fan trim fully counterclockwise.",
        0x09,
        minimum=0x00,
        maximum=0x05,
    ),
    Interaction(
        "fan-pot-center",
        "Fan trim center",
        "Turn the fan trim to its center detent.",
        0x09,
        minimum=0x60,
        maximum=0x90,
    ),
    Interaction(
        "fan-pot-high",
        "Fan trim high",
        "Turn the fan trim fully clockwise.",
        0x09,
        minimum=0xFA,
        maximum=0xFF,
    ),
    Interaction(
        "fan-pot-restored",
        "Fan trim restored",
        "Restore the fan trim to its normal setting, normally the center detent.",
        0x09,
    ),
    Interaction(
        "feed-pot-low",
        "Feed trim low",
        "First note the current feed setting, then turn the feed trim fully counterclockwise.",
        0x0A,
        minimum=0x00,
        maximum=0x05,
    ),
    Interaction(
        "feed-pot-center",
        "Feed trim center",
        "Turn the feed trim to its center detent.",
        0x0A,
        minimum=0x60,
        maximum=0x90,
    ),
    Interaction(
        "feed-pot-high",
        "Feed trim high",
        "Turn the feed trim fully clockwise.",
        0x0A,
        minimum=0xFA,
        maximum=0xFF,
    ),
    Interaction(
        "feed-pot-restored",
        "Feed trim restored",
        "Restore the feed trim to the setting you recorded before the test.",
        0x0A,
    ),
)


class Console:
    def __init__(self, *, input_function: Callable[[str], str] = input):
        self.input = input_function

    def confirm(self, statement: str) -> bool:
        while True:
            answer = self.input(f"{statement} [y/N]: ").strip().lower()
            if answer in ("y", "yes"):
                return True
            if answer in ("", "n", "no"):
                return False
            print("Please answer y or n.")

    def ready_or_skip(self, instruction: str) -> bool:
        print(f"\n{instruction}")
        answer = self.input("Press Enter when ready, or type s to skip: ").strip().lower()
        return answer not in ("s", "skip")

    def phrase(self, prompt: str, required: str) -> bool:
        answer = self.input(f"{prompt}\nType exactly: {required}\n> ")
        return answer == required

    def observation(self, prompt: str) -> str:
        while True:
            answer = self.input(f"{prompt} [y/n/u]: ").strip().lower()
            if answer in ("y", "yes"):
                return "yes"
            if answer in ("n", "no"):
                return "no"
            if answer in ("u", "unknown", "unsure"):
                return "unknown"
            print("Please answer y, n, or u for unknown.")


class _SharedAuditRecorder:
    """Let discovery transports share an audit without closing the session log."""

    def __init__(self, audit: AuditTrail):
        self.audit = audit

    def record(self, direction: str, data: bytes) -> None:
        self.audit.record(direction, data)

    def close(self) -> None:
        pass


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _timestamp_slug() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _write_json(path: Path, document: Mapping[str, object]) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="\n") as stream:
        json.dump(dict(document), stream, indent=2, sort_keys=True)
        stream.write("\n")
    temporary.replace(path)


def _prepare_output_directory(path: Path) -> Path:
    if path.exists() and any(path.iterdir()):
        raise FileExistsError(f"refusing to use non-empty output directory: {path}")
    path.mkdir(parents=True, exist_ok=True)
    (path / "snapshots").mkdir()
    (path / "backups").mkdir()
    return path


def _step(
    audit: AuditTrail,
    *,
    key: str,
    title: str,
    status: str,
    observations: Mapping[str, object] | None = None,
    message: str = "",
    checkpoint: int | None = None,
) -> dict[str, object]:
    span = audit.span(audit.checkpoint() if checkpoint is None else checkpoint)
    return {
        "key": key,
        "title": title,
        "status": status,
        "created_utc": _utc_now(),
        "message": message,
        "observations": dict(observations or {}),
        "audit_span": span.to_dict(),
    }


def _sample_register(
    session: ControllerSession,
    address: int,
    *,
    samples: int,
    sample_delay: float,
) -> list[int]:
    values: list[int] = []
    for index in range(samples):
        values.append(session.read_register(address))
        if sample_delay and index + 1 < samples:
            time.sleep(sample_delay)
    return values


def _evaluate(values: Sequence[int], interaction: Interaction) -> tuple[str, str]:
    if not values:
        return "error", "no samples were collected"
    matches = []
    for value in values:
        matched = True
        if interaction.expected is not None:
            matched = (value & interaction.mask) == interaction.expected
        if interaction.minimum is not None:
            matched = matched and value >= interaction.minimum
        if interaction.maximum is not None:
            matched = matched and value <= interaction.maximum
        matches.append(matched)
    if (
        interaction.expected is None
        and interaction.minimum is None
        and interaction.maximum is None
    ):
        return "observed", "recorded without an asserted expected value"
    if all(matches):
        return "pass", "every sample matched the evidence-backed expectation"
    return "fail", "one or more samples did not match the expected value/range"


def _expectation_document(interaction: Interaction) -> dict[str, object]:
    return {
        "register": f"CR{interaction.address:02X}",
        "mask": f"{interaction.mask:02X}",
        "expected": (
            f"{interaction.expected:02X}" if interaction.expected is not None else None
        ),
        "minimum": (
            f"{interaction.minimum:02X}" if interaction.minimum is not None else None
        ),
        "maximum": (
            f"{interaction.maximum:02X}" if interaction.maximum is not None else None
        ),
    }


def _run_interaction(
    session: ControllerSession,
    audit: AuditTrail,
    console: Console,
    interaction: Interaction,
    *,
    samples: int,
    sample_delay: float,
) -> dict[str, object]:
    if not console.ready_or_skip(interaction.instruction):
        return _step(
            audit,
            key=interaction.key,
            title=interaction.title,
            status="skipped",
            message="operator skipped this physical condition",
        )
    checkpoint = audit.checkpoint()
    try:
        values = _sample_register(
            session,
            interaction.address,
            samples=samples,
            sample_delay=sample_delay,
        )
        status, message = _evaluate(values, interaction)
        rendered = " ".join(f"{value:02X}" for value in values)
        print(f"{interaction.title}: CR{interaction.address:02X} = {rendered} -> {status}")
        return _step(
            audit,
            key=interaction.key,
            title=interaction.title,
            status=status,
            observations={
                "samples": [f"{value:02X}" for value in values],
                "stable": len(set(values)) == 1,
                "expectation": _expectation_document(interaction),
            },
            message=message,
            checkpoint=checkpoint,
        )
    except Exception as exc:
        print(f"{interaction.title}: ERROR: {exc}")
        return _step(
            audit,
            key=interaction.key,
            title=interaction.title,
            status="error",
            message=str(exc),
            checkpoint=checkpoint,
        )


def _capture_snapshot(
    session: ControllerSession,
    audit: AuditTrail,
    output_directory: Path,
    *,
    key: str,
    cycle: int,
    request_delay: float,
) -> tuple[dict[str, object], dict[str, object]]:
    checkpoint = audit.checkpoint()
    snapshot = session.poll_snapshot(request_delay=request_delay)
    document = snapshot.to_dict()
    path = output_directory / "snapshots" / f"{key}-{cycle:02d}.json"
    _write_json(path, document)
    step = _step(
        audit,
        key=f"{key}-{cycle:02d}",
        title=f"{key.replace('-', ' ').title()} cycle {cycle}",
        status="pass" if snapshot.fresh else "fail",
        observations={
            "path": str(path.relative_to(output_directory)),
            "controller_registers": document["controller_registers"],
            "telemetry_bytes": document["telemetry_bytes"],
            "unknown_cr02_bits": {
                "bit_1": bool(
                    snapshot.physical_inputs
                    and snapshot.physical_inputs.bit_1_unresolved
                ),
                "bit_7": bool(
                    snapshot.physical_inputs
                    and snapshot.physical_inputs.bit_7_unresolved
                ),
            },
        },
        message="complete CR00-CR0E typed snapshot",
        checkpoint=checkpoint,
    )
    return step, document


def _run_identity_repeats(
    session: ControllerSession,
    audit: AuditTrail,
    *,
    repeats: int,
    request_delay: float,
) -> dict[str, object]:
    checkpoint = audit.checkpoint()
    identities = [session.identity.to_dict()]
    for _ in range(repeats - 1):
        identities.append(session.refresh_identity(request_delay=request_delay).to_dict())
    stable = all(item == identities[0] for item in identities[1:])
    print(
        f"Identity: firmware {session.identity.firmware_version}, "
        f"format {session.identity.data_format:02X}, profile {session.profile.key}"
    )
    return _step(
        audit,
        key="identity-repeat",
        title="Repeated controller identity",
        status="pass" if stable else "fail",
        observations={"repeats": repeats, "identities": identities, "stable": stable},
        message="all identity reads matched" if stable else "identity reads differed",
        checkpoint=checkpoint,
    )


def _run_eeprom_backups(
    session: ControllerSession,
    audit: AuditTrail,
    output_directory: Path,
    *,
    copies: int,
    request_delay: float,
) -> dict[str, object]:
    checkpoint = audit.checkpoint()
    documents: list[dict[str, object]] = []
    hashes: list[str] = []
    for index in range(1, copies + 1):
        print(f"Reading EEPROM backup {index}/{copies}; this can take a while...")
        document = session.configuration_backup_document(request_delay=request_delay)
        path = output_directory / "backups" / f"eeprom-{index:02d}.json"
        _write_json(path, document)
        raw = bytes.fromhex(str(document["raw_hex"]))
        digest = hashlib.sha256(raw).hexdigest()
        hashes.append(digest)
        documents.append(
            {
                "path": str(path.relative_to(output_directory)),
                "raw_sha256": digest,
                "checksum": document["checksum"],
                "individualization": document["individualization"],
            }
        )
    checksums_valid = all(bool(item["checksum"]["matches"]) for item in documents)
    identical = len(set(hashes)) == 1
    status = "pass" if checksums_valid and identical else "fail"
    return _step(
        audit,
        key="eeprom-backup",
        title="Complete EEPROM backup and integrity",
        status=status,
        observations={
            "copies": documents,
            "all_checksums_match": checksums_valid,
            "all_copies_identical": identical,
        },
        message=(
            "all complete copies are checksum-valid and identical"
            if status == "pass"
            else "a checksum or cross-copy comparison failed"
        ),
        checkpoint=checkpoint,
    )


def _operator_status(observation: str) -> str:
    return {"yes": "pass", "no": "fail", "unknown": "indeterminate"}[observation]


def _drain_pending_frames(
    session: ControllerSession,
    *,
    max_frames: int = 1024,
) -> int:
    """Ingest queued unsolicited frames until one serial read timeout.

    Interactive prompts can leave several periodic telemetry bursts waiting in
    the host receive buffer.  A request sent into that backlog can be accepted
    by the controller while the caller times out parsing only stale frames.
    Draining through the recording transport preserves every byte and updates
    the monitor rather than silently discarding the evidence.
    """

    drained = 0
    while drained < max_frames:
        try:
            frame = session.client.receive_response()
        except TimeoutError:
            return drained
        except ValueError:
            drained += 1
            continue
        session.monitor.observe(frame)
        drained += 1
    raise TimeoutError(
        f"serial input did not become idle within {max_frames} queued frame(s)"
    )


def _send_remote_button(
    session: ControllerSession,
    audit: AuditTrail,
    console: Console,
    button: RemoteButton,
    *,
    key: str,
    title: str,
    observation_prompt: str,
) -> dict[str, object]:
    required = f"SEND {button.name}"
    if not console.phrase(
        f"Ready to transmit the reconstructed remote {button.name} command?",
        required,
    ):
        return _step(
            audit,
            key=key,
            title=title,
            status="skipped",
            message="per-command authorization phrase did not match",
        )
    checkpoint = audit.checkpoint()
    try:
        drained_before = _drain_pending_frames(session)
        receipt = session.client.remote_button(button)
        time.sleep(0.5)
        observed = console.observation(observation_prompt)
        after: dict[str, object] | None = None
        snapshot_error: str | None = None
        drained_after = 0
        try:
            drained_after = _drain_pending_frames(session)
            after = session.poll_snapshot(request_delay=0.10).to_dict()
        except Exception as exc:
            snapshot_error = str(exc)
        return _step(
            audit,
            key=key,
            title=title,
            status=_operator_status(observed),
            observations={
                "request_ascii": receipt.request.decode("ascii"),
                "request_hex": receipt.request.hex(" ").upper(),
                "operator_observed_expected_effect": observed,
                "queued_frames_ingested_before_command": drained_before,
                "queued_frames_ingested_after_observation": drained_after,
                "after": after,
                "post_command_snapshot_error": snapshot_error,
            },
            message=(
                "operator observation retained; post-command snapshot "
                + ("captured" if snapshot_error is None else "was unavailable")
            ),
            checkpoint=checkpoint,
        )
    except Exception as exc:
        return _step(
            audit,
            key=key,
            title=title,
            status="error",
            message=str(exc),
            checkpoint=checkpoint,
        )


def _run_control_tests(
    session: ControllerSession,
    audit: AuditTrail,
    console: Console,
    *,
    include_start: bool,
    start_observe_seconds: float,
) -> list[dict[str, object]]:
    results: list[dict[str, object]] = []
    print("\n=== OPTIONAL STATE-CHANGING REMOTE-CONTROL VALIDATION ===")
    print("The stove must be fully assembled, safely installed, and continuously supervised.")
    if not console.phrase("Authorize this entire control phase?", CONTROL_PHRASE):
        results.append(
            _step(
                audit,
                key="remote-control-phase",
                title="Remote-control phase",
                status="skipped",
                message="control authorization phrase did not match",
            )
        )
        return results
    safety = (
        "The stove has no exposed mains conductors and all operating covers are installed.",
        "The firebox door and ash drawer are closed and latched.",
        "The physical OFF control is immediately accessible and I will remain present.",
        "The stove is properly vented and safe to operate if an ON test was requested.",
    )
    for statement in safety:
        if not console.confirm(statement):
            raise SessionAborted(f"control safety condition declined: {statement}")

    if not include_start:
        reason = (
            "controller is required to be cold/off; OFF is not probative and "
            "UP/DOWN have no active heat level to change; no command was sent"
        )
        for key, title in (
            ("remote-off-cold", "Remote OFF while already cold/off"),
            ("remote-up", "Remote UP"),
            ("remote-down-restore", "Remote DOWN and level restoration"),
            ("remote-on-start", "Remote ON/start and OFF recovery"),
        ):
            results.append(
                _step(
                    audit,
                    key=key,
                    title=title,
                    status="skipped",
                    message=reason,
                )
            )
        return results

    results.append(
        _step(
            audit,
            key="remote-off-cold",
            title="Remote OFF while already cold/off",
            status="skipped",
            message="a no-op OFF while already off cannot prove command acceptance",
        )
    )

    _drain_pending_frames(session)
    before = session.poll_snapshot(request_delay=0.10)
    inputs = before.physical_inputs
    if inputs is None or inputs.firebox_door_open or inputs.ash_drawer_open:
        raise SessionAborted("fresh input snapshot does not prove both door and drawer closed")
    if not console.phrase(
        (
            "This will send remote ON and may begin fuel feed, fans, and ignition. "
            "Be ready to use the physical OFF control."
        ),
        START_PHRASE,
    ):
        results.append(
            _step(
                audit,
                key="remote-on-start",
                title="Remote ON/start and OFF recovery",
                status="skipped",
                message="start authorization phrase did not match",
            )
        )
        return results

    checkpoint = audit.checkpoint()
    start_attempted = False
    start_observation = "unknown"
    stop_observation = "unknown"
    snapshots: list[dict[str, object]] = []
    request_hex: list[str] = []
    up_result: dict[str, object] | None = None
    down_result: dict[str, object] | None = None
    post_shutdown_snapshot_error: str | None = None
    try:
        _drain_pending_frames(session)
        start_attempted = True
        start_receipt = session.client.remote_button(RemoteButton.ON)
        request_hex.append(start_receipt.request.hex(" ").upper())
        if start_observe_seconds:
            time.sleep(start_observe_seconds)
        start_observation = console.observation(
            "Did the stove visibly enter its normal startup sequence?"
        )
        if start_observation == "yes":
            up_result = _send_remote_button(
                session,
                audit,
                console,
                RemoteButton.UP,
                key="remote-up",
                title="Remote UP while running",
                observation_prompt=(
                    "Did the displayed/selected heat level increase exactly once?"
                ),
            )
            down_result = _send_remote_button(
                session,
                audit,
                console,
                RemoteButton.DOWN,
                key="remote-down-restore",
                title="Remote DOWN and level restoration while running",
                observation_prompt=(
                    "Did the displayed/selected heat level decrease exactly once, "
                    "restoring it?"
                ),
            )
        else:
            reason = "startup was not positively observed; UP/DOWN were not sent"
            up_result = _step(
                audit,
                key="remote-up",
                title="Remote UP while running",
                status="skipped",
                message=reason,
            )
            down_result = _step(
                audit,
                key="remote-down-restore",
                title="Remote DOWN and level restoration while running",
                status="skipped",
                message=reason,
            )
    finally:
        if start_attempted:
            print(
                "Sending remote OFF recovery command now. Use the physical OFF "
                "control too if needed."
            )
            try:
                stop_receipt = session.client.remote_button(RemoteButton.OFF)
                request_hex.append(stop_receipt.request.hex(" ").upper())
            except Exception as exc:
                print(f"WARNING: remote OFF transmission failed: {exc}", file=sys.stderr)
                print("USE THE PHYSICAL OFF CONTROL IMMEDIATELY.", file=sys.stderr)
    if start_attempted:
        stop_observation = console.observation(
            "Did the controller acknowledge OFF and begin its normal safe shutdown/cooldown?"
        )
        try:
            _drain_pending_frames(session)
            snapshots.append(session.poll_snapshot(request_delay=0.10).to_dict())
        except Exception as exc:
            post_shutdown_snapshot_error = str(exc)
    status = (
        "pass"
        if start_observation == "yes" and stop_observation == "yes"
        else "fail"
        if "no" in (start_observation, stop_observation)
        else "indeterminate"
    )
    results.append(
        _step(
            audit,
            key="remote-on-start",
            title="Remote ON/start and OFF recovery",
            status=status,
            observations={
                "requests_hex": request_hex,
                "start_observed": start_observation,
                "shutdown_observed": stop_observation,
                "poll_snapshots": snapshots,
                "post_shutdown_snapshot_error": post_shutdown_snapshot_error,
            },
            message="operator-observed startup and recovery; exact traffic preserved",
            checkpoint=checkpoint,
        )
    )
    assert up_result is not None and down_result is not None
    results.extend((up_result, down_result))
    return results


def _write_markdown_report(path: Path, summary: Mapping[str, object]) -> None:
    identity = summary.get("identity") or {}
    span = summary.get("audit_span") or {}
    lines = [
        "# OpenMaxFire live validation report",
        "",
        f"- Started: `{summary.get('started_utc')}`",
        f"- Completed: `{summary.get('completed_utc')}`",
        f"- Mode: `{summary.get('mode')}`",
        f"- Firmware: `{identity.get('firmware_version', 'unknown')}`",
        f"- Profile: `{identity.get('profile_key', 'unknown')}`",
        f"- Audit SHA-256: `{span.get('sha256', 'unavailable')}`",
        "",
        "## Results",
        "",
        "| Test | Status | Message |",
        "| --- | --- | --- |",
    ]
    for item in summary.get("steps", []):
        message = str(item.get("message", "")).replace("|", "\\|")
        lines.append(f"| {item.get('title')} | **{item.get('status')}** | {message} |")
    lines.extend(
        (
            "",
            "## Evidence boundary",
            "",
            "This session does not authorize configuration writes, factory Checkout actuators,",
            "raw commands, or firmware-loader traffic. A transmitted command is not reported as",
            "accepted without a corresponding controller or operator observation.",
            "",
        )
    )
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write("\n".join(lines))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Guided OpenMaxFire physical validation with exact-byte evidence"
    )
    parser.add_argument("--port", help="serial port, e.g. /dev/ttyUSB0 or COM3")
    parser.add_argument(
        "--baud",
        default="auto",
        choices=("auto", "9600", "19200"),
        help="read-only auto-detection by default",
    )
    parser.add_argument("--timeout", type=float, default=1.0)
    parser.add_argument("--request-delay", type=float, default=0.50)
    parser.add_argument("--samples", type=int, default=3)
    parser.add_argument("--sample-delay", type=float, default=0.25)
    parser.add_argument("--identity-repeats", type=int, default=3)
    parser.add_argument("--snapshot-cycles", type=int, default=3)
    parser.add_argument("--eeprom-copies", type=int, default=1)
    parser.add_argument("--skip-eeprom", action="store_true")
    parser.add_argument("--skip-interactive-inputs", action="store_true")
    parser.add_argument(
        "--include-control",
        action="store_true",
        help="enable the separately authorized remote-control phase",
    )
    parser.add_argument(
        "--include-start-test",
        action="store_true",
        help="offer state-aware ON/UP/DOWN/OFF validation while operating",
    )
    parser.add_argument("--start-observe-seconds", type=float, default=15.0)
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="new or empty output directory (default: live-validation/<UTC timestamp>)",
    )
    parser.add_argument(
        "--simulate",
        action="store_true",
        help="exercise only automatic phases against the in-memory format-04 simulator",
    )
    return parser


def _validate_args(parser: argparse.ArgumentParser, args: argparse.Namespace) -> None:
    if not args.simulate and not args.port:
        parser.error("--port is required unless --simulate is used")
    if args.include_start_test and not args.include_control:
        parser.error("--include-start-test requires --include-control")
    for name in ("samples", "identity_repeats", "snapshot_cycles", "eeprom_copies"):
        if getattr(args, name) < 1:
            parser.error(f"--{name.replace('_', '-')} must be at least 1")
    for name in ("timeout", "request_delay", "sample_delay", "start_observe_seconds"):
        value = getattr(args, name)
        if (
            not math.isfinite(value)
            or value < 0
            or (name == "timeout" and value == 0)
        ):
            parser.error(f"--{name.replace('_', '-')} has an invalid value")
    if args.simulate and (args.include_control or args.include_start_test):
        parser.error("state-changing phases are not available with --simulate")


def _read_only_safety(console: Console) -> list[str]:
    statements = (
        "The controller is cold/off and no startup or shutdown transition is active.",
        "The interface is verified 5 V TTL, with adapter VCC and J3 pin 3 disconnected.",
        "J3 ground/TX/RX were traced for this exact 9067-0604 board revision.",
        "There are no exposed mains conductors and I will not move internal wiring while powered.",
        (
            "I understand this default phase sends reads only, but opening the "
            "serial port is not electrically passive."
        ),
    )
    confirmed: list[str] = []
    print("=== READ-ONLY SAFETY CHECK ===")
    for statement in statements:
        if not console.confirm(statement):
            raise SessionAborted(f"safety condition declined: {statement}")
        confirmed.append(statement)
    return confirmed


def _connect_physical(
    args: argparse.Namespace,
    audit: AuditTrail,
) -> tuple[ControllerSession, dict[str, object] | None]:
    if args.baud != "auto":
        return (
            ControllerSession.connect(
                args.port,
                baudrate=int(args.baud),
                timeout=args.timeout,
                request_delay=args.request_delay,
                audit=audit,
            ),
            None,
        )

    shared_recorder = _SharedAuditRecorder(audit)

    def audited_transport(settings):
        return RecordingTransport(SerialTransport(settings), shared_recorder)

    detection = detect_controller(
        args.port,
        baudrates=(9600, 19200),
        timeout=args.timeout,
        request_delay=args.request_delay,
        transport_factory=audited_transport,
    )
    if detection.status is DetectionStatus.NO_RESPONSE:
        raise OpenMaxFireError(f"no supported controller responded on {args.port}")
    if detection.status is DetectionStatus.UNSUPPORTED:
        assert detection.identity is not None
        raise UnsupportedControllerError(
            f"unsupported controller {detection.identity.firmware_version}/"
            f"format {detection.identity.data_format:02X} on {args.port}"
        )
    assert detection.baudrate is not None
    session = ControllerSession.connect(
        args.port,
        baudrate=detection.baudrate,
        timeout=args.timeout,
        request_delay=args.request_delay,
        audit=audit,
    )
    return session, detection.to_dict()


def run(args: argparse.Namespace, *, console: Console | None = None) -> tuple[int, Path]:
    console = console or Console()
    output_directory = _prepare_output_directory(
        args.output_dir or Path("live-validation") / _timestamp_slug()
    )
    summary: dict[str, object] = {
        "schema": SCHEMA,
        "openmaxfire_version": openmaxfire.__version__,
        "started_utc": _utc_now(),
        "completed_utc": None,
        "mode": "simulated-read-only" if args.simulate else "physical",
        "requested": {
            "port": args.port,
            "baud": args.baud,
            "include_control": args.include_control,
            "include_start_test": args.include_start_test,
        },
        "safety_confirmations": [],
        "identity": None,
        "connection": None,
        "detection": None,
        "steps": [],
        "session_status": "started",
    }
    audit = AuditTrail(
        output_directory / "traffic.jsonl",
        metadata={
            "purpose": "guided live validation",
            "mode": summary["mode"],
            "requested_port": args.port,
            "requested_baud": args.baud,
            "configuration_writes": False,
            "checkout_actuators": False,
            "firmware_loader": False,
        },
    )
    session: ControllerSession | None = None
    exit_code = 0
    try:
        if not args.simulate:
            summary["safety_confirmations"] = _read_only_safety(console)
            session, detection = _connect_physical(args, audit)
            summary["detection"] = detection
        else:
            session = ControllerSession.simulated("fw202-format04", audit=audit)

        summary["identity"] = {
            **session.identity.to_dict(),
            "profile_key": session.profile.key,
        }
        summary["connection"] = session.connection.to_dict()
        steps = summary["steps"]
        assert isinstance(steps, list)
        steps.append(
            _run_identity_repeats(
                session,
                audit,
                repeats=args.identity_repeats,
                request_delay=args.request_delay,
            )
        )
        print("Capturing complete controller/telemetry snapshots...")
        for cycle in range(1, args.snapshot_cycles + 1):
            step, _ = _capture_snapshot(
                session,
                audit,
                output_directory,
                key="cold-baseline",
                cycle=cycle,
                request_delay=args.request_delay,
            )
            steps.append(step)

        if args.skip_eeprom:
            steps.append(
                _step(
                    audit,
                    key="eeprom-backup",
                    title="Complete EEPROM backup and integrity",
                    status="skipped",
                    message="--skip-eeprom was supplied",
                )
            )
        else:
            steps.append(
                _run_eeprom_backups(
                    session,
                    audit,
                    output_directory,
                    copies=args.eeprom_copies,
                    request_delay=args.request_delay,
                )
            )

        if not args.simulate and not args.skip_interactive_inputs:
            print("\n=== GUIDED PHYSICAL INPUT CORRELATION ===")
            print("Each condition is sampled repeatedly. Type s whenever a test is not safe today.")
            for interaction in INTERACTIONS:
                steps.append(
                    _run_interaction(
                        session,
                        audit,
                        console,
                        interaction,
                        samples=args.samples,
                        sample_delay=args.sample_delay,
                    )
                )
        else:
            steps.append(
                _step(
                    audit,
                    key="physical-inputs",
                    title="Guided physical-input correlation",
                    status="skipped",
                    message=(
                        "simulation has no operator inputs"
                        if args.simulate
                        else "--skip-interactive-inputs was supplied"
                    ),
                )
            )

        if args.include_control:
            steps.extend(
                _run_control_tests(
                    session,
                    audit,
                    console,
                    include_start=args.include_start_test,
                    start_observe_seconds=args.start_observe_seconds,
                )
            )
        else:
            steps.append(
                _step(
                    audit,
                    key="remote-control-phase",
                    title="Remote-control validation",
                    status="skipped",
                    message="default read-only run; no remote command was sent",
                )
            )
        summary["session_status"] = "completed"
    except SessionAborted as exc:
        summary["session_status"] = "aborted"
        summary["error"] = str(exc)
        print(f"Session aborted safely: {exc}", file=sys.stderr)
        exit_code = 2
    except KeyboardInterrupt:
        summary["session_status"] = "interrupted"
        summary["error"] = "operator interrupted the session"
        print("Session interrupted by operator.", file=sys.stderr)
        exit_code = 130
    except Exception as exc:
        summary["session_status"] = "error"
        summary["error"] = f"{type(exc).__name__}: {exc}"
        print(f"Validation error: {exc}", file=sys.stderr)
        exit_code = 1
    finally:
        if session is not None:
            session.close()
        else:
            audit.close()
        summary["completed_utc"] = _utc_now()
        summary["audit_span"] = audit.span().to_dict()
        _write_json(output_directory / "summary.json", summary)
        _write_markdown_report(output_directory / "RESULTS.md", summary)
    print(f"\nEvidence saved under: {output_directory}")
    print(f"Summary: {output_directory / 'summary.json'}")
    print(f"Exact traffic: {output_directory / 'traffic.jsonl'}")
    return exit_code, output_directory


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    _validate_args(parser, args)
    code, _ = run(args)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
