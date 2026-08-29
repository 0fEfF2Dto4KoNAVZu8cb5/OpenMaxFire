"""Controlled transition from the running MaxFire application into the resident loader."""

from __future__ import annotations

from .client import MaxFireClient, StoveIdentity
from .experimental_flasher import ExperimentalFlasherError, FlasherEventRecorder
from .transport import Transport

SOFTWARE_LOADER_RESET = b"CW0FC4"
SUPPORTED_RESET_SOURCE_VERSIONS = frozenset({"2.06", "2.70", "2.71"})


def reset_application_into_loader(
    transport: Transport,
    recorder: FlasherEventRecorder,
    *,
    request_delay: float = 0.10,
) -> StoveIdentity:
    """Verify the running application, then issue BixCheck's ``CW0FC4`` reset.

    This is intentionally state-changing.  The caller must begin binary
    ``EA`` probing immediately after this function returns.  No bootloader
    program block is sent here.
    """

    client = MaxFireClient(transport)
    identity = client.identify(request_delay=request_delay)
    recorder.record(
        "application_preflight_identity",
        firmware_version=identity.firmware_version,
        data_format=f"{identity.data_format:02X}",
        probe=f"{identity.probe:02X}",
        recognized=identity.recognized,
    )

    if identity.probe != 0:
        raise ExperimentalFlasherError(
            f"application preflight CR00 expected 00, received {identity.probe:02X}"
        )
    if identity.firmware_version not in SUPPORTED_RESET_SOURCE_VERSIONS:
        raise ExperimentalFlasherError(
            "software loader reset is allowed only from preserved 2.06, 2.70, or 2.71; "
            f"controller reported {identity.firmware_version}"
        )

    recorder.record(
        "tx",
        phase="application_loader_reset",
        data_hex=SOFTWARE_LOADER_RESET.hex(" ").upper(),
        byte_count=len(SOFTWARE_LOADER_RESET),
        firmware_version=identity.firmware_version,
    )
    transport.write(SOFTWARE_LOADER_RESET)
    recorder.record(
        "application_loader_reset_issued",
        firmware_version=identity.firmware_version,
    )
    return identity


__all__ = [
    "SOFTWARE_LOADER_RESET",
    "SUPPORTED_RESET_SOURCE_VERSIONS",
    "reset_application_into_loader",
]
