"""OpenMaxFire - open tooling for Bixby MaxFire 110/115."""

from .client import MaxFireClient
from .protocol import RemoteButton, encode_read_register, encode_write_register

__all__ = [
    "MaxFireClient",
    "RemoteButton",
    "encode_read_register",
    "encode_write_register",
]

__version__ = "0.1.1"
