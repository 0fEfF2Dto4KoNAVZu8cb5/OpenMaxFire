# BixCheck manual notes

Source reviewed: **BixCheck How-To Guide — Model 110 and Model 115**, document 2023480 Rev. A, dated 2007-05-08, covering BixCheck 5.x behavior.

## Confirmed capabilities from the guide

- custom Bixby PC interface cable P/N 2013324
- serial-port selection and communication reset guidance
- Monitor interface
- Fuel A / Fuel B calibration windows
- flue monitor
- telemetry
- configuration/readback and checksum validation
- individual calibration writes
- individualization and formatting workflows
- runtime data logging
- interactive/automatic checkout tests
- separate Downloader process for stove operational software

The guide states that the downloader uses a `_Downloader.hex` image and that the updater itself remains recoverable if a transfer is interrupted, allowing another programming attempt.

## Archival note

The original PDF was supplied during research but is not duplicated here in this bootstrap because the connector exposed document text rather than raw file bytes in the current session. Preserve the original PDF in `research/original-documents/` when its file bytes are available, along with SHA-256 and provenance.
