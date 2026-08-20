#!/usr/bin/env python3
"""Unverified CR00-CR0E differential monitor.

It sends only CR reads and uses the strict response grammar reconstructed from
all three BixCheck EXEs. Its electrical assumptions are not validated.
"""

from __future__ import annotations

import argparse
import time

from openmaxfire.protocol import AddressedResponse, ProtocolError, parse_response_line


def read_line(ser, limit: int = 255) -> bytes:
    line = bytearray()
    while len(line) <= limit:
        value = ser.read(1)
        if not value:
            return bytes(line)
        if value in (b"\r", b"\n"):
            if line:
                return bytes(line)
            continue
        line.extend(value)
    return bytes(line)


def read_reg(ser, register: int) -> tuple[int | None, bytes]:
    request = f"CR{register:02X}".encode("ascii")
    ser.reset_input_buffer()
    ser.write(request)
    ser.flush()
    raw = read_line(ser)
    try:
        response = parse_response_line(raw)
    except ProtocolError:
        return None, raw
    if (
        isinstance(response, AddressedResponse)
        and response.unit == "C"
        and response.address == register
    ):
        return response.value, raw
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
