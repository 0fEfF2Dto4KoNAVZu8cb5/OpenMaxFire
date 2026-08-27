# BixCheck firmware-downloader protocol

Status: statically reconstructed from BixCheck 5.0.21, 5.5.00, and 5.5.01,
the complete 2.06 PICkit firmware, and the recovered Downloader images. The
`EA`/`EB` identify exchange is corroborated in the experimental PIC16F877A
emulator. Physical erase, programming, interruption, and recovery behavior
has not yet been validated on expendable hardware.

## Two separate programming methods

Bixby distributed two fundamentally different image and programming paths:

- The J3/BixCheck Downloader sends an application image to a resident
  self-programming loader already installed in the PIC.
- A PICkit externally programs the complete PIC and can replace the
  application, resident loader, configuration word, User ID words, and data
  EEPROM.

The full 2.06 PICkit image maps all 8,192 PIC16F877A program words and 256
data-EEPROM bytes. The 2.06 Downloader image and the images embedded in
BixCheck 5.5.00 and 5.5.01 are application-update images. A PICkit image must
not be treated as a J3 Downloader image.

## Separation from normal J3 traffic

Normal service and monitor traffic is ASCII `CRxx` / `CWxxyy`. Firmware
download uses a distinct binary protocol on the same serial interface. Loader
bytes must never be sent by a read-only monitor or general register API.

Before switching protocols, `GetStoveVersion()` reads `CR08`, `CR0B`, `CR0C`,
`CR0D`, and `CR0E`, with approximately 100 ms between requests. BixCheck can
then issue the normal write `CW0FC4` through `AttemptStoveReset()`.

The application handles `CW0FC4` by delaying, disabling interrupts, clearing
`PCLATH`, and jumping to the hardware reset vector at address `0x0000`. The
resident reset vector redirects execution to the loader entry at `0x1E88`.
The vendor workflow also power-cycles the stove while BixCheck repeatedly
probes for the short reset-time loader window.

`CW0FC4` is state-changing and unsafe for ordinary use.

## High-level exchange

1. BixCheck parses the selected Downloader Intel HEX image.
2. The stove is reset or power-cycled.
3. BixCheck repeatedly sends `EA` until the loader answers `EB`.
4. BixCheck sends consecutive image words in `E3` program blocks.
5. The PIC checks, writes, and reads back each block.
6. BixCheck retransmits a block if the expected replies are not received.
7. BixCheck sends `ED` after every block succeeds.
8. The loader answers `E4` and transfers control to the application.

## Binary commands and responses

| Direction | Byte or frame | Reconstructed meaning |
| --- | --- | --- |
| Host → stove | `EA` | Identify loader; BixCheck repeats this probe |
| Stove → host | `EB` | Loader identified and ready |
| Host → stove | `E3` frame | Submit a program or EEPROM block |
| Stove → host | `E7` | Frame checksum accepted; programming is beginning |
| Stove → host | `E4` | Block write and PIC-side readback succeeded |
| Stove → host | `E5` | Write or PIC-side readback verification failed |
| Stove → host | `E8` | Received payload checksum did not match |
| Host → stove | `ED` | All blocks have been sent |
| Stove → host | `E4` | Completion acknowledged |

`E4` is overloaded: it acknowledges both a successfully verified block and
the final `ED` request. The `E7`, `E5`, and `E8` meanings are established from
the ordering and branches in the PIC loader, not merely from host-side names.

Unknown command bytes are ignored while the loader remains active. Another
`EA` produces another `EB`.

## Program-block frame

An `E3` transfer has this exact structure:

```text
E3
address_high
address_low
byte_count
checksum
data[byte_count]
```

- The address is a PIC word address, not an Intel HEX byte address.
- BixCheck divides the Intel HEX byte address by two.
- BixCheck combines consecutive words into payloads of at most 32 bytes, or
  16 PIC words.
- Each 14-bit PIC word is sent as its low byte followed by its high byte.
- The checksum is the sum of the data bytes modulo 256.
- The opcode, address, byte count, and checksum byte are not included in that
  sum.

The PIC receives the payload into RAM while independently summing its bytes.
A mismatch produces `E8` and no programming attempt. A match produces `E7`
before the self-programming routine is called.

## PIC-side Flash programming

The 2.06 loader follows the PIC16F877A four-word Flash programming rules:

1. Align the operation to a four-word program-memory row.
2. Read existing words before or after a partial update so untouched words in
   that row are preserved.
3. Load all four words into the device's write buffers.
4. Perform the required `0x55`, `0xAA`, write-enable sequence.
5. Allow the PIC to perform its four-word erase-and-write operation.
6. Read the programmed words back and compare them with the intended values.
7. Make up to two total row-write attempts before reporting failure.

A successful comparison returns `E4`; exhausted write or verification attempts
return `E5`. There is no separate host command to erase the whole chip. Erase
is part of the PIC's row-write operation.

This is local block verification only. BixCheck does not read the completed
image back or calculate a final whole-image checksum.

## Address handling and loader protection

The resident loader's directly protected range begins at `0x1E80`. Direct
program requests at or above `0x1E80` are skipped and treated as successfully
processed. This prevents a normal Downloader image from replacing the loader,
configuration word, or User ID words.

Application addresses `0x0000` through `0x0003` are a deliberate exception.
The loader redirects those four words to `0x1E84` through `0x1E87`. They form
the application's relocated reset trampoline. The physical reset vector at
`0x0000` remains owned by the resident loader and always enters the loader
first.

When the loader leaves, it executes the relocated trampoline, which selects
the final program page and transfers control to application startup at
`0x1800` in the recovered images.

The 2.71 application reaches `0x1E5E`, leaving only a small gap below the
`0x1E80` protected loader boundary.

## Data EEPROM, configuration, and sparse data

The loader recognizes addresses in the `0x21xx` range as data EEPROM writes.
However, the recovered 2.06, 2.70, and 2.71 Downloader images contain no
EEPROM words. A normal factory J3 application update therefore leaves EEPROM
calibration and settings in place.

The Downloader files contain configuration and User ID records, but their
addresses are inside the loader's direct skip range. They are not applied by
the J3 loader. The full PICkit image is different and can program those
regions.

BixCheck sends only words present in the sparse Intel HEX image. It does not
perform a mass erase of locations omitted from the file. A downgrade can
therefore leave stale, normally unreachable words above the older
application's final mapped address.

## Retry and cancellation behavior

BixCheck expects `E7` followed by `E4` for every block. Any missing or
unexpected byte causes the entire block to be sent again; the host does not
present `E5` and `E8` as distinct operator errors.

The original retry counter permits 30 attempts whose responses can be
accepted. Its control flow can transmit a 31st attempt, but aborts before
accepting that response. The current OpenMaxFire simulator models 30 retries
after an initial attempt, so its accepted-attempt budget is one larger than
BixCheck's and should be corrected separately.

The BixCheck Cancel control forces the retry counter to its terminal value so
the transfer exits through the same failure path.

## Completion and interrupted updates

`SendDone()` transmits `ED` and requires `E4`. A missing or different response
is treated as a fatal download failure. After replying, the PIC waits briefly
for one final serial receive, disables the loader UART state, and branches to
the relocated application reset code.

An interrupted transfer can leave application rows partially updated and the
stove application non-functional. The vendor documentation says the transfer
may be attempted again because the protected update software is not damaged.
This is consistent with the loader residing outside the normal update range.

J3 recovery cannot repair a loader erased or corrupted by external
programming. That condition requires a PICkit or equivalent programmer and a
complete image.

## Cross-version evidence

The normalized machine code for `GetStoveVersion()`, `AttemptStoveReset()`,
`LoadHex()`, `DownLoad()`, `Identify()`, and `SendDone()` is identical across
BixCheck 5.0.21, 5.5.00, and 5.5.01. This strongly indicates that Bixby kept
the host protocol stable from firmware 2.06 through 2.71.

The exact resident loader in the original 2.02 PIC remains unknown until that
chip is dumped. The 2.70 and 2.71 Downloader images do not replace a resident
loader, so a stove retains whichever loader was installed by its original
full-chip programming process.

## Emulator corroboration

When the experimental emulator queues `EA` at reset, the real 2.06 PICkit
firmware consumes it from `RCREG` and writes `EB` to `TXREG` after 43 modeled
instructions. This confirms the identify pair and its reset-window
relationship. The emulator intentionally does not yet execute physical Flash
programming.

## OpenMaxFire implementation consequences

The OpenMaxFire v0.8 loader remains simulator-only. It now distinguishes `E5`
from `E8`, models four-word partial-row preservation and two internal write
attempts, applies reset-vector relocation and the protected boundary, reproduces
30 accepted block attempts plus the terminal unread transmission, treats `ED`
as one-shot completion, and fails closed on simulated application reconnect.
Exact attempt responses and audit bytes remain available in the result.

The simulator also keeps these boundaries explicit:

- `E4` is PIC-side block verification, not whole-image physical readback;
- recovered Downloader images do not alter EEPROM;
- full PICkit images are rejected from J3 planning;
- simulator memory comparison and reconnect are not physical evidence;
- no serial loader transport, `CW0FC4`, or erase/program entry point exists;
- a verified external-programmer recovery path remains mandatory.

## Remaining validation work

- Dump and analyze the original firmware 2.02 resident loader.
- Prove a 2.02 clone and full PICkit recovery on a spare PIC.
- Capture an actual BixCheck update of expendable hardware.
- Confirm real loader timing, every response byte, interruption boundaries,
  and post-transfer startup.
- Test wrong checksum, failed write, disconnect, retry, downgrade, and
  cancellation cases without a heating load attached.

## Safety boundary

OpenMaxFire does not expose `CW0FC4`, identify, program-block, or done
operations through its normal client. Physical firmware programming remains
blocked. Validation requires an externally recoverable spare PIC or bench
controller that is not responsible for heating, an immutable backup, strict
image and device compatibility checks, and a proven recovery procedure.
