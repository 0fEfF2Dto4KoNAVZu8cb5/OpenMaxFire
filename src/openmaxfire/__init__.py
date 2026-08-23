"""OpenMaxFire - open tooling for Bixby MaxFire 110/115."""

from .client import CommandReceipt, MaxFireClient, StoveIdentity
from .monitor import MonitorState, replay_capture
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
from .transactions import (
    TransactionOperation,
    TransactionPlan,
    execute_transaction,
    load_transaction_plan,
    parse_transaction_plan,
)

__all__ = [
    "CommandReceipt",
    "MaxFireClient",
    "MonitorState",
    "StoveIdentity",
    "IgniterState",
    "OperatingState",
    "RemoteButton",
    "combine_telemetry_word",
    "decode_igniter_state",
    "decode_operating_state",
    "encode_read_register",
    "encode_write_register",
    "TransactionOperation",
    "TransactionPlan",
    "execute_transaction",
    "load_transaction_plan",
    "parse_transaction_plan",
    "replay_capture",
]

__version__ = "0.4.0"
