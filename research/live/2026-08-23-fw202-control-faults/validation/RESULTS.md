# OpenMaxFire live validation report

- Started: `2026-08-23T22:03:57.617249+00:00`
- Completed: `2026-08-23T22:07:05.248199+00:00`
- Mode: `physical`
- Firmware: `2.02`
- Profile: `fw202-format04`
- Audit SHA-256: `51f293c586823a233d0d44b68331623dbfa6b4d0da0640d5ef11639b119089a2`

## Results

| Test | Status | Message |
| --- | --- | --- |
| Repeated controller identity | **pass** | all identity reads matched |
| Cold Baseline cycle 1 | **pass** | complete CR00-CR0E typed snapshot |
| Complete EEPROM backup and integrity | **skipped** | --skip-eeprom was supplied |
| Guided physical-input correlation | **skipped** | --skip-interactive-inputs was supplied |
| Remote OFF while already cold/off | **skipped** | a no-op OFF while already off cannot prove command acceptance |
| Remote ON/start and OFF recovery | **indeterminate** | operator-observed startup and recovery; exact traffic preserved |
| Remote UP while running | **pass** | operator observation retained; post-command snapshot captured |
| Remote DOWN and level restoration while running | **pass** | operator observation retained; post-command snapshot was unavailable |

## Evidence boundary

This session does not authorize configuration writes, factory Checkout actuators,
raw commands, or firmware-loader traffic. A transmitted command is not reported as
accepted without a corresponding controller or operator observation.
