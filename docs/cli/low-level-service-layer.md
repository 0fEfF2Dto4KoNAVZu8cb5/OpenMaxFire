# Low-level service layer

Snapshot date: 2026-08-23

OpenMaxFire 0.4 provides the first complete register-level foundation beneath
future Monitor, Checkout, configuration, and GUI workflows. These primitives
are offline-tested. No A/C/D write, actuator action, or firmware-loader
operation has been validated on the physical production controller.

## Capability boundary

| Primitive | Python API | CLI | Evidence and boundary |
| --- | --- | --- | --- |
| A/C/D read | `query_register()` | `read --unit A/C/D` | C and A reads live-validated; D framing static only |
| Send-only A/C/D read | `read_register()` | — | Offline-tested transport primitive |
| Send-only A/C/D write | `write_register()` | `write --unit A/C/D` | Offline-tested; transmission is never reported as success |
| Write plus fresh readback | `write_register_verified()` | `write --verify` | Offline-tested; verifies only the addressed byte |
| Exact-byte exchange | `exchange_raw()` | `raw` | Response is uninterpreted; known loader traffic is blocked |
| Ordered register plan | `execute_transaction()` | `transaction` | Validated, fail-fast, optional per-write readback |
| Controller/EEPROM backup | `identify()` / `read_eeprom()` | `backup` | Live-validated read-only workflow |
| Firmware-loader state machine | — | — | Not implemented; isolated from generic traffic |
| PIC program-memory dump | — | — | No J3 read command has been discovered |

The same serial transport can carry all currently known BixCheck traffic, but
the ASCII register protocol and the firmware loader are different state
machines. A generic byte sender is not a safe substitute for a downloader.

## Generic register reads

All three reconstructed addressed units can be selected:

```bash
maxfirectl \
  --port /dev/ttyUSB0 \
  --baud 9600 \
  read 0x02 \
  --unit C \
  --i-understand-unverified-io
```

Use `--unit A` for internal EEPROM and `--unit D` only for research. Host-side
D-space meanings remain unresolved even though the framing is implemented.

## Generic register writes

The live command requires both acknowledgement flags:

```bash
maxfirectl \
  --port /dev/ttyUSB0 \
  --baud 9600 \
  write 0x6B 0x40 \
  --unit A \
  --verify \
  --settle-delay 0.10 \
  --i-understand-unverified-io \
  --i-understand-this-can-change-stove-state
```

Without `--verify`, the tool reports only that the six request bytes were
transmitted. With `--verify`, it sends a fresh read request for the same unit
and address and compares the returned byte. The response matcher requires an
actual `R` frame, so a possible `W` echo cannot be mistaken for readback.

Matching readback proves only that one byte reads as requested. It does not
prove that a motor moved, an igniter energized, a calibration is safe, or a
command-style C register produced the intended physical action.

## Exact-byte raw exchange

Raw mode appends no terminator and assigns no meaning to received bytes:

```bash
maxfirectl \
  --port /dev/ttyUSB0 \
  --baud 9600 \
  raw --hex "43 52 30 30" \
  --read-for 1.0 \
  --json \
  --i-understand-unverified-io \
  --i-understand-this-can-change-stove-state
```

`--ascii CR00` produces the same four transmitted bytes. Known loader markers
(`CW0FC4`, `EA`, `E3`, and `ED`) are refused before the serial port is opened.
They belong in a future loader implementation with image checks, expected
acknowledgements, bounded retries, and recovery behavior.

## Transaction plans

Transactions make multi-step research reproducible without embedding serial
logic in shell scripts. A plan contains only `read`, `write`, and `delay`
operations:

```json
{
  "schema": "openmaxfire.transaction.v1",
  "description": "example offline plan",
  "operations": [
    {"op": "read", "unit": "C", "address": "0x02"},
    {"op": "delay", "seconds": 0.25},
    {
      "op": "write",
      "unit": "A",
      "address": "0x6B",
      "value": "0x40",
      "verify": true,
      "settle_delay": 0.10
    }
  ]
}
```

Validate and canonicalize a plan without opening a serial port:

```bash
maxfirectl transaction examples/read-only-register-plan.json --dry-run
```

Live execution requires `--port`, `--baud`, and the normal live-I/O
acknowledgement. A plan containing a write additionally requires
`--i-understand-this-can-change-stove-state`. Execution stops immediately when
a requested readback does not match. `CW0FC4` is rejected during plan loading.
Exact TX/RX traffic can be preserved with the global `--traffic-log` option.

## What this enables

Once the remaining register meanings and safe sequences are verified, the
high-level features can all call this layer rather than implementing their own
serial behavior:

- Monitor and diagnostics: named reads and telemetry subscriptions.
- Normal control: guarded commands followed by state readback.
- Configuration: diff, backup, ordered writes, checksum, and full verification.
- Checkout: bounded test transactions with operator confirmation and automatic
  actuator-off cleanup.
- GUI: the same API and transaction receipts presented as buttons and reports.

## Work still required

1. Live-validate one deliberately selected, reversible write on suitable
   hardware and preserve its complete traffic/readback record.
2. Determine which C writes are readable state, command latches, timed actions,
   or actuator controls; same-address readback is not universally meaningful.
3. Resolve D-space host semantics and remaining format-04 telemetry fields.
4. Build EEPROM diff/restore above transactions with controller/data-format
   compatibility, checksum ordering, pre-write backup, and final verification.
5. Build Checkout profiles with actuator timeouts, cleanup, interlocks, and
   durable reports.
6. Implement the loader separately: image parsing, compatibility checks,
   identify, erase/program acknowledgements, retry limits, interrupted-transfer
   recovery, and post-flash verification.
7. Validate recovery on a spare controller before loader entry or firmware
   programming is allowed on a production stove.

The generic layer therefore closes the software-mechanics gap for register
traffic. It does not close the protocol-meaning, physical-safety, or firmware-
recovery gaps.
