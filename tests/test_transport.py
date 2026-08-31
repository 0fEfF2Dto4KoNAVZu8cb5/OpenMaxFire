import json
import tempfile
import unittest
from pathlib import Path
from types import ModuleType, SimpleNamespace
from unittest import mock

from openmaxfire.transport import (
    JsonlTrafficRecorder,
    RecordingTransport,
    SerialSettings,
    SerialTransport,
    list_serial_ports,
)


class FakeTransport:
    def __init__(self):
        self.writes = []
        self.reads = [b"CR", b"0000\n"]
        self.closed = False
        self.break_states = []

    def write(self, data):
        self.writes.append(data)

    def read(self, _size=1):
        return self.reads.pop(0) if self.reads else b""

    def set_break(self, active):
        self.break_states.append(active)

    def close(self):
        self.closed = True


class TransportTests(unittest.TestCase):
    def test_port_listing_is_sorted_and_normalized(self):
        ports = [
            SimpleNamespace(
                device="COM9",
                description="USB Serial",
                hwid="USB VID:PID=0403:6001",
                vid=0x0403,
                pid=0x6001,
                serial_number="ABC",
                manufacturer="FTDI",
                product="FT232R",
                location="1-2",
            ),
            SimpleNamespace(
                device="COM2",
                description="Communications Port",
                hwid="ACPI",
                vid=None,
                pid=None,
                serial_number=None,
                manufacturer=None,
                product=None,
                location=None,
            ),
        ]
        serial_module = ModuleType("serial")
        tools_module = ModuleType("serial.tools")
        list_ports_module = ModuleType("serial.tools.list_ports")
        list_ports_module.comports = mock.Mock(return_value=ports)
        tools_module.list_ports = list_ports_module
        serial_module.tools = tools_module
        with mock.patch.dict(
            "sys.modules",
            {
                "serial": serial_module,
                "serial.tools": tools_module,
                "serial.tools.list_ports": list_ports_module,
            },
        ):
            result = list_serial_ports()
        self.assertEqual([item.device for item in result], ["COM2", "COM9"])
        self.assertEqual(result[1].usb_id, "0403:6001")
        self.assertEqual(result[1].to_dict()["manufacturer"], "FTDI")

    def test_settings_reject_invalid_values(self):
        with self.assertRaises(ValueError):
            SerialSettings("", 9600)
        with self.assertRaises(ValueError):
            SerialSettings("COM3", 0)
        with self.assertRaises(ValueError):
            SerialSettings("COM3", 9600, 0)
        with self.assertRaises(ValueError):
            SerialSettings("COM3", 9600, float("nan"))

    def test_serial_transport_applies_bixcheck_settings_portably(self):
        serial_module = ModuleType("serial")
        serial_module.EIGHTBITS = 8
        serial_module.PARITY_NONE = "N"
        serial_module.STOPBITS_ONE = 1
        device = mock.Mock()
        device.write.return_value = 4
        serial_module.Serial = mock.Mock(return_value=device)
        with mock.patch.dict("sys.modules", {"serial": serial_module}):
            transport = SerialTransport(SerialSettings("COM7", 19200, 0.35))
            transport.write(b"CR00")
            transport.set_break(True)
            self.assertTrue(device.break_condition)
            transport.set_break(False)
            self.assertFalse(device.break_condition)
            transport.close()
        serial_module.Serial.assert_called_once_with(
            port="COM7",
            baudrate=19200,
            bytesize=8,
            parity="N",
            stopbits=1,
            timeout=0.35,
            write_timeout=0.35,
            xonxoff=False,
            rtscts=False,
            dsrdtr=False,
            exclusive=None,
        )
        device.write.assert_called_once_with(b"CR00")
        device.flush.assert_called_once_with()
        device.close.assert_called_once_with()

    def test_recording_transport_preserves_exact_chunks(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "capture.jsonl"
            base = FakeTransport()
            recorder = JsonlTrafficRecorder(path, metadata={"port": "COM3"})
            transport = RecordingTransport(base, recorder)
            transport.write(b"CR00")
            transport.set_break(True)
            transport.set_break(False)
            self.assertEqual(transport.read(2), b"CR")
            self.assertEqual(transport.read(5), b"0000\n")
            transport.close()

            events = [json.loads(line) for line in path.read_text().splitlines()]
            self.assertEqual(events[0]["event"], "session")
            self.assertEqual(events[0]["metadata"]["port"], "COM3")
            self.assertEqual(
                [(item["direction"], item["data_hex"]) for item in events[1:]],
                [("tx", "43 52 30 30"), ("rx", "43 52"), ("rx", "30 30 30 30 0A")],
            )
            self.assertTrue(base.closed)
            self.assertEqual(base.break_states, [True, False])


if __name__ == "__main__":
    unittest.main()
