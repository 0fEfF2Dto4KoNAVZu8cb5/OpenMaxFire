# Architecture

OpenMaxFire has two related products with deliberately different scopes.

## Cross-platform service tool

The Windows/Linux/macOS CLI/application is the eventual BixCheck replacement.
Its long-term scope includes serial communication, stove identification,
telemetry, remote control, fuel/hardware configuration, calibration,
blocked-flue and lean-burn monitoring, thermostat/auto-restart settings,
trim-pot modes, configuration readback/write/format, logging, factory Checkout,
debug tools, firmware identification, bootloader communication, firmware
flashing, and post-flash calibration.

Dangerous service functions must remain visibly separated from normal monitoring and control.

The portable architecture has four boundaries:

- `protocol`: OS-independent request encoding, response parsing, register
  interpretation, conversions, and checksums;
- `client`: bounded request/response matching, identity, read-only A-space
  acquisition, and later verified control workflows;
- `transport`: pyserial port enumeration and 8N1 I/O across COM, `/dev/tty*`,
  and `/dev/cu.*` names, plus exact JSONL traffic recording;
- `cli`: user-facing safety gates and durable artifacts.

No protocol or safety decision may depend on a Windows or POSIX device-name
shape. Platform-specific packaging is a thin delivery layer over the same
tested Python library. The Linux/macOS PTY virtual endpoint is an optional lab
adapter, not part of the portable protocol core.

The CLI is the authoritative, scriptable engine. A future desktop GUI should be
a thin client of the same APIs rather than a second protocol implementation.
Standalone Windows, Linux, and macOS releases should eventually let stove
owners use the tool without installing Python.

## Permanent ESP32/ESPHome controller

The permanent appliance-adjacent controller gets only the reliable everyday subset:

- read-only telemetry and faults
- current and target heat level
- start, stop, up, and down
- command acknowledgement and state verification
- Home Assistant entities

It does not replace BixCheck's calibration, Checkout, raw-write, memory-format, or firmware-flash functions.

The current two-board hardware candidate and its unresolved validation gates are
documented in [Candidate permanent-controller hardware](hardware/permanent-controller-candidate.md).

## Failure model

The factory stove controller owns combustion and appliance safety. OpenMaxFire observes and requests actions.

- Loss of Home Assistant must not disable the stove.
- Loss of Wi-Fi, MQTT, or Ethernet must not disable the stove.
- Loss or removal of the ESP32 must not disable the front panel and must transfer the thermostat input to the physical backup thermostat path.
- A stale or ambiguous connection must block new remote commands.
- A transmitted command is not successful until the resulting stove state is read back.
- Firmware/configuration writes are never part of ordinary automation.

For whole-house coordination, the pellet stove and backup heat source retain independent thermostat behavior. If automation disappears, both may temporarily call for heat, but neither is made dependent on the other for basic operation.
