# PICkit 3 read-only firmware preservation

Status: prepared for the removed original PIC16F877A, its socket, and spare
chips. No original-chip read has happened yet. This procedure deliberately
separates preservation from cloning and contains a hard stop for code
protection.

## Non-negotiable rule

The first session with the original chip is **read/export only**. Never click
Program, Erase, Blank Check, or any action described as erase before read. Do
not load a factory HEX file while the original chip is in the socket. If the
tool reports code protection, stop and preserve the output/log; do not clear
protection. Microchip states that protected PIC16F87XA program/data reads return
zeros and the only supported removal path is a chip erase, which destroys the
program, EEPROM, configuration, and ID contents.

The original chip is already removed from the stove board, which is the best
boundary for this work: no stove mains power, controller power, J3 cable, or
other board connection belongs in the read setup.

## Software

Use MPLAB X IDE/IPE **6.20** for a PICkit 3. Microchip identifies 6.20 as the
last MPLAB X release with PICkit 3 support; newer releases target newer tools.

- [MPLAB X IDE downloads and PICkit 3 support note](https://www.microchip.com/en-us/tools-resources/develop/mplab-x-ide)
- [MPLAB IPE guide](https://www.microchip.com/DS50002227)
- [Microchip: read a device and save the HEX file](https://developerhelp.microchip.com/xwiki/bin/view/software-tools/ides/x/projects/read-device/)
- [Microchip: export HEX from IPE](https://developerhelp.microchip.com/xwiki/bin/view/software-tools/ipe/production-mode/exporting-hex-file/)

Install the software and drivers before connecting the PICkit 3. Disable any
Programmer-To-Go behavior for this session.

## Bare-chip/socket wiring

Confirm the PIC notch and pin 1 before inserting either the original or a
spare. On the 40-pin PDIP PIC16F877A, Microchip's programming specification
maps MCLR/VPP to pin 1, RB6/PGC to pin 39, and RB7/PGD to pin 40. Both VDD and
both VSS pins must be connected.

| PICkit 3 header | Signal | PIC16F877A PDIP |
| ---: | --- | ---: |
| 1 | MCLR/VPP | 1 |
| 2 | VDD target | 11 and 32 |
| 3 | VSS/ground | 12 and 31 |
| 4 | PGD/ICSPDAT | 40, RB7 |
| 5 | PGC/ICSPCLK | 39, RB6 |
| 6 | PGM/LVP | Normally unused for high-voltage entry; connect only when the socket adapter and selected IPE method explicitly require LVP |

The PICkit header's pin-1 triangle and the chip's pin-1 notch/dot are separate
references; verify both. Do not copy wire colors. If a purchased socket adapter
has its own mapping, continuity-check it against the table before inserting the
original chip.

For a bare chip, allow the PICkit to supply the target voltage selected by IPE;
do not attach another supply at the same time. The PICkit 3 source is limited,
but a bare PIC is within the intended small-target use. Do not hot-plug or move
socket wiring while the programmer or target is powered.

Primary hardware references:

- [PICkit 3 user's guide and six-pin header](https://ww1.microchip.com/downloads/en/devicedoc/52116a.pdf)
- [PIC16F87XA programming specification](https://ww1.microchip.com/downloads/en/DeviceDoc/39589b.pdf)

## Original-chip read sequence

1. Photograph the original chip, its orientation, the empty socket, the
   adapter labels, and every connection before applying USB power.
2. Start MPLAB IPE 6.20. Select `PIC16F877A`, select the detected PICkit 3, and
   connect.
3. Confirm that Program Memory, Data EEPROM, Configuration Memory, and User ID
   memory are included in the read/export view. Device ID may also be present.
4. Click **Read** once. Save the complete output log and export the device
   memory to `openmaxfire-202-original-read-01.hex`.
5. Disconnect in software, remove USB power, wait, and reseat the chip. Repeat
   twice as `read-02.hex` and `read-03.hex`. Independent power cycles matter;
   exporting the same in-memory read three times is not three reads.
6. Do not normalize, edit, or open-and-save the HEX files in another tool.
   Make read-only backup copies before analysis.
7. Authenticate all three exports with the offline checker below.

```bash
PYTHONPATH=src python tools/pickit_preservation.py \
  openmaxfire-202-original-read-01.hex \
  openmaxfire-202-original-read-02.hex \
  openmaxfire-202-original-read-03.hex \
  --output openmaxfire-202-original-manifest.json
```

The report normalizes erased/omitted locations and independently compares
program memory, all 256 EEPROM bytes, four User ID words, and the configuration
word. It records raw-file and normalized SHA-256 digests. Success requires at
least two semantically identical reads, readable CP/CPD configuration bits,
program content, and EEPROM content. Three matching reads remain the project
procedure.

If the report exits nonzero, stop. Do not average, patch, or choose the dump
that “looks right.” Preserve all files and diagnose the connection or
protection result first.

## Code-protection stop

For the PIC16F877A configuration word:

- CP bit 13 = 0 means program-memory code protection is enabled;
- CPD bit 8 = 0 means data-EEPROM code protection is enabled.

The checker treats enabled or unknown protection as a blocker. Do not attempt
to bypass it, do not use “preserve memory” as a workaround, and do not erase
the original. Microchip's IPE documentation also warns that preserve-memory
operations involve a read followed by bulk erase and reprogramming; that is
not a read-only backup operation.

## Spare-chip clone sequence

Cloning starts only after the original has three matching reads and the
original is labeled, removed from the programmer, and stored safely.

1. Insert a verified spare PIC16F877A into the socket.
2. Import the authenticated original HEX into IPE.
3. Confirm the selected device and memory regions again, then Program and
   Verify the **spare only**.
4. Power-cycle the programmer and read the spare back to a new HEX file.
5. Compare the original reference and spare readback:

```bash
PYTHONPATH=src python tools/pickit_preservation.py \
  openmaxfire-202-original-read-01.hex \
  openmaxfire-202-clone-readback-01.hex \
  --purpose clone-compare \
  --output openmaxfire-202-clone-compare.json
```

The clone is not proven by IPE's Program message alone. It needs a matching
readback report and, later, a controlled board test. A clone may have different
device-revision bits in its Device ID; the preservation comparison intentionally
authenticates program, EEPROM, User IDs, and configuration instead.

## Files to retain

- every untouched original-chip HEX read;
- every PICkit/IPE output log;
- the repeated-read JSON manifest;
- clear connection/orientation photographs;
- the exact MPLAB X/IPE version and PICkit 3 serial/firmware details;
- every spare-chip program log, verify log, readback HEX, and comparison report.

Do not reinstall or power the original chip merely to “see if it works” before
the dump set has been copied and authenticated. The original is the only known
source for firmware 2.02 and its resident loader.
