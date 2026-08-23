"""Machine-readable BixCheck Checkout catalog and offline planning.

The 45 reachable factory tests are represented here as data.  This module does
not execute actuator commands; all such plans remain blocked until the relevant
controller profile is physically validated and cleanup/recovery is proven.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Mapping

from .profiles import Capability, CapabilityState, ControllerProfile
from .transactions import TransactionOperation


class CheckoutKind(str, Enum):
    VERIFICATION = "verification"
    PASSIVE = "passive"
    ACTUATOR = "actuator"
    MANUAL = "manual"


class CheckoutOutcome(str, Enum):
    PASS = "pass"
    FAIL = "fail"
    INDETERMINATE = "indeterminate"
    NOT_RUN = "not_run"


@dataclass(frozen=True, slots=True)
class RegisterExpectation:
    unit: str
    address: int
    mask: int = 0xFF
    expected: int | None = None
    minimum: int | None = None
    maximum: int | None = None

    def evaluate(self, values: Mapping[tuple[str, int], int]) -> CheckoutOutcome:
        value = values.get((self.unit, self.address))
        if value is None:
            return CheckoutOutcome.INDETERMINATE
        masked = value & self.mask
        if self.expected is not None and masked != self.expected:
            return CheckoutOutcome.FAIL
        if self.minimum is not None and masked < self.minimum:
            return CheckoutOutcome.FAIL
        if self.maximum is not None and masked > self.maximum:
            return CheckoutOutcome.FAIL
        return CheckoutOutcome.PASS

    def to_dict(self) -> dict[str, object]:
        return {
            "register": f"{self.unit}R{self.address:02X}",
            "mask": f"{self.mask:02X}",
            "expected": f"{self.expected:02X}" if self.expected is not None else None,
            "minimum": f"{self.minimum:02X}" if self.minimum is not None else None,
            "maximum": f"{self.maximum:02X}" if self.maximum is not None else None,
        }


@dataclass(frozen=True, slots=True)
class CheckoutTestDefinition:
    number: int
    key: str
    title: str
    kind: CheckoutKind
    instruction: str
    failure_hint: str = ""
    expectations: tuple[RegisterExpectation, ...] = ()
    command: tuple[int, int] | None = None
    command_by_format: Mapping[int, tuple[int, int]] | None = None
    cleanup: tuple[int, int] | None = None
    timeout_seconds: float | None = None
    evidence: str = "vendor BixCheck/manual plus static reconstruction"

    @property
    def state_changing(self) -> bool:
        return self.command is not None or self.command_by_format is not None

    def command_for(self, profile: ControllerProfile) -> tuple[int, int] | None:
        if self.command_by_format is not None:
            return self.command_by_format.get(profile.data_format)
        return self.command

    def evaluate(self, values: Mapping[tuple[str, int], int]) -> CheckoutOutcome:
        if not self.expectations:
            return CheckoutOutcome.INDETERMINATE
        outcomes = tuple(expectation.evaluate(values) for expectation in self.expectations)
        if CheckoutOutcome.FAIL in outcomes:
            return CheckoutOutcome.FAIL
        if CheckoutOutcome.INDETERMINATE in outcomes:
            return CheckoutOutcome.INDETERMINATE
        return CheckoutOutcome.PASS

    def to_dict(self) -> dict[str, object]:
        return {
            "number": self.number,
            "key": self.key,
            "title": self.title,
            "kind": self.kind.value,
            "instruction": self.instruction,
            "failure_hint": self.failure_hint,
            "state_changing": self.state_changing,
            "expectations": [item.to_dict() for item in self.expectations],
            "timeout_seconds": self.timeout_seconds,
            "evidence": self.evidence,
        }


def _expect(address: int, expected: int, *, mask: int = 0xFF) -> RegisterExpectation:
    return RegisterExpectation("C", address, mask=mask, expected=expected)


def _passive(
    number: int,
    key: str,
    title: str,
    instruction: str,
    *expectations: RegisterExpectation,
    failure_hint: str = "",
) -> CheckoutTestDefinition:
    return CheckoutTestDefinition(
        number,
        key,
        title,
        CheckoutKind.PASSIVE,
        instruction,
        failure_hint,
        tuple(expectations),
    )


def _manual(
    number: int,
    key: str,
    title: str,
    instruction: str,
    *,
    failure_hint: str = "",
) -> CheckoutTestDefinition:
    return CheckoutTestDefinition(
        number,
        key,
        title,
        CheckoutKind.MANUAL,
        instruction,
        failure_hint,
    )


_TESTS: list[CheckoutTestDefinition] = [
    CheckoutTestDefinition(1, "communication", "Data communications link", CheckoutKind.VERIFICATION, "Read controller identity", "Connection or software version"),
    CheckoutTestDefinition(2, "checksum", "Configuration checksum verified", CheckoutKind.VERIFICATION, "Read EEPROM and verify its checksum", "Configuration/checksum mismatch"),
    CheckoutTestDefinition(3, "data_format", "Data format matched", CheckoutKind.VERIFICATION, "Compare controller and EEPROM data formats", "Incorrect software/data format"),
    _passive(4, "buttons_none", "No front-panel buttons pressed", "Do not press any front-panel buttons", _expect(0x01, 0x00)),
    _passive(5, "button_on", "Front-panel ON button", "Press only ON", _expect(0x01, 0x02)),
    _passive(6, "button_off", "Front-panel OFF button", "Press only OFF", _expect(0x01, 0x01)),
    _passive(7, "button_up", "Front-panel UP button", "Press only UP", _expect(0x01, 0x04)),
    _passive(8, "button_down", "Front-panel DOWN button", "Press only DOWN", _expect(0x01, 0x08)),
    CheckoutTestDefinition(9, "leds_on", "All front-panel LEDs on", CheckoutKind.ACTUATOR, "Confirm all LEDs illuminate", "Control cable", command=(0x04, 0xFF), cleanup=(0x04, 0x00), timeout_seconds=10.0),
    CheckoutTestDefinition(10, "leds_off", "All front-panel LEDs off", CheckoutKind.ACTUATOR, "Confirm all LEDs turn off", "Control cable", command=(0x04, 0x00), cleanup=(0x04, 0x00), timeout_seconds=10.0),
    _passive(11, "door_open", "Door switch open", "Open the front door", _expect(0x02, 0x20, mask=0x20), failure_hint="Switch wiring or circuit board"),
    _passive(12, "door_closed", "Door switch closed", "Close the front door", _expect(0x02, 0x00, mask=0x20), failure_hint="Switch wiring or switch tab"),
    _passive(13, "drawer_open", "Ash-drawer switch open", "Open the ash drawer", _expect(0x02, 0x40, mask=0x40), failure_hint="Switch wiring"),
    _passive(14, "drawer_closed", "Ash-drawer switch closed", "Close the ash drawer", _expect(0x02, 0x00, mask=0x40), failure_hint="Switch wiring"),
    CheckoutTestDefinition(15, "plate_motor_on", "Plate motor on", CheckoutKind.ACTUATOR, "Confirm the plate motor runs", "Motor wiring", command=(0x05, 0x00), timeout_seconds=30.0),
    _passive(16, "plate_motor_off", "Plate motor off", "Wait for the plate motor to stop", _expect(0x02, 0x01, mask=0x01), _expect(0x03, 0x00, mask=0x02), failure_hint="Limit switch"),
    _manual(17, "plates_burn_position", "Plates in burn position", "Confirm the plates are in burn position", failure_hint="Limit switch or motor brake"),
    CheckoutTestDefinition(18, "air_pump_on", "Air pump on", CheckoutKind.ACTUATOR, "Confirm the air pump runs", "Pump wiring", command=(0x06, 0x00), cleanup=(0x07, 0x00), timeout_seconds=10.0),
    CheckoutTestDefinition(19, "air_pump_off", "Air pump off", CheckoutKind.ACTUATOR, "Confirm the air pump stops", "Pump wiring", command=(0x07, 0x00), cleanup=(0x07, 0x00), timeout_seconds=10.0),
]


for number, level, old, new in (
    (20, 1, 0x01, 0x19),
    (21, 2, 0x02, 0x32),
    (22, 3, 0x03, 0x4B),
    (23, 4, 0x04, 0x64),
):
    _TESTS.append(
        CheckoutTestDefinition(
            number,
            f"convection_{level}",
            f"Convection fan level {level}",
            CheckoutKind.ACTUATOR,
            f"Confirm convection fan level {level}",
            "Fan wiring",
            command_by_format=MappingProxyType(
                {0x04: (0x08, old), 0x05: (0x08, old), 0x07: (0x08, new)}
            ),
            cleanup=(0x08, 0x00),
            timeout_seconds=10.0,
        )
    )


_TESTS.extend(
    (
        CheckoutTestDefinition(24, "convection_off", "Convection fan off", CheckoutKind.ACTUATOR, "Confirm the convection fan stops", "Fan wiring", command=(0x08, 0x00), cleanup=(0x08, 0x00), timeout_seconds=10.0),
        _manual(25, "thermometer", "Board thermometer plausibility", "Read CR04 and confirm a plausible temperature", failure_hint="Igniter-board wiring"),
        _manual(26, "fan_pot_low", "Fan potentiometer low", "Turn the fan potentiometer fully left"),
        _manual(27, "fan_pot_high", "Fan potentiometer high", "Turn the fan potentiometer fully right"),
        _manual(28, "fan_pot_center", "Fan potentiometer center detent", "Turn the fan potentiometer to center detent"),
        _manual(29, "feed_pot_low", "Feed potentiometer low", "Turn the feed potentiometer fully left"),
        _manual(30, "feed_pot_high", "Feed potentiometer high", "Turn the feed potentiometer fully right"),
        _manual(31, "feed_pot_center", "Feed potentiometer center detent", "Turn the feed potentiometer to center detent"),
        _manual(32, "thermocouple", "Thermocouple connected", "Confirm the thermocouple is connected", failure_hint="Connection"),
        _passive(33, "thermostat_open", "Thermostat open", "Open the thermostat contact", _expect(0x06, 0x04, mask=0x04)),
        _passive(34, "thermostat_closed", "Thermostat closed", "Close the thermostat contact", _expect(0x06, 0x00, mask=0x04)),
        _manual(35, "power_wiring", "Power-inlet wiring observation", "Inspect factory power-inlet wire order"),
        _passive(36, "fuel_b_wood", "Fuel switch wood/Fuel B", "Select wood/Fuel B", _expect(0x02, 0x00, mask=0x04)),
        _passive(37, "fuel_a_corn", "Fuel switch corn/Fuel A", "Select corn/Fuel A", _expect(0x02, 0x04, mask=0x04)),
        CheckoutTestDefinition(38, "exhaust_full", "Exhaust fan full power", CheckoutKind.ACTUATOR, "Run the exhaust fan at full power", "Fan wiring or R59", expectations=(RegisterExpectation("C", 0x05, minimum=0x78),), command=(0x09, 0x80), cleanup=(0x09, 0x00), timeout_seconds=15.0),
        CheckoutTestDefinition(39, "exhaust_half", "Exhaust fan half power", CheckoutKind.ACTUATOR, "Run the exhaust fan at half power", "Fan wiring or R59", expectations=(RegisterExpectation("C", 0x05, minimum=0x38, maximum=0x48),), command=(0x09, 0x40), cleanup=(0x09, 0x00), timeout_seconds=15.0),
        CheckoutTestDefinition(40, "exhaust_off", "Exhaust fan off", CheckoutKind.ACTUATOR, "Stop the exhaust fan", "Fan wiring or R59", expectations=(RegisterExpectation("C", 0x05, maximum=0x03),), command=(0x09, 0x00), cleanup=(0x09, 0x00), timeout_seconds=15.0),
        CheckoutTestDefinition(41, "igniter_1_test", "Left/#1 igniter test", CheckoutKind.ACTUATOR, "Run the timed igniter-1 workflow", "Igniter connection, fuse, or igniter", timeout_seconds=270.0),
        CheckoutTestDefinition(42, "igniter_2_test", "Right/#2 igniter test", CheckoutKind.ACTUATOR, "Run the timed igniter-2 workflow", "Igniter connection, fuse, or igniter", command=(0x0D, 0x00), timeout_seconds=270.0),
        CheckoutTestDefinition(43, "igniter_1_check", "Left/#1 igniter follow-up", CheckoutKind.ACTUATOR, "Check igniter-1 result", "Igniter connection, fuse, or igniter"),
        CheckoutTestDefinition(44, "igniter_2_check", "Right/#2 igniter follow-up", CheckoutKind.ACTUATOR, "Check igniter-2 result", "Igniter connection, fuse, or igniter", command=(0x0A, 0x00)),
        CheckoutTestDefinition(45, "feed_motor_sensor", "Feed motor and sensor", CheckoutKind.ACTUATOR, "Test feed motor, magnets, and sensor", "Sensor, motor, or magnets", expectations=(RegisterExpectation("C", 0x07, minimum=0x10, maximum=0x68),), command=(0x0B, 0x20), timeout_seconds=30.0),
    )
)


if tuple(test.number for test in _TESTS) != tuple(range(1, 46)):
    raise RuntimeError("Checkout catalog must contain exactly tests 1 through 45")

CHECKOUT_TESTS: tuple[CheckoutTestDefinition, ...] = tuple(_TESTS)
CHECKOUT_TESTS_BY_NUMBER: Mapping[int, CheckoutTestDefinition] = MappingProxyType(
    {test.number: test for test in CHECKOUT_TESTS}
)


@dataclass(frozen=True, slots=True)
class CheckoutPlan:
    profile_key: str
    test: CheckoutTestDefinition
    operations: tuple[TransactionOperation, ...]
    cleanup: tuple[TransactionOperation, ...]
    executable: bool
    blockers: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "schema": "openmaxfire.checkout-plan.v1",
            "profile_key": self.profile_key,
            "test": self.test.to_dict(),
            "operations": [operation.to_dict() for operation in self.operations],
            "cleanup": [operation.to_dict() for operation in self.cleanup],
            "executable": self.executable,
            "blockers": list(self.blockers),
        }


def checkout_test(number: int) -> CheckoutTestDefinition:
    try:
        return CHECKOUT_TESTS_BY_NUMBER[number]
    except KeyError as exc:
        raise ValueError("Checkout test number must be between 1 and 45") from exc


def plan_checkout_test(number: int, profile: ControllerProfile) -> CheckoutPlan:
    """Return an offline plan; actuator execution remains deliberately blocked."""

    test = checkout_test(number)
    command = test.command_for(profile)
    operations = (
        (
            TransactionOperation(
                op="write", unit="C", address=command[0], value=command[1]
            ),
        )
        if command
        else ()
    )
    cleanup = (
        (
            TransactionOperation(
                op="write", unit="C", address=test.cleanup[0], value=test.cleanup[1]
            ),
        )
        if test.cleanup
        else ()
    )
    blockers: list[str] = []
    if test.kind in (CheckoutKind.MANUAL, CheckoutKind.VERIFICATION):
        blockers.append("requires a higher-level observation/verification provider")
    if test.kind is CheckoutKind.ACTUATOR:
        state = profile.capabilities.state(Capability.CHECKOUT_ACTUATOR)
        if state is not CapabilityState.AVAILABLE:
            blockers.append(f"actuator Checkout capability is {state.value}")
        if command is None:
            blockers.append("complete action sequence is not reconstructed")
        if test.cleanup is None:
            blockers.append("proven actuator-off cleanup is not available")
    if test.command_by_format is not None and command is None:
        blockers.append("no command encoding is known for this data format")
    return CheckoutPlan(
        profile_key=profile.key,
        test=test,
        operations=operations,
        cleanup=cleanup,
        executable=not blockers,
        blockers=tuple(blockers),
    )


@dataclass(frozen=True, slots=True)
class CheckoutResult:
    test_number: int
    outcome: CheckoutOutcome
    observations: Mapping[str, object]
    message: str = ""


@dataclass(frozen=True, slots=True)
class CheckoutReport:
    profile_key: str
    configuration_checksum: str
    configuration_backup_sha256: str
    results: tuple[CheckoutResult, ...]

    @property
    def complete(self) -> bool:
        return {result.test_number for result in self.results} == set(range(1, 46))

    @property
    def passed(self) -> bool:
        return self.complete and all(
            result.outcome is CheckoutOutcome.PASS for result in self.results
        )
