# Documentation index

This directory contains interpreted OpenMaxFire documentation. Original vendor
files remain under `preservation/original/`; raw live evidence remains under
`research/live/`; generated disassemblies and tables remain under
`reverse-engineering/`.

## Start here

| Document | Purpose |
| --- | --- |
| [Research status](STATUS.md) | Established facts, evidence levels, unresolved questions, and current safety boundary |
| [Project roadmap](ROADMAP.md) | Preservation, bench validation, software, firmware, and permanent-controller work |
| [Research log](RESEARCH_LOG.md) | Chronological record of findings and implementation milestones |
| [Safety policy](../SAFETY.md) | Non-negotiable electrical, combustion, actuator, and firmware boundaries |

## Historical research and recovery leads

| Document | Purpose |
| --- | --- |
| [Forum research leads](research/forum-research-leads.md) | Candidate firmware, possible historical recipients, repair reports, lost community documentation, confidence labels, and required verification |

## Software architecture

| Area | Entry point |
| --- | --- |
| Reusable Python API | [API architecture and roadmap](api/README.md) |
| Current API milestone | [v0.7 audit and loader laboratory](api/v0.7-audit-loader-lab.md) |
| Fault-state API | [Fault model](api/fault-model.md) |
| Cross-platform CLI | [Service-tool guide](cli/cross-platform-service-tool.md) |
| Low-level CLI layer | [Low-level service layer](cli/low-level-service-layer.md) |

The API, CLI, future GUI, and future Home Assistant integration are separate
layers. Controller semantics and safety rules belong in the API.

## Protocol and live controller

| Topic | Entry point |
| --- | --- |
| J3 working specification | [J3 protocol](protocol/j3-protocol.md) |
| Quick register reference | [Serial command cheat sheet](protocol/serial-command-cheat-sheet.md) |
| Controller writes | [Controller write map](protocol/controller-writes.md) |
| Telemetry | [Telemetry fields](protocol/telemetry-fields.md) |
| Faults and flashing indicators | [Fault protocol](protocol/faults.md) |
| Firmware 2.02 live session | [Live format-04 report](reverse-engineering/live-fw202-format04.md) |
| Guided physical validation | [Live-validation session](research/live-validation-session.md) |

## Static analysis and hardware

| Topic | Entry point |
| --- | --- |
| BixCheck generations | [BixCheck comparison](reverse-engineering/bixcheck-comparison.md) |
| BixCheck workflows | [Runtime workflows](reverse-engineering/bixcheck-runtime-workflows.md) |
| Firmware generations | [Firmware comparison](reverse-engineering/firmware-comparison.md) |
| Firmware loader | [Downloader protocol](reverse-engineering/bixcheck-downloader-protocol.md) |
| PIC emulation | [Exhaustive emulator pass](reverse-engineering/emulator-deep-pass.md) |
| Operating states | [Operating-state machine](reverse-engineering/operating-state-machine.md) |
| Bare controller | [Bare-controller photographs](hardware/bare-controller-photographs.md) |
| Permanent interface | [Candidate hardware](hardware/permanent-controller-candidate.md) and [daughterboard design](hardware/daughterboard-preliminary-design.md) |
| Owner manual | [Model 115 manual analysis](manuals/maxfire-owner-manual-2020866-rev-a.md) |

Machine-readable register evidence is indexed separately under
[`protocol/`](../protocol/README.md).
