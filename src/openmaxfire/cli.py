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


LIVE_COMMANDS = frozenset(("capture", "read", "identify", "backup", "button"))


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


def _add_live_ack(parser: argparse.ArgumentParser, *, writes: bool = False) -> None:
    noun = "commands" if writes else "serial I/O"
    parser.add_argument(
        "--i-understand-unverified-io",
        action="store_true",
        help=f"required until J3 electrical behavior and {noun} are live-validated",
    )


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
        help="required for live I/O: 9600 for 2.06; 19200 intended for 2.70/2.71",
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
    read.add_argument("--unit", choices=("A", "C"), default="C")
    _add_live_ack(read)

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

    button = sub.add_parser("button", help="transmit a reconstructed remote front-panel command")
    button.add_argument("button", choices=[item.name.lower() for item in RemoteButton])
    _add_live_ack(button, writes=True)

    return p


def _validate_live_args(args: argparse.Namespace) -> int | None:
    if args.command not in LIVE_COMMANDS:
        return None
    if not args.port or args.baud is None:
        print("--port and --baud are required for live I/O", file=sys.stderr)
        return 2
    if args.request_delay < 0:
        print("--request-delay must be finite and nonnegative", file=sys.stderr)
        return 2
    if not args.i_understand_unverified_io:
        print(
            "Refusing live I/O: J3 electrical levels, pinout, and serial behavior are not yet "
            "validated on the physical stove. Pass --i-understand-unverified-io only on a "
            "protected bench setup after reading SAFETY.md.",
            file=sys.stderr,
        )
        return 3
    if args.command == "capture" and args.traffic_log is not None:
        print("capture uses --output as its traffic log; do not also pass --traffic-log", file=sys.stderr)
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

    error_code = _validate_live_args(args)
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
