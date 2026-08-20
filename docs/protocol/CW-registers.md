# CW register map

The `CWxxYY` write grammar is confirmed, but a complete semantic map is not yet established.

## Policy

Do not fuzz unknown write addresses on a live stove. Writes can change calibration, configuration, outputs, state, or service settings.

## Next static-analysis task

Trace each write-dispatch comparison in the parser, document the destination RAM/SFR/action, then correlate known BixCheck controls with those handlers.
