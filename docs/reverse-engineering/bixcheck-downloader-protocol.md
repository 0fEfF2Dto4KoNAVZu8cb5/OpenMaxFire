# BixCheck firmware-downloader protocol

Status: statically reconstructed from all three EXEs and partially corroborated
in the experimental PIC16F877A emulator. It has not been used against a stove.

## Separation from normal traffic

Normal service/monitor traffic is ASCII `CRxx` / `CWxxyy`. Firmware download is
a distinct binary bootloader protocol. Bytes in this document must never be
sent by a read-only monitor or general register API.

Before switching protocols, `GetStoveVersion()` reads `CR08`, `CR0B`, `CR0C`,
`CR0D`, and `CR0E`, with approximately 100 ms between requests. BixCheck then
uses the normal write `CW0FC4` in `AttemptStoveReset()` to request entry into
the reset-time loader. That command is state-changing and unsafe for ordinary
use.

## Binary exchange

| Direction | Byte / frame | Reconstructed role |
| --- | --- | --- |
| Host → stove | `EA` | Identify probe, repeated until acknowledged |
| Stove → host | `EB` | Loader identified |
| Host → stove | `E3` | Begin program block |
| Host → stove | address high, address low | PIC word address |
| Host → stove | byte count | Payload size; host groups up to 32 bytes / 16 PIC words |
| Host → stove | checksum | Sum of data bytes modulo 256 |
| Host → stove | data bytes | Raw low/high PIC program-word bytes |
| Stove → host | `E7`, then `E4` | Two-stage block acknowledgement observed by host logic |
| Host → stove | `ED` | Download complete |
| Stove → host | `E4` | Completion acknowledgement |

The exact semantic names of the `E7` and `E4` block stages are inferred from
control flow; only the byte order and wait sequence are established. The host
retries a block up to roughly 30 times.

`LoadHex()` validates/parses Intel HEX records, groups consecutive PIC word
addresses, and prepares these blocks. The code path is semantically identical
in BixCheck 5.0.21, 5.5.00, and 5.5.01.

## Emulator corroboration

The PICkit 2.06 image includes the reset-time service region absent from the
Downloader image. When the emulator queues `EA` at reset, the actual firmware
consumes it from RCREG and writes `EB` to TXREG after 43 modeled instructions.
That confirms the identify pair and boot-window timing relationship inside the
preserved code. It does not validate real serial timing, flash programming, or
recovery behavior.

## Safety boundary

OpenMaxFire does not expose `CW0FC4`, identify, erase, program-block, or done
operations through its normal client. Future downloader work requires a
separate expert-only process, an immutable configuration backup, image/device
compatibility checks, a proven external-programmer recovery path, and bench
hardware that is not responsible for heating.
