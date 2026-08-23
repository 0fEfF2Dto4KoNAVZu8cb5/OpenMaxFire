import unittest

from openmaxfire.monitor import MonitorState
from openmaxfire.protocol import AddressedResponse, TelemetryResponse


def addressed(address, value):
    return AddressedResponse("C", "R", address, value, f"CR{address:02x}{value:02x}".encode())


class TypedSnapshotTests(unittest.TestCase):
    def test_later_profile_decodes_documented_measurements(self):
        state = MonitorState(stale_after=10)
        for address, value in {
            0x00: 0,
            0x01: 4,
            0x02: 0x24,
            0x06: 4,
            0x08: 7,
            0x0B: 2,
            0x0C: 0x71,
            0x0D: 0,
            0x0E: 0,
        }.items():
            state.observe(addressed(address, value), monotonic_ns=1)
        for frame in (
            TelemetryResponse(0x00, (0xFE,), b"T00fe"),
            TelemetryResponse(0x02, (0xFF,), b"T02ff"),
            TelemetryResponse(0x04, (10,), b"T040a"),
            TelemetryResponse(0x08, (7,), b"T0807"),
            TelemetryResponse(0x09, (0x4B,), b"T094b"),
            TelemetryResponse(0x0A, (0x12, 0x34), b"T0a1234"),
            TelemetryResponse(0x0E, (0x00, 0x78), b"T0e0078"),
            TelemetryResponse(0x10, (0x00, 0x78), b"T100078"),
            TelemetryResponse(0x13, (0xA5,), b"T13a5"),
        ):
            state.observe(frame, monotonic_ns=1)

        snapshot = state.typed_snapshot(now_monotonic_ns=2)
        self.assertEqual(snapshot.profile_key, "fw271-format07")
        self.assertEqual(snapshot.telemetry.board_temperature_c, -2)
        self.assertEqual(snapshot.telemetry.board_temperature_f, 29)
        self.assertEqual(snapshot.telemetry.fan_trim_percent, 30)
        self.assertEqual(snapshot.telemetry.exhaust_fan_rpm, 240)
        self.assertEqual(snapshot.telemetry.ash_level, 0x1234)
        self.assertEqual(snapshot.telemetry.feed_cycle_seconds, 2.0)
        self.assertEqual(snapshot.target_heat_level, 4)
        self.assertTrue(snapshot.operating_state.thermostat)
        self.assertEqual(snapshot.alarms.raw, 0xA5)

    def test_format04_does_not_apply_later_state_decoder(self):
        state = MonitorState()
        for address, value in {
            0x00: 0,
            0x08: 4,
            0x0B: 2,
            0x0C: 2,
            0x0D: 0,
            0x0E: 0,
        }.items():
            state.observe(addressed(address, value), monotonic_ns=1)
        state.observe(TelemetryResponse(0x08, (0x18,), b"T0818"), monotonic_ns=1)
        state.observe(TelemetryResponse(0x09, (0x4B,), b"T094b"), monotonic_ns=1)
        typed = state.typed_snapshot(now_monotonic_ns=1)
        self.assertIsNone(typed.operating_state)
        self.assertEqual(typed.telemetry.format04_state_unresolved_raw, 0x4B)
        self.assertTrue(typed.alarms.firebox_door_warning)
        self.assertTrue(typed.alarms.ash_drawer_warning)


if __name__ == "__main__":
    unittest.main()
