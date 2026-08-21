# Controller-board notes

## Confirmed from firmware

Firmware metadata and valid code disassembly identify the controller as a Microchip PIC16F877A.

Startup TRIS configuration makes these pins inputs:

- RA0-RA5
- RB0, RB4, RB6, and RB7
- RD0, RD1, RD3, and RD4
- RE0 and RE1

RB1 and RB5 are outputs even though CR03 reports their states.

The common input scanners in 2.06, 2.70, and 2.71 also establish two RD3
multiplexer banks. RD2 selects the active-low four-button bank, while RD7
selects an active-high three-input external-switch bank; RD6:RD5 select the
individual input in each bank. The results are exposed as CR01 and CR02 bits
0-2. See the [multiplexer cross-reference](maxfire-motherboard-pinout.md).

Two additional sensor paths are identical in 2.06, 2.70, and 2.71:

- RA4/T0CKI counts J10 exhaust-sensor falling edges in TMR0. The firmware
  latches that count to RAM `0x34`, which is returned as `CR05`.
- RD0 detects a high-then-low J9 feeder-wheel sensor cycle while RB1 is active.
  The elapsed RB0-interrupt count is latched and scaled into `CR07`; the
  instantaneous RD0 state is also exposed as `CR02.4`.

The exact instruction PCs and transforms are in the
[register map](../protocol/register-map.md). The RB0 interrupt is the
phase-control timebase and is strongly consistent with AC zero crossing, but
that physical role and the resulting CR05/CR07 engineering units remain
unmeasured.

These are firmware-level facts, not a complete physical schematic. The
9067-0404 diagram provides related-family labels. New installed-board
photographs show the component side, confirm connector placement, and expose a
`-0604` suffix consistent with the owner-reported 9067-0604 board. The complete
prefix, revision-specific continuity, solder-side routing, and electrical
polarity remain unverified.

## Installed-board evidence

The [installed-controller photographs](installed-controller-photographs.md)
directly show the main-PCB `-0604` suffix, component side, harness routing,
auxiliary output board, and black four-contact main-board J3. The full
`9067-0604` part number, manufacture in December 2005, and internal assembly
mark `12/15` remain owner-reported. The solder side and oscillator marking are
still needed.

The preserved `MaxFire Mother Board Pin Out` image visibly shows the earlier or
related PCB part number `9067-0404`. It strongly corroborates the controller
family, connector roles, and input names, but it is not an exact-revision
schematic for serial 5215.
