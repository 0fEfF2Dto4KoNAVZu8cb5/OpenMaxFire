# BixCheck factory Checkout inventory

The vendor manual documents 37 interactive/verification tests followed by eight
automatic tests. Static extraction finds 46 data records, but the ninth
automatic record is unreachable. Checkout directly actuates appliance hardware
and must remain isolated from normal monitoring/control.

## Interactive tests

| # | Test |
| ---: | --- |
| 01 | Data communications link |
| 02 | Configuration checksum verified |
| 03 | Data format matched |
| 04 | No front-panel buttons pressed |
| 05 | Front-panel ON button |
| 06 | Front-panel OFF button |
| 07 | Front-panel UP button |
| 08 | Front-panel DOWN button |
| 09 | All front-panel LEDs on |
| 10 | All front-panel LEDs off |
| 11 | Door switch open |
| 12 | Door switch closed |
| 13 | Ash-drawer switch open |
| 14 | Ash-drawer switch closed |
| 15 | Plate motor on |
| 16 | Plate motor off |
| 17 | Plates in burn position |
| 18 | Air pump on |
| 19 | Air pump off |
| 20 | Convection/circulator fan at 25% |
| 21 | Convection/circulator fan at 50% |
| 22 | Convection/circulator fan at 75% |
| 23 | Convection/circulator fan at 100% |
| 24 | Convection/circulator fan off |
| 25 | Board thermometer plausibility |
| 26 | Fan potentiometer low |
| 27 | Fan potentiometer high |
| 28 | Fan potentiometer center detent |
| 29 | Feed potentiometer low |
| 30 | Feed potentiometer high |
| 31 | Feed potentiometer center detent |
| 32 | Thermocouple connected |
| 33 | Thermostat open; level-1 standby |
| 34 | Thermostat closed; normal operation |
| 35 | Power-inlet wiring observation |
| 36 | Fuel switch wood/Fuel B |
| 37 | Fuel switch corn/Fuel A |

## Automatic tests

| # | Test |
| ---: | --- |
| 38 | Exhaust fan full power and measured speed |
| 39 | Exhaust fan half power and measured speed |
| 40 | Exhaust fan off |
| 41 | Left/#1 igniter 4.5-minute test |
| 42 | Right/#2 igniter 4.5-minute test |
| 43 | Left/#1 igniter follow-up check |
| 44 | Right/#2 igniter follow-up check |
| 45 | Feed motor and sensor |

## Reconstructed action map

The first three interactive/verification results establish communications,
checksum, and data-format compatibility. The remaining 34-record interactive
table uses these direct serial actions (numbers are the manual/display numbers):

| Test(s) | Direct action |
| --- | --- |
| 04-08 front-panel buttons | Read `CR01`; none/ON/OFF/UP/DOWN are `00/02/01/04/08` |
| 09 LEDs on | `CW04FF` |
| 10 LEDs off | `CW0400` |
| 11-14 door/drawer switch states | Read `CR02`; door is bit 5/RD1, drawer bit 6/RD4 |
| 15 plate motor on | `CW0500` |
| 16 plate motor off | No direct write; result checks `CR02.0` (burn-drive limit switch) and `CR03.1` |
| 17 plates in burn position | No direct write; wait/observe |
| 18 air pump on | `CW0600` |
| 19 air pump off | `CW0700` |
| 20 convection level 1 | `CW0801` on old format; `CW0819` on newer format |
| 21 convection level 2 | `CW0802` / `CW0832` |
| 22 convection level 3 | `CW0803` / `CW084B` |
| 23 convection level 4 | `CW0804` / `CW0864` |
| 24 convection fan off | `CW0800` |
| 25 thermometer | Read `CR04` |
| 26-28 fan potentiometer | Read `CR09` (AN3) |
| 29-31 feed potentiometer | Read `CR0A` (AN4) |
| 33-34 thermostat | Read `CR06` bit 2 (RB4) |
| 32, 35-37 remaining inputs | No direct actuation; observe operator/input state |

The pin/register assignments above are emulator- or static-firmware-confirmed
and cross-referenced to BixCheck masks. They are not yet validated on serial
5215. The controller's shared input scanner plus its Fuel A/B configuration
bank selection establish `CR02.2`: `1` is Fuel A/corn and `0` is Fuel B/wood.
Retained BixCheck predicates agree, but the reachable 5.5 fuel-test rows omit
the machine check and rely on the operator. The preserved 9067-0404 diagram
independently labels this physical input `Fuel Switch`.

Automatic sender actions are identical across all three EXEs:

| Test | Direct action |
| ---: | --- |
| 38 | `CW0980` exhaust full |
| 39 | `CW0940` exhaust half |
| 40 | `CW0900` exhaust off |
| 41 | no direct sender write; timed igniter-1 workflow |
| 42 | `CW0D00` igniter-2 workflow |
| 43 | no direct sender write; igniter-1 follow-up |
| 44 | `CW0A00` igniter-2 follow-up |
| 45 | `CW0B20` feed motor/sensor workflow |

These commands are documentation, not a supported control surface. Several
values directly energize motors, fans, pumps, or igniters.

## Dormant record

All three EXEs contain a ninth automatic record labeled `Plate motor cycle
test`, with instruction `Testing the plate motor` and failure hint `Plate
motor`. Both `Bixby110SetupCheckoutAutomaticTests()` and the action dispatcher
iterate only indices 0-7, so index 8 is never presented or executed. The
operational count therefore remains 45, not 46.

## Report requirements

A replacement report should preserve stove identity, firmware/data format, checksums, serial number, production date, model, both fuel tables, operator identity, timestamp, every result, diagnostic hints, and an immutable configuration backup.

The complete 0x122-byte record tables and reachability flag are exported in
each version's `checkout-tests.csv`; the exact sender assembly is in
`checkout-core.asm`.
