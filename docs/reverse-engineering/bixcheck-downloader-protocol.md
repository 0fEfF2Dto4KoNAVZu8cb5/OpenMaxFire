# BixCheck firmware-downloader protocol

Status: statically reconstructed from BixCheck 5.0.21, 5.5.00, and 5.5.01,
the complete 2.06 PICkit firmware, and the recovered Downloader images. The
`EA`/`EB` identify exchange is corroborated in the experimental PIC16F877A
emulator. Physical erase, programming, interruption, and recovery behavior
has not yet been validated on expendable hardware. Version 0.9 implements a
guarded physical host path behind spare-recovery and human safety interlocks;
that implementation is not evidence that the physical path is validated.

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

## Fixed loader baud and short reset window

BixCheck 5.5's general serial constructor supports selector `1` for 9,600 and
selector `2` for 19,200. `Bixby110Downloader()` always passes selector `1`.
The Downloader therefore uses **9,600 baud even when the installed or target
2.70/2.71 application uses 19,200**.

The resident 2.02/2.06 loader independently confirms this rate. Its USART
initialization sets asynchronous high-speed mode and `SPBRG=0x40`. With the
photographed 10.000 MHz oscillator, the PIC16 baud equation gives approximately
9,615 baud, the normal 9,600 setting.

The first loader receive is also short. It permits three Timer1 overflow
periods with `TMR1H=0x0B`, using the 10 MHz instruction clock. The resulting
reset-time window is approximately 78 ms. A host that sends `EA` and then waits
350 ms for each reply can repeatedly miss the entire window. The guarded
OpenMaxFire executor uses a 20 ms probe read timeout plus 20 ms spacing during
manual power-cycle entry, then switches to a longer block-response timeout.

The Downloader dialog exposes Read delay, Write delay, Retry delay, and
Interleave controls. Vendor screenshots and initialization use zero for all
four. Write delay is between the five-byte E3 header and its payload; Interleave
can add approximately millisecond pacing after a configured percentage of
bytes. Retry delay is not used by the preserved core block loop. UART wire
pacing at 9,600 already spaces bytes by about 1 ms, so OpenMaxFire sends one
complete frame and adds no default artificial interleave.

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
accepting that response. The OpenMaxFire v0.8 simulator reproduces this as one
initial transmission plus 29 accepted retries, followed by the terminal unread
31st transmission.

The BixCheck Cancel control forces the retry counter to its terminal value so
the transfer exits through the same failure path.

The OpenMaxFire physical policy deliberately does not reproduce that edge. It
classifies `E8`, `E5`, pre-accept timeout, post-accept timeout, unexpected
bytes, and transport failures independently and never emits a final unread
frame. `E8` and pre-accept timeout permit two retries; a post-`E7` timeout and
the first session-wide `E5` permit one. The second `E5`, unexpected bytes, and
transport failures abort immediately. No combination may transmit one block
more than four times. A retry after `E7` is especially bounded because the
previous write may have completed even if `E4` was lost; repeating identical
row data is idempotent but causes another erase/write cycle.

A timeout before observing `E7` is also treated as ambiguous, not proof that no
write occurred: the response itself may have been lost. A delayed `E4` is
accepted only when `E7` was already consumed for that same attempt; a delayed
`E7 E4` pair is accepted only when neither byte was consumed. A stray `E4`
after `E5`/`E8` cannot forge block success, and failure while checking the
receive buffer aborts without retransmission.

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

The complete original 2.02 PIC export preserved on 2026-08-28 proves its
resident `0x1E80`-`0x1FFF` loader is word-for-word identical to the factory
2.06 PICkit loader analyzed here. The 2.70 and 2.71 Downloader images do not
replace that resident loader, so a stove retains whichever loader was installed
by its original full-chip programming process.

## Emulator corroboration

When the experimental emulator queues `EA` at reset, the real 2.06 PICkit
firmware consumes it from `RCREG` and writes `EB` to `TXREG` after 43 modeled
instructions. This confirms the identify pair and its reset-window
relationship. The emulator intentionally does not yet execute physical Flash
programming.

## OpenMaxFire implementation consequences

The OpenMaxFire v0.8 simulator distinguishes `E5` from `E8`, models four-word
partial-row preservation and two internal write attempts, applies reset-vector
relocation and the protected boundary, reproduces BixCheck's 30 accepted block
attempts plus its terminal unread transmission, treats `ED` as one-shot
completion, and fails closed on simulated application reconnect. Exact attempt
responses and audit bytes remain available in the result.

Version 0.9 adds a separate guarded physical host. It accepts only exact
allowlisted factory Downloader images, authenticates the complete block-frame
sequence, requires a manual power cycle and proven external recovery, performs
a zero-`E3` physical rehearsal, uses a short loader-entry probe timeout, applies
the outcome-specific four-transmission ceiling above, and verifies target
identity plus byte-identical EEPROM afterward. It keeps one exclusive serial
handle across phases and does not reproduce BixCheck's terminal unread
transmission. Recovery requires an unresolved durable marker and is delegated
forward one session at a time so an old successful/recovered bundle cannot be
reused as a same-version rewrite path.

The implementation keeps these boundaries explicit:

- `E4` is PIC-side block verification, not whole-image physical readback;
- recovered Downloader images do not alter EEPROM;
- full PICkit images are rejected from J3 planning;
- simulator memory comparison and reconnect are not physical evidence;
- loader traffic is isolated from the normal/raw client and `CW0FC4` remains
  unexposed;
- a verified external-programmer recovery path remains mandatory.

## Remaining validation work

- Complete independent repeat reads of the original firmware 2.02 PIC.
- Prove a 2.02 clone and full PICkit recovery on a spare PIC.
- Capture an actual BixCheck update of expendable hardware for comparison.
- Confirm real loader timing, every response byte, interruption boundaries,
  post-transfer startup, and full-memory results.
- Execute the complete
  [J3 flasher qualification plan](../guides/j3-flasher-qualification.md),
  including forced power, USB, process, sleep, checksum, write, and completion
  faults without a heating load attached.

## Safety boundary

OpenMaxFire does not expose `CW0FC4`, identify, program-block, or done
operations through its normal or raw client. The dedicated physical executor
is experimental and refuses to run until its image, controller, backup,
wiring, cold/off state, disconnected igniters, and spare-recovery gates pass.
Production use remains blocked by policy until the executor is validated on an
externally recoverable spare PIC or bench controller that is not responsible
for heating.
