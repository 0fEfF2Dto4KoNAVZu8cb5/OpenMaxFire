import unittest

from openmaxfire.experimental_flasher import (
    ExperimentalJ3Flasher,
    FlasherEventRecorder,
    PhysicalFlasherPolicy,
)
from openmaxfire.loader_entry import SOFTWARE_LOADER_RESET, reset_application_into_loader


class ResetTransitionTransport:
    def __init__(self):
        self.timeout = 0.25
        self.mode = "application"
        self.incoming = bytearray()
        self.writes = []
        self.closed = False

    def set_timeout(self, timeout):
        self.timeout = float(timeout)

    def write(self, data: bytes):
        payload = bytes(data)
        self.writes.append(payload)
        if self.mode == "application":
            responses = {
                b"CR00": b"CR0000\n",
                b"CR08": b"CR0805\n",
                b"CR0B": b"CR0b02\n",
                b"CR0C": b"CR0c06\n",
                b"CR0D": b"CR0d00\n",
                b"CR0E": b"CR0e00\n",
            }
            if payload == SOFTWARE_LOADER_RESET:
                self.mode = "loader"
                return
            self.incoming.extend(responses.get(payload, b""))
            return

        if payload == b"\xEA":
            self.incoming.extend(b"\xEB")
        elif payload.startswith(b"\xE3"):
            self.incoming.extend(b"\xE7\xE4")
        elif payload == b"\xED":
            self.incoming.extend(b"\xE4")

    def read(self, size: int = 1) -> bytes:
        if not self.incoming:
            return b""
        chunk = bytes(self.incoming[:size])
        del self.incoming[:size]
        return chunk

    def close(self):
        self.closed = True


class LoaderEntryTests(unittest.TestCase):
    def test_software_reset_verifies_application_then_enters_loader(self):
        transport = ResetTransitionTransport()
        recorder = FlasherEventRecorder(None)

        identity = reset_application_into_loader(transport, recorder, request_delay=0)

        self.assertEqual(identity.firmware_version, "2.06")
        self.assertEqual(identity.data_format, 0x05)
        self.assertEqual(transport.mode, "loader")
        self.assertIn(SOFTWARE_LOADER_RESET, transport.writes)

    def test_protected_test_after_software_reset_completes(self):
        transport = ResetTransitionTransport()
        recorder = FlasherEventRecorder(None)
        reset_application_into_loader(transport, recorder, request_delay=0)
        flasher = ExperimentalJ3Flasher(
            transport,
            policy=PhysicalFlasherPolicy(
                identify_attempts=3,
                identify_interval=0,
                identify_read_timeout=0.01,
                timeout_retries=0,
                checksum_retries=0,
            ),
            recorder=recorder,
        )

        result = flasher.run_protected_test()

        self.assertTrue(result["success"])
        reset_index = transport.writes.index(SOFTWARE_LOADER_RESET)
        ea_index = transport.writes.index(b"\xEA")
        self.assertLess(reset_index, ea_index)
        self.assertTrue(any(item.startswith(b"\xE3") for item in transport.writes))
        self.assertEqual(transport.writes[-1], b"\xED")
        self.assertEqual(transport.timeout, 0.25)


if __name__ == "__main__":
    unittest.main()
