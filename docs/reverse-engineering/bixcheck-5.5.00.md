# BixCheck 5.5.00 reverse engineering

## Artifact identity

| Field | Value |
| --- | --- |
| Package | `BixCheck_080206.zip` |
| Executable | `BixCheck_080206.exe` |
| Size | 462,052 bytes |
| SHA-256 | `12dd738a10f72f18a672aeec6ec5e1456ff478103ca84fc154c4f73594aac3d6` |
| PE linker timestamp | 2008-02-07 03:37:32 UTC |
| Application | BixCheck Control/Monitor/Checkout 5.5.00 |
| Downloader | 2.70 |
| Intended stove software | 02.70 |
| Data format | 07 |

## Transitional role

5.5.00 is the major functional transition between the 2.06/data-format-05 and
2.71 generations. It retains 655 function symbols at 654 unique offsets,
selects either 9,600 or 19,200 baud at 8N1, and uses 30,480-byte Win32 serial
queues.

The wire grammar itself does not change: reads are four bytes, writes are six,
requests have no terminator, and responses are terminated by CR or LF. The
matching firmware 2.70 dynamically emits `CR0000` plus LF for the `CR00` probe
inside the experimental PIC emulator.

## Additions over 5.0.21

The retained symbol comparison finds 16 project functions added and four
removed. New functionality includes:

- lean-burn raw/percentage transforms;
- signed `-128..127` entry validation and improved range checks;
- an argument-taking `CollectResponse` path and selectable serial mode;
- overloaded register-write helpers;
- expanded logging/report helpers;
- a downloader memory-bank erase check;
- version/mode arguments added to several constructors.

The adjustment table grows from 71 to 82 records. New A6B-A6E and A9B-A9E
fields cover lean-burn threshold, fan adjustment, feed adjustment, ratio/ash
trimpot mode, and automatic-restart disable. Explicit maximum/minimum bounds are
populated, and checksum coverage for format 07 extends through AFF.

## Difference from 5.5.01

5.5.00 still labels the third fuel choice `2% ash Biomass`; 5.5.01 renames it
`Wheat` and changes three eight-byte profile blocks. Its 30-record telemetry
table is the same as 5.0.21, before the four records added/repositioned in
5.5.01.

No project functions are added or removed in 5.5.01. The request builder,
checksum, Checkout action senders, and downloader core are semantically
equivalent. See [bixcheck-comparison.md](bixcheck-comparison.md) for the exact
matrix and `reverse-engineering/bixcheck/5.5.00/` for machine-readable evidence.
