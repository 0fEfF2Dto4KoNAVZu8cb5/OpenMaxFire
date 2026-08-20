"""Low-level MaxFire 110/115 J3 protocol primitives.

The command encodings in this module are reconstructed from static analysis of
BixCheck 5.5.01 (BixCheck_080315.exe).  They have NOT yet been validated on a
physical stove.  Keep that distinction explicit in any downstream software.
"""

from __future__ import annotations

from enum import IntEnum


CONTROLLER_PREFIX = "C"
READ_OPCODE = "R"
WRITE_OPCODE = "W"

# Statically reconstructed from BixCheck 5.5.01:
# remote front-panel actions are writes to controller register 0x0E.
REMOTE_BUTTON_REGISTER = 0x0E


class RemoteButton(IntEnum):
    """Values stored in BixCheck's Bixby110RCButtonData table."""

    OFF = 0x11
    ON = 0x12
    UP = 0x14
    DOWN = 0x18


def _byte(value: int, name: str) -> int:
    if not isinstance(value, int) or not 0 <= value <= 0xFF:
        raise ValueError(f"{name} must be an integer from 0x00 to 0xFF")
    return value


def encode_read_register(address: int) -> bytes:
    """Encode a controller register read as ASCII ``CRXX``.

    Example: register 0x0E -> b"CR0E".
    """

    address = _byte(address, "address")
    return f"{CONTROLLER_PREFIX}{READ_OPCODE}{address:02X}".encode("ascii")


def encode_write_register(address: int, value: int) -> bytes:
    """Encode a controller register write as ASCII ``CWXXYY``.

    Example: write 0x14 to register 0x0E -> b"CW0E14".
    """

    address = _byte(address, "address")
    value = _byte(value, "value")
    return f"{CONTROLLER_PREFIX}{WRITE_OPCODE}{address:02X}{value:02X}".encode("ascii")


def encode_remote_button(button: RemoteButton) -> bytes:
    """Encode the statically reconstructed BixCheck remote-button write."""

    try:
        button = RemoteButton(button)
    except ValueError as exc:
        raise ValueError(f"unknown remote button value: {button!r}") from exc
    return encode_write_register(REMOTE_BUTTON_REGISTER, int(button))
