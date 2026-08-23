#!/usr/bin/env python3
"""Compatibility wrapper for the first-class maxfirectl monitor command.

New work should invoke maxfirectl directly. This wrapper retains the original
positional-port interface without resetting the serial input buffer or
discarding interleaved telemetry.
"""

from __future__ import annotations

import argparse

from openmaxfire.cli import main as maxfirectl_main


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("port")
    parser.add_argument("--baud", type=int, required=True, choices=(9600, 19200))
    parser.add_argument("--timeout", type=float, default=1.0)
    parser.add_argument("--request-delay", type=float, default=0.10)
    parser.add_argument("--duration", type=float, default=0.0)
    parser.add_argument("--cycles", type=int)
    parser.add_argument("--output")
    parser.add_argument("--traffic-log")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--i-understand-unverified-j3", action="store_true")
    args = parser.parse_args()

    command = [
        "--port",
        args.port,
        "--baud",
        str(args.baud),
        "--timeout",
        str(args.timeout),
        "--request-delay",
        str(args.request_delay),
    ]
    if args.traffic_log:
        command.extend(("--traffic-log", args.traffic_log))
    command.extend(("monitor", "--duration", str(args.duration)))
    if args.cycles is not None:
        command.extend(("--cycles", str(args.cycles)))
    if args.output:
        command.extend(("--output", args.output))
    if args.json:
        command.append("--json")
    if args.i_understand_unverified_j3:
        command.append("--i-understand-unverified-io")
    return maxfirectl_main(command)


if __name__ == "__main__":
    raise SystemExit(main())
