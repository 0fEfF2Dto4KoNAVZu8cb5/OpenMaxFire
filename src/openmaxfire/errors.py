"""Stable exception taxonomy for reusable OpenMaxFire API consumers.

Domain result objects describe expected controller outcomes.  These exceptions
represent caller, compatibility, safety, verification, or transport conditions
that prevent a workflow from producing such an outcome.
"""

from __future__ import annotations


class OpenMaxFireError(Exception):
    """Base class for public OpenMaxFire API exceptions."""


class UnsupportedControllerError(OpenMaxFireError):
    """The detected firmware/data-format pairing has no exact profile."""


class CapabilityUnavailableError(OpenMaxFireError):
    """A controller profile does not currently expose a requested capability."""


class SafetyInterlockError(OpenMaxFireError):
    """A machine-enforceable prerequisite or cleanup guarantee is absent."""


class VerificationError(OpenMaxFireError):
    """A state-changing operation could not be verified from fresh evidence."""


class LoaderUnavailableError(CapabilityUnavailableError):
    """Firmware loader execution is intentionally unavailable or unproven."""
