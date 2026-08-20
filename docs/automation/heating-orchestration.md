# Heating-source orchestration

The desired whole-house behavior is automatic coordination between the MaxFire and a backup heat source while preserving independent thermostatic operation.

## Reliability rule

When Home Assistant is healthy it may decide which heat source should carry the load. If Home Assistant or any network component fails, both heating systems retain their own thermostats. They may overlap, but the house is not left without heat because of an automation failure.

## OpenMaxFire inputs needed

- fresh, timestamped stove state
- current and target heat level
- startup, running, ramping, cooling, off, and fault states
- alarm/blocked-flue/lean-fire indicators
- command acknowledgements and readback
- thermocouple trend
- preferably firebox-door and ash-drawer state after mapping

## Hopper refill problem

If the pellet stove is off or unpowered while backup heat is running, internal J3 data alone cannot reliably prove that the hopper was refilled. A door/lid event only proves access, not fuel quantity.

Options, strongest first:

1. Hopper load cells or another actual mass/level sensor.
2. A lid sensor plus measured feed use and conservative confidence rules.
3. A user confirmation helper as a fallback.

Automatic switching back to pellets should require a positive fuel-available signal, a safe stove state, successful startup acknowledgement, and evidence that the thermocouple is rising. Failure to ignite should return control to backup heat without repeated unsafe start attempts.
