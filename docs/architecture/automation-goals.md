# Automation goals

Long-term smart-heating objectives discussed during research include:

- automatic heat-level management
- robust operation even if Home Assistant is unavailable
- coordinated use with another heating source without making either system dependent on HA
- automatic recognition of stove operating/fuel state where telemetry allows
- automatic hopper-refill detection if a reliable observable state can be derived
- door/hopper-state detection from existing protocol if possible
- command verification rather than fire-and-forget control

The current firmware work is specifically investigating whether a door/hopper-related input is already exposed through `CR02` / `CR06`, which would avoid a firmware patch.
