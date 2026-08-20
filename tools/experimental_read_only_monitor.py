#!/usr/bin/env python3
"""Unverified CR00-CR0E differential monitor.

This is preserved from the pre-cable research plan. It sends only CR reads,
but its electrical assumptions and response parser are not validated.
"""

from __future__ import annotations

import argparse
import time


def read_reg(ser, register: int) -> tuple[int | None, bytes]:
    request = f"CR{register:02X}".encode("ascii")
    ser.reset_input_buffer()
    ser.write(request)
    ser.flush()
    raw = ser.readline()

    # Historical parser hypothesis: echoed CRXX followed by one hex byte.
    line = raw.decode("ascii", errors="replace").strip()
    prefix = f"CR{register:02X}"
    if line.startswith(prefix) and len(line) >= 6:
        try:
            return int(line[4:6], 16), raw
        except ValueError:
            pass
    return None, raw


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("port")
    parser.add_argument("--baud", type=int, required=True)
    parser.add_argument("--first", type=lambda value: int(value, 0), default=0)
    parser.add_argument("--last", type=lambda value: int(value, 0), default=0x0E)
    parser.add_argument("--i-understand-unverified-j3", action="store_true")
    args = parser.parse_args()

    if not args.i_understand_unverified_j3:
        parser.error("read SAFETY.md and pass --i-understand-unverified-j3 on a protected setup")

    import serial

    with serial.Serial(args.port, args.baud, timeout=0.35) as ser:
        previous: dict[int, int] = {}
        while True:
            for register in range(args.first, args.last + 1):
                value, raw = read_reg(ser, register)
                if value is None:
                    if raw:
                        print(f"raw CR{register:02X}: {raw!r}", flush=True)
                    continue
                old = previous.get(register)
                if old is not None and old != value:
                    changed = old ^ value
                    now = time.strftime("%H:%M:%S")
                    print(
                        f"{now} CR{register:02X}: 0x{old:02X} -> "
                        f"0x{value:02X} changed=0x{changed:02X}",
                        flush=True,
                    )
                previous[register] = value
                time.sleep(0.025)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
