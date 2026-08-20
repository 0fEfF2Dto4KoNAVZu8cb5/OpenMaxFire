"""maxfirectl command-line utility."""

from __future__ import annotations

import argparse
import sys

from .client import MaxFireClient
from .protocol import RemoteButton, encode_read_register, encode_remote_button, encode_write_register
from .transport import SerialSettings, SerialTransport


def _int_auto(value: str) -> int:
    return int(value, 0)


def _connect(args: argparse.Namespace) -> MaxFireClient:
    return MaxFireClient(SerialTransport(SerialSettings(args.port, args.baud, args.timeout)))


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="maxfirectl", description="OpenMaxFire service/protocol utility")
    p.add_argument("--port", help="serial port, e.g. /dev/ttyUSB0 or COM3")
    p.add_argument(
        "--baud",
        type=int,
        help="required for live I/O; BixCheck uses 9600 (2.06) or 19200 (2.70/2.71)",
    )
    p.add_argument("--timeout", type=float, default=0.25)

    sub = p.add_subparsers(dest="command", required=True)

    enc = sub.add_parser("encode", help="show a reconstructed J3 command without transmitting it")
    enc_sub = enc.add_subparsers(dest="encode_command", required=True)
    er = enc_sub.add_parser("read")
    er.add_argument("address", type=_int_auto)
    ew = enc_sub.add_parser("write")
    ew.add_argument("address", type=_int_auto)
    ew.add_argument("value", type=_int_auto)
    eb = enc_sub.add_parser("button")
    eb.add_argument("button", choices=[b.name.lower() for b in RemoteButton])

    rr = sub.add_parser("read", help="transmit a register read")
    rr.add_argument("address", type=_int_auto)
    rr.add_argument(
        "--i-understand-unverified-io",
        action="store_true",
        help="required until the electrical interface and serial settings are live-validated",
    )

    rb = sub.add_parser("button", help="transmit a reconstructed remote front-panel command")
    rb.add_argument("button", choices=[b.name.lower() for b in RemoteButton])
    rb.add_argument(
        "--i-understand-unverified-io",
        action="store_true",
        help="required until the electrical interface and commands are live-validated",
    )

    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.command == "encode":
        if args.encode_command == "read":
            payload = encode_read_register(args.address)
        elif args.encode_command == "write":
            payload = encode_write_register(args.address, args.value)
        else:
            payload = encode_remote_button(RemoteButton[args.button.upper()])
        print(payload.decode("ascii"))
        return 0

    if not args.port or args.baud is None:
        print("--port and --baud are required for live I/O", file=sys.stderr)
        return 2

    if not args.i_understand_unverified_io:
        print(
            "Refusing live I/O: J3 electrical levels, pinout, and serial behavior are not yet "
            "validated on the physical stove. Pass --i-understand-unverified-io only on a "
            "protected bench setup after reading SAFETY.md.",
            file=sys.stderr,
        )
        return 3

    client = _connect(args)
    try:
        if args.command == "read":
            receipt = client.read_register(args.address)
        elif args.command == "button":
            receipt = client.remote_button(RemoteButton[args.button.upper()])
        else:
            raise AssertionError(args.command)
        print(receipt.request.decode("ascii"))
        return 0
    finally:
        client.close()


if __name__ == "__main__":
    raise SystemExit(main())
