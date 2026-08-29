#!/usr/bin/env python3
"""Experimental physical Bixby MaxFire J3 flasher.

Not installed as maxfirectl. Run explicitly from a source checkout.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

from openmaxfire.client import MaxFireClient
from openmaxfire.experimental_flasher import (
    ExperimentalFlasherError,
    ExperimentalJ3Flasher,
    FlasherEventRecorder,
    PhysicalFlasherPolicy,
    dry_run_image,
    validate_j3_image,
)
from openmaxfire.firmware import FirmwareImage, FirmwareImageError
from openmaxfire.loader_entry import reset_application_into_loader
from openmaxfire.transport import SerialSettings, SerialTransport


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
        cmd.add_argument("--event-log", required=True, type=Path)
        cmd.add_argument("--identify-attempts", type=int, default=1500)
        cmd.add_argument(
            "--identify-interval",
            "--identify-delay",
            dest="identify_interval",
            type=float,
            default=0.015,
            help="target interval between EA probes in seconds (default: 0.015)",
        )
        cmd.add_argument(
            "--identify-read-timeout",
            type=float,
            default=0.010,
            help="temporary read timeout while probing for EB (default: 0.010)",
        )
        cmd.add_argument("--timeout-retries", type=int, default=2)
        cmd.add_argument("--checksum-retries", type=int, default=2)
        cmd.add_argument("--unexpected-retries", type=int, default=0)
        cmd.add_argument(
            "--i-understand-this-can-brick",
            action="store_true",
            required=True,
            help="required acknowledgement for all physical loader operations",
        )
        if name in ("protected-test", "flash"):
            cmd.add_argument(
                "--power-cycle-entry",
                action="store_true",
                help=(
                    "do not issue CW0FC4; instead wait for a manual power-cycle. "
                    "Default is BixCheck-style software reset from the running application"
                ),
            )
        if name == "flash":
            cmd.add_argument("image", type=Path)
            cmd.add_argument(
                "--post-baud",
                type=int,
                choices=(9600, 19200),
                help="after ED/E4, reopen the port at this baud and run read-only identify",
            )
            cmd.add_argument(
                "--post-delay",
                type=float,
                default=1.0,
                help="seconds to wait before optional post-flash identify (default: 1.0)",
            )

    return p


def _policy(args: argparse.Namespace) -> PhysicalFlasherPolicy:
    return PhysicalFlasherPolicy(
        identify_attempts=args.identify_attempts,
        identify_interval=args.identify_interval,
        identify_read_timeout=args.identify_read_timeout,
        timeout_retries=args.timeout_retries,
        checksum_retries=args.checksum_retries,
        unexpected_retries=args.unexpected_retries,
    )


def _post_flash_identity(args: argparse.Namespace) -> dict[str, object] | None:
    if args.post_baud is None:
        return None
    if args.post_delay < 0:
        raise ValueError("post-delay must be nonnegative")
    if args.post_delay:
        time.sleep(args.post_delay)
    transport = SerialTransport(SerialSettings(args.port, args.post_baud, args.timeout))
    try:
        identity = MaxFireClient(transport).identify(request_delay=0.10)
        return identity.to_dict()
    finally:
        transport.close()


def _enter_loader_if_requested(
    args: argparse.Namespace,
    transport: SerialTransport,
    recorder: FlasherEventRecorder,
) -> None:
    if getattr(args, "power_cycle_entry", False):
        recorder.record("loader_entry_mode", mode="manual_power_cycle")
        return
    recorder.record("loader_entry_mode", mode="application_CW0FC4")
    reset_application_into_loader(transport, recorder)


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    if args.command == "dry-run":
        image = FirmwareImage.load(args.image)
        print(json.dumps(dry_run_image(image), indent=2, sort_keys=True))
        return 0

    recorder = FlasherEventRecorder(args.event_log)
    transport = SerialTransport(SerialSettings(args.port, args.baud, args.timeout))
    flasher = ExperimentalJ3Flasher(transport, policy=_policy(args), recorder=recorder)
    closed = False
    try:
        if args.command == "probe":
            attempts = flasher.identify()
            result = {"mode": "probe", "success": True, "identify_attempt": attempts}
        elif args.command == "protected-test":
            _enter_loader_if_requested(args, transport, recorder)
            result = flasher.run_protected_test()
        else:
            image = FirmwareImage.load(args.image)
            validate_j3_image(image)
            _enter_loader_if_requested(args, transport, recorder)
            result = flasher.flash(image)
            transport.close()
            closed = True
            identity = _post_flash_identity(args)
            if identity is not None:
                result["post_flash_identity"] = identity
                result["post_flash_identity_matches_target"] = (
                    identity.get("firmware_version") == image.firmware_version
                )
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    finally:
        try:
            if not closed:
                transport.close()
        finally:
            recorder.close()


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ExperimentalFlasherError, FirmwareImageError, PermissionError, OSError, TimeoutError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
