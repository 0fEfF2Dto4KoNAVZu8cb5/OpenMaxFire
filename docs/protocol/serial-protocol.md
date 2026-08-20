# Serial protocol

## Confirmed command grammar

Firmware analysis directly identifies the ASCII parser:

- `CRxx` — read byte/register `xx`
- `CWxxYY` — write byte/value `YY` to register/command `xx`

`xx` and `YY` are two ASCII hexadecimal digits.

The parser checks for `C` followed by `R` or `W`. Firmware also contains ASCII-hex conversion routines and transmits responses as ASCII with LF (`0x0A`) termination.

## Relevant firmware addresses

- command first-character check (`C`): around program address `0x10E8`
- write selector (`W`): around `0x10F4`
- read selector (`R`): around `0x120E`
- ASCII-hex decoder: around `0x0F60`
- two-digit byte parser: around `0x0F7C`

See the annotated disassembly for context.

## Research discipline

Write commands are potentially operational/calibration commands. Unknown `CW` addresses must not be fuzzed on a live stove. Prefer static mapping and known-safe commands first.
