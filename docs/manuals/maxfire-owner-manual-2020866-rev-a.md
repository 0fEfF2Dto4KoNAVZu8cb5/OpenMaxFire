# MaxFire owner manual 2020866 Rev. A

## Preserved source

| Property | Value |
| --- | --- |
| Repository path | `preservation/original/manuals/7346103.pdf` |
| Embedded title | `Owner Manual_115_2020866 Rev A` |
| Printed document number | `2020866 REV A` |
| Author metadata | Bixby Energy Systems |
| PDF pages | 40 (cover, contents, and 38 numbered manual pages) |
| PDF creation metadata | 2005-10-17 |
| PDF modification metadata | 2008-10-22 |
| Size | 1,595,527 bytes |
| SHA-256 | `ed04d708590fa8bec0d0276463abd736409ddbdd8d8eee6c7a66fb0cd7fba33d` |

The PDF is the factory *Installation, Operating and Maintenance Instructions*
for the MaxFire multi-fuel room heater. Its embedded title associates it with
the Model 115. The creation and modification dates above are PDF metadata, not
independently verified publication or revision dates.

This Rev. A manual predates the preserved 2.70/2.71 format-07 software. It is
strong vendor evidence for the appliance and its factory behavior, but later
firmware/configuration features must be identified separately.

## Operating behavior documented by Bixby

- Eight heat levels are selected with the front-panel UP and DOWN buttons.
- Startup normally takes 3-7 minutes; a stable flame can take up to 20 minutes.
- During shutdown the flame normally goes out in 3-10 minutes, while the
  convection and exhaust fans continue for approximately 30 minutes.
- A power interruption shorter than about 10 seconds resumes at the selected
  level. A longer interruption requires a restart and flashes indicator 1.
- The hopper holds approximately 106 lb (48 kg). The stove must be operated
  with the hopper door closed.
- The fuel selector identifies corn as Fuel A and wood pellets as Fuel B. The
  wiring diagram states brown-switch open = Fuel A and closed = Fuel B,
  independently agreeing with the firmware's `CR02.2` mapping.

## Thermostat behavior and automation boundary

The manual permits an unpowered on/off 24 V AC wall thermostat and warns not to
use a powered thermostat. It states that the thermostat does **not** start the
stove. On a heat call, an already-running stove operates at its selected level;
without a call it drops to level 1 and the panel indicators slowly flash
together.

OpenMaxFire therefore must not treat the factory wall thermostat as a complete
independent restart fallback. Format-07 BixCheck data includes later thermostat
heat-level and auto-restart configuration fields, so the exact behavior of
firmware 2.70/2.71 and serial 5215 must be verified before automation relies on
it.

## Door, drawer, and fault behavior

| Indicator | Factory description |
| --- | --- |
| 1 | Power interruption |
| 2 | Operating temperature not reached |
| 3 | Exhaust or hopper overheating |
| 2 + 3 | Empty hopper or possible blocked flue |
| 4 | Firebox door open; more than about one minute causes shutdown |
| 5 | Ash drawer open; prevents startup and more than about 20 minutes causes shutdown |
| 6 | Exhaust-fan failure |
| 7 | Fire-pot mechanical malfunction |
| 7 + 1 | Left igniter failed |
| 7 + 2 | Right igniter failed |
| 7 + 1 + 2 | Both igniters failed; automatic start is unavailable |
| 7 + 1 through 3 | Internal or possible igniter electrical fault |
| 8 | Feeder-wheel failure |

The ash drawer must be fully latched. Opening it disables the automatic ash
dump. These factory interlocks remain authoritative; remote software must
observe them and must never bypass them.

## Maintenance schedule

| Component/task | Factory interval or trigger |
| --- | --- |
| Ash drawer | Check every few days; typically empty after 100-200 lb (one or two hoppers) |
| Fire-pot sidewalls and holes | Monthly; keep combustion holes clear |
| Heat-exchanger tubes | Operate cleaning levers and vacuum as needed |
| Vent system | Inspect at least annually |
| Exhaust fan and manifold | Annually |
| Hopper, feeder tube, and lower paddle holes | Monthly |
| Ignition-air compressor filter | Inspect annually |
| Room-air filter | Check monthly; replace every two to three months |

The manual requires the stove to be cool and disconnected from power before
maintenance. Installation, venting, clearances, combustion-air requirements,
and service procedures should be taken directly from the preserved manual and
applicable local codes rather than abbreviated project notes.

## Wiring and protocol corroboration

The factory wiring diagram on numbered page 31 independently confirms the
computer connector `J3`, control panel `J7`, trim controls `J8`, feeder and
exhaust sensors, thermocouple `J18`, external thermostat, door/drawer/fuel/
burner-limit switches, fans, motors, igniters, air compressor, and hopper
over-temperature safety switch.

It does **not** label J3 pin functions, voltages, polarity, or electrical
standard, so it does not make a direct USB-UART or RS-232 connection safe. It
also shows no hopper-level or hopper-lid sensor, supporting the conclusion that
fuel availability cannot be proved from J3 telemetry alone.

The manual corroborates these existing offline mappings without replacing live
validation:

- firebox door: `CR02.5` / RD1;
- ash drawer: `CR02.6` / RD4;
- thermostat: `CR06.2` / RB4;
- fuel selector: `CR02.2`, Fuel A/corn when set and Fuel B/wood when clear;
- J9 feeder-wheel sensor and J10 exhaust-fan sensor roles.

## Service-parts anchors

The manual's service list identifies the following useful reference numbers:

- `4000080` igniter;
- `4000121` air pump;
- `4000113` burner-drive motor assembly;
- `4000006` feeder wheel;
- `4000098` feeder-wheel motor assembly;
- `4000014` convection-fan capacitor;
- `4000048` air filter;
- `4000072` control pad;
- `4000064` main control board;
- `4000105` exhaust fan;
- `4000056` exhaust-fan gasket;
- `4000353` burner top plate; and
- `4000361` feeder-wheel sensor.

Recovered vendor material retains its original rights and is not relicensed by
OpenMaxFire.
