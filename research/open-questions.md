# Open questions

1. Which `CR02` / `CR06` bit corresponds to the firebox door, hopper switch, fuel switch, or other physical interlocks?
2. What is the verified J3 pinout and voltage level on the specific stove board?
3. Is the controller oscillator physically 20 MHz, confirming 38400 baud from the UART divisor?
4. What are the full semantics of `CR00` onward beyond the currently mapped static handlers?
5. What is the complete `CW` dispatch table and which writes correspond to BixCheck controls/calibration fields?
6. Which BixCheck telemetry fields map to which CR reads/internal RAM values?
7. Can hopper refill be inferred reliably from existing telemetry without adding a sensor?
8. Does any firmware revision expose door state explicitly under a different read register?
9. What exact bootloader/downloader protocol is used for firmware flashing?
10. Which firmware images are embedded inside surviving BixCheck executables, and can all versions be extracted and hashed?
