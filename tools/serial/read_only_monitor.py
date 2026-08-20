#!/usr/bin/env python3
"""Read-only Bixby CR register monitor.

Use only after the J3 electrical interface and serial settings have been verified.
This tool never sends CW write commands.
"""
import argparse
import time
import serial


def read_reg(ser: serial.Serial, reg: int):
    cmd = f"CR{reg:02X}".encode("ascii")
    ser.reset_input_buffer()
    ser.write(cmd)
    ser.flush()
    line = ser.readline().decode("ascii", errors="replace").strip()
    prefix = f"CR{reg:02X}"
    if line.startswith(prefix) and len(line) >= 6:
        try:
            return int(line[4:6], 16), line
        except ValueError:
            pass
    return None, line


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("port")
    ap.add_argument("--baud", type=int, default=38400)
    ap.add_argument("--first", type=lambda x: int(x, 0), default=0)
    ap.add_argument("--last", type=lambda x: int(x, 0), default=0x0E)
    args = ap.parse_args()

    with serial.Serial(args.port, args.baud, timeout=0.35) as ser:
        previous = {}
        while True:
            for reg in range(args.first, args.last + 1):
                value, raw = read_reg(ser, reg)
                if value is None:
                    continue
                old = previous.get(reg)
                if old is not None and old != value:
                    print(f"{time.strftime('%H:%M:%S')} CR{reg:02X}: 0x{old:02X} -> 0x{value:02X} changed=0x{old ^ value:02X}", flush=True)
                previous[reg] = value
                time.sleep(0.025)


if __name__ == "__main__":
    main()
