# Experimental PIC16F877A emulation

## Purpose

`tools/pic14_emulator.py` provides a deterministic offline execution harness
for the preserved firmware. It was built because a full PIC simulator was not
available in the analysis environment and static disassembly alone could not
prove that independently reconstructed receive/transmit paths joined into a
complete exchange.

This is not an appliance simulator. It cannot model combustion or prove that a
command is safe on physical hardware.

## Implemented model

The harness implements all 35 baseline/mid-range instructions used by these
PIC14 images, including:

- banked direct and indirect file-register access;
- STATUS flags, PCL/PCLATH paging, computed jumps, and the eight-level stack;
- calls, returns, interrupt entry, and `RETFIE`;
- UART RCREG/PIR1 receive and TXREG transmit behavior;
- program image and data-EEPROM loading from validated Intel HEX;
- minimal Timer0/Timer1/Timer2, ADC-completion, EEPROM-read, and I²C completion
  behavior needed to traverse the firmware.

Tight `DECFSZ`/`GOTO`-self software-delay loops are fast-forwarded while keeping
their terminal register state. I²C reads return a fixed synthetic value so
startup can complete. These choices make protocol exploration practical but
mean timing and hardware-state conclusions are invalid.

## Probe results

| Image | Injected bytes | Actual firmware TX | Result |
| --- | --- | --- | --- |
| 2.06 Downloader | ASCII `CR00` | `43 52 30 30 30 30 0A` (`CR0000` + LF) | Completed |
| 2.70 embedded | ASCII `CR00` | `43 52 30 30 30 30 0A` | Completed |
| 2.71 embedded | ASCII `CR00` | `43 52 30 30 30 30 0A` | Completed |
| 2.06 PICkit/service | raw `EA` at reset | `EB` | Completed in 43 modeled instructions |

For all three application generations, the emulator:

1. follows the real reset vector and startup code;
2. executes the firmware's UART interrupt path to consume each request byte;
3. reaches the real `C`/`R` parser and CR00 handler;
4. executes the real ASCII-hex formatter; and
5. captures the real TXREG writes.

That is strong independent support for request length, response structure, the
CR00 constant, and LF termination. It also confirms the bootloader's `EA`/`EB`
identify pair. These remain emulated findings until reproduced through a
protected, read-only J3 connection.

## Reproducing

```bash
python tools/pic14_emulator.py project --repo-root .
```

The command writes per-image JSON summaries, UART/peripheral event CSVs, and
the final 1,024-instruction trace window under
`reverse-engineering/firmware/emulation/`.

To probe a standalone image without changing it:

```bash
python tools/pic14_emulator.py probe path/to/image.hex --bytes 43523030
```

## Explicit limitations

- No voltage levels, oscillator tolerance, baud timing, cable polarity, or
  physical pinout is modeled.
- Analog inputs, switches, fans, motors, igniters, flame dynamics, and safety
  behavior are not modeled.
- Timer and I²C behavior is synthetic and not cycle-accurate.
- The bootloader program/erase path has not been emulated or exercised.
- A passing trace is evidence about software control flow, not permission to
  send writes to a stove.
