#!/usr/bin/env python3
"""Authenticate repeated PIC16F877A read exports without touching hardware."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from openmaxfire.preservation import compare_pic16f877a_dumps


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Compare two or more PIC16F877A Intel HEX read exports by program "
            "memory, EEPROM, User IDs, and configuration word. This tool has "
            "no programmer or hardware-write capability."
        )
    )
    parser.add_argument(
        "images",
        nargs="+",
        type=Path,
        help="independently exported Intel HEX dump (at least two)",
    )
    parser.add_argument(
        "--purpose",
        choices=("repeated-dump", "clone-compare"),
        default="repeated-dump",
        help="interpret all inputs as repeated original reads or reference/clone reads",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="write the JSON report to this new path instead of stdout",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="allow --output to replace an existing report",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        resolved = [image.resolve() for image in args.images]
        if len(set(resolved)) != len(resolved):
            raise ValueError(
                "each independent read must be supplied from a distinct file path"
            )
        report = compare_pic16f877a_dumps(args.images, purpose=args.purpose)
        payload = json.dumps(report.to_dict(), indent=2, sort_keys=True) + "\n"
        if args.output is None:
            sys.stdout.write(payload)
        else:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            with args.output.open(
                "w" if args.overwrite else "x", encoding="utf-8", newline="\n"
            ) as stream:
                stream.write(payload)
    except (OSError, ValueError) as exc:
        print(f"preservation check failed: {exc}", file=sys.stderr)
        return 2
    return 0 if report.authenticated else 1


if __name__ == "__main__":
    raise SystemExit(main())
