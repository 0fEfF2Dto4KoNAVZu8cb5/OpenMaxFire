"""Typed EEPROM images, field schemas, diffs, and offline restore planning.

This module does not perform serial I/O.  It prepares validated plans above the
generic transaction layer; a future explicitly authorized service is required
to execute them against hardware.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Mapping

from .profiles import ControllerProfile
from .protocol import (
    CHECKSUM_END_BY_FORMAT,
    calculate_configuration_checksum,
    percentage_to_stove_multiply_parameter,
    stove_multiply_parameter_to_percentage,
)
from .transactions import TransactionOperation


class ConfigurationFieldKind(str, Enum):
    UINT8 = "uint8"
    STRING = "string"
    BIT = "bit"
    LEAN_THRESHOLD = "lean_threshold"
    LEAN_FAN = "lean_fan"
    LEAN_FEED = "lean_feed"


@dataclass(frozen=True, slots=True)
class ConfigurationField:
    name: str
    address: int
    kind: ConfigurationFieldKind
    minimum: int | None = None
    maximum: int | None = None
    length: int = 1
    mask: int = 0
    writable: bool = True
    evidence: str = "static BixCheck table"

    def decode(self, raw: bytes) -> object:
        if self.kind is ConfigurationFieldKind.STRING:
            return raw[self.address : self.address + self.length].decode(
                "ascii", errors="backslashreplace"
            ).rstrip("\0\xff ")
        value = raw[self.address]
        if self.kind is ConfigurationFieldKind.BIT:
            return bool(value & self.mask)
        if self.kind in (
            ConfigurationFieldKind.LEAN_THRESHOLD,
            ConfigurationFieldKind.LEAN_FAN,
            ConfigurationFieldKind.LEAN_FEED,
        ):
            return stove_multiply_parameter_to_percentage(value, self.address)
        return value

    def encode_into(
        self,
        image: bytearray,
        value: object,
        *,
        allow_read_only: bool = False,
    ) -> None:
        if not self.writable and not allow_read_only:
            raise PermissionError(f"configuration field {self.name!r} is read-only")
        if self.kind is ConfigurationFieldKind.STRING:
            if not isinstance(value, str):
                raise ValueError(f"{self.name} must be an ASCII string")
            try:
                encoded = value.encode("ascii")
            except UnicodeEncodeError as exc:
                raise ValueError(f"{self.name} must contain only ASCII") from exc
            if len(encoded) > self.length:
                raise ValueError(f"{self.name} cannot exceed {self.length} bytes")
            image[self.address : self.address + self.length] = encoded.ljust(
                self.length, b"\0"
            )
            return
        if self.kind is ConfigurationFieldKind.BIT:
            if not isinstance(value, bool):
                raise ValueError(f"{self.name} must be true or false")
            if value:
                image[self.address] |= self.mask
            else:
                image[self.address] &= ~self.mask & 0xFF
            return
        if isinstance(value, bool) or not isinstance(value, int):
            raise ValueError(f"{self.name} must be an integer")
        if self.minimum is not None and value < self.minimum:
            raise ValueError(f"{self.name} must be at least {self.minimum}")
        if self.maximum is not None and value > self.maximum:
            raise ValueError(f"{self.name} must be at most {self.maximum}")
        if self.kind in (
            ConfigurationFieldKind.LEAN_THRESHOLD,
            ConfigurationFieldKind.LEAN_FAN,
            ConfigurationFieldKind.LEAN_FEED,
        ):
            image[self.address] = percentage_to_stove_multiply_parameter(
                value, self.address
            )
        else:
            if not 0 <= value <= 0xFF:
                raise ValueError(f"{self.name} must fit in one byte")
            image[self.address] = value


@dataclass(frozen=True, slots=True)
class ConfigurationSchema:
    data_format: int
    checksum_end: int
    fields: tuple[ConfigurationField, ...]

    @property
    def by_name(self) -> Mapping[str, ConfigurationField]:
        return MappingProxyType({field.name: field for field in self.fields})

    def fields_at(self, address: int) -> tuple[ConfigurationField, ...]:
        return tuple(
            field
            for field in self.fields
            if field.address <= address < field.address + field.length
        )


def _fuel_fields(
    bank: str,
    base: int,
    *,
    thermostat: bool,
    lean_burn: bool,
) -> list[ConfigurationField]:
    prefix = f"fuel_{bank}"
    fields: list[ConfigurationField] = []
    for offset, category in ((0x00, "fan"), (0x08, "feed"), (0x10, "ash_increment")):
        for level in range(1, 9):
            fields.append(
                ConfigurationField(
                    f"{prefix}.{category}.level_{level}",
                    base + offset + level - 1,
                    ConfigurationFieldKind.UINT8,
                    0,
                    255,
                )
            )
    for offset, name in (
        (0x18, "startup_fan"),
        (0x19, "startup_feed"),
        (0x1A, "startup_time_percent"),
        (0x1B, "igniter_time_percent"),
        (0x20, "ash_dump_fan"),
        (0x21, "ash_dump_feed"),
        (0x22, "ash_dump_time_percent"),
        (0x24, "ash_dump_target_percent"),
        (0x28, "convection_tc_25_percent"),
        (0x29, "convection_tc_100_percent"),
    ):
        fields.append(
            ConfigurationField(
                f"{prefix}.{name}",
                base + offset,
                ConfigurationFieldKind.UINT8,
                0,
                255,
            )
        )
    fields.append(
        ConfigurationField(
            f"{prefix}.ash_dump_heat_level",
            base + 0x23,
            ConfigurationFieldKind.UINT8,
            0,
            8,
        )
    )
    if thermostat:
        fields.append(
            ConfigurationField(
                f"{prefix}.thermostat_heat_level",
                base + 0x2A,
                ConfigurationFieldKind.UINT8,
                0,
                8,
            )
        )
    if lean_burn:
        fields.extend(
            (
                ConfigurationField(
                    f"{prefix}.lean_burn_threshold_percent",
                    base + 0x2B,
                    ConfigurationFieldKind.LEAN_THRESHOLD,
                    0,
                    100,
                ),
                ConfigurationField(
                    f"{prefix}.lean_burn_fan_percent",
                    base + 0x2C,
                    ConfigurationFieldKind.LEAN_FAN,
                    -30,
                    30,
                ),
                ConfigurationField(
                    f"{prefix}.lean_burn_feed_percent",
                    base + 0x2D,
                    ConfigurationFieldKind.LEAN_FEED,
                    -30,
                    30,
                ),
                ConfigurationField(
                    f"{prefix}.ratio_ash_trimpot_mode",
                    base + 0x2E,
                    ConfigurationFieldKind.BIT,
                    mask=0x01,
                ),
                ConfigurationField(
                    f"{prefix}.disable_auto_restart",
                    base + 0x2E,
                    ConfigurationFieldKind.BIT,
                    mask=0x02,
                ),
            )
        )
    return fields


def _schema(data_format: int) -> ConfigurationSchema:
    if data_format not in CHECKSUM_END_BY_FORMAT:
        raise ValueError(f"unsupported configuration data format: {data_format:02X}")
    fields = [
        ConfigurationField(
            "data_format", 0x02, ConfigurationFieldKind.UINT8, 0, 255, writable=False
        ),
        ConfigurationField(
            "serial_number", 0x03, ConfigurationFieldKind.STRING, length=8, writable=False
        ),
        ConfigurationField(
            "production_date", 0x0B, ConfigurationFieldKind.STRING, length=8, writable=False
        ),
        ConfigurationField(
            "model_name", 0x13, ConfigurationFieldKind.STRING, length=16, writable=False
        ),
        ConfigurationField(
            "individualization_spare",
            0x23,
            ConfigurationFieldKind.STRING,
            length=13,
            writable=False,
        ),
    ]
    if data_format == 0x05:
        fields.extend(_fuel_fields("a", 0x40, thermostat=False, lean_burn=False))
        fields.extend(_fuel_fields("b", 0x70, thermostat=True, lean_burn=False))
    elif data_format == 0x07:
        fields.extend(_fuel_fields("a", 0x40, thermostat=True, lean_burn=True))
        fields.extend(_fuel_fields("b", 0x70, thermostat=True, lean_burn=True))
    return ConfigurationSchema(
        data_format=data_format,
        checksum_end=CHECKSUM_END_BY_FORMAT[data_format],
        fields=tuple(fields),
    )


SCHEMAS: Mapping[int, ConfigurationSchema] = MappingProxyType(
    {data_format: _schema(data_format) for data_format in CHECKSUM_END_BY_FORMAT}
)


def configuration_schema(data_format: int) -> ConfigurationSchema:
    try:
        return SCHEMAS[data_format]
    except KeyError as exc:
        raise ValueError(f"unsupported configuration data format: {data_format:02X}") from exc


@dataclass(frozen=True, slots=True)
class ConfigurationIssue:
    code: str
    message: str


@dataclass(frozen=True, slots=True)
class ConfigurationValidation:
    issues: tuple[ConfigurationIssue, ...]

    @property
    def valid(self) -> bool:
        return not self.issues


@dataclass(frozen=True, slots=True)
class ConfigurationChange:
    address: int
    before: int
    after: int
    fields: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "address": f"A{self.address:02X}",
            "before": f"{self.before:02X}",
            "after": f"{self.after:02X}",
            "fields": list(self.fields),
        }


@dataclass(frozen=True, slots=True)
class ConfigurationImage:
    raw: bytes

    def __post_init__(self) -> None:
        if len(self.raw) != 0x100:
            raise ValueError("configuration image must contain exactly 256 bytes")

    @classmethod
    def from_bytes(cls, raw: bytes | bytearray | memoryview) -> "ConfigurationImage":
        return cls(bytes(raw))

    @classmethod
    def from_mapping(cls, values: Mapping[int, int]) -> "ConfigurationImage":
        missing = [address for address in range(0x100) if address not in values]
        if missing:
            raise ValueError(f"configuration map is missing A{missing[0]:02X}")
        raw = bytearray(0x100)
        for address in range(0x100):
            value = values[address]
            if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= 0xFF:
                raise ValueError(f"configuration A{address:02X} is not a byte")
            raw[address] = value
        return cls(bytes(raw))

    @classmethod
    def from_backup_document(cls, document: Mapping[str, object]) -> "ConfigurationImage":
        raw_hex = document.get("raw_hex")
        if isinstance(raw_hex, str):
            try:
                return cls.from_bytes(bytes.fromhex(raw_hex))
            except ValueError as exc:
                raise ValueError("backup raw_hex is not valid hexadecimal") from exc
        eeprom = document.get("eeprom")
        if not isinstance(eeprom, Mapping):
            raise ValueError("backup must contain raw_hex or an eeprom mapping")
        values: dict[int, int] = {}
        for address in range(0x100):
            key = f"A{address:02X}"
            value = eeprom.get(key)
            if not isinstance(value, str):
                raise ValueError(f"backup is missing {key}")
            try:
                values[address] = int(value, 16)
            except ValueError as exc:
                raise ValueError(f"backup {key} is not hexadecimal") from exc
        return cls.from_mapping(values)

    @property
    def data_format(self) -> int:
        return self.raw[0x02]

    @property
    def stored_checksum(self) -> int:
        return (self.raw[0x00] << 8) | self.raw[0x01]

    @property
    def calculated_checksum(self) -> int:
        return calculate_configuration_checksum(self.data_format, self.raw[0x02:])

    @property
    def checksum_valid(self) -> bool:
        return self.stored_checksum == self.calculated_checksum

    def decoded(self) -> dict[str, object]:
        schema = configuration_schema(self.data_format)
        return {field.name: field.decode(self.raw) for field in schema.fields}

    def validate(self, profile: ControllerProfile | None = None) -> ConfigurationValidation:
        issues: list[ConfigurationIssue] = []
        try:
            calculated = self.calculated_checksum
        except ValueError as exc:
            issues.append(ConfigurationIssue("unsupported_format", str(exc)))
        else:
            if self.stored_checksum != calculated:
                issues.append(
                    ConfigurationIssue(
                        "checksum_mismatch",
                        f"stored {self.stored_checksum:04X} != calculated {calculated:04X}",
                    )
                )
        if profile and profile.data_format != self.data_format:
            issues.append(
                ConfigurationIssue(
                    "profile_format_mismatch",
                    f"profile {profile.key} expects format {profile.data_format:02X}, "
                    f"image contains {self.data_format:02X}",
                )
            )
        return ConfigurationValidation(tuple(issues))

    def with_checksum(self) -> "ConfigurationImage":
        updated = bytearray(self.raw)
        checksum = calculate_configuration_checksum(self.data_format, updated[0x02:])
        updated[0x00] = checksum >> 8
        updated[0x01] = checksum & 0xFF
        return ConfigurationImage(bytes(updated))

    def with_edits(
        self,
        edits: Mapping[str, object],
        *,
        allow_identity: bool = False,
    ) -> "ConfigurationImage":
        schema = configuration_schema(self.data_format)
        fields = schema.by_name
        unknown = sorted(name for name in edits if name not in fields)
        if unknown:
            raise ValueError(f"unknown configuration field: {unknown[0]}")
        updated = bytearray(self.raw)
        for name, value in edits.items():
            fields[name].encode_into(updated, value, allow_read_only=allow_identity)
        if updated[0x02] != self.data_format:
            raise ValueError("configuration edits cannot change data format")
        return ConfigurationImage(bytes(updated)).with_checksum()

    def diff(self, other: "ConfigurationImage") -> tuple[ConfigurationChange, ...]:
        schema = configuration_schema(other.data_format)
        changes: list[ConfigurationChange] = []
        for address, (before, after) in enumerate(zip(self.raw, other.raw)):
            if before == after:
                continue
            names = tuple(field.name for field in schema.fields_at(address))
            if address in (0x00, 0x01):
                names = ("stored_checksum",)
            changes.append(ConfigurationChange(address, before, after, names))
        return tuple(changes)


@dataclass(frozen=True, slots=True)
class ConfigurationPlan:
    profile_key: str
    current: ConfigurationImage
    target: ConfigurationImage
    changes: tuple[ConfigurationChange, ...]
    operations: tuple[TransactionOperation, ...]
    verify_addresses: tuple[int, ...]
    prewrite_backup_required: bool = True

    @property
    def has_writes(self) -> bool:
        return bool(self.operations)

    def to_dict(self) -> dict[str, object]:
        return {
            "schema": "openmaxfire.configuration-plan.v1",
            "profile_key": self.profile_key,
            "prewrite_backup_required": self.prewrite_backup_required,
            "source_checksum": f"{self.current.stored_checksum:04X}",
            "target_checksum": f"{self.target.stored_checksum:04X}",
            "changes": [change.to_dict() for change in self.changes],
            "operations": [operation.to_dict() for operation in self.operations],
            "verify_addresses": [f"A{address:02X}" for address in self.verify_addresses],
            "execution_supported": False,
            "evidence_boundary": (
                "Offline plan only; no EEPROM restore/write workflow is live-validated."
            ),
        }


def _plan(
    current: ConfigurationImage,
    target: ConfigurationImage,
    profile: ControllerProfile,
) -> ConfigurationPlan:
    current_validation = current.validate(profile)
    target_validation = target.validate(profile)
    if not current_validation.valid:
        raise ValueError(current_validation.issues[0].message)
    if not target_validation.valid:
        raise ValueError(target_validation.issues[0].message)
    changes = current.diff(target)
    changed = {change.address for change in changes}
    order = sorted(address for address in changed if address not in (0x00, 0x01))
    operations = tuple(
        TransactionOperation(
            op="write",
            unit="A",
            address=address,
            value=target.raw[address],
            verify=True,
            settle_delay=0.10,
        )
        for address in order
    )
    if order:
        # CW01 ignores its supplied value, recomputes the format-specific
        # checksum in firmware, and persists EEPROM A00/A01.  Keep that proven
        # controller operation after every A-space data write rather than
        # writing checksum bytes directly.
        operations += (
            TransactionOperation(
                op="write",
                unit="C",
                address=0x01,
                value=0x00,
                verify=False,
            ),
        )
    return ConfigurationPlan(
        profile_key=profile.key,
        current=current,
        target=target,
        changes=changes,
        operations=operations,
        verify_addresses=tuple(range(0x100)),
    )


def plan_configuration_update(
    current: ConfigurationImage,
    edits: Mapping[str, object],
    profile: ControllerProfile,
) -> ConfigurationPlan:
    """Build a no-I/O field edit plan with checksum bytes written last."""

    return _plan(current, current.with_edits(edits), profile)


def plan_configuration_restore(
    current: ConfigurationImage,
    target: ConfigurationImage,
    profile: ControllerProfile,
    *,
    allow_identity_changes: bool = False,
) -> ConfigurationPlan:
    """Build a no-I/O restore plan while preserving identity by default."""

    if current.data_format != target.data_format:
        raise ValueError("restore cannot change the controller data format")
    identity_range = range(0x02, 0x30)
    if not allow_identity_changes and any(
        current.raw[address] != target.raw[address] for address in identity_range
    ):
        raise PermissionError("restore would change data-format or identity bytes")
    return _plan(current, target, profile)
