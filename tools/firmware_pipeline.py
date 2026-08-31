#!/usr/bin/env python3
"""Reproducible extraction and static analysis for preserved Bixby firmware.

The tool intentionally uses only the Python standard library.  It validates
Intel HEX checksums, understands sparse PIC16F877A memory, extracts the ASCII-
hex encoded payload used by later BixCheck executables, and emits a conservative
PIC14 disassembly.  It never communicates with or writes to a stove.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import sys
import zipfile
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


HEX_DIGITS = frozenset(b"0123456789abcdefABCDEF")
PRINTABLE = frozenset(range(0x20, 0x7F))


class FirmwareError(ValueError):
    """A malformed or unexpected preserved artifact."""


@dataclass(frozen=True)
class IHexImage:
    memory: dict[int, int]
    record_counts: Counter[int]
    comments: tuple[str, ...]
    start_segment: int | None = None
    start_linear: int | None = None

    @property
    def words(self) -> dict[int, int]:
        result: dict[int, int] = {}
        for byte_address in sorted(self.memory):
            if byte_address & 1:
                continue
            if byte_address + 1 not in self.memory:
                raise FirmwareError(
                    f"orphan byte at 0x{byte_address:08X}; PIC word is incomplete"
                )
            result[byte_address // 2] = (
                self.memory[byte_address]
                | (self.memory[byte_address + 1] << 8)
            )
        return result


@dataclass(frozen=True)
class Instruction:
    mnemonic: str
    operands: str = ""
    kind: str = "instruction"
    target: int | None = None


@dataclass(frozen=True)
class ImageSpec:
    version: str
    variant: str
    filename: str
    extracted_path: str
    analysis_dir: str
    disassembly_dir: str
    source_description: str


IMAGE_SPECS = (
    ImageSpec(
        "2.02",
        "pickit",
        "Bixby_0202_260827_PICkit.hex",
        "reverse-engineering/firmware/2.02/extracted/Bixby_0202_260827_PICkit.hex",
        "reverse-engineering/firmware/2.02/analysis",
        "reverse-engineering/firmware/2.02/disassembly",
        "owner-supplied PICkit read of the original firmware-2.02 controller",
    ),
    ImageSpec(
        "2.06",
        "downloader",
        "Bixby_02060021_Downloader.hex",
        "reverse-engineering/firmware/2.06/extracted/Bixby_02060021_Downloader.hex",
        "reverse-engineering/firmware/2.06/analysis/downloader",
        "reverse-engineering/firmware/2.06/disassembly",
        "Bixby 1.10/1.15 firmware 02.06.00.21 vendor package (Downloader image)",
    ),
    ImageSpec(
        "2.06",
        "pickit",
        "Bixby_02060021_PICkit.hex",
        "reverse-engineering/firmware/2.06/extracted/Bixby_02060021_PICkit.hex",
        "reverse-engineering/firmware/2.06/analysis/pickit",
        "reverse-engineering/firmware/2.06/disassembly",
        "Bixby 1.10/1.15 firmware 02.06.00.21 vendor package (PICkit image)",
    ),
    ImageSpec(
        "2.70",
        "embedded",
        "Bixby_0270_070206.hex",
        "reverse-engineering/firmware/2.70/extracted/Bixby_0270_070206.hex",
        "reverse-engineering/firmware/2.70/analysis",
        "reverse-engineering/firmware/2.70/disassembly",
        "payload embedded in preserved BixCheck_080206.exe",
    ),
    ImageSpec(
        "2.71",
        "embedded",
        "Bixby_0271_080315.hex",
        "reverse-engineering/firmware/2.71/extracted/Bixby_0271_080315.hex",
        "reverse-engineering/firmware/2.71/analysis/portable",
        "reverse-engineering/firmware/2.71/disassembly",
        "payload embedded in preserved BixCheck_080315.exe",
    ),
)


KNOWN_ANNOTATIONS: dict[str, dict[int, str]] = {
    "2.02": {
        0x0000: "Reset vector; redirects through the resident serial loader at 0x1E88.",
        0x0004: "Application interrupt vector; saves context before source dispatch.",
        0x00FA: "UART receive interrupt routine.",
        0x0EDA: "Read next byte from the command receive buffer.",
        0x0F13: "Decode one uppercase ASCII hexadecimal nibble.",
        0x0F2F: "Decode two ASCII hexadecimal characters into one byte.",
        0x1073: "Controller parser checks first command byte for ASCII 'C'.",
        0x107F: "Controller parser checks second command byte for ASCII 'W'.",
        0x115F: "Controller parser compares second command byte with ASCII 'R'.",
        0x12B7: "Format a controller response as ASCII hexadecimal.",
        0x12E5: "CW00-CW0E computed write-dispatch table; format 04 has no CW0F entry.",
        0x12FB: "CR00-CR0C computed read-dispatch table; CR0D/CR0E use the generic zero response.",
        0x1800: "Application startup and peripheral initialization.",
        0x1809: "UART initialization; SPBRG is loaded with 0x40.",
        0x1E80: "Resident-loader protected reset-trampoline region begins.",
        0x1E84: "Relocated application reset vector written by the serial loader.",
        0x1E88: "Resident serial-loader entry; byte-identical to the preserved 2.06 PICkit loader.",
    },
    "2.06": {
        0x0000: "Reset vector; Downloader enters the application, PICkit image redirects through its bootloader.",
        0x0004: "Interrupt vector; saves context before source dispatch.",
        0x00C6: "UART receive interrupt routine (signature match; medium confidence).",
        0x0134: "Front-panel button multiplexer scan: RD2 selects the active-low button bank, RD6:RD5 address OFF/ON/UP/DOWN, and RD3 is the shared return.",
        0x03FF: "Fuel-select input chooses the EEPROM calibration bank; a clear CR02.2 adds 0x30 to select Fuel B.",
        0x079C: "Second 2.06 fuel-table read path; a clear CR02.2 adds the same 0x30 Fuel-B offset.",
        0x086A: "Non-periodic T20 display-LED event path; live 2.06 traffic alternates values with a flashing panel light.",
        0x0F03: "External sensor multiplexer scan: RD7 selects the bank, RD6:RD5 address three active-high RD3 inputs, and results become CR02 bits 0-2.",
        0x0E71: "Read next byte from the command receive buffer.",
        0x0EA4: "Decode one uppercase ASCII hexadecimal nibble.",
        0x0EC0: "Decode two ASCII hexadecimal characters into one byte.",
        0x1008: "Controller parser checks first command byte for ASCII 'C'.",
        0x1014: "Controller parser checks second command byte for ASCII 'W'.",
        0x113F: "Controller parser compares second command byte with ASCII 'R'.",
        0x1145: "Parse CR register number.",
        0x1152: "Branch into low CR-register dispatch.",
        0x115A: "CR02 handler.",
        0x118C: "CR03 handler.",
        0x11AD: "CR06 handler.",
        0x1265: "Format a controller response as ASCII hexadecimal.",
        0x12A7: "CR00-CR0E computed dispatch table.",
        0x1800: "Application startup and peripheral initialization.",
        0x1804: "UART initialization; SPBRG is loaded with 0x40 in this generation.",
        0x1879: "Receiver recovery/re-enable path.",
        0x1E27: "PICkit-only service/bootloader region begins immediately after the Downloader image ends.",
        0x1E88: "PICkit reset target and serial bootloader entry path.",
    },
    "2.70": {
        0x0000: "Reset vector; enters application startup at 0x1800.",
        0x0004: "Interrupt vector; saves context before source dispatch.",
        0x00AE: "UART receive interrupt routine.",
        0x0118: "Front-panel button multiplexer scan: RD2 selects the active-low button bank, RD6:RD5 address OFF/ON/UP/DOWN, and RD3 is the shared return.",
        0x03D0: "Fuel-select input chooses the EEPROM calibration bank; a clear CR02.2 adds 0x30 to select Fuel B.",
        0x07E2: "Non-periodic T20 display-LED event path.",
        0x1004: "External sensor multiplexer scan: RD7 selects the bank, RD6:RD5 address three active-high RD3 inputs, and results become CR02 bits 0-2.",
        0x0F63: "Read next byte from the command receive buffer.",
        0x0F95: "Decode one uppercase ASCII hexadecimal nibble.",
        0x0FB1: "Decode two ASCII hexadecimal characters into one byte.",
        0x1112: "Controller parser checks first command byte for ASCII 'C'.",
        0x111E: "Controller parser checks second command byte for ASCII 'W'.",
        0x1234: "Controller parser compares second command byte with ASCII 'R'.",
        0x123A: "Parse CR register number.",
        0x1247: "Branch into low CR-register dispatch.",
        0x124F: "CR02 handler.",
        0x127D: "CR03 handler.",
        0x129E: "CR06 handler.",
        0x1352: "Format a controller response as ASCII hexadecimal.",
        0x1391: "CR00-CR0E computed dispatch table.",
        0x1800: "Application startup and peripheral initialization.",
        0x1804: "UART initialization; SPBRG is loaded with 0x20.",
        0x1872: "Receiver recovery/re-enable path.",
    },
    "2.71": {
        0x0000: "Reset vector; loads PCLATH and enters application startup at 0x1825.",
        0x0004: "Interrupt vector; saves context before source dispatch.",
        0x00AE: "UART receive interrupt routine.",
        0x0118: "Front-panel button multiplexer scan: RD2 selects the active-low button bank, RD6:RD5 address OFF/ON/UP/DOWN, and RD3 is the shared return.",
        0x03D0: "Fuel-select input chooses the EEPROM calibration bank; a clear CR02.2 adds 0x30 to select Fuel B.",
        0x07E2: "Non-periodic T20 display-LED event path.",
        0x0FBF: "External sensor multiplexer scan: RD7 selects the bank, RD6:RD5 address three active-high RD3 inputs, and results become CR02 bits 0-2.",
        0x0F2E: "Read next byte from the command receive buffer.",
        0x0F60: "Decode one uppercase ASCII hexadecimal nibble.",
        0x0F7C: "Decode two ASCII hexadecimal characters into one byte.",
        0x10E8: "Controller parser checks first command byte for ASCII 'C'.",
        0x10F4: "Controller parser checks second command byte for ASCII 'W'.",
        0x120E: "Controller parser compares second command byte with ASCII 'R'.",
        0x1214: "Parse CR register number.",
        0x1221: "Branch into low CR-register dispatch.",
        0x1229: "CR02 handler.",
        0x125B: "CR03 handler.",
        0x127C: "CR06 handler.",
        0x132F: "Format a controller response as ASCII hexadecimal.",
        0x136E: "CR00-CR0E computed dispatch table.",
        0x1825: "Application startup and peripheral initialization.",
        0x1829: "UART initialization; SPBRG is loaded with 0x20.",
        0x1897: "Receiver recovery/re-enable path.",
    },
}


ANCHORS = (
    ("reset_vector", {"2.02": 0x0000, "2.06": 0x0000, "2.70": 0x0000, "2.71": 0x0000}),
    ("interrupt_vector", {"2.02": 0x0004, "2.06": 0x0004, "2.70": 0x0004, "2.71": 0x0004}),
    ("uart_rx_isr", {"2.02": 0x00FA, "2.06": 0x00C6, "2.70": 0x00AE, "2.71": 0x00AE}),
    ("command_buffer_get_char", {"2.02": 0x0EDA, "2.06": 0x0E71, "2.70": 0x0F63, "2.71": 0x0F2E}),
    ("ascii_hex_nibble", {"2.02": 0x0F13, "2.06": 0x0EA4, "2.70": 0x0F95, "2.71": 0x0F60}),
    ("ascii_hex_byte", {"2.02": 0x0F2F, "2.06": 0x0EC0, "2.70": 0x0FB1, "2.71": 0x0F7C}),
    ("command_C_check", {"2.02": 0x1073, "2.06": 0x1008, "2.70": 0x1112, "2.71": 0x10E8}),
    ("command_W_check", {"2.02": 0x107F, "2.06": 0x1014, "2.70": 0x111E, "2.71": 0x10F4}),
    ("command_R_check", {"2.02": 0x115F, "2.06": 0x113F, "2.70": 0x1234, "2.71": 0x120E}),
    ("CR_dispatch", {"2.02": 0x12FB, "2.06": 0x12A7, "2.70": 0x1391, "2.71": 0x136E}),
    ("response_formatter", {"2.02": 0x12B7, "2.06": 0x1265, "2.70": 0x1352, "2.71": 0x132F}),
    ("application_startup", {"2.02": 0x1800, "2.06": 0x1800, "2.70": 0x1800, "2.71": 0x1825}),
    ("uart_initialization", {"2.02": 0x1809, "2.06": 0x1804, "2.70": 0x1804, "2.71": 0x1829}),
)


EVENT_T20_PATHS = {
    "2.06": {
        "entry": 0x086A,
        "sender": 0x0783,
        "sequence": (
            0x3020, 0x00D6, 0x1283, 0x0848, 0x1683,
            0x00D7, 0x118A, 0x1283, 0x2783,
        ),
    },
    "2.70": {
        "entry": 0x07E2,
        "sender": 0x0771,
        "sequence": (
            0x3020, 0x00D4, 0x1283, 0x0848,
            0x1683, 0x00D5, 0x1283, 0x2771,
        ),
    },
    "2.71": {
        "entry": 0x07E2,
        "sender": 0x0771,
        "sequence": (
            0x3020, 0x00D4, 0x1283, 0x0848,
            0x1683, 0x00D5, 0x1283, 0x2771,
        ),
    },
}


CR_HANDLER_MATRIX: dict[str, tuple[int, ...]] = {
    # Format 04 exposes real handlers only for CR00-CR0C.  CR0D and CR0E
    # still produce the parser's generic 0x00 response, but do not have table
    # entries and therefore must not be presented as implemented registers.
    "2.02": (0x1173, 0x1176, 0x117A, 0x11AC, 0x11C5, 0x11C9, 0x11CD,
             0x11E1, 0x11EF, 0x11F3, 0x11F7, 0x11FB, 0x11FF),
    "2.06": (0x1153, 0x1156, 0x115A, 0x118C, 0x11A5, 0x11A9, 0x11AD, 0x11C1,
             0x11CF, 0x11D3, 0x11D7, 0x11DB, 0x11DF, 0x11E3, 0x11E6),
    "2.70": (0x1248, 0x124B, 0x124F, 0x127D, 0x1296, 0x129A, 0x129E, 0x12B2,
             0x12C0, 0x12C4, 0x12C8, 0x12CC, 0x12D0, 0x12D4, 0x12D7),
    "2.71": (0x1222, 0x1225, 0x1229, 0x125B, 0x1274, 0x1278, 0x127C, 0x1290,
             0x129E, 0x12A2, 0x12A6, 0x12AA, 0x12AE, 0x12B2, 0x12B5),
}


# The C-unit write dispatcher immediately precedes the CR table in every
# application image.  Each entry is the resolved destination for CW00-CW0F.
# These addresses are checked against the computed-goto words when the project
# pipeline runs; keeping them here also gives the emulator bounded handler
# entry points for otherwise-silent write requests.
CW_HANDLER_MATRIX: dict[str, tuple[int, ...]] = {
    # Format 04 rejects register 0x0F before dispatch.  In particular, the
    # later-generation CW0FC4 reset/loader request is absent from firmware 2.02.
    "2.02": (0x109B, 0x10A1, 0x10EC, 0x10EF, 0x10F2, 0x10FB, 0x1102, 0x1107,
             0x110E, 0x1114, 0x111D, 0x1125, 0x1133, 0x1142, 0x1155),
    "2.06": (0x1030, 0x1036, 0x107B, 0x1080, 0x1085, 0x108E, 0x1095, 0x109A,
             0x10A1, 0x10A7, 0x10C5, 0x10D1, 0x10DF, 0x10ED, 0x1104, 0x110B),
    "2.70": (0x113A, 0x1140, 0x1185, 0x118A, 0x118F, 0x1198, 0x119B, 0x11A0,
             0x11A7, 0x11AD, 0x11CB, 0x11D3, 0x11E1, 0x11ED, 0x11FE, 0x1205),
    "2.71": (0x1110, 0x1116, 0x115B, 0x1160, 0x1165, 0x116E, 0x1171, 0x1176,
             0x117D, 0x1183, 0x11A1, 0x11A9, 0x11B7, 0x11C3, 0x11D8, 0x11DF),
}


CW_DISPATCH_PC = {
    "2.02": 0x12E5,
    "2.06": 0x1293,
    "2.70": 0x137D,
    "2.71": 0x135A,
}


# Normal silent writes converge here before returning to the parser.  CW05 and
# CW0A enter longer actuator-control routines and need not reach this point in
# the deliberately incomplete synthetic peripheral model.
CW_EXIT_PC = {
    "2.02": 0x115D,
    "2.06": 0x113D,
    "2.70": 0x1232,
    "2.71": 0x120C,
}


CW_SEMANTICS: tuple[tuple[str, str, str], ...] = (
    ("service countdown", "zero clears the bank-1 service countdown", "static"),
    ("persist configuration checksum", "recomputes and writes checksum bytes to data EEPROM A00/A01", "static plus emulator"),
    ("telemetry suppression enable", "sets the telemetry-suppression flag and loads countdown 0x78", "static"),
    ("telemetry suppression disable", "clears telemetry suppression and parser scratch bytes", "static"),
    ("front-panel LEDs", "copies value to the LED output routine", "BixCheck checkout plus firmware"),
    ("burn-drive motor", "enters the plate/burn-drive motor routine", "BixCheck checkout plus firmware"),
    ("air compressor on", "calls the air-compressor-on routine", "BixCheck checkout plus firmware"),
    ("air compressor off", "calls the air-compressor-off routine", "BixCheck checkout plus firmware"),
    ("convection fan", "copies value to the convection-fan target", "BixCheck checkout plus firmware"),
    ("exhaust fan", "scales value through the exhaust phase-control routine", "BixCheck checkout plus firmware"),
    ("igniter follow-up", "enters the second igniter follow-up routine", "BixCheck checkout plus firmware"),
    ("feed motor/sensor", "uses the high nibble as the feed-test drive parameter", "BixCheck checkout plus firmware"),
    ("controller service", "runs a service routine and rewrites RAM 0x43 mode bits; exact purpose unresolved", "static; purpose unresolved"),
    ("igniter workflow", "enters igniter workflow, sets countdown 0x82, emits I plus LF", "BixCheck checkout plus firmware"),
    ("remote buttons", "stores the value as a synthetic panel-button code", "BixCheck tables plus firmware"),
    ("reset/loader request", "value 0xC4 enters the reset/bootloader path", "BixCheck downloader plus firmware"),
)


TELEMETRY_PATHS = {
    "2.02": {
        "block_entry": 0x0DA3,
        "index_ram": 0x0A0,
        "value_ram": 0x0CA,
        "aux_value_ram": 0x0CB,
        "t_sender": 0x0D8A,
        "t_call": 0x0ECC,
        "last_index": 0x15,
    },
    "2.06": {
        "block_entry": 0x0CF2,
        "index_ram": 0x0A1,
        "value_ram": 0x0CA,
        "aux_value_ram": 0x0CB,
        "t_sender": 0x0783,
        "t_call": 0x0E5D,
        "last_index": 0x1D,
    },
    "2.70": {
        "block_entry": 0x0DBD,
        "index_ram": 0x0A0,
        "value_ram": 0x0C8,
        "aux_value_ram": 0x0C9,
        "t_sender": 0x0771,
        "t_call": 0x0F4F,
        "last_index": 0x1D,
    },
    "2.71": {
        "block_entry": 0x0DA6,
        "index_ram": 0x0A0,
        "value_ram": 0x0C8,
        "aux_value_ram": 0x0C9,
        "t_sender": 0x0771,
        "t_call": 0x0F1A,
        "last_index": 0x1E,
    },
}


# The state byte is bank-0 RAM 0x4C. Firmware 2.02 emits it at T0C; later
# versions emit it at T09. The main loop masks its high three bits and routes
# the eight 0x00..0x70 families through the destinations below.
STATE_DISPATCH_PC = {
    "2.02": 0x191F,
    "2.06": 0x18DB,
    "2.70": 0x18D4,
    "2.71": 0x18F9,
}


STATE_FAMILY_HANDLERS: dict[str, tuple[int, ...]] = {
    "2.02": (0x1942, 0x1988, 0x19C3, 0x1A86, 0x1C2C, 0x1C2C, 0x1D87, 0x1D9E),
    "2.06": (0x18F5, 0x192B, 0x1976, 0x19E8, 0x1BBA, 0x1BBA, 0x1CE0, 0x1E25),
    "2.70": (0x18EE, 0x192B, 0x1982, 0x1A02, 0x1BDB, 0x1BDB, 0x1D19, 0x1E3D),
    "2.71": (0x1913, 0x1950, 0x19A7, 0x1A27, 0x1C00, 0x1C00, 0x1D3E, 0x1E5D),
}


STATE_FAMILY_NAMES = (
    "initial/reset",
    "cooldown",
    "off",
    "startup",
    "operating",
    "ramping",
    "ash dump",
    "fallback/undefined",
)


STATE_BRANCH_OFFSETS = {
    # 2.02 uses an explicit compare chain; later builds use a denser branch
    # sequence.  Both resolve the same eight high-nibble state families.
    "2.02": (5, 9, 13, 17, 21, 25, 29, 33),
    "2.06": (3, 6, 9, 12, 15, 18, 21, 24),
    "2.70": (3, 6, 9, 12, 15, 18, 21, 24),
    "2.71": (3, 6, 9, 12, 15, 18, 21, 24),
}


CR_CONSTANTS: dict[str, dict[int, int]] = {
    "2.02": {0x00: 0x00, 0x08: 0x04, 0x0B: 0x02, 0x0C: 0x02},
    "2.06": {0x00: 0x00, 0x08: 0x05, 0x0B: 0x02, 0x0C: 0x06, 0x0D: 0x00, 0x0E: 0x21},
    "2.70": {0x00: 0x00, 0x08: 0x07, 0x0B: 0x02, 0x0C: 0x70, 0x0D: 0x00, 0x0E: 0x02},
    "2.71": {0x00: 0x00, 0x08: 0x07, 0x0B: 0x02, 0x0C: 0x71, 0x0D: 0x00, 0x0E: 0x00},
}


BUTTON_MUX_PATTERN = (
    0x3004, 0x0088, 0x1052, 0x1D88, 0x1452,
    0x3024, 0x0088, 0x10D2, 0x1D88, 0x14D2,
    0x3044, 0x0088, 0x1152, 0x1D88, 0x1552,
    0x3064, 0x0088, 0x11D2, 0x1D88, 0x15D2,
)


BUTTON_MUX_PATTERN_202 = (
    0x3004, 0x0088, 0x1051, 0x1D88, 0x1451,
    0x3024, 0x0088, 0x10D1, 0x1D88, 0x14D1,
    0x3044, 0x0088, 0x1151, 0x1D88, 0x1551,
    0x3064, 0x0088, 0x11D1, 0x1D88, 0x15D1,
)


SENSOR_MUX_PATTERN = (
    0x301F, 0x0588, 0x3080, 0x0788, 0x1051, 0x1988, 0x1451,
    0x3020, 0x0788, 0x10D1, 0x1988, 0x14D1,
    0x3020, 0x0788, 0x1151, 0x1988, 0x1551,
)


SENSOR_MUX_PATTERN_202 = (
    0x301F, 0x0588, 0x3080, 0x0788, 0x1050, 0x1988, 0x1450,
    0x3020, 0x0788, 0x10D0, 0x1988, 0x14D0,
    0x3020, 0x0788, 0x1150, 0x1988, 0x1550,
)


MUX_SCAN_PATTERNS = {
    "2.02": {
        "front_panel": BUTTON_MUX_PATTERN_202,
        "external_sensors": SENSOR_MUX_PATTERN_202,
    },
    "2.06": {
        "front_panel": BUTTON_MUX_PATTERN,
        "external_sensors": SENSOR_MUX_PATTERN,
    },
    "2.70": {
        "front_panel": BUTTON_MUX_PATTERN,
        "external_sensors": SENSOR_MUX_PATTERN,
    },
    "2.71": {
        "front_panel": BUTTON_MUX_PATTERN,
        "external_sensors": SENSOR_MUX_PATTERN,
    },
}


MUX_SCAN_EXPECTED = {
    "2.02": {"front_panel": 0x0166, "external_sensors": 0x0F72},
    "2.06": {"front_panel": 0x0134, "external_sensors": 0x0F03},
    "2.70": {"front_panel": 0x0118, "external_sensors": 0x1004},
    "2.71": {"front_panel": 0x0118, "external_sensors": 0x0FBF},
}


# Masked signatures for the two speed/sensor paths named by the preserved
# 9067-0404 motherboard diagram. A mask of 0x3800 accepts any PIC14 GOTO
# destination while still requiring the instruction class. These signatures
# intentionally stop at firmware data flow; connector routing and electrical
# levels on the owner's reported 9067-0604 board remain unverified.
SENSOR_PATH_PATTERNS: dict[str, tuple[tuple[int, int], ...]] = {
    "exhaust_t0cki_setup": (
        (0x30BF, 0x3FFF), (0x1683, 0x3FFF), (0x0081, 0x3FFF),
        (0x1283, 0x3FFF), (0x0181, 0x3FFF), (0x110B, 0x3FFF),
    ),
    "external_tick_feed_counter": (
        (0x1C86, 0x3FFF), (0x2800, 0x3800), (0x0AC6, 0x3FFF),
        (0x1903, 0x3FFF), (0x0AC7, 0x3FFF),
    ),
    "exhaust_counter_latch": (
        (0x0801, 0x3FFF), (0x190B, 0x3FFF), (0x30FF, 0x3FFF),
        (0x00B4, 0x3FFF), (0x0181, 0x3FFF), (0x110B, 0x3FFF),
    ),
    "feeder_rd0_cycle": (
        (0x1C86, 0x3FFF), (0x2800, 0x3800), (0x1808, 0x3FFF),
        (0x2800, 0x3800), (0x1E43, 0x3FFF), (0x2800, 0x3800),
        (0x17C3, 0x3FFF), (0x2800, 0x3800), (0x1643, 0x3FFF),
    ),
    "feeder_period_latch": (
        (0x30F0, 0x3FFF), (0x05C3, 0x3FFF), (0x0847, 0x3FFF),
        (0x00C5, 0x3FFF), (0x0846, 0x3FFF), (0x00C4, 0x3FFF),
    ),
    "feeder_cr07_scale": (
        (0x0C45, 0x3FFF), (0x00FA, 0x3FFF), (0x0C44, 0x3FFF),
        (0x00F9, 0x3FFF), (0x0CFA, 0x3FFF), (0x0CF9, 0x3FFF),
        (0x0CFA, 0x3FFF), (0x0CF9, 0x3FFF), (0x0CFA, 0x3FFF),
        (0x0CF9, 0x3FFF), (0x0879, 0x3FFF),
    ),
}


SENSOR_PATH_PATTERN_OVERRIDES = {
    "2.02": {
        "feeder_period_latch": (
            (0x30F0, 0x3FFF), (0x05C3, 0x3FFF), (0x1003, 0x3FFF),
            (0x0C47, 0x3FFF), (0x00C5, 0x3FFF),
            (0x0C46, 0x3FFF), (0x00C4, 0x3FFF),
        ),
    },
}


SENSOR_PATH_EXPECTED = {
    "2.02": {
        "exhaust_t0cki_setup": 0x0264,
        "external_tick_feed_counter": 0x01A4,
        "exhaust_counter_latch": 0x01B0,
        "feeder_rd0_cycle": 0x0B3A,
        "feeder_period_latch": 0x0CD0,
        "feeder_cr07_scale": 0x11E1,
    },
    "2.06": {
        "exhaust_t0cki_setup": 0x0221,
        "external_tick_feed_counter": 0x0171,
        "exhaust_counter_latch": 0x017D,
        "feeder_rd0_cycle": 0x08B6,
        "feeder_period_latch": 0x0B58,
        "feeder_cr07_scale": 0x11C1,
    },
    "2.70": {
        "exhaust_t0cki_setup": 0x01FF,
        "external_tick_feed_counter": 0x0155,
        "exhaust_counter_latch": 0x0161,
        "feeder_rd0_cycle": 0x083E,
        "feeder_period_latch": 0x0BD7,
        "feeder_cr07_scale": 0x12B2,
    },
    "2.71": {
        "exhaust_t0cki_setup": 0x01FF,
        "external_tick_feed_counter": 0x0155,
        "exhaust_counter_latch": 0x0161,
        "feeder_rd0_cycle": 0x083E,
        "feeder_period_latch": 0x0C29,
        "feeder_cr07_scale": 0x1290,
    },
}


for _version, _handlers in CR_HANDLER_MATRIX.items():
    for _register, _handler in enumerate(_handlers):
        _constant = CR_CONSTANTS.get(_version, {}).get(_register)
        _detail = f"; returns constant 0x{_constant:02X}" if _constant is not None else ""
        KNOWN_ANNOTATIONS[_version].setdefault(
            _handler, f"CR{_register:02X} read handler{_detail}."
        )

for _version, _handlers in CW_HANDLER_MATRIX.items():
    KNOWN_ANNOTATIONS[_version].setdefault(
        CW_DISPATCH_PC[_version], "CW00-CW0F computed write-dispatch table."
    )
    KNOWN_ANNOTATIONS[_version].setdefault(
        CW_EXIT_PC[_version], "Common exit for normal silent C-unit writes."
    )
    for _register, _handler in enumerate(_handlers):
        _name, _effect, _evidence = CW_SEMANTICS[_register]
        KNOWN_ANNOTATIONS[_version].setdefault(
            _handler, f"CW{_register:02X} write handler: {_name}; {_effect}."
        )

for _version, _path in TELEMETRY_PATHS.items():
    KNOWN_ANNOTATIONS[_version].setdefault(
        _path["block_entry"], "Periodic telemetry slot producer block."
    )
    KNOWN_ANNOTATIONS[_version].setdefault(
        _path["t_sender"], "Emit one T<index><value> line and LF."
    )
    KNOWN_ANNOTATIONS[_version].setdefault(
        _path["t_call"], "Call the periodic T-frame transmitter for the current slot."
    )

for _version, _handlers in STATE_FAMILY_HANDLERS.items():
    _state_slot = "T0C" if _version == "2.02" else "T09"
    KNOWN_ANNOTATIONS[_version].setdefault(
        STATE_DISPATCH_PC[_version],
        f"Dispatch {_state_slot} controller-state family from bank-0 RAM 0x4C.",
    )
    for _family, _handler in enumerate(_handlers):
        KNOWN_ANNOTATIONS[_version].setdefault(
            _handler,
            f"{_state_slot} state family 0x{_family:X}0: {STATE_FAMILY_NAMES[_family]}.",
        )

for _version, _stages in SENSOR_PATH_EXPECTED.items():
    _stage_notes = {
        "exhaust_t0cki_setup": "Configure TMR0 for unprescaled falling-edge counts on RA4/T0CKI (J10 exhaust-sensor path after cross-reference).",
        "external_tick_feed_counter": "Increment the feeder elapsed counter while RB1 is active; this ISR path is driven by RB0 external-interrupt ticks.",
        "exhaust_counter_latch": "Latch the TMR0 exhaust-sensor count into RAM 0x34 every 30 RB0 external-interrupt ticks.",
        "feeder_rd0_cycle": "Detect an RD0 high-then-low feeder-wheel sensor cycle while the RB1 feed-motor output is active.",
        "feeder_period_latch": "Latch the feeder cycle interval from RAM 0x47:0x46 into 0x45:0x44 for CR07.",
        "feeder_cr07_scale": "Scale the latched feeder interval right by four and return its low byte as CR07.",
    }
    for _stage, _address in _stages.items():
        _note = _stage_notes[_stage]
        if _version == "2.02" and _stage == "feeder_period_latch":
            _note = (
                "Shift the feeder interval RAM 0x47:0x46 right once into "
                "0x45:0x44 before CR07 applies its four-bit scale."
            )
        KNOWN_ANNOTATIONS[_version].setdefault(_address, _note)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def find_word_sequence(words: dict[int, int], pattern: tuple[int, ...]) -> list[int]:
    """Return every contiguous program address matching a PIC word pattern."""

    matches: list[int] = []
    for start in sorted(words):
        if all((words.get(start + offset, -1) & 0x3FFF) == expected
               for offset, expected in enumerate(pattern)):
            matches.append(start)
    return matches


def find_masked_word_sequence(
    words: dict[int, int], pattern: tuple[tuple[int, int], ...]
) -> list[int]:
    """Return contiguous matches where each PIC word is compared through a mask."""

    matches: list[int] = []
    for start in sorted(words):
        if all(
            (words.get(start + offset, -1) & mask) == (expected & mask)
            for offset, (expected, mask) in enumerate(pattern)
        ):
            matches.append(start)
    return matches


def write_bytes(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def parse_ihex(data: bytes) -> IHexImage:
    memory: dict[int, int] = {}
    counts: Counter[int] = Counter()
    comments: list[str] = []
    base = 0
    start_segment = None
    start_linear = None
    saw_eof = False

    try:
        text = data.decode("ascii")
    except UnicodeDecodeError as exc:
        raise FirmwareError("Intel HEX file is not ASCII") from exc

    for line_number, raw_line in enumerate(text.splitlines(), 1):
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith(";"):
            comments.append(line[1:].strip())
            continue
        if saw_eof:
            raise FirmwareError(f"record after EOF at line {line_number}")
        if not line.startswith(":"):
            raise FirmwareError(f"invalid record prefix at line {line_number}")
        try:
            record = bytes.fromhex(line[1:])
        except ValueError as exc:
            raise FirmwareError(f"invalid hexadecimal at line {line_number}") from exc
        if len(record) < 5 or len(record) != record[0] + 5:
            raise FirmwareError(f"invalid byte count at line {line_number}")
        if sum(record) & 0xFF:
            raise FirmwareError(f"checksum failure at line {line_number}")
        count = record[0]
        offset = (record[1] << 8) | record[2]
        record_type = record[3]
        payload = record[4 : 4 + count]
        counts[record_type] += 1

        if record_type == 0x00:
            for index, value in enumerate(payload):
                address = base + offset + index
                previous = memory.get(address)
                if previous is not None and previous != value:
                    raise FirmwareError(
                        f"conflicting data at 0x{address:08X}, line {line_number}"
                    )
                memory[address] = value
        elif record_type == 0x01:
            if count or offset:
                raise FirmwareError(f"malformed EOF at line {line_number}")
            saw_eof = True
        elif record_type == 0x02:
            if count != 2:
                raise FirmwareError(f"malformed type-02 record at line {line_number}")
            base = int.from_bytes(payload, "big") << 4
        elif record_type == 0x03:
            if count != 4:
                raise FirmwareError(f"malformed type-03 record at line {line_number}")
            start_segment = int.from_bytes(payload, "big")
        elif record_type == 0x04:
            if count != 2:
                raise FirmwareError(f"malformed type-04 record at line {line_number}")
            base = int.from_bytes(payload, "big") << 16
        elif record_type == 0x05:
            if count != 4:
                raise FirmwareError(f"malformed type-05 record at line {line_number}")
            start_linear = int.from_bytes(payload, "big")
        else:
            raise FirmwareError(
                f"unsupported Intel HEX record type 0x{record_type:02X} at line {line_number}"
            )

    if not saw_eof:
        raise FirmwareError("Intel HEX EOF record is missing")
    if not memory:
        raise FirmwareError("Intel HEX contains no data")
    image = IHexImage(memory, counts, tuple(comments), start_segment, start_linear)
    # Materialize now so incomplete words fail during validation, not later output.
    image.words
    return image


def extract_ascii_hex_payload(executable: bytes, expected_name: str) -> tuple[bytes, dict[str, int | str]]:
    marker = expected_name.encode("ascii")
    marker_offset = executable.find(marker)
    if marker_offset < 0:
        raise FirmwareError(f"embedded filename not found: {expected_name}")
    if marker_offset == 0 or executable[marker_offset - 1] != 0:
        raise FirmwareError("embedded filename is not preceded by the expected NUL separator")
    encoded_end = marker_offset - 1
    encoded_start = encoded_end
    while encoded_start and executable[encoded_start - 1] in HEX_DIGITS:
        encoded_start -= 1
    encoded = executable[encoded_start:encoded_end]
    if not encoded or len(encoded) & 1:
        raise FirmwareError("embedded ASCII-hex payload has invalid length")
    try:
        payload = bytes.fromhex(encoded.decode("ascii"))
    except ValueError as exc:
        raise FirmwareError("embedded ASCII-hex payload is malformed") from exc
    parse_ihex(payload)
    return payload, {
        "filename": expected_name,
        "marker_offset": marker_offset,
        "encoded_start": encoded_start,
        "encoded_end": encoded_end,
        "encoded_bytes": len(encoded),
        "decoded_bytes": len(payload),
        "decoded_sha256": sha256(payload),
    }


def decode_pic14(word: int) -> Instruction:
    word &= 0x3FFF
    exact = {
        0x0000: ("nop", ""),
        0x0008: ("return", ""),
        0x0009: ("retfie", ""),
        0x0062: ("option", ""),
        0x0063: ("sleep", ""),
        0x0064: ("clrwdt", ""),
        0x0065: ("tris", "0x05"),
        0x0066: ("tris", "0x06"),
        0x0067: ("tris", "0x07"),
    }
    if word in exact:
        mnemonic, operands = exact[word]
        return Instruction(mnemonic, operands)
    if (word & 0x3F80) == 0x0080:
        return Instruction("movwf", f"0x{word & 0x7F:02X}")
    if (word & 0x3F80) == 0x0100:
        return Instruction("clrw")
    if (word & 0x3F80) == 0x0180:
        return Instruction("clrf", f"0x{word & 0x7F:02X}")
    byte_ops = {
        0x0200: "subwf", 0x0300: "decf", 0x0400: "iorwf",
        0x0500: "andwf", 0x0600: "xorwf", 0x0700: "addwf",
        0x0800: "movf", 0x0900: "comf", 0x0A00: "incf",
        0x0B00: "decfsz", 0x0C00: "rrf", 0x0D00: "rlf",
        0x0E00: "swapf", 0x0F00: "incfsz",
    }
    byte_key = word & 0x3F00
    if byte_key in byte_ops:
        destination = "F" if word & 0x80 else "W"
        return Instruction(byte_ops[byte_key], f"0x{word & 0x7F:02X}, {destination}")
    bit_ops = {0x1000: "bcf", 0x1400: "bsf", 0x1800: "btfsc", 0x1C00: "btfss"}
    bit_key = word & 0x3C00
    if bit_key in bit_ops:
        return Instruction(bit_ops[bit_key], f"0x{word & 0x7F:02X}, {((word >> 7) & 7)}")
    if (word & 0x3800) == 0x2000:
        target = word & 0x07FF
        return Instruction("call", f"0x{target:03X}", target=target)
    if (word & 0x3800) == 0x2800:
        target = word & 0x07FF
        return Instruction("goto", f"0x{target:03X}", target=target)
    literal_ops_8 = {
        0x3000: "movlw", 0x3400: "retlw", 0x3800: "iorlw",
        0x3900: "andlw", 0x3A00: "xorlw",
    }
    literal_key = word & 0x3F00
    if literal_key in literal_ops_8:
        return Instruction(literal_ops_8[literal_key], f"0x{word & 0xFF:02X}")
    literal_ops_9 = {0x3C00: "sublw", 0x3E00: "addlw"}
    literal_key_9 = word & 0x3E00
    if literal_key_9 in literal_ops_9:
        return Instruction(literal_ops_9[literal_key_9], f"0x{word & 0xFF:02X}")
    return Instruction(".word", f"0x{word:04X}", kind="unknown")


def region_for_word(address: int) -> str:
    if 0x0000 <= address <= 0x1FFF:
        return "program"
    if 0x2000 <= address <= 0x2003:
        return "user_id"
    if address == 0x2007:
        return "configuration"
    if 0x2100 <= address <= 0x21FF:
        return "eeprom"
    return "other"


def contiguous_ranges(addresses: Iterable[int]) -> list[tuple[int, int]]:
    ordered = sorted(set(addresses))
    if not ordered:
        return []
    ranges: list[tuple[int, int]] = []
    start = previous = ordered[0]
    for address in ordered[1:]:
        if address != previous + 1:
            ranges.append((start, previous))
            start = address
        previous = address
    ranges.append((start, previous))
    return ranges


def collect_literal_runs(words: dict[int, int]) -> list[dict[str, int | str]]:
    runs: list[dict[str, int | str]] = []
    current_start: int | None = None
    current = bytearray()
    previous: int | None = None
    for address in sorted(a for a in words if region_for_word(a) == "program"):
        instruction = decode_pic14(words[address])
        is_literal = instruction.mnemonic == "retlw" and (words[address] & 0xFF) in PRINTABLE
        if is_literal and (previous is None or address == previous + 1):
            if current_start is None:
                current_start = address
            current.append(words[address] & 0xFF)
        else:
            if current_start is not None and len(current) >= 4:
                runs.append({
                    "start": current_start,
                    "end": current_start + len(current) - 1,
                    "text": current.decode("ascii"),
                })
            current_start = address if is_literal else None
            current = bytearray([words[address] & 0xFF]) if is_literal else bytearray()
        previous = address
    if current_start is not None and len(current) >= 4:
        runs.append({
            "start": current_start,
            "end": current_start + len(current) - 1,
            "text": current.decode("ascii"),
        })
    return runs


def disassembly_text(spec: ImageSpec, words: dict[int, int], annotated: bool) -> str:
    title = "ANNOTATED" if annotated else "PORTABLE"
    lines = [
        "; =============================================================================",
        f"; BIXBY {spec.version} {spec.variant.upper()} - {title} PIC16F877A DISASSEMBLY",
        "; Generated by tools/firmware_pipeline.py; instruction words are unchanged.",
        "; File-register operands are numeric because the active bank is state-dependent.",
        "; CALL/GOTO operands show only the encoded low 11 bits; PCLATH supplies page bits.",
        "; This conservative format avoids silently inventing bank or page resolution.",
        "; =============================================================================",
        "",
    ]
    annotations = KNOWN_ANNOTATIONS.get(spec.version, {}) if annotated else {}
    last_address: int | None = None
    for address in sorted(words):
        region = region_for_word(address)
        if region != "program":
            continue
        if last_address is None or address != last_address + 1:
            lines.append(f"; --- mapped program range begins at 0x{address:04X} ---")
        if address in annotations:
            lines.extend(["", f"; RE: {annotations[address]}"])
        instruction = decode_pic14(words[address])
        suffix = ""
        if instruction.target is not None:
            suffix = " ; low-11 target; resolve page through PCLATH"
        operands = f" {instruction.operands}" if instruction.operands else ""
        lines.append(
            f"{address:04X}: {words[address] & 0x3FFF:04X}  "
            f"{instruction.mnemonic:<7}{operands}{suffix}"
        )
        last_address = address
    lines.append("")
    return "\n".join(lines)


def analyze_image(root: Path, spec: ImageSpec) -> dict[str, object]:
    source = root / spec.extracted_path
    raw = source.read_bytes()
    image = parse_ihex(raw)
    words = image.words
    program = {a: w for a, w in words.items() if region_for_word(a) == "program"}
    decoded = Counter(decode_pic14(word).mnemonic for word in program.values())
    unknown = sum(1 for word in program.values() if decode_pic14(word).kind == "unknown")
    regions: dict[str, list[int]] = defaultdict(list)
    for address in words:
        regions[region_for_word(address)].append(address)

    summary: dict[str, object] = {
        "schema_version": 1,
        "image": spec.filename,
        "firmware_version": spec.version,
        "variant": spec.variant,
        "source": spec.source_description,
        "sha256": sha256(raw),
        "file_size": len(raw),
        "comments": list(image.comments),
        "intel_hex_record_counts": {
            f"0x{record_type:02X}": count
            for record_type, count in sorted(image.record_counts.items())
        },
        "mapped_bytes": len(image.memory),
        "mapped_words": len(words),
        "program_words": len(program),
        "program_word_min": min(program),
        "program_word_max": max(program),
        "erased_program_words_0x3FFF": sum((word & 0x3FFF) == 0x3FFF for word in program.values()),
        "configuration_word": (
            f"0x{words[0x2007] & 0x3FFF:04X}" if 0x2007 in words else None
        ),
        "user_id_words": {
            f"0x{address:04X}": f"0x{words[address] & 0x3FFF:04X}"
            for address in range(0x2000, 0x2004)
            if address in words
        },
        "eeprom_words": len(regions.get("eeprom", [])),
        "decoded_instruction_counts": dict(sorted(decoded.items())),
        "undecoded_program_words": unknown,
    }

    analysis_dir = root / spec.analysis_dir
    analysis_dir.mkdir(parents=True, exist_ok=True)
    write_text(analysis_dir / "summary.json", json.dumps(summary, indent=2) + "\n")

    with (analysis_dir / "memory-ranges.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(("region", "start_word", "end_word", "word_count"))
        for region in ("program", "user_id", "configuration", "eeprom", "other"):
            for start, end in contiguous_ranges(regions.get(region, [])):
                writer.writerow((region, f"0x{start:04X}", f"0x{end:04X}", end - start + 1))

    with (analysis_dir / "program-words.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(("word_address", "word", "mnemonic", "operands", "decode_status"))
        for address, word in sorted(program.items()):
            instruction = decode_pic14(word)
            writer.writerow((
                f"0x{address:04X}", f"0x{word & 0x3FFF:04X}", instruction.mnemonic,
                instruction.operands, instruction.kind,
            ))

    literal_runs = collect_literal_runs(words)
    with (analysis_dir / "retlw-string-candidates.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(("start_word", "end_word", "text"))
        for run in literal_runs:
            writer.writerow((f"0x{run['start']:04X}", f"0x{run['end']:04X}", run["text"]))

    if regions.get("eeprom"):
        with (analysis_dir / "eeprom.csv").open("w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle, lineterminator="\n")
            writer.writerow(("word_address", "value", "printable"))
            for address in regions["eeprom"]:
                value = words[address] & 0xFF
                writer.writerow((
                    f"0x{address:04X}", f"0x{value:02X}",
                    chr(value) if value in PRINTABLE else "",
                ))

    if program:
        binary = bytearray([0xFF] * ((max(program) + 1) * 2))
        for address, word in program.items():
            binary[address * 2] = word & 0xFF
            binary[address * 2 + 1] = (word >> 8) & 0xFF
        write_bytes(analysis_dir / "program.bin", bytes(binary))

    base = Path(spec.filename).stem
    disassembly_dir = root / spec.disassembly_dir
    write_text(
        disassembly_dir / f"{base}_portable_disassembly.asm",
        disassembly_text(spec, words, annotated=False),
    )
    write_text(
        disassembly_dir / f"{base}_portable_annotated.asm",
        disassembly_text(spec, words, annotated=True),
    )
    return summary


def compare_images(root: Path, parsed: dict[str, tuple[ImageSpec, IHexImage]]) -> None:
    output = root / "reverse-engineering/firmware/comparison"
    output.mkdir(parents=True, exist_ok=True)
    labels = list(parsed)
    pairwise: list[dict[str, object]] = []
    for index, left_label in enumerate(labels):
        left_spec, left_image = parsed[left_label]
        left = left_image.words
        for right_label in labels[index + 1 :]:
            right_spec, right_image = parsed[right_label]
            right = right_image.words
            left_program = {a: w for a, w in left.items() if region_for_word(a) == "program"}
            right_program = {a: w for a, w in right.items() if region_for_word(a) == "program"}
            common = set(left_program) & set(right_program)
            same = sum(left_program[a] == right_program[a] for a in common)
            pairwise.append({
                "left": left_label,
                "right": right_label,
                "common_program_addresses": len(common),
                "same_words_at_same_address": same,
                "different_words_at_same_address": len(common) - same,
                "left_only_program_words": len(set(left_program) - set(right_program)),
                "right_only_program_words": len(set(right_program) - set(left_program)),
                "note": "Same-address counts are descriptive only; compiled routines can relocate between builds.",
            })
    write_text(output / "pairwise-summary.json", json.dumps(pairwise, indent=2) + "\n")

    fw202 = parsed["2.02-pickit"][1].words
    fw206_pickit = parsed["2.06-pickit"][1].words
    region_comparison: dict[str, object] = {
        "schema_version": 1,
        "left": "2.02-pickit",
        "right": "2.06-pickit",
        "regions": {},
        "evidence_boundary": (
            "Same-address comparison; application routines may relocate between builds."
        ),
    }
    for name, start, end in (
        ("complete_program", 0x0000, 0x2000),
        ("application_delivery_range", 0x0000, 0x1E80),
        ("protected_loader_range", 0x1E80, 0x2000),
        ("reset_vector", 0x0000, 0x0004),
        ("resident_loader_body", 0x1E88, 0x2000),
    ):
        addresses = range(start, end)
        same = sum(fw202.get(address) == fw206_pickit.get(address) for address in addresses)
        region_comparison["regions"][name] = {
            "start_word": f"0x{start:04X}",
            "end_word_exclusive": f"0x{end:04X}",
            "word_count": end - start,
            "same_words": same,
            "different_words": end - start - same,
            "byte_identical": same == end - start,
        }
    write_text(
        output / "2.02-vs-2.06-pickit.json",
        json.dumps(region_comparison, indent=2) + "\n",
    )

    application_versions = ("2.02", "2.06", "2.70", "2.71")

    with (output / "anchors.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(("anchor", *application_versions, "confidence"))
        for name, values in ANCHORS:
            confidence = "medium" if name == "uart_rx_isr" else "high"
            writer.writerow((
                name,
                *(f"0x{values[version]:04X}" for version in application_versions),
                confidence,
            ))

    old = parsed["2.06-downloader"][1].words
    pickit = parsed["2.06-pickit"][1].words
    rows: list[tuple[str, str, str, str]] = []
    for address in sorted(set(old) | set(pickit)):
        left = old.get(address)
        right = pickit.get(address)
        if left == right:
            continue
        state = "changed" if left is not None and right is not None else ("downloader-only" if left is not None else "pickit-only")
        rows.append((
            f"0x{address:04X}",
            "" if left is None else f"0x{left & 0x3FFF:04X}",
            "" if right is None else f"0x{right & 0x3FFF:04X}",
            state,
        ))
    with (output / "2.06-downloader-vs-pickit.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(("word_address", "downloader_word", "pickit_word", "status"))
        writer.writerows(rows)

    with (output / "cr00-cr0e-handlers.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(("register", *(
            field
            for version in application_versions
            for field in (f"{version}_handler", f"{version}_constant")
        )))
        for register in range(0x0F):
            row: list[str] = [f"CR{register:02X}"]
            for version in application_versions:
                handlers = CR_HANDLER_MATRIX[version]
                row.append(
                    "" if register >= len(handlers)
                    else f"0x{handlers[register]:04X}"
                )
                constant = CR_CONSTANTS[version].get(register)
                row.append("" if constant is None else f"0x{constant:02X}")
            writer.writerow(row)

    with (output / "cw00-cw0f-handlers.csv").open(
        "w", encoding="utf-8", newline=""
    ) as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow((
            "register", "name", "static_effect", "evidence",
            *(f"{version}_handler" for version in application_versions),
        ))
        for register, (name, effect, evidence) in enumerate(CW_SEMANTICS):
            writer.writerow((
                f"CW{register:02X}", name, effect, evidence,
                *(
                    "" if register >= len(CW_HANDLER_MATRIX[version])
                    else f"0x{CW_HANDLER_MATRIX[version][register]:04X}"
                    for version in application_versions
                ),
            ))

    telemetry_rows: list[tuple[str, ...]] = []
    application_labels = {
        "2.02": "2.02-pickit",
        "2.06": "2.06-downloader",
        "2.70": "2.70-embedded",
        "2.71": "2.71-embedded",
    }
    for version, label in application_labels.items():
        spec, image = parsed[label]
        dispatch = CW_DISPATCH_PC[version]
        for register, expected in enumerate(CW_HANDLER_MATRIX[version]):
            word = image.words.get(dispatch + 4 + register)
            if word is None or decode_pic14(word).mnemonic != "goto":
                raise FirmwareError(
                    f"{version} CW{register:02X}: no GOTO at dispatch entry "
                    f"0x{dispatch + 4 + register:04X}"
                )
            if (word & 0x07FF) != (expected & 0x07FF):
                raise FirmwareError(
                    f"{version} CW{register:02X}: dispatcher encodes "
                    f"0x{word & 0x07FF:03X}, expected handler 0x{expected:04X}"
                )
        path = TELEMETRY_PATHS[version]
        sender = path["t_sender"]
        # The sender always begins by loading ASCII T and ends by returning
        # immediately after the LF write.  This deliberately narrow check
        # proves the stable one-index/one-value wire shape without pretending
        # to resolve every producer here.
        if image.words.get(sender) != 0x3054:
            raise FirmwareError(
                f"{version}: telemetry sender at 0x{sender:04X} does not load ASCII T"
            )
        if decode_pic14(image.words[path["t_call"]]).mnemonic != "call":
            raise FirmwareError(
                f"{version}: telemetry call site 0x{path['t_call']:04X} is not CALL"
            )
        telemetry_rows.append((
            version, spec.filename, f"0x{path['block_entry']:04X}",
            f"0x{path['index_ram']:03X}", f"0x{path['value_ram']:03X}",
            f"0x{path['aux_value_ram']:03X}", f"0x{path['t_call']:04X}",
            f"0x{sender:04X}", f"0x{path['last_index']:02X}",
            "T<index:02x><value:02x>\\n",
        ))
    with (output / "telemetry-paths.csv").open(
        "w", encoding="utf-8", newline=""
    ) as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow((
            "version", "image", "producer_block_pc", "index_ram", "value_ram",
            "aux_value_ram", "sender_call_pc", "sender_pc", "last_periodic_index",
            "wire_shape",
        ))
        writer.writerows(telemetry_rows)

    state_rows: list[tuple[str, ...]] = []
    for version, label in application_labels.items():
        spec, image = parsed[label]
        dispatch = STATE_DISPATCH_PC[version]
        if image.words.get(dispatch) != 0x084C or image.words.get(dispatch + 1) != 0x3970:
            raise FirmwareError(
                f"{version}: state dispatcher at 0x{dispatch:04X} does not read "
                "RAM 0x4C and mask 0x70"
            )
        for family, (offset, expected) in enumerate(
            zip(
                STATE_BRANCH_OFFSETS[version],
                STATE_FAMILY_HANDLERS[version],
                strict=True,
            )
        ):
            word = image.words.get(dispatch + offset)
            if word is None or decode_pic14(word).mnemonic != "goto":
                raise FirmwareError(
                    f"{version}: state family 0x{family:X}0 has no GOTO at "
                    f"0x{dispatch + offset:04X}"
                )
            if (word & 0x07FF) != (expected & 0x07FF):
                raise FirmwareError(
                    f"{version}: state family 0x{family:X}0 targets low address "
                    f"0x{word & 0x07FF:03X}, expected 0x{expected:04X}"
                )
            state_rows.append(
                (
                    version,
                    spec.filename,
                    "0x04C",
                    f"0x{dispatch:04X}",
                    f"0x{family:X}0",
                    STATE_FAMILY_NAMES[family],
                    f"0x{expected:04X}",
                    "high-nibble family; low bits retain substate/level flags",
                )
            )
    with (output / "state-family-dispatch.csv").open(
        "w", encoding="utf-8", newline=""
    ) as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(
            (
                "version", "image", "state_ram", "dispatch_pc", "family",
                "firmware_working_meaning", "handler_pc", "encoding_note",
            )
        )
        writer.writerows(state_rows)

    sensor_stage_rows: list[tuple[str, ...]] = []
    sensor_stage_descriptions = {
        "exhaust_t0cki_setup": (
            "J10 exhaust-fan sensor", "configure_counter",
            "OPTION_REG=0xBF selects unprescaled RA4/T0CKI high-to-low transitions for TMR0",
            "CR05", "high static; physical route and electrical levels not live-validated",
        ),
        "external_tick_feed_counter": (
            "J9 feeder-wheel sensor", "elapsed_tick_counter",
            "while RB1 feed-motor output is high, increment RAM 0x47:0x46 on each RB0 external interrupt",
            "CR07", "high static; RB0 tick engineering timebase not live-measured",
        ),
        "exhaust_counter_latch": (
            "J10 exhaust-fan sensor", "sample_latch",
            "every 30 RB0 external-interrupt ticks, copy TMR0 to RAM 0x34; overflow becomes 0xFF; clear TMR0",
            "CR05", "high static; reported byte is a pulse count, not a proven RPM value",
        ),
        "feeder_rd0_cycle": (
            "J9 feeder-wheel sensor", "edge_detector",
            "while RB1 is high, remember RD0 high and flag the following RD0 low transition",
            "CR02 bit 4 / CR07", "high static; physical polarity not live-validated",
        ),
        "feeder_period_latch": (
            "J9 feeder-wheel sensor", "period_latch",
            "on the completed RD0 cycle, copy RAM 0x47:0x46 to 0x45:0x44, bound it, then reset timer and flags",
            "CR07", "high static; engineering unit unresolved",
        ),
        "feeder_cr07_scale": (
            "J9 feeder-wheel sensor", "protocol_scale",
            "return the low byte of RAM 0x45:0x44 shifted right four places",
            "CR07", "high static transform; wrap/fault semantics unresolved",
        ),
    }
    for version in SENSOR_PATH_EXPECTED:
        label = application_labels[version]
        spec, image = parsed[label]
        for stage, pattern in SENSOR_PATH_PATTERNS.items():
            pattern = SENSOR_PATH_PATTERN_OVERRIDES.get(version, {}).get(
                stage, pattern
            )
            expected = SENSOR_PATH_EXPECTED[version][stage]
            found = find_masked_word_sequence(image.words, pattern)
            if found != [expected]:
                raise FirmwareError(
                    f"{version} {stage} signature: expected [0x{expected:04X}], "
                    f"found {[f'0x{item:04X}' for item in found]}"
                )
            signal, stage_name, operation, protocol, confidence = sensor_stage_descriptions[stage]
            if version == "2.02" and stage == "feeder_period_latch":
                operation = (
                    "on the completed RD0 cycle, shift RAM 0x47:0x46 right "
                    "once into 0x45:0x44, bound it, then reset timer and flags"
                )
            sensor_stage_rows.append((
                version, spec.filename, signal, stage_name, f"0x{expected:04X}",
                operation, protocol, confidence,
            ))
    with (output / "sensor-signal-paths.csv").open(
        "w", encoding="utf-8", newline=""
    ) as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow((
            "version", "image", "physical_signal", "stage", "pc", "operation",
            "protocol_mapping", "confidence",
        ))
        writer.writerows(sensor_stage_rows)

    mux_rows: list[tuple[str, ...]] = []
    front_panel_slots = (
        (0, 0x04, "00", "OFF", "CR01 bit 0 / value 0x01"),
        (1, 0x24, "01", "ON", "CR01 bit 1 / value 0x02"),
        (2, 0x44, "10", "UP", "CR01 bit 2 / value 0x04"),
        (3, 0x64, "11", "DOWN", "CR01 bit 3 / value 0x08"),
    )
    sensor_slots = (
        (
            0, 0x80, "00", "burn-drive motor limit switch",
            "CR02 bit 0",
            "BixCheck plate-motor-off predicate plus motherboard diagram",
            "high static; physical polarity not live-validated",
        ),
        (
            1, 0xA0, "01", "unassigned external sensor slot",
            "CR02 bit 1", "firmware scan only", "unknown",
        ),
        (
            2, 0xC0, "10", "fuel-select switch",
            "CR02 bit 2; 1=Fuel A/corn, 0=Fuel B/wood",
            "firmware 0x30 EEPROM-bank offset, dormant BixCheck predicates, and motherboard diagram",
            "high static; polarity live-validated on serial 5215 running 2.02",
        ),
    )
    for version in MUX_SCAN_EXPECTED:
        label = application_labels[version]
        spec, image = parsed[label]
        patterns = MUX_SCAN_PATTERNS[version]
        matches: dict[str, int] = {}
        for family, pattern in patterns.items():
            found = find_word_sequence(image.words, pattern)
            expected = MUX_SCAN_EXPECTED[version][family]
            if found != [expected]:
                raise FirmwareError(
                    f"{version} {family} mux signature: expected "
                    f"[0x{expected:04X}], found {[f'0x{item:04X}' for item in found]}"
                )
            matches[family] = expected
        for slot, selector, address, name, protocol in front_panel_slots:
            destination = (
                f"RAM 0x51 bit {slot}, debounced to RAM 0x52"
                if version == "2.02"
                else f"bank-1 RAM 0x52 bit {slot}, debounced to 0x53"
            )
            mux_rows.append((
                version, spec.filename, "front_panel", f"0x{matches['front_panel']:04X}",
                f"0x{selector:02X}", "RD2=1, RD7=0", f"RD6:RD5={address}",
                "RD3 active-low", destination,
                protocol, name, "firmware scan plus BixCheck button codes and board diagram",
                "high static; connector pin not live-validated",
            ))
        for slot, selector, address, name, protocol, evidence, confidence in sensor_slots:
            destination = (
                f"RAM 0x50 bit {slot}"
                if version == "2.02"
                else f"bank-1 RAM 0x51 bit {slot}"
            )
            mux_rows.append((
                version, spec.filename, "external_sensors",
                f"0x{matches['external_sensors']:04X}", f"0x{selector:02X}",
                "RD7=1, RD2=0", f"RD6:RD5={address}", "RD3 active-high",
                destination, protocol, name, evidence, confidence,
            ))
    with (output / "multiplexed-inputs.csv").open(
        "w", encoding="utf-8", newline=""
    ) as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow((
            "version", "image", "scan_family", "routine_pc", "selector_value",
            "bank_enable", "address_lines", "sample_pin", "destination",
            "protocol_mapping", "physical_interpretation", "evidence", "confidence",
        ))
        writer.writerows(mux_rows)


def read_zip_member(archive: Path, pattern: str) -> tuple[str, bytes]:
    regex = re.compile(pattern, re.IGNORECASE)
    with zipfile.ZipFile(archive) as package:
        matches = [name for name in package.namelist() if regex.search(Path(name).name)]
        if len(matches) != 1:
            raise FirmwareError(
                f"expected one member matching {pattern!r} in {archive}, found {matches}"
            )
        return matches[0], package.read(matches[0])


def run_project(root: Path) -> None:
    package_dir = root / "preservation/original/vendor-packages"
    package_inventory: dict[str, list[dict[str, object]]] = {}
    for archive in sorted(package_dir.glob("*.zip")):
        members: list[dict[str, object]] = []
        with zipfile.ZipFile(archive) as package:
            for member in package.infolist():
                if member.is_dir():
                    continue
                payload = package.read(member)
                members.append({
                    "path": member.filename,
                    "size": len(payload),
                    "sha256": sha256(payload),
                })
        package_inventory[archive.name] = members
    write_text(
        root / "reverse-engineering/firmware/package-inventory.json",
        json.dumps(package_inventory, indent=2) + "\n",
    )

    package_206 = package_dir / "Bixby110_115_02060021_and_manual.zip"
    for filename in ("Bixby_02060021_Downloader.hex", "Bixby_02060021_PICkit.hex"):
        _, payload = read_zip_member(package_206, re.escape(filename) + r"$")
        write_bytes(
            root / "reverse-engineering/firmware/2.06/extracted" / filename,
            payload,
        )

    original_202 = (
        root
        / "preservation/original/firmware/2.02/Bixby_0202_260827_PICkit.hex"
    )
    derived_202 = (
        root
        / "reverse-engineering/firmware/2.02/extracted/Bixby_0202_260827_PICkit.hex"
    )
    original_202_payload = original_202.read_bytes()
    if derived_202.exists() and derived_202.read_bytes() != original_202_payload:
        raise FirmwareError(
            f"existing 2.02 analysis copy does not match original read: {derived_202}"
        )
    write_bytes(derived_202, original_202_payload)

    extraction_metadata: dict[str, object] = {
        "2.02": {
            "source": "owner-supplied PICkit read of the original controller",
            "original_path": str(original_202.relative_to(root)),
            "analysis_copy": str(derived_202.relative_to(root)),
            "sha256": sha256(original_202_payload),
            "relationship": "byte-identical copy",
            "independent_repeat_reads": "pending",
        }
    }
    for version, archive_name, embedded_name in (
        ("2.70", "BixCheck_080206.zip", "Bixby_0270_070206.hex"),
        ("2.71", "BixCheck_080315.zip", "Bixby_0271_080315.hex"),
    ):
        member, executable = read_zip_member(package_dir / archive_name, r"\.exe$")
        payload, metadata = extract_ascii_hex_payload(executable, embedded_name)
        destination = root / f"reverse-engineering/firmware/{version}/extracted/{embedded_name}"
        if destination.exists() and destination.read_bytes() != payload:
            raise FirmwareError(f"existing extraction does not match package: {destination}")
        write_bytes(destination, payload)
        extraction_metadata[version] = {
            "package": archive_name,
            "executable_member": member,
            "executable_sha256": sha256(executable),
            **metadata,
        }
    write_text(
        root / "reverse-engineering/firmware/extraction-metadata.json",
        json.dumps(extraction_metadata, indent=2) + "\n",
    )

    parsed: dict[str, tuple[ImageSpec, IHexImage]] = {}
    summaries: list[dict[str, object]] = []
    for spec in IMAGE_SPECS:
        summary = analyze_image(root, spec)
        summaries.append(summary)
        raw = (root / spec.extracted_path).read_bytes()
        parsed[f"{spec.version}-{spec.variant}"] = (spec, parse_ihex(raw))
    compare_images(root, parsed)
    write_text(
        root / "reverse-engineering/firmware/image-index.json",
        json.dumps(summaries, indent=2) + "\n",
    )


def command_extract(args: argparse.Namespace) -> None:
    payload, metadata = extract_ascii_hex_payload(Path(args.executable).read_bytes(), args.name)
    write_bytes(Path(args.output), payload)
    print(json.dumps(metadata, indent=2))


def command_analyze(args: argparse.Namespace) -> None:
    source = Path(args.hex)
    output = Path(args.output)
    root = output.parent
    relative_source = source.name
    spec = ImageSpec(
        args.version, args.variant, source.name, relative_source,
        output.name, output.name, f"standalone analysis of {source}",
    )
    # Standalone mode uses a private staging root to keep the common analyzer simple.
    staging = output.parent / ".firmware-pipeline-staging"
    staging.mkdir(parents=True, exist_ok=True)
    write_bytes(staging / relative_source, source.read_bytes())
    staged_spec = ImageSpec(
        spec.version, spec.variant, spec.filename, relative_source,
        "analysis", "disassembly", spec.source_description,
    )
    analyze_image(staging, staged_spec)
    output.mkdir(parents=True, exist_ok=True)
    for item in (staging / "analysis").iterdir():
        item.replace(output / item.name)
    for item in (staging / "disassembly").iterdir():
        item.replace(output / item.name)
    (staging / relative_source).unlink()
    (staging / "analysis").rmdir()
    (staging / "disassembly").rmdir()
    staging.rmdir()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    project = subparsers.add_parser("project", help="regenerate the complete repository analysis")
    project.add_argument("--repo-root", type=Path, default=Path.cwd())
    extract = subparsers.add_parser("extract-embedded", help="extract one payload from a BixCheck executable")
    extract.add_argument("executable")
    extract.add_argument("name", help="embedded HEX filename")
    extract.add_argument("output")
    extract.set_defaults(func=command_extract)
    analyze = subparsers.add_parser("analyze", help="analyze one Intel HEX image")
    analyze.add_argument("hex")
    analyze.add_argument("output")
    analyze.add_argument("--version", default="unknown")
    analyze.add_argument("--variant", default="standalone")
    analyze.set_defaults(func=command_analyze)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        if args.command == "project":
            run_project(args.repo_root.resolve())
        else:
            args.func(args)
    except (FirmwareError, FileNotFoundError, zipfile.BadZipFile) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
