"""High-level OpenMaxFire client.

Version 0.1 deliberately keeps the high-level surface small.  Raw register
writes are available to research tooling, while ordinary users get only the
known front-panel abstraction.  Factory checkout commands are intentionally
not exposed here yet.
"""

from __future__ import annotations

from dataclasses import dataclass

from .protocol import RemoteButton, encode_read_register, encode_remote_button, encode_write_register
from .transport import Transport


@dataclass(frozen=True, slots=True)
class CommandReceipt:
    request: bytes
    response: bytes | None = None
    verified: bool = False


class MaxFireClient:
    def __init__(self, transport: Transport):
        self.transport = transport

    def send_raw(self, command: bytes) -> CommandReceipt:
        self.transport.write(command)
        return CommandReceipt(request=command)

    def read_register(self, address: int) -> CommandReceipt:
        """Send a register-read request.

        Response parsing is intentionally not claimed yet; the BixCheck receive
        state machine is the next reverse-engineering milestone.
        """

        return self.send_raw(encode_read_register(address))

    def write_register(self, address: int, value: int) -> CommandReceipt:
        """Research-level raw register write. Use only with a documented map."""

        return self.send_raw(encode_write_register(address, value))

    def remote_button(self, button: RemoteButton) -> CommandReceipt:
        """Send a reconstructed BixCheck front-panel remote-control action.

        WARNING: statically confirmed in BixCheck 5.5.01, but not yet live-tested.
        """

        return self.send_raw(encode_remote_button(button))

    def close(self) -> None:
        self.transport.close()
