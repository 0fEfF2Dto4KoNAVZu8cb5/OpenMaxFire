# BixCheck 5.5.01 reverse engineering

## Artifact identity

| Field | Value |
| --- | --- |
| Preserved package | `BixCheck_080315.zip` |
| Executable | `BixCheck_080315.exe` |
| Size | 464,650 bytes |
| SHA-256 | `b681f79d284bc5da6d087ce052f916853402144430d4adbceaa2ed2e911c2792` |
| PE linker timestamp | 2008-03-16 04:31:21 UTC |
| Application | BixCheck Control/Monitor/Checkout 5.5.01 |
| Downloader | 2.71 |
| Intended stove software | 02.71 |
| Data format | 07 |

The EXE was not executed during the static pass. `tools/analyze_bixcheck.py`
verifies the package member hash, parses PE sections and retained COFF symbols,
disassembles code with GNU `objdump`, decodes the embedded application tables,
and produces deterministic CSV/JSON evidence.

## Recoverable source architecture

The PE header says ordinary debug information and line numbers were removed,
but the MinGW COFF table retains 655 function symbols at 654 unique code
offsets, demangled C++ names, and original compilation-unit names. Important
units include:

- `async.cpp`: Win32 serial setup and buffered I/O
- `Bixby110DataElements.cpp`: request/response grammar, data tables, checksum,
  and configuration conversions
- `Bixby110chkdlg.cpp`: factory Checkout workflow and reporting
- `Bixby110dlg.cpp`: Monitor/control UI and register operations
- `Bixby110Downloader.cpp`: Intel HEX loader and binary bootloader client

This is substantially richer than a string-only analysis. It allows methods to
be bounded, hashed, compared across builds, and archived as focused assembly.

## Normal serial protocol

The Win32 serial layer selects 9,600 or 19,200 baud and configures 8 data bits,
no parity, one stop bit, DTR enabled, RTS enabled, binary mode, and no CTS/DSR
or software flow control. `SetupComm` requests 30,480-byte input and output
buffers.

`bixby110io::regio()` emits uppercase ASCII with no request terminator:

| Operation | Exact request |
| --- | --- |
| Read | `<unit>R<address:02X>` (4 bytes) |
| Write | `<unit>W<address:02X><value:02X>` (6 bytes) |

`scanio()` accepts CR or LF response termination, strips leading control bytes
`01`, `02`, or `03`, and dispatches these forms:

- addressed response: `<A|C|D><operation><address:02X><value:02X>`;
- one-byte telemetry: `T<index:02X><value:02X>`;
- a compatibility two-byte receive representation:
  `T<index:02X><value0:02X><value1:02X>`;
- `M` and `I` status/control families, whose inner semantics remain unresolved.

Incoming hexadecimal accepts either case. The vendor parser performs weak
length and invalid-character checking; the replacement parser is intentionally
stricter. `CollectResponse()` makes at most 16 scan attempts and ignores
telemetry frames while waiting for a non-telemetry reply.

The later firmware-producer pass establishes that all preserved application
images physically send only the one-byte T form. BixCheck assembles a logical
16-bit field from two adjacent five-character T lines. It also accepts and
stores addressed D-unit auxiliary lines separately from T telemetry.

The real 2.71 firmware has also been run in the experimental PIC14 emulator: an
injected `CR00` produced `CR0000` plus LF. This is independent dynamic support
for the grammar, not a live-J3 validation.

## Recovered object and table layouts

The `bixby110io` object contains four 256-byte data areas:

| Object offset | Role |
| ---: | --- |
| `0x030` | D-unit data |
| `0x130` | A/unit-0 EEPROM data |
| `0x230` | telemetry data |
| `0x330` | serial-object pointer |
| `0x434` | C/command data |
| `0x634` | receive string |
| `0x734` | transmit string |

The global UI/configuration records are 0x58 bytes each. Their recovered layout
is documented in [configuration.md](../bixcheck/configuration.md), and every
record is exported in `reverse-engineering/bixcheck/5.5.01/data-elements.csv`.

5.5.01 contains 82 adjustment records and 34 telemetry/display records. Its
release-specific changes are:

- `Wheat` replaces `2% ash Biomass` in both Fuel A and Fuel B selection lists;
- 24 bytes in the corresponding fuel combustion profile change;
- telemetry `T19` is relabeled `BF drop limit`;
- `T1E` adds `LB drop limit`;
- virtual time-to-ash-dump moves from index `V1B` to `V1C`;
- `TFD`, `TFE`, and `TFF` add low-temperature count, sample maximum, and recent
  sample.

No functions were added or removed relative to 5.5.00. Most changed method
hashes come from the four-record table insertion shifting object offsets. The
register builder, checksum, checkout action senders, and downloader core remain
semantically equivalent.

## Configuration math

The 5.5 generation adds lean-burn parameters at A6B-A6E and A9B-A9E. The EXE
converts their raw values for display and reverses that conversion before
writing or calculating a checksum. The exact assembly is preserved in
`protocol-core.asm`; equivalent tested Python lives in
`src/openmaxfire/protocol.py`.

The configuration checksum starts at A02, adds each logical byte to a 16-bit
accumulator, then rotates the accumulator left by one bit. Data format 07 covers
through AFF. Displayed lean-burn values at A6B-A6D and A9B-A9D are converted
back to stove encoding before inclusion.

## Checkout and downloader

All 46 embedded Checkout records are byte-identical across the three EXEs.
Forty-five are reachable: 37 interactive/verification tests and eight automatic
tests. A ninth automatic record, `Plate motor cycle test`, exists in data but is
excluded by both the UI setup loop and action dispatcher.

The Downloader code is also semantically unchanged across all three builds.
It reads CR08 and CR0B-CR0E for identity, can use `CW0FC4` to request reset,
then switches to a separate raw-binary bootloader protocol. The reset request
works in the paired 2.06/2.70/2.71 applications but is absent from the exact
original 2.02 image, which therefore needs hardware reset for its first update. See
[bixcheck-downloader-protocol.md](bixcheck-downloader-protocol.md). Downloader
traffic must never be exposed through ordinary monitoring APIs.

## Generated evidence

The per-build directory contains:

- `summary.json`: PE identity, counts, and serial facts;
- `functions.csv` and `call-graph.csv`: retained function inventory and calls;
- `data-elements.csv`: decoded UI/configuration/telemetry records;
- `checkout-tests.csv`: all records plus reachability;
- `combustion-adjustments.csv`: raw adjustment arrays;
- `selected-strings.csv`: provenance-focused string inventory;
- `protocol-core.asm`, `checkout-core.asm`, and `downloader-core.asm`: exact
  focused disassembly excerpts;
- `telemetry-core.asm`, `write-ui-core.asm`, `logging-core.asm`, and
  `monitor-core.asm`: exact display/conversion, write/UI, log/report, and
  monitoring workflow excerpts.

Build-specific addresses are evidence locators, not stable protocol constants.
J3 signal direction and non-inverted 5 V TTL traffic were later live-validated,
and physical loader sessions supplied adverse first-block evidence. Conclusions
about corrected programming, interruption, and recovery remain unvalidated on
expendable hardware.
