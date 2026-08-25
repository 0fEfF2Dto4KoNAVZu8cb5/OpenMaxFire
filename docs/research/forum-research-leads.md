# Historical forum research leads

Survey date: 2026-08-25

This document records potentially useful leads found while reviewing public
Bixby MaxFire discussions. It is a lead register, not a collection of
established technical facts.

## Evidence boundary

A forum post directly establishes only that a particular account made a claim
at a particular time. It does not by itself establish that the claim is
technically correct, that a reported part is interchangeable, or that a file
has the version the poster assigned to it.

This document uses the following labels:

- **Forum record**: the linked public post and its wording were directly
  observed.
- **Community-reported**: a technical or historical claim made by a forum
  participant, without independent confirmation.
- **Corroborated community report**: more than one participant reported
  compatible information. This is stronger as a lead, but is still not proof.
- **Project-supported**: preserved vendor material, firmware analysis,
  photographs, emulator results, or live OpenMaxFire evidence independently
  supports at least part of the report.
- **Candidate artifact**: a named file or document that has not yet been
  recovered and authenticated.

Nothing in this document should be promoted into the established-facts table
in [`docs/STATUS.md`](../STATUS.md) without the corresponding stronger evidence.

## Survey scope and limitations

The review covered the public results returned on the survey date by the
[Hearth.com Bixby MaxFire search](https://www.hearth.com/talk/search/8920391/?q=bixby+maxfire&o=relevance),
the [Hearth.com history search for `rona`](https://www.hearth.com/talk/search/8920473/?t=post&c%5Busers%5D=rona&o=date),
and directly related public Firewood Hoarders Club material.

Accessible coverage was:

- 3 MaxFire search-result pages
- 57 unique threads
- 72 thread pages after following pagination
- all 35 accessible pages of Rona's Hearth.com history
- 1,033 Rona posts in that history
- 161 posts explicitly mentioning Bixby, MaxFire, or UBB, distributed across
  91 thread titles

These counts describe what the forum search exposed on the survey date. Deleted,
private, unindexed, edited, or inaccessible material may be missing. Search
result URLs may also be temporary.

## Highest-priority firmware lead: `81229.com`

### What the forum establishes

In February 2020, Hearth.com user `daj024` reported possessing two files named
`80315.com` and `81229.com`, a Bixby communication cable, and instructions
previously supplied by Rona. The poster called the two files versions of
BixCheck, but the `.com` filenames and known Bixby packaging make it plausible
that they were controller firmware or downloader payloads rather than the
BixCheck desktop executables.

Source: [Bixby MaxFire 115 software, post by daj024](https://www.hearth.com/talk/threads/bixby-maxfire-115-software.173235/#post-2422727)

The attached [`Bixby comms instructions.webp`](https://www.hearth.com/talk/attachments/bixby-comms-instructions-webp.256923/)
was still downloadable during the survey.

### Interpretation

- **Candidate artifact**: `81229.com` has not been recovered by OpenMaxFire.
- `80315.com` resembles the `080315` date/build identifier associated with the
  preserved 2.71 generation.
- `81229.com` plausibly represents `081229`, or 2008-12-29.
- It could be firmware 2.73, another unpreserved build, or a mislabeled or
  duplicate file. The filename alone cannot decide this.
- No second public copy of `81229.com` was located during the survey.

### Required authentication if recovered

1. Preserve the original file without renaming or modification.
2. Preserve original folder structure, timestamps, enclosing archive, and any
   accompanying email or instructions where possible.
3. Calculate cryptographic hashes.
4. Identify the file format before attempting to execute or load it.
5. Extract any firmware identity constants and compare the entire image with
   the preserved 2.06, 2.70, and 2.71 corpus.
6. Do not install it on the only working controller. Any loader test requires
   a recoverable spare controller or cloned PIC.

`daj024` is the strongest known recovery lead because the account named the
file and reported possessing it as recently as 2020.

## Firmware 2.73 existence and reported behavior

### Possession reports

- In 2015, `jawquin` reported operating a MaxFire 115 with firmware 2.73.
  [Hearth.com firmware-update thread](https://www.hearth.com/talk/threads/how-do-i-do-a-firmware-update-on-my-bixby-maxfire-115.124007/#post-1907716)
- On Firewood Hoarders Club, Rona reported possessing software versions 2.02,
  2.06, 2.70, 2.71, and 2.73, plus BixCheck and dealer manuals for the 115,
  UBB, and 120.
  [Firewood Hoarders Club Bixby thread](https://firewoodhoardersclub.com/forums/threads/bixby-maxfire.886/)

These are **corroborated community reports** that a 2.73 image existed and was
distributed. OpenMaxFire does not yet possess the image, so its bytes, identity,
compatibility, and exact behavior remain unconfirmed.

### Reported fuel-selector change

The forum history gives one concrete possible difference between 2.71 and 2.73:

- Rona reported that 2.73 allowed the physical switch to select corn or
  pellets. [Rona's 2.73 comment](https://www.hearth.com/talk/threads/nh-craigslist-harman.141599/#post-1907922)
- `jawquin` reported that the rocker switch worked on a stove described as
  running 2.73, with no computer needed.
- `Bioburner` reported that a stove with 2.71 required a connected computer to
  change between the corn and pellet configurations.

The last two reports appear in the
[firmware-update thread](https://www.hearth.com/talk/threads/how-do-i-do-a-firmware-update-on-my-bixby-maxfire-115.124007/).

Status: **corroborated community report, partially project-supported**.

OpenMaxFire static analysis independently confirms that the preserved firmware
can read the physical fuel selector at `CR02.2` and contains separate Fuel A
and Fuel B configuration paths. That supports the feasibility of the reported
behavior but does not prove how missing firmware 2.73 uses the input. See the
[firmware comparison](../reverse-engineering/firmware-comparison.md).

If 2.73 is recovered, fuel selection is a high-value first comparison target.

## Possible historical software recipients

These public handles may have received, operated, or requested software from
Rona. Inclusion here does not establish that they still possess any files.
No private identity or contact information is recorded.

| Handle | Forum evidence | Lead value |
| --- | --- | --- |
| `daj024` | Named `80315.com` and `81229.com`, reported owning a cable and Rona's instructions in 2020 | Highest-priority file lead |
| `jawquin` | Reported actively running 2.73 in 2015 | Possible installed-chip or file source |
| `Skinner` | Specifically requested 2.73 from Rona, who directed the user to continue by email | Possible recipient |
| `csloan88` | Requested diagnostic software; Rona replied that a private message was sent | Possible recipient |
| `alexismyboy` | Requested BixCheck software and manuals on both forums | Possible recipient or manual source |
| `Kpblegen` | Reported having Bixby software and a cable, plus a Model 100 and two Model 115 stoves | Software and Model 100 research lead |

The first five contacts appear in the
[firmware-update thread](https://www.hearth.com/talk/threads/how-do-i-do-a-firmware-update-on-my-bixby-maxfire-115.124007/)
or the [Firewood Hoarders Club thread](https://firewoodhoardersclub.com/forums/threads/bixby-maxfire.886/).
The Model 100 lead appears in
[`Bixby MaxFire 100`](https://www.hearth.com/talk/threads/bixby-maxfire-100.182576/).

Rona reported in December 2020 that an old computer had failed and that much
information was lost. Rona nevertheless continued posting on Hearth.com into
February 2022 and offered an extra Bixby cable in late 2021 before reporting it
sold in January 2022.
[J3 cable thread](https://www.hearth.com/talk/threads/bixby-maxfire-115-main-board-schematic-j3-port-pins-signals.184244/)

Interpretation: contacting Rona may still be useful, but historical recipients
may be equally or more likely to retain the original files.

## Exhaust fault and J10 sensor reports

Rona suggested that a running exhaust fan accompanied by light 6 could result
from the black exhaust-sensor wire not being connected to J10.
[Hearth.com firmware-update thread, 2019 response](https://www.hearth.com/talk/threads/how-do-i-do-a-firmware-update-on-my-bixby-maxfire-115.124007/#post-2393205)

Status: **community-reported, strongly project-supported in principle**.

Static analysis independently establishes that the preserved 2.06, 2.70, and
2.71 firmware generations count the J10 exhaust-sensor pulses through
`RA4/T0CKI` and return the sampled count through `CR05`. Therefore a fan can
receive power and visibly rotate while the controller still sees too few or no
sensor pulses. Possible causes include the sensor, connector, alignment,
sensing target, wiring, or board input path. See the
[firmware comparison](../reverse-engineering/firmware-comparison.md).

An old community compilation claims ten sensing blades or pulses per
revolution and recommends observing the reported RPM in BixCheck. The document
is a useful lead, but the exact ten-per-revolution statement has not been
confirmed from preserved factory documentation or physical measurement.

Source: [Corn Burner Codes](https://www.scribd.com/doc/22685305/Corn-Burner-Codes)

## Cable and J3 history

Rona described the working service cable as a USB cable containing a chip plus
a mating Bixby connector, and reported that owners often had difficulty
constructing one. The historical wording could easily be mistaken for a
proprietary protocol.

OpenMaxFire has since **live-validated** that the relevant connection is 5 V
TTL serial using an FTDI adapter with adapter VCC disconnected. The correct J3
pinout and evidence are documented in the
[J3 working specification](../protocol/j3-protocol.md).

The surviving `Bixby comms instructions` attachment remains worth preserving
for historical cable identity, wire-color, connector, and driver information,
but it must not override the corrected live wiring evidence.

## Thermocouple connector lead

Rona repeatedly reported that the stiff brown exhaust thermocouple lead can
loosen from the upper-right connector on the main board, identified in the
forum as J18. Rona also warned that a physically similar connector on the
smaller igniter board is not the correct connection.

Sources:

- [Firewood Hoarders Club Bixby thread](https://firewoodhoardersclub.com/forums/threads/bixby-maxfire.886/)
- [Bixby MaxFire 115 troubleshooting](https://www.hearth.com/talk/threads/bixby-maxfire-115-troubleshooting.155047/)

Status: **repeated community report**. The connector location and complete
electrical path should be verified photographically and by continuity or
factory documentation before being promoted to an established pinout.

## Hardware and repairability leads

The following reports may help locate replacement parts or design repairs, but
none should be treated as an approved substitution without dimensional,
electrical, temperature, material, and safety verification.

| Reported lead | Current status | Required confirmation |
| --- | --- | --- |
| Convection-fan bearings are in the 608 family | Repeated community report | Read original bearing markings; measure dimensions; verify sealing, clearance, speed, temperature, and load rating |
| A St. Croix stove uses the same exhaust fan | Single community report; no model or part number supplied | Identify exact St. Croix model and both manufacturer part numbers; compare motor, wheel, sensor target, voltage, current, RPM, airflow, temperature rating, rotation, and mounting |
| Lower-cost feeder-wheel motors may work if RPM matches | Community report | Confirm gearbox ratio, shaft, torque, duty cycle, current, rotation, mounting, and temperature rating |
| Broken cast feeder-motor mounting legs can be bridged with tubular spacers and through-bolts | Owner-reported repair | Inspect load path, alignment, clearances, electrical isolation, fastener retention, and long-term heat/vibration behavior |
| Metal igniters were offered as longer-lived ceramic-igniter replacements | Community report with historical service anecdotes | Recover exact part number and verify voltage, wattage, dimensions, thermal behavior, current sensing, insulation, and safe failure mode |

Relevant threads:

- [Convection fan bearing discussion](https://www.hearth.com/talk/threads/bixby-maxfire-115-convection-fan-issues.164383/page-2#post-2251934)
- [Feeder-wheel motor mount repair](https://www.hearth.com/talk/threads/bixby-maxfire-feeder-wheel-motor-mounts-broken-fixed.152776/)
- [Bixby MaxFire 115 software and repair discussion](https://www.hearth.com/talk/threads/bixby-maxfire-115-software.173235/)
- [Bixby MaxFire 115 troubleshooting](https://www.hearth.com/talk/threads/bixby-maxfire-115-troubleshooting.155047/)

## Model 100 and related-controller scope

The forum material indicates that the Model 100 may use a substantially
different two-motor or dual-plate ash-dump arrangement from the 110/115.
This is a **community-reported design difference** and should be confirmed with
a Model 100 manual, photographs, board numbers, wiring, and firmware before any
OpenMaxFire compatibility claim is made.

Source: [Bixby MaxFire 100](https://www.hearth.com/talk/threads/bixby-maxfire-100.182576/)

Rona also reported possessing dealer documentation for the UBB and 120. Those
manuals, plus any separate Model 100 or Model 110 manual, are useful
preservation targets even where a Model 115 manual already exists.

## Lost iBurnCorn material

The Scribd item titled `Corn Burner Codes` appears to preserve approximately
18 pages of an older Bixby/iBurnCorn or Quark community compilation. It
contains reported serial ranges, model differences, fault troubleshooting,
sensor descriptions, ash-dump notes, trim information, and links to older
resources.

Source: [Corn Burner Codes](https://www.scribd.com/doc/22685305/Corn-Burner-Codes)

This document is historically useful but remains community-authored and may
mix accurate service experience with inference or error. Each technical claim
must be checked independently. Any preservation or redistribution must also
retain the source's original rights and licensing status.

## Version-specific thermostat lead

Rona reported that newer software could be configured with a programmable
thermostat to start and stop a stove. Other recovered factory material for the
Model 115 Rev. A says that the thermostat does not start a fully off stove.

Status: **unresolved, possibly version- or configuration-specific**.

This should not be generalized into current behavior. It is a useful future
comparison test for 2.02, 2.06, 2.70, 2.71, and especially 2.73, using a
recoverable controller and a documented safe test procedure.

Source: [Hearth.com thermostat discussion](https://www.hearth.com/talk/threads/anyone-with-a-maxfire-pellet-stove.31824/#post-413992)

## Prioritized follow-up

1. Ask `daj024` specifically for the untouched `81229.com`, `80315.com`, any
   enclosing archive, original timestamps, and accompanying messages.
2. Ask `jawquin` whether the 2.73 file, original computer, cable media, or
   controller chip still exists.
3. Ask `Skinner`, `csloan88`, and `alexismyboy` whether Rona actually sent files
   and whether their original copies remain.
4. Ask `Kpblegen` for the exact software files and Model 100 documentation or
   photographs still retained.
5. Preserve the communication-instructions attachment with provenance and
   hashes, while keeping the corrected live J3 wiring authoritative.
6. Catalog the iBurnCorn-derived compilation as a secondary source and verify
   its individual claims against vendor material, code, photographs, and live
   measurements.
7. Track the unresolved hardware substitutions by exact manufacturer part
   number rather than adopting forum descriptions as compatibility claims.

The most important unresolved item from this survey is `81229.com`. It is the
only newly discovered filename that plausibly points to an unpreserved later
firmware generation, but it remains unidentified until the actual bytes are
recovered.
