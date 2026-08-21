# Heating-source orchestration

The desired whole-house behavior is automatic coordination between the MaxFire and a backup heat source while preserving independent thermostatic operation.

## Reliability rule

When Home Assistant is healthy it may decide which heat source should carry the load. The backup system retains its own thermostat. The MaxFire's factory thermostat input must not be assumed to provide equivalent automatic restart: document 2020866 Rev. A says it does not start the stove and only changes an already-running stove between the selected level and level 1. Later format-07 configuration includes thermostat heat-level and auto-restart fields, but serial 5215's exact behavior has not been live-validated. A failed automation must therefore leave the backup heat independently available and the stove in a safe factory-controlled state.

## OpenMaxFire inputs needed

- fresh, timestamped stove state
- current and target heat level
- startup, running, ramping, cooling, off, and fault states
- alarm/blocked-flue/lean-fire indicators
- command acknowledgements and readback
- thermocouple trend
- firebox-door and ash-drawer state; remote start must be blocked while either is open

## Hopper refill problem

If the pellet stove is off or unpowered while backup heat is running, internal J3 data alone cannot reliably prove that the hopper was refilled. The factory owner-manual wiring diagram shows a hopper over-temperature switch but no hopper-level or hopper-lid sensor. A separately added lid event would prove access, not fuel quantity.

Options, strongest first:

1. Hopper load cells or another actual mass/level sensor.
2. A lid sensor plus measured feed use and conservative confidence rules.
3. A user confirmation helper as a fallback.

Automatic switching back to pellets should require a positive fuel-available signal, a safe stove state, successful startup acknowledgement, and evidence that the thermocouple is rising. Failure to ignite should return control to backup heat without repeated unsafe start attempts.
