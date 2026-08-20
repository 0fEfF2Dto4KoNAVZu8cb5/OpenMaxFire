# BixCheck 5.5.01 reverse engineering

Source: `preservation/original/binaries/BixCheck_080315.exe`

SHA-256: `b681f79d284bc5da6d087ce052f916853402144430d4adbceaa2ed2e911c2792`

The PE32 executable reports BixCheck control/monitor/Checkout version 5.5.01, Downloader 2.71, stove software 02.71, and database version 07. Its linker timestamp is 2008-03-16 14:31:21 UTC.

## Useful retained symbols

The binary has stripped normal debugging information but retains many GCC C++ symbol strings, including:

- `bixby110io::getrs232port()`
- `bixby110io::sendcommand()`
- `bixby110io::scanio()`
- `bixby110io::regio()`
- `bixby110io::writereg()`
- `bixby110io::readreg()`
- `bixby110io::CollectResponse()`
- `bixby110io::GetEEPROMContents()`
- `bixby110io::CalculateChecksum()`
- `bixby110control::BixbyWriteRegister()`
- `bixby110checkout::SendInteractiveAction()`
- `bixby110downloader::Identify()`
- `bixby110downloader::DownLoad()`

The searchable string inventories are preserved under `reverse-engineering/bixcheck/5.5.01/`.

## Remote-control evidence

`Bixby110RCButtonData` is located at VA 0x0043D380 in this build. Its OFF/ON/UP/DOWN entries contain values `0x11`, `0x12`, `0x14`, and `0x18`.

Handlers around VA 0x0041B0D7 and neighboring paths load those values and call:

`bixby110io::writereg('C', 0x0E, value)`

`writereg()` calls `regio()` with opcode `W`; `regio()` emits uppercase hexadecimal ASCII. This reconstructs `CW0E14` for UP and the other commands in the protocol document.

These addresses are build-specific. Do not assume they are stable in BixCheck 5.5.00 or 5.0.21.
