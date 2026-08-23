"""Profile-specific fault and panel-indicator decoding.

Firmware 2.02/data format 04 exposes the eight flashing problem indicators as
an instantaneous ``T08`` bitmap.  A zero sample can therefore mean either
"nothing is flashing" or merely "the lamps are in the dark half of their
flash cycle".  Temporal retention belongs in :mod:`openmaxfire.monitor`; this
module only decodes an already accumulated indicator mask.
"""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping


# The live feeder-wheel capture contained a maximum 6.14-second interval
# between T08=80 samples.  Eight seconds provides margin while still clearing
# promptly after sustained zero samples.
FORMAT04_INDICATOR_HOLD_SECONDS = 8.0


@dataclass(frozen=True, slots=True)
class FaultIndicatorPattern:
    """One owner-manual flashing-light pattern."""

    mask: int
    lights: tuple[int, ...]
    code: str
    label: str
    evidence: str


@dataclass(frozen=True, slots=True)
class FaultIndication:
    """Decoded result for one accumulated format-04 indicator mask."""

    mask: int
    lights: tuple[int, ...]
    code: str | None
    label: str | None
    evidence: str
    recognized: bool


def indicator_lights(mask: int) -> tuple[int, ...]:
    """Return one-based panel-light numbers represented by an eight-bit mask."""

    if not isinstance(mask, int) or isinstance(mask, bool) or not 0 <= mask <= 0xFF:
        raise ValueError("indicator mask must be an integer from 0x00 through 0xFF")
    return tuple(index + 1 for index in range(8) if mask & (1 << index))


_LIVE = "live-confirmed on firmware 2.02/data format 04"
_DOCUMENTED = "factory-documented light pattern; serial mask inferred"


FORMAT04_FAULT_PATTERNS: Mapping[int, FaultIndicatorPattern] = MappingProxyType(
    {
        0x01: FaultIndicatorPattern(
            0x01,
            (1,),
            "power_interruption",
            "Power interruption during operation",
            _DOCUMENTED,
        ),
        0x02: FaultIndicatorPattern(
            0x02,
            (2,),
            "operating_temperature_not_reached",
            "Operating temperature not reached",
            _DOCUMENTED,
        ),
        0x04: FaultIndicatorPattern(
            0x04,
            (3,),
            "exhaust_or_hopper_overtemperature",
            "Exhaust system or hopper area overheating",
            _DOCUMENTED,
        ),
        0x06: FaultIndicatorPattern(
            0x06,
            (2, 3),
            "empty_hopper_or_possible_blocked_flue",
            "Empty hopper or possible blocked flue",
            _DOCUMENTED,
        ),
        0x08: FaultIndicatorPattern(
            0x08,
            (4,),
            "firebox_door_open",
            "Firebox door open",
            _LIVE,
        ),
        0x10: FaultIndicatorPattern(
            0x10,
            (5,),
            "ash_drawer_open",
            "Ash drawer open",
            _LIVE,
        ),
        0x20: FaultIndicatorPattern(
            0x20,
            (6,),
            "exhaust_fan_failure",
            "Exhaust-fan failure",
            _DOCUMENTED,
        ),
        0x40: FaultIndicatorPattern(
            0x40,
            (7,),
            "firepot_mechanical_malfunction",
            "Fire-pot mechanical malfunction",
            _DOCUMENTED,
        ),
        0x41: FaultIndicatorPattern(
            0x41,
            (1, 7),
            "left_igniter_failure",
            "Left igniter failure",
            _DOCUMENTED,
        ),
        0x42: FaultIndicatorPattern(
            0x42,
            (2, 7),
            "right_igniter_failure",
            "Right igniter failure",
            _DOCUMENTED,
        ),
        0x43: FaultIndicatorPattern(
            0x43,
            (1, 2, 7),
            "both_igniters_failed",
            "Both igniters failed",
            _DOCUMENTED,
        ),
        0x47: FaultIndicatorPattern(
            0x47,
            (1, 2, 3, 7),
            "internal_or_igniter_electrical_fault",
            "Internal error or possible igniter electrical fault",
            _DOCUMENTED,
        ),
        0x80: FaultIndicatorPattern(
            0x80,
            (8,),
            "feeder_wheel_failure",
            "Feeder-wheel failure",
            _LIVE,
        ),
    }
)


def decode_format04_indicator_mask(mask: int) -> FaultIndication:
    """Decode one accumulated format-04 flashing-indicator mask.

    Unknown combinations remain lossless: callers still receive the raw mask
    and individual light numbers without an invented fault meaning.
    """

    lights = indicator_lights(mask)
    pattern = FORMAT04_FAULT_PATTERNS.get(mask)
    if pattern is None:
        return FaultIndication(
            mask=mask,
            lights=lights,
            code=None,
            label=None,
            evidence=(
                "no active flashing indicator"
                if mask == 0
                else "unrecognized light combination; raw mask preserved"
            ),
            recognized=mask == 0,
        )
    return FaultIndication(
        mask=mask,
        lights=pattern.lights,
        code=pattern.code,
        label=pattern.label,
        evidence=pattern.evidence,
        recognized=True,
    )
