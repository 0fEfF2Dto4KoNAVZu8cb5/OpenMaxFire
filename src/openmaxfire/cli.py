"""Cross-platform ``maxfirectl`` command-line utility."""

from __future__ import annotations

import argparse
import json
import math
import signal
import sys
import time
from pathlib import Path
from typing import Mapping

from .audit import AuditTrail
from .backup import build_eeprom_backup, save_json_document
from .client import (
    MaxFireClient,
    StoveIdentity,
    contains_loader_traffic,
    validate_generic_raw_payload,
)
from .errors import OpenMaxFireError, SafetyInterlockError, VerificationError
from .firmware import FirmwareImage
from .flashing import (
    LOADER_BAUDRATE,
    FlashJournal,
    FlashSessionState,
    FlashSessionStatus,
    FlashSafetyInterlocks,
    LiveAttemptEvent,
    LiveLoaderPolicy,
    approve_live_firmware,
    delegate_recovery_source,
    execute_loader_rehearsal,
    execute_live_loader_plan,
    load_recovery_bundle,
    prepare_live_flash,
    prepare_recovery_flash,
    preserve_recovery_bundle,
    qualify_flash_preparation,
    recover_live_loader_completion,
    wait_for_application_ready,
    verify_application_unchanged,
    verify_post_flash,
    validate_live_transition,
)
from .loader import LoaderAttemptOutcome, build_loader_plan
from .runtime_safety import DeferredTerminationSignals, SleepInhibitor
from .monitor import (
    JsonlMonitorRecorder,
    MonitorState,
    format_monitor_summary,
    replay_capture,
)
from .protocol import (
    ProtocolError,
    RemoteButton,
    encode_read_register,
    encode_remote_button,
    encode_write_register,
)
from .transport import (
    JsonlTrafficRecorder,
    RecordingTransport,
    SerialSettings,
    SerialTransport,
    list_serial_ports,
)
from .transactions import (
    TransactionPlan,
    execute_transaction,
    load_transaction_plan,
)
from .profiles import PROFILES_BY_KEY


LIVE_COMMANDS = frozenset(
    ("capture", "read", "write", "raw", "transaction", "identify", "backup", "monitor", "button")
)
MONITOR_REGISTERS = tuple(range(0x0F))
_LIVE_E3_CLI_DISABLED_MESSAGE = (
    "Refusing physical loader traffic: the manual AC/BREAK rehearsal, "
    "programming, and recovery workflows are retired. Only flash --plan-only "
    "is available; future zero-write or write execution requires a separately "
    "implemented fixture-specific path on safely powered spare hardware."
)


def _int_auto(value: str) -> int:
    return int(value, 0)


def _byte_auto(value: str) -> int:
    try:
        parsed = _int_auto(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("expected a byte value such as 0x0E") from exc
    if not 0 <= parsed <= 0xFF:
        raise argparse.ArgumentTypeError("value must be between 0x00 and 0xFF")
    return parsed


def _positive_float(value: str) -> float:
    try:
        parsed = float(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("expected a positive number") from exc
    if not math.isfinite(parsed) or parsed <= 0:
        raise argparse.ArgumentTypeError("value must be greater than zero")
    return parsed


def _nonnegative_float(value: str) -> float:
    try:
        parsed = float(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("expected a nonnegative number") from exc
    if not math.isfinite(parsed) or parsed < 0:
        raise argparse.ArgumentTypeError("value must be zero or greater")
    return parsed


def _positive_int(value: str) -> int:
    try:
        parsed = int(value, 0)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("expected a positive integer") from exc
    if parsed < 1:
        raise argparse.ArgumentTypeError("value must be at least one")
    return parsed


def _add_live_ack(parser: argparse.ArgumentParser, *, writes: bool = False) -> None:
    noun = "commands" if writes else "serial I/O"
    parser.add_argument(
        "--i-understand-unverified-io",
        action="store_true",
        help=f"required until J3 electrical behavior and {noun} are live-validated",
    )


def _add_state_change_ack(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--i-understand-this-can-change-stove-state",
        action="store_true",
        help="required for raw or state-changing live traffic",
    )


def _raw_hex(value: str) -> bytes:
    compact = "".join(value.replace(":", " ").replace(",", " ").split())
    if not compact:
        raise argparse.ArgumentTypeError("raw hexadecimal payload cannot be empty")
    try:
        return bytes.fromhex(compact)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            "expected hexadecimal bytes such as 43 52 30 30"
        ) from exc


def _display_bytes(value: bytes) -> str:
    return "".join(
        chr(byte) if 0x20 <= byte <= 0x7E else f"\\x{byte:02X}"
        for byte in value
    )


def _is_loader_traffic(value: bytes) -> bool:
    return contains_loader_traffic(value)


def _connect(
    args: argparse.Namespace,
    *,
    traffic_path: Path | None = None,
    overwrite_traffic: bool = False,
) -> MaxFireClient:
    settings = SerialSettings(args.port, args.baud, args.timeout)
    recorder = None
    if traffic_path is not None:
        recorder = JsonlTrafficRecorder(
            traffic_path,
            metadata={
                "command": args.command,
                "port": settings.port,
                "baudrate": settings.baudrate,
                "timeout": settings.timeout,
                "serial_format": "8N1",
                "dtr": True,
                "rts": True,
                "flow_control": "none",
                "request_terminator": "none",
            },
            overwrite=overwrite_traffic,
        )
    try:
        transport = SerialTransport(settings)
    except BaseException:
        if recorder is not None:
            recorder.close()
        raise
    if recorder is not None:
        transport = RecordingTransport(transport, recorder)
    return MaxFireClient(transport)


def _print_identity(identity: StoveIdentity, *, as_json: bool) -> None:
    document = identity.to_dict()
    if as_json:
        print(json.dumps(document, indent=2, sort_keys=True))
        return
    print(f"Firmware: {identity.firmware_version}")
    print(f"Data format: {identity.data_format:02X}")
    for register, value in document["registers"].items():
        print(f"{register}={value}")
    print("Static pairing recognized: " + ("yes" if identity.recognized else "no"))


def _run_ports(args: argparse.Namespace) -> int:
    ports = list_serial_ports()
    if args.json:
        print(json.dumps([port.to_dict() for port in ports], indent=2, sort_keys=True))
        return 0
    if not ports:
        print("No serial ports found.")
        return 0
    for port in ports:
        details = [port.description or "serial port"]
        if port.usb_id:
            details.append(f"USB {port.usb_id}")
        if port.serial_number:
            details.append(f"serial={port.serial_number}")
        if port.manufacturer:
            details.append(f"manufacturer={port.manufacturer}")
        if port.product and port.product != port.description:
            details.append(f"product={port.product}")
        if port.location:
            details.append(f"location={port.location}")
        print(f"{port.device}: " + " | ".join(details))
    return 0


def _run_replay(args: argparse.Namespace) -> int:
    result = replay_capture(args.input, stale_after=args.stale_after)
    now_ns = result.last_monotonic_ns if result.last_monotonic_ns is not None else 0
    snapshot = result.state.snapshot(
        now_monotonic_ns=now_ns,
        source="replay",
    )
    snapshot["replay"] = {
        "input": str(args.input),
        "session_metadata": dict(result.session_metadata),
        "traffic_events": result.traffic_events,
        "rx_chunks": result.rx_chunks,
        "rx_bytes": result.rx_bytes,
        "parsed_frames": result.parsed_frames,
        "malformed_lines": result.malformed_lines,
        "trailing_hex": result.trailing_bytes.hex(" ").upper(),
    }
    if args.output is not None:
        save_json_document(snapshot, args.output, overwrite=args.overwrite)
    if args.json:
        print(json.dumps(snapshot, sort_keys=True))
    else:
        print(format_monitor_summary(snapshot))
        print(
            f"Replay: frames={result.parsed_frames} malformed={result.malformed_lines} "
            f"rx-bytes={result.rx_bytes} trailing={len(result.trailing_bytes)}"
        )
        if args.output is not None:
            print(f"Saved final replay snapshot: {args.output}")
    return 0


def _run_monitor(client: MaxFireClient, args: argparse.Namespace) -> int:
    state = MonitorState(stale_after=args.stale_after)
    recorder = None
    if args.output is not None:
        recorder = JsonlMonitorRecorder(
            args.output,
            metadata={
                "command": "monitor",
                "port": args.port,
                "baudrate": args.baud,
                "request_delay": args.request_delay,
                "poll_registers": [f"CR{address:02X}" for address in MONITOR_REGISTERS],
                "read_only": True,
            },
            overwrite=args.overwrite,
        )

    started = time.monotonic()
    deadline = started + args.duration if args.duration else None
    cycles = 0
    total_timeouts = 0
    try:
        while True:
            cycle_timeouts = 0
            for index, address in enumerate(MONITOR_REGISTERS):
                try:
                    client.query_register(address, on_frame=state.observe)
                except TimeoutError:
                    cycle_timeouts += 1
                    total_timeouts += 1
                if deadline is not None and time.monotonic() >= deadline:
                    break
                if args.request_delay and index + 1 < len(MONITOR_REGISTERS):
                    time.sleep(args.request_delay)

            cycles += 1
            snapshot = state.snapshot(source="live")
            snapshot["poll"] = {
                "cycle": cycles,
                "cycle_timeouts": cycle_timeouts,
                "total_timeouts": total_timeouts,
                "registers": [f"CR{address:02X}" for address in MONITOR_REGISTERS],
                "read_only": True,
            }
            if args.json:
                print(json.dumps(snapshot, sort_keys=True), flush=True)
            else:
                print(format_monitor_summary(snapshot), flush=True)
            if recorder is not None:
                recorder.record(snapshot)

            if args.cycles is not None and cycles >= args.cycles:
                break
            if deadline is not None and time.monotonic() >= deadline:
                break
    finally:
        if recorder is not None:
            recorder.close()
    return 0


def _flash_interlocks(args: argparse.Namespace) -> FlashSafetyInterlocks:
    return FlashSafetyInterlocks(
        stove_cold_and_off=args.confirm_stove_cold_and_off,
        igniters_physically_unplugged=args.confirm_igniters_unplugged,
        actuator_loads_physically_unplugged=(
            args.confirm_actuator_loads_unplugged
        ),
        correct_5v_ttl_wiring=args.confirm_correct_5v_ttl_wiring,
        j3_pin3_disconnected=args.confirm_j3_pin3_disconnected,
        adapter_vcc_disconnected=args.confirm_adapter_vcc_disconnected,
        pickit_recovery_tested_on_spare=args.confirm_pickit_recovery_tested_on_spare,
        computer_power_stable=args.confirm_computer_power_stable,
        stove_power_stable=args.confirm_stove_power_stable,
        calibration_plan_ready=args.confirm_calibration_plan,
        downgrade_stale_flash_accepted=False,
        recovery_target_matches_backup=args.confirm_recovery_target_matches_backup,
    )


class _NullTrafficRecorder:
    """Post-write fallback when diagnostics fail but verification must continue."""

    def record(self, direction: str, data: bytes) -> None:
        return None

    def close(self) -> None:
        return None


def _remember_host_diagnostic(
    errors: list[str], label: str, exc: BaseException
) -> None:
    message = f"{label}: {type(exc).__name__}: {exc}"
    if message not in errors and len(errors) < 20:
        errors.append(message)
        _safe_console(message, error=True)


def _open_recorded_client(
    args: argparse.Namespace,
    *,
    transport,
    baudrate: int,
    traffic_path: Path,
    phase: str,
    diagnostic_errors: list[str] | None = None,
) -> MaxFireClient:
    transport.set_baudrate(baudrate)
    transport.set_timeout(args.timeout)
    try:
        recorder = JsonlTrafficRecorder(
            traffic_path,
            metadata={
                "command": "flash",
                "phase": phase,
                "port": args.port,
                "baudrate": baudrate,
                "timeout": args.timeout,
                "serial_format": "8N1",
                "flow_control": "none",
                "single_exclusive_handle": (
                    not getattr(args, "hold_tx_break_during_power_off", False)
                ),
            },
            durable=True,
        )
    except (OSError, RuntimeError, ValueError) as exc:
        if diagnostic_errors is None:
            raise
        _remember_host_diagnostic(
            diagnostic_errors, f"{phase} traffic recorder unavailable", exc
        )
        recorder = _NullTrafficRecorder()
    try:
        return MaxFireClient(
            RecordingTransport(
                transport,
                recorder,
                close_transport=False,
                diagnostic_errors=diagnostic_errors,
            )
        )
    except BaseException:
        recorder.close()
        raise


def _run_flash_plan(args: argparse.Namespace, image: FirmwareImage) -> int:
    if args.current_profile is None:
        print("flash --plan-only requires --current-profile", file=sys.stderr)
        return 2
    approved = approve_live_firmware(image)
    profile = PROFILES_BY_KEY[args.current_profile]
    plan = build_loader_plan(image, profile, authenticated_simulator_plan=True)
    migration = approved.target_profile.data_format != profile.data_format
    calibration = approved.firmware_version != profile.firmware_version
    downgrade = tuple(map(int, approved.firmware_version.split("."))) < tuple(
        map(int, profile.firmware_version.split("."))
    )
    validate_live_transition(profile.firmware_version, approved.firmware_version)
    document = {
        "schema": "openmaxfire.live-flash-plan.v2",
        "approved_firmware": approved.to_dict(),
        "current_profile": profile.to_dict(),
        "data_format_migration_required": migration,
        "calibration_required": calibration,
        "downgrade": downgrade,
        "execution_mode": "offline_authenticated_plan",
        "physical_e3_enabled": False,
        "safety_boundary": (
            "planning only; all physical loader traffic is hard-disabled pending a "
            "separately implemented and electrically qualified loader-entry fixture"
        ),
        "loader_plan": plan.to_dict(),
    }
    print(json.dumps(document, indent=None if args.json else 2, sort_keys=True))
    return 0


def _attempt_post_flash(
    args: argparse.Namespace,
    preparation,
    *,
    transport,
    session_dir: Path,
    attempt: int,
    diagnostic_errors: list[str],
):
    client = _open_recorded_client(
        args,
        transport=transport,
        baudrate=preparation.approved.application_baudrate,
        traffic_path=session_dir / f"postflash-traffic-{attempt}.jsonl",
        phase=f"postflash-{attempt}",
        diagnostic_errors=diagnostic_errors,
    )
    try:
        time.sleep(args.handoff_delay)
        readiness = wait_for_application_ready(
            client,
            timeout=args.application_ready_timeout,
        )
        save_json_document(
            readiness.to_dict(),
            session_dir / f"postflash-readiness-{attempt}.json",
        )
        return verify_post_flash(
            client,
            preparation,
            request_delay=args.request_delay,
        )
    finally:
        client.close()


def _save_flash_result(session_dir: Path, document: dict[str, object]) -> None:
    path = session_dir / "result.json"
    save_json_document(document, path, overwrite=path.exists())


def _safe_console(message: str, *, error: bool = False) -> None:
    try:
        print(message, file=sys.stderr if error else sys.stdout, flush=True)
    except OSError:
        # Console/log-pipe failure must not interrupt a controller once the
        # application image may be partial.
        pass


def _power_off_phrase(prompt: str, expected: str) -> bool:
    try:
        return input(prompt).strip() == expected
    except EOFError:
        return False


def _run_flash(args: argparse.Namespace) -> int:
    # The only physical loader entry currently implemented below crosses a
    # manual AC power boundary, optionally while a USB-powered FTDI asserts
    # BREAK. Reject every physical loader invocation before image access,
    # session mutation, serial I/O, or an operator power-cycle prompt. The
    # direct executor API remains available for simulator qualification.
    if not args.plan_only:
        print(_LIVE_E3_CLI_DISABLED_MESSAGE, file=sys.stderr)
        return 4

    journal: FlashJournal | None = None
    session_state: FlashSessionState | None = None
    serial_transport = None
    session_dir: Path | None = args.session_dir
    programming_armed = False
    tx_break_active = False
    final_written = False
    preexisting_recovery = args.recover_from_session is not None
    host_diagnostic_errors: list[str] = []

    def change_tx_break(active: bool, *, phase: str, purpose: str) -> None:
        nonlocal tx_break_active
        if serial_transport is None:
            raise SafetyInterlockError(
                "UART BREAK control requires an open exclusive serial handle"
            )
        serial_transport.set_break(active)
        tx_break_active = active
        if journal is not None:
            journal.record(
                "tx_break_changed",
                active=active,
                phase=phase,
                purpose=purpose,
            )

    def close_after_confirmed_usb_removal(*, phase: str) -> None:
        nonlocal serial_transport, tx_break_active
        if serial_transport is None:
            raise SafetyInterlockError(
                "USB power removal requires an open serial handle to close"
            )
        try:
            serial_transport.close()
        except OSError:
            # Physical USB removal commonly invalidates the old handle before
            # pySerial can close it. The operator phrase is the power-removal
            # interlock; the stale handle must never be reused.
            pass
        serial_transport = None
        tx_break_active = False
        if journal is not None:
            journal.record(
                "tx_break_changed",
                active=False,
                phase=phase,
                purpose="FTDI USB power physically removed; stale handle closed",
            )
            journal.record(
                "serial_handle_closed_for_usb_power_removal",
                phase=phase,
            )

    def reopen_serial_after_usb_reconnect(*, baudrate: int, phase: str) -> None:
        nonlocal serial_transport
        if serial_transport is not None:
            raise SafetyInterlockError(
                "refusing to reopen FTDI while an earlier serial handle remains"
            )
        last_error: OSError | None = None
        for attempt in range(1, 21):
            try:
                serial_transport = SerialTransport(
                    SerialSettings(
                        args.port,
                        baudrate,
                        args.timeout,
                        exclusive=True,
                    )
                )
                if journal is not None:
                    journal.record(
                        "serial_handle_reopened_after_usb_power_removal",
                        phase=phase,
                        baudrate=baudrate,
                        attempt=attempt,
                    )
                return
            except OSError as exc:
                last_error = exc
                time.sleep(0.25)
        raise OSError(
            f"FTDI did not re-enumerate on {args.port} after USB reconnect: "
            f"{last_error}"
        )

    try:
        if args.plan_only:
            if args.image is None:
                print("flash --plan-only requires an image", file=sys.stderr)
                return 2
            if args.session_dir is not None:
                print("--session-dir is not used with --plan-only", file=sys.stderr)
                return 2
            if args.traffic_log is not None:
                print("--traffic-log is not used with --plan-only", file=sys.stderr)
                return 2
            if args.recover_from_session is not None:
                print("--recover-from-session is only valid for live flashing", file=sys.stderr)
                return 2
            if args.rehearsal_only:
                print("--rehearsal-only cannot be combined with --plan-only", file=sys.stderr)
                return 2
            if args.hold_tx_break_during_power_off:
                print(
                    "--hold-tx-break-during-power-off requires a live flash run",
                    file=sys.stderr,
                )
                return 2
            image = FirmwareImage.load(args.image)
            approve_live_firmware(image)
            return _run_flash_plan(args, image)

        if not args.port or args.baud is None:
            print("--port and --baud are required for live flashing", file=sys.stderr)
            return 2
        if args.current_profile is not None:
            print("--current-profile is only valid with --plan-only", file=sys.stderr)
            return 2
        if args.session_dir is None:
            print("live flashing requires a new --session-dir", file=sys.stderr)
            return 2
        if args.rehearsal_only and args.recover_from_session is not None:
            print(
                "--rehearsal-only is unavailable with --recover-from-session",
                file=sys.stderr,
            )
            return 2
        if args.traffic_log is not None:
            print(
                "flash records its own session traffic; do not pass --traffic-log",
                file=sys.stderr,
            )
            return 2
        if args.recover_from_session is None and args.image is None:
            print("live flashing requires an image", file=sys.stderr)
            return 2

        recovery_source = args.recover_from_session
        source_preparation: Mapping[str, object] | None = None
        source_backup: Mapping[str, object] | None = None
        recovery_manifest: Mapping[str, object] | None = None
        if recovery_source is None:
            assert args.image is not None
            image_source_path = args.image
            image = FirmwareImage.load(image_source_path)
            approve_live_firmware(image)
        else:
            image, source_preparation, source_backup, recovery_manifest = (
                load_recovery_bundle(
                    recovery_source,
                    supplied_image=args.image,
                )
            )
            image_source_path = (
                recovery_source
                / "rescue"
                / str(recovery_manifest["firmware_filename"])
            )

        policy = LiveLoaderPolicy(
            identify_attempts=args.loader_identify_attempts,
            identify_retry_delay=args.loader_identify_retry_delay,
            retry_delay=args.retry_delay,
            probe_timeout=args.loader_probe_timeout,
            post_identify_settle_delay=args.loader_settle_delay,
            response_timeout=args.loader_response_timeout,
        )

        session_dir = args.session_dir
        interlocks = _flash_interlocks(args)
        # Opening a serial device can transition DTR/RTS. Require every base
        # physical prerequisite before even the read-only preflight opens it.
        interlocks.validate(
            # Every supported live transition changes firmware version. Require
            # the calibration plan before opening a serial device at all.
            calibration_required=True,
            downgrade=False,
            recovery_mode=preexisting_recovery,
        )
        session_dir.mkdir(parents=True, exist_ok=False)
        session_state = FlashSessionState(
            session_dir,
            metadata={
                "port": args.port,
                "current_baudrate": args.baud,
                "target_baudrate": approve_live_firmware(image).application_baudrate,
                "image_sha256": image.sha256,
                "recovery_source": str(recovery_source) if recovery_source else None,
                "hold_tx_break_during_power_off": (
                    args.hold_tx_break_during_power_off
                ),
            },
        )

        if recovery_source is None:
            serial_transport = SerialTransport(
                SerialSettings(args.port, args.baud, args.timeout, exclusive=True)
            )
            preflight_client = _open_recorded_client(
                args,
                transport=serial_transport,
                baudrate=args.baud,
                traffic_path=session_dir / "preflight-traffic.jsonl",
                phase="preflight",
            )
            try:
                preparation = prepare_live_flash(
                    preflight_client,
                    image,
                    port=args.port,
                    current_baudrate=args.baud,
                    interlocks=interlocks,
                    request_delay=args.request_delay,
                    backup_path=session_dir / "eeprom-before.json",
                )
            finally:
                preflight_client.close()
        else:
            assert source_preparation is not None and source_backup is not None
            source_plan = source_preparation.get("loader_plan")
            if (
                not isinstance(source_plan, dict)
                or source_plan.get("image_sha256") != image.sha256
            ):
                raise VerificationError(
                    "recovery session was prepared for a different firmware image"
                )
            preparation = prepare_recovery_flash(
                image,
                source_backup,
                port=args.port,
                current_baudrate=args.baud,
                interlocks=interlocks,
            )
            rebuilt = preparation.to_dict()
            if (
                source_plan.get("profile_key") != preparation.current_profile.key
                or source_preparation.get("eeprom_before_sha256")
                != rebuilt["eeprom_before_sha256"]
            ):
                raise VerificationError(
                    "recovery session preparation and EEPROM backup do not match"
                )

        if preparation.recovery_mode:
            save_json_document(preparation.eeprom_backup, session_dir / "eeprom-before.json")
        preparation_document = preparation.to_dict()
        save_json_document(preparation_document, session_dir / "preparation.json")
        offline_qualification = qualify_flash_preparation(preparation)
        save_json_document(
            offline_qualification.to_dict(),
            session_dir / "offline-qualification.json",
        )
        recovery_bundle = preserve_recovery_bundle(
            image_source_path,
            image,
            preparation_document,
            session_dir=session_dir,
        )
        journal = FlashJournal(
            session_dir / "journal.jsonl",
            metadata={
                "port": args.port,
                "current_baudrate": args.baud,
                "loader_baudrate": LOADER_BAUDRATE,
                "target_baudrate": preparation.approved.application_baudrate,
                "image_sha256": image.sha256,
                "current_profile": preparation.current_profile.key,
                "target_profile": preparation.approved.target_profile_key,
                "interlocks": interlocks.to_dict(),
                "recovery_mode": preparation.recovery_mode,
                "recovery_source": str(recovery_source) if recovery_source else None,
                "recovery_manifest": recovery_bundle,
                "single_exclusive_serial_handle": (
                    not args.hold_tx_break_during_power_off
                ),
                "usb_power_removal_before_application_verification": (
                    args.hold_tx_break_during_power_off
                ),
                "hold_tx_break_during_power_off": (
                    args.hold_tx_break_during_power_off
                ),
            },
        )
        session_state.transition(
            FlashSessionStatus.PREPARED,
            message=(
                "recovery artifacts and exact replay plan authenticated"
                if preparation.recovery_mode
                else "stable identity, repeated EEPROM backup, and offline image simulation passed"
            ),
            recovery_required=preparation.recovery_mode,
            current_profile=preparation.current_profile.key,
            target_profile=preparation.approved.target_profile_key,
        )
        if recovery_source is not None:
            delegation = delegate_recovery_source(
                recovery_source,
                session_dir,
                image_sha256=image.sha256,
            )
            journal.record(
                "recovery_source_delegated", delegation=dict(delegation)
            )

        if preparation.recovery_mode:
            _safe_console("Recovery session and saved EEPROM backup authenticated.")
        else:
            _safe_console(
                "Preflight passed: identity was stable, EEPROM A00-AFF matched twice, "
                "and the exact image passed whole-plan simulation."
            )

        if not preparation.recovery_mode:
            assert serial_transport is not None
            session_state.transition(
                FlashSessionStatus.REHEARSAL_ARMED,
                message="waiting for the non-writing loader rehearsal power cycle",
                recovery_required=False,
            )
            if args.hold_tx_break_during_power_off:
                change_tx_break(
                    True,
                    phase="rehearsal_power_off",
                    purpose="hold FTDI TX low while controller power is removed",
                )
                _safe_console(
                    "NON-WRITING REHEARSAL: FTDI TX BREAK is active (orange TX held "
                    "low). Disconnect stove AC now. Keep both igniters physically "
                    "unplugged and hazardous actuator loads disconnected; do not "
                    "restore AC until instructed."
                )
            else:
                _safe_console(
                    "NON-WRITING REHEARSAL: disconnect stove AC now. Keep both "
                    "igniters physically unplugged and hazardous actuator loads "
                    "disconnected."
                )
            if not _power_off_phrase(
                "After AC is physically disconnected, type POWER OFF FOR REHEARSAL: ",
                "POWER OFF FOR REHEARSAL",
            ):
                journal.record(
                    "operator_abort",
                    reason="rehearsal power-off phrase did not match",
                )
                session_state.transition(
                    FlashSessionStatus.ABORTED_SAFE,
                    message="operator aborted before non-writing loader traffic",
                    recovery_required=False,
                )
                final = {
                    "schema": "openmaxfire.flash-result.v2",
                    "successful": False,
                    "programming_performed": False,
                    "recovery_required": False,
                    "message": "aborted before loader rehearsal; no E3 frame was sent",
                }
                _save_flash_result(session_dir, final)
                final_written = True
                _safe_console(final["message"], error=True)  # type: ignore[arg-type]
                return 3

            serial_transport.set_baudrate(LOADER_BAUDRATE)
            if tx_break_active:
                change_tx_break(
                    False,
                    phase="rehearsal_loader_probe",
                    purpose="release FTDI TX immediately before loader probes",
                )
            rehearsal_audit = AuditTrail(
                session_dir / "rehearsal-traffic.jsonl",
                metadata={
                    "command": "flash",
                    "phase": "non-writing-loader-rehearsal",
                    "port": args.port,
                    "baudrate": LOADER_BAUDRATE,
                    "image_sha256": image.sha256,
                    "program_blocks_allowed": False,
                    "identify_retry_delay": policy.identify_retry_delay,
                    "probe_timeout": policy.probe_timeout,
                    "tx_break_held_during_power_off": (
                        args.hold_tx_break_during_power_off
                    ),
                    "buffered_identify_capture": True,
                },
                durable=True,
                buffered=True,
            )
            try:
                _safe_console(
                    f"Rehearsal probe armed at {LOADER_BAUDRATE} baud. Restore stove "
                    "AC now; no program block will be sent."
                )
                rehearsal = execute_loader_rehearsal(
                    serial_transport,
                    preparation,
                    interlocks=interlocks,
                    policy=policy,
                    audit=rehearsal_audit,
                    journal=journal,
                )
            finally:
                rehearsal_audit.close()
            save_json_document(
                rehearsal.to_dict(), session_dir / "rehearsal-loader-result.json"
            )
            if not rehearsal.successful:
                session_state.transition(
                    FlashSessionStatus.REHEARSAL_FAILED,
                    message=rehearsal.message,
                    recovery_required=False,
                )
                final = {
                    "schema": "openmaxfire.flash-result.v2",
                    "successful": False,
                    "programming_performed": False,
                    "recovery_required": False,
                    "rehearsal": rehearsal.to_dict(),
                    "message": rehearsal.message,
                }
                _save_flash_result(session_dir, final)
                final_written = True
                _safe_console(
                    "Rehearsal failed; flashing is blocked and no E3 frame was sent.",
                    error=True,
                )
                return 5

            rehearsal_client = _open_recorded_client(
                args,
                transport=serial_transport,
                baudrate=args.baud,
                traffic_path=session_dir / "rehearsal-app-traffic.jsonl",
                phase="rehearsal-application-return",
            )
            try:
                time.sleep(args.handoff_delay)
                readiness = wait_for_application_ready(
                    rehearsal_client,
                    timeout=args.application_ready_timeout,
                )
                save_json_document(
                    readiness.to_dict(),
                    session_dir / "rehearsal-application-readiness.json",
                )
                journal.record(
                    "rehearsal_application_ready",
                    **readiness.to_dict(),
                )
                unchanged, _, rehearsal_backup = verify_application_unchanged(
                    rehearsal_client,
                    preparation,
                    port=args.port,
                    baudrate=args.baud,
                    request_delay=args.request_delay,
                )
            finally:
                rehearsal_client.close()
            save_json_document(
                unchanged.to_dict(), session_dir / "rehearsal-verification.json"
            )
            save_json_document(
                rehearsal_backup, session_dir / "rehearsal-eeprom.json"
            )
            session_state.transition(
                FlashSessionStatus.REHEARSAL_COMPLETE,
                message=(
                    "EA/EB and ED/E4 completed with zero E3 frames; original identity "
                    "and EEPROM were unchanged"
                ),
                recovery_required=False,
            )
            _safe_console(
                "Rehearsal passed: loader entry/handoff worked, zero program blocks "
                "were sent, and the original application plus EEPROM were unchanged."
            )
            if args.rehearsal_only:
                final = {
                    "schema": "openmaxfire.flash-result.v2",
                    "successful": True,
                    "programming_performed": False,
                    "recovery_required": False,
                    "rehearsal": rehearsal.to_dict(),
                    "application_unchanged": unchanged.to_dict(),
                    "message": "non-writing loader rehearsal verified; firmware was not changed",
                }
                _save_flash_result(session_dir, final)
                final_written = True
                _safe_console(f"Complete rehearsal session: {session_dir}")
                return 0

        with SleepInhibitor() as sleep_inhibitor:
            journal.record(
                "sleep_inhibitor_acquired",
                backend=sleep_inhibitor.backend,
            )
            if args.hold_tx_break_during_power_off:
                if serial_transport is None:
                    serial_transport = SerialTransport(
                        SerialSettings(
                            args.port,
                            LOADER_BAUDRATE,
                            args.timeout,
                            exclusive=True,
                        )
                    )
                change_tx_break(
                    True,
                    phase="flash_power_off",
                    purpose="hold FTDI TX low while controller power is removed",
                )
                _safe_console(
                    "FLASH POWER CYCLE: FTDI TX BREAK is active (orange TX held low). "
                    "Disconnect stove AC now. The exact recovery image is already "
                    "preserved in this session; do not restore AC until instructed."
                )
            else:
                _safe_console(
                    "FLASH POWER CYCLE: disconnect stove AC now. The exact recovery "
                    "image is already preserved in this session."
                )
            if not _power_off_phrase(
                "After AC is physically disconnected, type POWER OFF FOR FLASH: ",
                "POWER OFF FOR FLASH",
            ):
                journal.record(
                    "operator_abort", reason="flash power-off phrase did not match"
                )
                session_state.transition(
                    FlashSessionStatus.ABORTED_SAFE,
                    message="operator aborted before any E3 program frame",
                    recovery_required=preparation.recovery_mode,
                )
                final = {
                    "schema": "openmaxfire.flash-result.v2",
                    "successful": False,
                    "programming_performed": False,
                    "recovery_required": preparation.recovery_mode,
                    "message": "aborted before this session sent any E3 frame",
                }
                _save_flash_result(session_dir, final)
                final_written = True
                return 6 if preparation.recovery_mode else 3

            # The operator may spend an arbitrary time at the power-off prompt.
            # Re-check the acquired assertion immediately before any possible E3.
            sleep_inhibitor.ensure_active()

            if serial_transport is None:
                serial_transport = SerialTransport(
                    SerialSettings(
                        args.port,
                        LOADER_BAUDRATE,
                        args.timeout,
                        exclusive=True,
                    )
                )
            else:
                serial_transport.set_baudrate(LOADER_BAUDRATE)
                serial_transport.set_timeout(args.timeout)
            if tx_break_active:
                change_tx_break(
                    False,
                    phase="flash_loader_probe",
                    purpose="release FTDI TX immediately before loader probes",
                )

            audit = AuditTrail(
                session_dir / "loader-traffic.jsonl",
                metadata={
                    "command": "flash",
                    "phase": "loader",
                    "port": args.port,
                    "baudrate": LOADER_BAUDRATE,
                    "image_sha256": image.sha256,
                    "sleep_inhibitor": sleep_inhibitor.backend,
                    "identify_retry_delay": policy.identify_retry_delay,
                    "probe_timeout": policy.probe_timeout,
                    "single_exclusive_handle": (
                        not args.hold_tx_break_during_power_off
                    ),
                    "usb_power_removal_before_verification": (
                        args.hold_tx_break_during_power_off
                    ),
                    "tx_break_held_during_power_off": (
                        args.hold_tx_break_during_power_off
                    ),
                    "buffered_identify_capture": True,
                },
                durable=True,
                buffered=True,
            )
            session_state.transition(
                FlashSessionStatus.PROGRAMMING,
                message=(
                    "programming is armed; exact-image replay from block zero is required "
                    "until post-flash verification completes"
                ),
                recovery_required=True,
                blocks_total=len(preparation.loader_plan.blocks),
                blocks_completed=0,
            )
            programming_armed = True
            _safe_console(
                f"Loader probe armed at {LOADER_BAUDRATE} baud. Restore stove AC now; "
                "do not disturb AC, USB, J3, or the computer. Cancellation is deferred."
            )

            def progress(current, total, receipt):
                if current == 1 or current == total or current % 25 == 0:
                    try:
                        sleep_inhibitor.ensure_active()
                    except OpenMaxFireError as exc:
                        # Once a block may be written, finishing the exact image
                        # is safer than intentionally aborting. Record the lost
                        # assertion and continue under the stable-power gate.
                        _remember_host_diagnostic(
                            host_diagnostic_errors,
                            "host sleep inhibitor lost during programming",
                            exc,
                        )
                if (
                    current == 1
                    or current == total
                    or current % 25 == 0
                    or not receipt.acknowledged
                ):
                    _safe_console(
                        f"Program blocks: {current}/{total} "
                        f"address=0x{receipt.word_address:04X} attempts={receipt.attempts}"
                    )

            def attempt_notice(event: LiveAttemptEvent) -> None:
                if event.receipt.outcome is LoaderAttemptOutcome.ACKNOWLEDGED:
                    return
                action = "RETRY" if event.will_retry else "ABORT"
                _safe_console(
                    f"Loader {event.receipt.outcome.value}: block "
                    f"{event.block_number}/{event.blocks_total} "
                    f"address=0x{event.word_address:04X} attempt={event.receipt.attempt} "
                    f"action={action} — {event.decision}",
                    error=True,
                )

            def cancellation_notice(signum: int) -> None:
                name = signal.Signals(signum).name
                _safe_console(
                    f"{name} was received and deferred until the critical loader "
                    "exchange reached a recoverable boundary.",
                    error=True,
                )
                try:
                    journal.record("cancellation_deferred", signal=name)
                except Exception:
                    pass

            deferred = DeferredTerminationSignals(cancellation_notice)
            try:
                with deferred:
                    loader_result = execute_live_loader_plan(
                        serial_transport,
                        preparation,
                        interlocks=interlocks,
                        policy=policy,
                        audit=audit,
                        journal=journal,
                        progress=progress,
                        attempt_callback=attempt_notice,
                    )
            finally:
                try:
                    audit.close()
                except OSError as exc:
                    _safe_console(f"Could not close loader audit cleanly: {exc}", error=True)

            try:
                save_json_document(
                    loader_result.to_dict(), session_dir / "loader-result.json"
                )
            except (OSError, RuntimeError, ValueError) as exc:
                _remember_host_diagnostic(
                    host_diagnostic_errors,
                    "loader result could not be persisted; verification will continue",
                    exc,
                )
            if not loader_result.pic_side_blocks_verified:
                journal.record("flash_failed", message=loader_result.message)
                recovery_required = loader_result.recovery_required
                session_state.transition(
                    (
                        FlashSessionStatus.RECOVERY_REQUIRED
                        if recovery_required
                        else FlashSessionStatus.FAILED_SAFE
                    ),
                    message=loader_result.message,
                    recovery_required=recovery_required,
                    blocks_total=loader_result.blocks_total,
                    blocks_completed=loader_result.blocks_completed,
                    failure_outcome=(
                        loader_result.failure_outcome.value
                        if loader_result.failure_outcome is not None
                        else None
                    ),
                )
                final = {
                    "schema": "openmaxfire.flash-result.v2",
                    "successful": False,
                    "ready_for_operation": False,
                    "programming_performed": bool(loader_result.block_receipts),
                    "recovery_required": recovery_required,
                    "loader": loader_result.to_dict(),
                    "cancellation_deferred": deferred.requested,
                    "deferred_signals": list(deferred.signal_names),
                    "message": loader_result.message,
                }
                _save_flash_result(session_dir, final)
                final_written = True
                programming_armed = recovery_required
                _safe_console(
                    (
                        f"RECOVERY REQUIRED: {loader_result.message}"
                        if recovery_required
                        else f"Flashing did not begin: {loader_result.message}"
                    ),
                    error=True,
                )
                _safe_console(f"Session preserved at {session_dir}", error=True)
                return 6 if recovery_required else 5

            try:
                session_state.transition(
                    FlashSessionStatus.VERIFYING,
                    message=(
                        "all program blocks have PIC-side E4; target identity and EEPROM "
                        "verification are still required"
                    ),
                    recovery_required=True,
                    blocks_total=loader_result.blocks_total,
                    blocks_completed=loader_result.blocks_completed,
                )
            except (OSError, RuntimeError, ValueError) as exc:
                _remember_host_diagnostic(
                    host_diagnostic_errors,
                    "verification state update failed; recovery marker remains authoritative",
                    exc,
                )
            post = None
            post_eeprom = None
            post_backup = None
            post_error: BaseException | None = None
            if (
                not args.hold_tx_break_during_power_off
                or not loader_result.completion_acknowledged
            ):
                time.sleep(args.handoff_delay)
                try:
                    post, post_eeprom, post_backup = _attempt_post_flash(
                        args,
                        preparation,
                        transport=serial_transport,
                        session_dir=session_dir,
                        attempt=1,
                        diagnostic_errors=host_diagnostic_errors,
                    )
                except VerificationError as exc:
                    post_error = exc
                except (OSError, ProtocolError, TimeoutError, ValueError) as exc:
                    post_error = exc

            completion_recovered = False
            if post is None and not loader_result.completion_acknowledged:
                serial_transport.set_baudrate(LOADER_BAUDRATE)
                serial_transport.set_timeout(args.timeout)
                recovery_audit = None
                try:
                    recovery_audit = AuditTrail(
                        session_dir / "completion-recovery-traffic.jsonl",
                        metadata={
                            "command": "flash",
                            "phase": "completion-recovery",
                            "port": args.port,
                            "baudrate": LOADER_BAUDRATE,
                            "image_sha256": image.sha256,
                        },
                        durable=True,
                    )
                except (OSError, RuntimeError, ValueError) as exc:
                    _remember_host_diagnostic(
                        host_diagnostic_errors,
                        "completion-recovery traffic recorder unavailable",
                        exc,
                    )
                try:
                    completion_recovered = recover_live_loader_completion(
                        serial_transport,
                        loader_result,
                        audit=recovery_audit,
                        journal=journal,
                    )
                finally:
                    if recovery_audit is not None:
                        try:
                            recovery_audit.close()
                        except OSError as exc:
                            _remember_host_diagnostic(
                                host_diagnostic_errors,
                                "completion-recovery traffic recorder close failed",
                                exc,
                            )
                if completion_recovered:
                    try:
                        post, post_eeprom, post_backup = _attempt_post_flash(
                            args,
                            preparation,
                            transport=serial_transport,
                            session_dir=session_dir,
                            attempt=2,
                            diagnostic_errors=host_diagnostic_errors,
                        )
                        post_error = None
                    except (OSError, ProtocolError, TimeoutError, ValueError) as exc:
                        post_error = exc

            if args.hold_tx_break_during_power_off:
                change_tx_break(
                    True,
                    phase="post_flash_cold_boot_power_off",
                    purpose="force a cold target-application boot after programming",
                )
                _safe_console(
                    "POST-FLASH COLD BOOT: all authenticated program blocks have PIC-side "
                    "readback evidence. FTDI TX BREAK is active (orange TX held low). "
                    "Disconnect stove AC, then physically unplug FTDI USB from the "
                    "computer. Do not restore AC until instructed."
                )
                if not _power_off_phrase(
                    "After AC is off and FTDI USB is unplugged, type AC OFF USB OUT "
                    "AFTER FLASH: ",
                    "AC OFF USB OUT AFTER FLASH",
                ):
                    message = (
                        "target cold boot was aborted after programming; verification "
                        "and exact-image recovery remain required"
                    )
                    journal.record("operator_abort", reason=message)
                    session_state.transition(
                        FlashSessionStatus.RECOVERY_REQUIRED,
                        message=message,
                        recovery_required=True,
                        blocks_total=loader_result.blocks_total,
                        blocks_completed=loader_result.blocks_completed,
                    )
                    final = {
                        "schema": "openmaxfire.flash-result.v2",
                        "successful": False,
                        "ready_for_operation": False,
                        "programming_performed": True,
                        "recovery_required": True,
                        "loader": loader_result.to_dict(),
                        "cancellation_deferred": deferred.requested,
                        "deferred_signals": list(deferred.signal_names),
                        "message": message,
                    }
                    _save_flash_result(session_dir, final)
                    final_written = True
                    _safe_console(f"RECOVERY REQUIRED: {message}", error=True)
                    return 6
                close_after_confirmed_usb_removal(
                    phase="post_flash_usb_power_removed",
                )
                _safe_console(
                    "FTDI USB power removal confirmed and the stale serial handle is "
                    "closed. Restore stove AC with USB still unplugged; wait for normal "
                    "target-controller startup. Keep the igniters unplugged and "
                    "hazardous actuator loads disconnected."
                )
                if not _power_off_phrase(
                    "After the target application normally starts, type TARGET "
                    "APPLICATION BOOTED: ",
                    "TARGET APPLICATION BOOTED",
                ):
                    message = (
                        "target cold boot was not confirmed after programming; "
                        "verification and exact-image recovery remain required"
                    )
                    journal.record("operator_abort", reason=message)
                    session_state.transition(
                        FlashSessionStatus.RECOVERY_REQUIRED,
                        message=message,
                        recovery_required=True,
                        blocks_total=loader_result.blocks_total,
                        blocks_completed=loader_result.blocks_completed,
                    )
                    final = {
                        "schema": "openmaxfire.flash-result.v2",
                        "successful": False,
                        "ready_for_operation": False,
                        "programming_performed": True,
                        "recovery_required": True,
                        "loader": loader_result.to_dict(),
                        "cancellation_deferred": deferred.requested,
                        "deferred_signals": list(deferred.signal_names),
                        "message": message,
                    }
                    _save_flash_result(session_dir, final)
                    final_written = True
                    _safe_console(f"RECOVERY REQUIRED: {message}", error=True)
                    return 6
                journal.record(
                    "application_boot_confirmed",
                    phase="post_flash_cold_boot",
                    expected_profile=preparation.approved.target_profile_key,
                )
                _safe_console(
                    "Leave stove AC on and reconnect FTDI USB to the computer now."
                )
                if not _power_off_phrase(
                    "After FTDI re-enumerates, type USB CONNECTED AFTER FLASH: ",
                    "USB CONNECTED AFTER FLASH",
                ):
                    message = (
                        "FTDI reconnect was not confirmed after programming; target "
                        "verification and exact-image recovery remain required"
                    )
                    journal.record("operator_abort", reason=message)
                    session_state.transition(
                        FlashSessionStatus.RECOVERY_REQUIRED,
                        message=message,
                        recovery_required=True,
                        blocks_total=loader_result.blocks_total,
                        blocks_completed=loader_result.blocks_completed,
                    )
                    final = {
                        "schema": "openmaxfire.flash-result.v2",
                        "successful": False,
                        "ready_for_operation": False,
                        "programming_performed": True,
                        "recovery_required": True,
                        "loader": loader_result.to_dict(),
                        "cancellation_deferred": deferred.requested,
                        "deferred_signals": list(deferred.signal_names),
                        "message": message,
                    }
                    _save_flash_result(session_dir, final)
                    final_written = True
                    _safe_console(f"RECOVERY REQUIRED: {message}", error=True)
                    return 6
                reopen_serial_after_usb_reconnect(
                    baudrate=preparation.approved.application_baudrate,
                    phase="post_flash_usb_reconnected",
                )
                time.sleep(args.handoff_delay)
                post = None
                post_eeprom = None
                post_backup = None
                try:
                    post, post_eeprom, post_backup = _attempt_post_flash(
                        args,
                        preparation,
                        transport=serial_transport,
                        session_dir=session_dir,
                        attempt=3,
                        diagnostic_errors=host_diagnostic_errors,
                    )
                    post_error = None
                except (OSError, ProtocolError, TimeoutError, ValueError) as exc:
                    post_error = exc

            if post is None:
                message = (
                    "target application could not be verified after all blocks were accepted"
                    + (f": {post_error}" if post_error is not None else "")
                )
                journal.record("postflash_failed", message=message)
                session_state.transition(
                    FlashSessionStatus.RECOVERY_REQUIRED,
                    message=message,
                    recovery_required=True,
                    blocks_total=loader_result.blocks_total,
                    blocks_completed=loader_result.blocks_completed,
                )
                final = {
                    "schema": "openmaxfire.flash-result.v2",
                    "successful": False,
                    "ready_for_operation": False,
                    "programming_performed": True,
                    "recovery_required": True,
                    "loader": loader_result.to_dict(),
                    "host_diagnostic_errors": list(host_diagnostic_errors),
                    "diagnostics_complete": not (
                        loader_result.diagnostic_errors or host_diagnostic_errors
                    ),
                    "completion_recovered": completion_recovered,
                    "cancellation_deferred": deferred.requested,
                    "deferred_signals": list(deferred.signal_names),
                    "message": message,
                }
                _save_flash_result(session_dir, final)
                final_written = True
                _safe_console(f"RECOVERY REQUIRED: {message}", error=True)
                _safe_console(f"Session preserved at {session_dir}", error=True)
                return 6

            assert post_eeprom is not None and post_backup is not None
            save_json_document(post_backup, session_dir / "eeprom-after.json")
            hardware_inspection_required = loader_result.write_failure_events > 0
            ready_for_operation = (
                post.ready_for_operation and not hardware_inspection_required
            )
            if preparation.data_format_migration_required:
                message = (
                    "firmware and unchanged EEPROM verified; calibration/Format is required "
                    "before reconnecting igniters or operating the stove"
                )
            elif post.calibration_required:
                message = (
                    "firmware and unchanged EEPROM verified; vendor Monitor calibration "
                    "is required before reconnecting igniters or operating the stove"
                )
            else:
                message = "firmware identity and unchanged EEPROM verified"
            if hardware_inspection_required:
                message += (
                    "; a recovered E5 requires socket/VDD/controller inspection before operation"
                )
            final = {
                "schema": "openmaxfire.flash-result.v2",
                "successful": post.programming_verified,
                "ready_for_operation": ready_for_operation,
                "programming_performed": True,
                "recovery_required": False,
                "hardware_inspection_required": hardware_inspection_required,
                "loader": loader_result.to_dict(),
                "host_diagnostic_errors": list(host_diagnostic_errors),
                "diagnostics_complete": not (
                    loader_result.diagnostic_errors or host_diagnostic_errors
                ),
                "completion_evidence": (
                    "loader_e4"
                    if loader_result.completion_acknowledged
                    else "target_application_identity"
                ),
                "completion_recovered": completion_recovered,
                "post_flash": post.to_dict(),
                "cancellation_deferred": deferred.requested,
                "deferred_signals": list(deferred.signal_names),
                "message": message,
            }
            _save_flash_result(session_dir, final)
            session_state.transition(
                (
                    FlashSessionStatus.CALIBRATION_REQUIRED
                    if post.calibration_required or hardware_inspection_required
                    else FlashSessionStatus.COMPLETE
                ),
                message=message,
                recovery_required=False,
                programming_verified=post.programming_verified,
                ready_for_operation=ready_for_operation,
                hardware_inspection_required=hardware_inspection_required,
            )
            final_written = True
            programming_armed = False
            journal.record(
                "flash_complete",
                programming_verified=post.programming_verified,
                ready_for_operation=ready_for_operation,
                calibration_required=post.calibration_required,
                hardware_inspection_required=hardware_inspection_required,
                cancellation_deferred=deferred.requested,
            )
            _safe_console("Firmware identity and unchanged EEPROM verified.")
            if post.calibration_required or hardware_inspection_required:
                if preparation.data_format_migration_required:
                    _safe_console(
                        "DO NOT reconnect the igniters or operate the stove yet. In "
                        "BixCheck Monitor, select the model, Individualize, Calculate "
                        "Fuel A/B, then Format as required by the vendor procedure."
                    )
                elif post.calibration_required:
                    _safe_console(
                        "DO NOT reconnect the igniters or operate the stove yet. Complete "
                        "the target version's vendor Monitor calibration procedure first."
                    )
                if hardware_inspection_required:
                    _safe_console(
                        "A transient E5 recovered, but operation remains blocked pending "
                        "qualified socket/contact and controller-VDD inspection."
                    )
            if deferred.requested:
                _safe_console(
                    "A cancellation request was deferred; the verified update was allowed "
                    "to reach its safe boundary."
                )
            _safe_console(f"Complete session: {session_dir}")
            return 0
    except FileExistsError as exc:
        print(f"Refusing to replace existing path: {exc.filename}", file=sys.stderr)
        return 6 if preexisting_recovery else 4
    except KeyboardInterrupt:
        message = "operator interrupted before the protected critical section"
        recovery_required = programming_armed or preexisting_recovery
        if session_state is not None:
            try:
                session_state.transition(
                    (
                        FlashSessionStatus.RECOVERY_REQUIRED
                        if recovery_required
                        else FlashSessionStatus.ABORTED_SAFE
                    ),
                    message=message,
                    recovery_required=recovery_required,
                )
            except Exception:
                pass
        if session_dir is not None and session_dir.exists() and not final_written:
            try:
                _save_flash_result(
                    session_dir,
                    {
                        "schema": "openmaxfire.flash-result.v2",
                        "successful": False,
                        "ready_for_operation": False,
                        "recovery_required": recovery_required,
                        "message": message,
                    },
                )
            except Exception:
                pass
        _safe_console(message, error=True)
        return 6 if recovery_required else 130
    except (OSError, OpenMaxFireError, ProtocolError, TimeoutError, ValueError) as exc:
        message = f"OpenMaxFire flash error: {exc}"
        recovery_required = programming_armed or preexisting_recovery
        if session_state is not None:
            try:
                session_state.transition(
                    (
                        FlashSessionStatus.RECOVERY_REQUIRED
                        if recovery_required
                        else FlashSessionStatus.FAILED_SAFE
                    ),
                    message=message,
                    recovery_required=recovery_required,
                )
            except Exception:
                pass
        if session_dir is not None and session_dir.exists() and not final_written:
            try:
                _save_flash_result(
                    session_dir,
                    {
                        "schema": "openmaxfire.flash-result.v2",
                        "successful": False,
                        "ready_for_operation": False,
                        "recovery_required": recovery_required,
                        "message": message,
                    },
                )
            except Exception:
                pass
        _safe_console(message, error=True)
        return 6 if recovery_required else 4
    finally:
        if tx_break_active and serial_transport is not None:
            try:
                serial_transport.set_break(False)
                tx_break_active = False
                if journal is not None:
                    journal.record(
                        "tx_break_changed",
                        active=False,
                        phase="final_cleanup",
                        purpose="fail-safe BREAK release before closing serial handle",
                    )
            except (OSError, AttributeError, TypeError, ValueError) as exc:
                _safe_console(
                    f"Warning: explicit UART BREAK release failed; closing the serial "
                    f"handle: {exc}",
                    error=True,
                )
        if journal is not None:
            try:
                journal.close()
            except OSError:
                pass
        if serial_transport is not None:
            try:
                serial_transport.close()
            except OSError:
                pass


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="maxfirectl",
        description="Cross-platform OpenMaxFire service/protocol utility",
    )
    p.add_argument("--port", help="serial port, e.g. COM3, /dev/ttyUSB0, or /dev/cu.usbserial-*")
    p.add_argument(
        "--baud",
        type=int,
        choices=(9600, 19200),
        help=(
            "required for live I/O: 9600 for live 2.02 and preserved 2.06; "
            "19200 intended for 2.70/2.71"
        ),
    )
    p.add_argument(
        "--timeout",
        type=_positive_float,
        default=0.35,
        help="serial read/write timeout in seconds",
    )
    p.add_argument(
        "--request-delay",
        type=_nonnegative_float,
        default=0.10,
        help="delay between multi-register read requests in seconds (default: 0.10)",
    )
    p.add_argument(
        "--traffic-log",
        type=Path,
        help="record exact TX/RX chunks and timing as JSON Lines",
    )
    p.add_argument(
        "--overwrite-traffic-log",
        action="store_true",
        help="replace an existing --traffic-log instead of refusing",
    )

    sub = p.add_subparsers(dest="command", required=True)

    ports = sub.add_parser("ports", help="list serial ports without opening them")
    ports.add_argument("--json", action="store_true", help="emit machine-readable JSON")

    enc = sub.add_parser("encode", help="show a reconstructed J3 command without transmitting it")
    enc_sub = enc.add_subparsers(dest="encode_command", required=True)
    er = enc_sub.add_parser("read")
    er.add_argument("address", type=_byte_auto)
    er.add_argument("--unit", choices=("A", "C", "D"), default="C")
    ew = enc_sub.add_parser("write")
    ew.add_argument("address", type=_byte_auto)
    ew.add_argument("value", type=_byte_auto)
    ew.add_argument("--unit", choices=("A", "C", "D"), default="C")
    eb = enc_sub.add_parser("button")
    eb.add_argument("button", choices=[button.name.lower() for button in RemoteButton])

    capture = sub.add_parser(
        "capture",
        help="receive only for a bounded time and write a timestamped JSONL transcript",
    )
    capture.add_argument("--duration", type=_positive_float, default=10.0)
    capture.add_argument("--output", required=True, type=Path)
    capture.add_argument("--overwrite", action="store_true")
    _add_live_ack(capture)

    read = sub.add_parser("read", help="read and display one controller or EEPROM byte")
    read.add_argument("address", type=_byte_auto)
    read.add_argument("--unit", choices=("A", "C", "D"), default="C")
    _add_live_ack(read)

    write = sub.add_parser(
        "write",
        help="write one A/C/D byte, optionally followed by a fresh readback",
    )
    write.add_argument("address", type=_byte_auto)
    write.add_argument("value", type=_byte_auto)
    write.add_argument("--unit", choices=("A", "C", "D"), default="C")
    write.add_argument(
        "--verify",
        action="store_true",
        help="read the same address after writing and require an equal byte",
    )
    write.add_argument(
        "--settle-delay",
        type=_nonnegative_float,
        default=0.10,
        help="delay before --verify readback in seconds (default: 0.10)",
    )
    _add_live_ack(write, writes=True)
    _add_state_change_ack(write)

    raw = sub.add_parser(
        "raw",
        help=(
            "transmit one exact A/C/D register request and capture an "
            "uninterpreted response window"
        ),
    )
    raw_payload = raw.add_mutually_exclusive_group(required=True)
    raw_payload.add_argument(
        "--ascii", help="one complete A/C/D request; no terminator is added"
    )
    raw_payload.add_argument(
        "--hex", dest="raw_hex", type=_raw_hex, help="one complete A/C/D request as hex"
    )
    raw.add_argument(
        "--read-for",
        type=_nonnegative_float,
        default=1.0,
        help="raw receive window after transmission; zero sends only (default: 1.0)",
    )
    raw.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    _add_live_ack(raw, writes=True)
    _add_state_change_ack(raw)

    transaction = sub.add_parser(
        "transaction",
        help="validate or execute a fail-fast JSON A/C/D register transaction",
    )
    transaction.add_argument("input", type=Path)
    transaction.add_argument(
        "--dry-run",
        action="store_true",
        help="validate and print the canonical plan without opening a serial port",
    )
    transaction.add_argument("--json", action="store_true", help="emit compact JSON")
    _add_live_ack(transaction, writes=True)
    _add_state_change_ack(transaction)

    identify = sub.add_parser(
        "identify",
        help="read CR00, CR08, and CR0B-CR0E without issuing writes",
    )
    identify.add_argument("--json", action="store_true")
    _add_live_ack(identify)

    backup = sub.add_parser(
        "backup",
        help="identify the stove and save a complete read-only AR00-ARFF JSON backup",
    )
    backup.add_argument("--output", required=True, type=Path)
    backup.add_argument("--overwrite", action="store_true")
    _add_live_ack(backup)

    monitor = sub.add_parser(
        "monitor",
        help="continuously poll CR00-CR0E, retain interleaved telemetry, and emit snapshots",
    )
    monitor.add_argument(
        "--duration",
        type=_nonnegative_float,
        default=0.0,
        help="stop after this many seconds; zero means run until interrupted",
    )
    monitor.add_argument(
        "--cycles",
        type=_positive_int,
        help="stop after this many complete CR00-CR0E polling cycles",
    )
    monitor.add_argument("--stale-after", type=_positive_float, default=10.0)
    monitor.add_argument("--output", type=Path, help="write decoded snapshots as JSON Lines")
    monitor.add_argument("--overwrite", action="store_true")
    monitor.add_argument("--json", action="store_true", help="emit snapshots as JSON Lines")
    _add_live_ack(monitor)

    replay = sub.add_parser(
        "replay",
        help="reconstruct a final monitor state from a serial-capture JSONL file offline",
    )
    replay.add_argument("input", type=Path)
    replay.add_argument("--stale-after", type=_positive_float, default=10.0)
    replay.add_argument("--output", type=Path, help="save the final decoded snapshot as JSON")
    replay.add_argument("--overwrite", action="store_true")
    replay.add_argument("--json", action="store_true", help="emit the final snapshot as JSON")

    button = sub.add_parser("button", help="transmit a reconstructed remote front-panel command")
    button.add_argument("button", choices=[item.name.lower() for item in RemoteButton])
    _add_live_ack(button, writes=True)
    _add_state_change_ack(button)

    flash = sub.add_parser(
        "flash",
        help="authenticate a J3 firmware plan offline",
        description=(
            "Authenticate a J3 firmware plan offline. All physical loader "
            "traffic, including non-writing rehearsal, E3 programming, and "
            "recovery, is disabled until a fixture-specific path is implemented "
            "and qualified on safely powered spare hardware."
        ),
    )
    flash.add_argument(
        "image",
        nargs="?",
        type=Path,
        help=(
            "exact preserved factory Downloader HEX image for --plan-only"
        ),
    )
    flash.add_argument(
        "--plan-only",
        action="store_true",
        help="authenticate and print the complete plan without opening a serial port",
    )
    flash.add_argument(
        "--current-profile",
        choices=tuple(PROFILES_BY_KEY),
        help="current controller profile, required only for --plan-only",
    )
    flash.add_argument(
        "--session-dir",
        type=Path,
        help="new directory for backups, journal, byte traffic, and results",
    )
    flash.add_argument(
        "--recover-from-session",
        type=Path,
        help=(
            "dormant recovery-bundle input; CLI replay is rejected while all "
            "physical loader traffic is disabled"
        ),
    )
    flash.add_argument(
        "--rehearsal-only",
        action="store_true",
        help=(
            "retired; physical EA/EB and ED/E4 traffic is rejected before image "
            "or serial access"
        ),
    )
    flash.add_argument(
        "--hold-tx-break-during-power-off",
        action="store_true",
        help=(
            "retired with the manual-AC physical loader workflow; accepted only "
            "as syntax and always rejected outside --plan-only validation"
        ),
    )
    flash.add_argument("--json", action="store_true", help="compact JSON for --plan-only")
    flash.add_argument(
        "--loader-identify-attempts",
        type=_positive_int,
        default=1500,
        help="rapid bounded EA/EB probes after the manual power cycle (default: 1500)",
    )
    flash.add_argument(
        "--loader-identify-retry-delay",
        type=_nonnegative_float,
        default=0.0,
        help=(
            "additional delay between missed EA/EB identify probes in seconds "
            "(0 to 0.050; default: 0)"
        ),
    )
    flash.add_argument(
        "--retry-delay",
        type=_nonnegative_float,
        default=0.020,
        help=(
            "dormant direct-executor program-block retry delay; the CLI "
            "cannot send E3 (default: 0.020)"
        ),
    )
    flash.add_argument(
        "--loader-probe-timeout",
        type=_positive_float,
        default=0.020,
        help=(
            "timeout for each EA/EB loader identify probe in seconds "
            "(0.001 to 0.050; default: 0.020)"
        ),
    )
    flash.add_argument(
        "--loader-settle-delay",
        type=_nonnegative_float,
        default=0.0,
        help=(
            "dormant direct-executor delay after EB and before E3; the CLI "
            "cannot send E3 (default: 0.0)"
        ),
    )
    flash.add_argument(
        "--loader-response-timeout",
        type=_positive_float,
        default=0.50,
        help=(
            "timeout for loader responses (E4 in a rehearsal; E7/E4 only in "
            "the dormant direct executor; default: 0.50)"
        ),
    )
    flash.add_argument(
        "--handoff-delay",
        type=_nonnegative_float,
        default=0.75,
        help=(
            "minimum transmit-silent settle time before passively waiting for "
            "application telemetry (default: 0.75)"
        ),
    )
    flash.add_argument(
        "--application-ready-timeout",
        type=_positive_float,
        default=30.0,
        help=(
            "maximum passive wait for unsolicited T/DW telemetry before any "
            "application request is allowed (default: 30)"
        ),
    )
    flash.add_argument("--confirm-stove-cold-and-off", action="store_true")
    flash.add_argument("--confirm-igniters-unplugged", action="store_true")
    flash.add_argument(
        "--confirm-actuator-loads-unplugged",
        action="store_true",
        help=(
            "confirm hazardous actuator loads are physically disconnected for the "
            "powered rehearsal"
        ),
    )
    flash.add_argument("--confirm-correct-5v-ttl-wiring", action="store_true")
    flash.add_argument("--confirm-j3-pin3-disconnected", action="store_true")
    flash.add_argument("--confirm-adapter-vcc-disconnected", action="store_true")
    flash.add_argument("--confirm-pickit-recovery-tested-on-spare", action="store_true")
    flash.add_argument("--confirm-computer-power-stable", action="store_true")
    flash.add_argument("--confirm-stove-power-stable", action="store_true")
    flash.add_argument(
        "--confirm-calibration-plan",
        action="store_true",
        help="required whenever the target firmware version differs",
    )
    flash.add_argument(
        "--confirm-recovery-target-matches-backup",
        action="store_true",
        help=(
            "dormant recovery interlock; --recover-from-session is rejected "
            "by the CLI E3 lock"
        ),
    )

    return p


def _validate_live_args(
    args: argparse.Namespace,
    *,
    transaction_plan: TransactionPlan | None = None,
) -> int | None:
    if args.command not in LIVE_COMMANDS:
        return None
    if args.command == "transaction" and args.dry_run:
        return None
    if not args.port or args.baud is None:
        print("--port and --baud are required for live I/O", file=sys.stderr)
        return 2
    if args.request_delay < 0:
        print("--request-delay must be finite and nonnegative", file=sys.stderr)
        return 2
    if not args.i_understand_unverified_io:
        print(
            "Refusing live I/O: J3 ground/TX/RX and 9,600-baud reads are live-validated on "
            "serial 5215, but pin 3, idle margins, loaded operation, and writes remain "
            "unresolved. Pass --i-understand-unverified-io only after reading SAFETY.md.",
            file=sys.stderr,
        )
        return 3
    needs_state_ack = args.command in ("write", "raw", "button") or (
        args.command == "transaction"
        and transaction_plan is not None
        and transaction_plan.has_writes
    )
    if needs_state_ack and not args.i_understand_this_can_change_stove_state:
        print(
            "Refusing state-changing traffic: pass "
            "--i-understand-this-can-change-stove-state after reviewing the exact bytes.",
            file=sys.stderr,
        )
        return 3
    if args.command == "capture" and args.traffic_log is not None:
        print(
            "capture uses --output as its traffic log; do not also pass --traffic-log",
            file=sys.stderr,
        )
        return 2
    if (
        args.command == "monitor"
        and args.output is not None
        and args.traffic_log is not None
        and args.output.resolve() == args.traffic_log.resolve()
    ):
        print("monitor --output and --traffic-log must be different files", file=sys.stderr)
        return 2
    return None


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.command == "ports":
        return _run_ports(args)

    if args.command == "encode":
        if args.encode_command == "read":
            payload = encode_read_register(args.address, unit=args.unit)
        elif args.encode_command == "write":
            payload = encode_write_register(args.address, args.value, unit=args.unit)
        else:
            payload = encode_remote_button(RemoteButton[args.button.upper()])
        print(payload.decode("ascii"))
        return 0

    if args.command == "replay":
        try:
            return _run_replay(args)
        except FileExistsError as exc:
            print(f"Refusing to replace existing file: {exc.filename}", file=sys.stderr)
            return 4
        except (OSError, ProtocolError, ValueError) as exc:
            print(f"OpenMaxFire error: {exc}", file=sys.stderr)
            return 4

    if args.command == "flash":
        try:
            return _run_flash(args)
        except KeyboardInterrupt:
            print(
                "Interrupted. Preserve power if programming had begun; inspect the "
                "session journal.",
                file=sys.stderr,
            )
            return 130

    transaction_plan = None
    if args.command == "transaction":
        try:
            transaction_plan = load_transaction_plan(args.input)
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            print(f"OpenMaxFire error: {exc}", file=sys.stderr)
            return 4
        if args.dry_run:
            if args.traffic_log is not None:
                print(
                    "--traffic-log cannot be used with transaction --dry-run",
                    file=sys.stderr,
                )
                return 2
            indent = None if args.json else 2
            print(json.dumps(transaction_plan.to_dict(), indent=indent, sort_keys=True))
            return 0

    raw_payload = None
    if args.command == "raw":
        if args.ascii is not None:
            try:
                raw_payload = args.ascii.encode("ascii")
            except UnicodeEncodeError:
                print(
                    "OpenMaxFire error: --ascii payload must contain only ASCII characters",
                    file=sys.stderr,
                )
                return 4
            if not raw_payload:
                print("OpenMaxFire error: raw ASCII payload cannot be empty", file=sys.stderr)
                return 4
        else:
            raw_payload = args.raw_hex
        try:
            validate_generic_raw_payload(raw_payload)
        except (SafetyInterlockError, ValueError) as exc:
            print(
                f"OpenMaxFire error: {exc}",
                file=sys.stderr,
            )
            return 4

    if args.command == "write":
        write_payload = encode_write_register(args.address, args.value, unit=args.unit)
        if contains_loader_traffic(write_payload):
            print(
                "OpenMaxFire error: the CW0F reset/loader register family is forbidden "
                "through generic register writes, including CW0FC4",
                file=sys.stderr,
            )
            return 4

    error_code = _validate_live_args(args, transaction_plan=transaction_plan)
    if error_code is not None:
        return error_code

    traffic_path = args.output if args.command == "capture" else args.traffic_log
    overwrite_traffic = (
        args.overwrite if args.command == "capture" else args.overwrite_traffic_log
    )
    client: MaxFireClient | None = None
    try:
        client = _connect(
            args,
            traffic_path=traffic_path,
            overwrite_traffic=overwrite_traffic,
        )
        if args.command == "capture":
            captured = client.capture_receive_only(args.duration)
            print(f"Captured {len(captured)} bytes in {args.duration:g} seconds: {args.output}")
        elif args.command == "read":
            response = client.query_register(args.address, unit=args.unit)
            print(
                f"{args.unit}R{args.address:02X}=0x{response.value:02X} "
                f"raw={response.raw.decode('ascii')}"
            )
        elif args.command == "write":
            if args.verify:
                receipt = client.write_register_verified(
                    args.address,
                    args.value,
                    unit=args.unit,
                    settle_delay=args.settle_delay,
                )
                readback = (
                    receipt.response.decode("ascii")
                    if receipt.response is not None
                    else "none"
                )
                print(
                    f"{receipt.request.decode('ascii')} readback={readback} "
                    f"verified={'yes' if receipt.verified else 'no'}"
                )
                if not receipt.verified:
                    return 5
            else:
                receipt = client.write_register(
                    args.address,
                    args.value,
                    unit=args.unit,
                )
                print(
                    f"{receipt.request.decode('ascii')} transmitted; "
                    "controller acceptance not verified"
                )
        elif args.command == "raw":
            assert raw_payload is not None
            receipt = client.exchange_raw(raw_payload, receive_duration=args.read_for)
            response = receipt.response or b""
            document = {
                "tx_ascii": _display_bytes(receipt.request),
                "tx_hex": receipt.request.hex(" ").upper(),
                "rx_ascii": _display_bytes(response),
                "rx_hex": response.hex(" ").upper(),
                "rx_byte_count": len(response),
                "verified": False,
            }
            if args.json:
                print(json.dumps(document, sort_keys=True))
            else:
                print(f"TX {document['tx_hex']}  {document['tx_ascii']}")
                print(f"RX {document['rx_hex'] or '(none)'}  {document['rx_ascii'] or '(none)'}")
                print("No acknowledgement or success semantics inferred.")
        elif args.command == "transaction":
            assert transaction_plan is not None
            document = execute_transaction(
                client,
                transaction_plan,
                allow_writes=transaction_plan.has_writes,
            )
            print(json.dumps(document, indent=None if args.json else 2, sort_keys=True))
            if not document["success"]:
                return 5
        elif args.command == "identify":
            identity = client.identify(request_delay=args.request_delay)
            _print_identity(identity, as_json=args.json)
        elif args.command == "backup":
            identity = client.identify(request_delay=args.request_delay)
            if args.request_delay:
                time.sleep(args.request_delay)
            eeprom = client.read_eeprom(request_delay=args.request_delay)
            document = build_eeprom_backup(
                identity,
                eeprom,
                port=args.port,
                baudrate=args.baud,
            )
            save_json_document(document, args.output, overwrite=args.overwrite)
            print(f"Saved complete read-only A00-AFF backup: {args.output}")
            print(
                "Stored/calculated checksum: "
                f"{document['checksum']['stored']}/{document['checksum']['calculated']} "
                f"match={document['checksum']['matches']}"
            )
        elif args.command == "monitor":
            return _run_monitor(client, args)
        elif args.command == "button":
            receipt = client.remote_button(RemoteButton[args.button.upper()])
            print(receipt.request.decode("ascii"))
        else:
            raise AssertionError(args.command)
        return 0
    except FileExistsError as exc:
        print(f"Refusing to replace existing file: {exc.filename}", file=sys.stderr)
        return 4
    except (OSError, ProtocolError, TimeoutError, ValueError) as exc:
        print(f"OpenMaxFire error: {exc}", file=sys.stderr)
        return 4
    except KeyboardInterrupt:
        print("Interrupted.", file=sys.stderr)
        return 130
    finally:
        if client is not None:
            client.close()


if __name__ == "__main__":
    raise SystemExit(main())
