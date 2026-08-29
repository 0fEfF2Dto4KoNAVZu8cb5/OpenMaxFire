#!/usr/bin/env python3
"""Experimental physical Bixby MaxFire J3 flasher.

Not installed as maxfirectl. Run explicitly from a source checkout.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from openmaxfire.experimental_flasher import (
    ExperimentalFlasherError,
    ExperimentalJ3Flasher,
    FlasherEventRecorder,
    PhysicalFlasherPolicy,
    dry_run_image,
)
from openmaxfire.firmware import FirmwareImage, FirmwareImageError
from openmaxfire.transport import SerialSettings, SerialTransport


AUTH_PHRASE = "I-UNDERSTAND-J3-FLASHING-CAN-BRICK-THE-CONTROLLER"


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description=(
            "EXPERIMENTAL destructive J3 loader research tool. Requires an "
            "externally recoverable spare PIC/controller for physical writes."
        )
    )
    sub = p.add_subparsers(dest="command", required=True)

    dry = sub.add_parser("dry-run", help="validate a J3 image and print its block plan")
    dry.add_argument("image", type=Path)

    for name, help_text in (
        ("probe", "probe EA->EB only; sends no E3 programming block"),
        (
            "protected-test",
            "enter loader and send one protected-range E3 block that must be skipped by the loader",
        ),
        ("flash", "program a complete preserved J3 Downloader-format image"),
    ):
        cmd = sub.add_parser(name, help=help_text)
        cmd.add_argument("--port", required=True)
        cmd.add_argument("--baud", required=True, type=int, choices=(9600, 19200))
        cmd.add_argument("--timeout", type=float, default=0.25)
        cmd.add_argument("--event-log", type=Path)
        cmd.add_argument("--identify-attempts", type=int, default=150)
        cmd.add_argument("--identify-delay", type=float, default=0.02)
        cmd.add_argument("--timeout-retries", type=int, default=2)
        cmd.add_argument("--checksum-retries", type=int, default=2)
        cmd.add_argument("--unexpected-retries", type=int, default=0)
        cmd.add_argument(
            "--authorize",
            metavar="PHRASE",
            required=True,
            help=f"must exactly equal: {AUTH_PHRASE}",
        )
        if name == "flash":
            cmd.add_argument("image", type=Path)

    return p


def _authorized(args: argparse.Namespace) -> None:
    if args.authorize != AUTH_PHRASE:
        raise PermissionError("destructive loader operation authorization phrase did not match")


def _policy(args: argparse.Namespace) -> PhysicalFlasherPolicy:
    return PhysicalFlasherPolicy(
        identify_attempts=args.identify_attempts,
        identify_delay=args.identify_delay,
        timeout_retries=args.timeout_retries,
        checksum_retries=args.checksum_retries,
        unexpected_retries=args.unexpected_retries,
    )


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    if args.command == "dry-run":
        image = FirmwareImage.load(args.image)
        print(json.dumps(dry_run_image(image), indent=2, sort_keys=True))
        return 0

    _authorized(args)
    recorder = FlasherEventRecorder(args.event_log)
    transport = SerialTransport(SerialSettings(args.port, args.baud, args.timeout))
    flasher = ExperimentalJ3Flasher(transport, policy=_policy(args), recorder=recorder)
    try:
        if args.command == "probe":
            attempts = flasher.identify()
            result = {"mode": "probe", "success": True, "identify_attempt": attempts}
        elif args.command == "protected-test":
            result = flasher.run_protected_test()
        else:
            image = FirmwareImage.load(args.image)
            result = flasher.flash(image)
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    finally:
        try:
            transport.close()
        finally:
            recorder.close()


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ExperimentalFlasherError, FirmwareImageError, PermissionError, OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
