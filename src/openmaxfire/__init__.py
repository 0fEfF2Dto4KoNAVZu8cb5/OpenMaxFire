"""OpenMaxFire - open tooling for Bixby MaxFire 110/115."""

from .client import MaxFireClient, StoveIdentity
from .protocol import (
    IgniterState,
    OperatingState,
    RemoteButton,
    combine_telemetry_word,
    decode_igniter_state,
    decode_operating_state,
    encode_read_register,
    encode_write_register,
)

__all__ = [
    "MaxFireClient",
    "StoveIdentity",
    "IgniterState",
    "OperatingState",
    "RemoteButton",
    "combine_telemetry_word",
    "decode_igniter_state",
    "decode_operating_state",
    "encode_read_register",
    "encode_write_register",
]

__version__ = "0.2.0"
