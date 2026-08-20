# Research log

## 2026-08-18

- Defined the preservation-first project scope.
- Recovered the BixCheck 5.x manual and three vendor software packages.
- Identified BixCheck's Monitor, calibration, telemetry, logging, Checkout, and Downloader functions.
- Recorded the factory cable part number and J3 location from vendor documentation.
- Established the reliability requirement: the smart layer must not impair factory operation.

## 2026-08-19

- Built the first OpenMaxFire v0.1 Python protocol/CLI skeleton.
- Statically reconstructed `CRXX` and `CWXXYY` command encodings from BixCheck 5.5.01.
- Reconstructed remote OFF/ON/UP/DOWN writes to controller register 0x0E.
- Recorded the owner's stove/PCB identification details.
- Investigated door-state feasibility and automatic heating-source coordination.

## 2026-08-20

- Extracted embedded `Bixby_0271_080315.hex` from BixCheck 5.5.01.
- Parsed and disassembled firmware 2.71 as PIC16F877A code.
- Annotated the reset vector, UART setup, ASCII-hex decoder, read/write parser, CR register handlers, and response terminator.
- Identified UART register values `SPBRG=0x20`, `TXSTA=0x26`, and `RCSTA=0x90`.
- Mapped CR00-CR0E static handlers and narrowed door-switch candidates to CR02/CR06 input bits.
- Created this structured GitHub archive and documented the initial baud/divisor ambiguity.
- Completed a reproducible deep reverse-engineering pass over BixCheck 5.0.21,
  5.5.00, and 5.5.01 using retained MinGW COFF symbols, focused disassembly,
  decoded tables, call graphs, and normalized function comparison.
- Established exact BixCheck host settings: 5.0.21 uses 9,600 baud; 5.5.x
  selects 9,600/19,200; all are 8N1. This resolves the earlier divisor ambiguity
  in favor of a strongly inferred 10 MHz controller oscillator.
- Reconstructed the complete outer response grammar, no-terminator request
  framing, 34-record 5.5.01 telemetry map, 0x58-byte configuration record,
  lean-burn transforms, and add/rotate checksum.
- Decoded all direct Checkout actions and found the dormant, unreachable ninth
  automatic plate-motor record shared by every EXE.
- Reconstructed Downloader identity/block framing and kept it isolated from the
  normal protocol API.
- Built a read-only-by-default PTY serial lab and strict response parser.
- Built an experimental PIC16F877A execution harness. The real 2.06, 2.70, and
  2.71 images responded to `CR00` with `CR0000` plus LF; the PICkit loader
  responded to reset-time `EA` with `EB`.
- Extended the emulator across every CR00-CR0E handler in all three application
  generations. All 45 handlers and formatters completed, with exact RAM/SFR
  read dependencies, instruction watchpoints, and net-change exports.
- Discovered that the real response formatter uses lowercase hexadecimal
  letters (`CR0A` returns `CR0a...`) even though host requests are uppercase.
- Added separate GPIO latch/input modeling and cross-referenced BixCheck's
  result masks: firebox door=CR02.5/RD1, ash drawer=CR02.6/RD4, and
  thermostat=CR06.2/RB4. CR02.2 remains a provisional fuel-select mux slot.
- Added reset-time ten-bit ADC replay and identified fan potentiometer=CR09/AN3
  and feed potentiometer=CR0A/AN4 across all three generations.
- Corrected A-unit storage to the PIC16F877A internal data EEPROM path, built
  checksum-valid synthetic format-05/07 fixtures, and verified all 768
  AR00-ARFF reads byte-for-byte.
