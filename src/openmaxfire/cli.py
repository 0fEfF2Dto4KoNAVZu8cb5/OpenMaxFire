"""Cross-platform ``maxfirectl`` command-line utility."""

from __future__ import annotations

import argparse
import json
import math
import sys
import time
from pathlib import Path

from .backup import build_eeprom_backup, save_json_document
from .client import MaxFireClient, StoveIdentity
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


LIVE_COMMANDS = frozenset(
    ("capture", "read", "write", "raw", "transaction", "identify", "backup", "monitor", "button")
)
MONITOR_REGISTERS = tuple(range(0x0F))


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
    return value == b"CW0FC4" or value.startswith((b"EA", b"E3", b"ED"))


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
        help="transmit exact bytes and capture an uninterpreted response window",
    )
    raw_payload = raw.add_mutually_exclusive_group(required=True)
    raw_payload.add_argument("--ascii", help="exact ASCII bytes; no terminator is added")
    raw_payload.add_argument("--hex", dest="raw_hex", type=_raw_hex, help="exact hex bytes")
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
        print("capture uses --output as its traffic log; do not also pass --traffic-log", file=sys.stderr)
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
        if _is_loader_traffic(raw_payload):
            print(
                "OpenMaxFire error: known firmware-loader traffic is isolated from raw "
                "mode until loader acknowledgement and recovery behavior are implemented",
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
