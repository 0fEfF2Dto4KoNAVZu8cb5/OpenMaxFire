import signal
import unittest
from types import SimpleNamespace
from unittest import mock

from openmaxfire.errors import SafetyInterlockError
from openmaxfire.runtime_safety import DeferredTerminationSignals, SleepInhibitor


class FakeInhibitorProcess:
    def __init__(self):
        self.stderr = SimpleNamespace(read=lambda: "")
        self.terminated = False
        self.killed = False

    def poll(self):
        return None

    def terminate(self):
        self.terminated = True

    def wait(self, timeout=None):
        return 0

    def kill(self):
        self.killed = True


class RuntimeSafetyTests(unittest.TestCase):
    def test_linux_sleep_inhibitor_is_held_and_released(self):
        process = FakeInhibitorProcess()

        def which(name):
            return f"/usr/bin/{name}"

        with mock.patch("openmaxfire.runtime_safety.platform.system", return_value="Linux"):
            with mock.patch("openmaxfire.runtime_safety.shutil.which", side_effect=which):
                with mock.patch(
                    "openmaxfire.runtime_safety.subprocess.Popen", return_value=process
                ) as popen:
                    with mock.patch("openmaxfire.runtime_safety.time.sleep"):
                        with SleepInhibitor() as inhibitor:
                            self.assertTrue(inhibitor.active)
                            self.assertEqual(inhibitor.backend, "linux.systemd-inhibit")
                            inhibitor.ensure_active()
        command = popen.call_args.args[0]
        self.assertIn("--what=sleep:shutdown:idle", command)
        self.assertIn("--mode=block", command)
        self.assertTrue(process.terminated)
        self.assertFalse(process.killed)

    def test_sleep_inhibitor_fails_closed_when_backend_is_missing(self):
        with mock.patch("openmaxfire.runtime_safety.platform.system", return_value="Linux"):
            with mock.patch("openmaxfire.runtime_safety.shutil.which", return_value=None):
                with self.assertRaises(SafetyInterlockError):
                    SleepInhibitor().__enter__()

    def test_sleep_inhibitor_detects_helper_exit_before_programming(self):
        process = FakeInhibitorProcess()
        with mock.patch("openmaxfire.runtime_safety.platform.system", return_value="Linux"):
            with mock.patch(
                "openmaxfire.runtime_safety.shutil.which",
                side_effect=lambda name: f"/usr/bin/{name}",
            ):
                with mock.patch(
                    "openmaxfire.runtime_safety.subprocess.Popen", return_value=process
                ):
                    with mock.patch("openmaxfire.runtime_safety.time.sleep"):
                        inhibitor = SleepInhibitor().__enter__()
        process.poll = lambda: 1
        with self.assertRaises(SafetyInterlockError):
            inhibitor.ensure_active()
        inhibitor.close()

    def test_terminal_signals_are_deferred_and_reported(self):
        received = []
        guard = DeferredTerminationSignals(received.append)
        previous = signal.getsignal(signal.SIGINT)
        with guard:
            guard._handler(signal.SIGINT, None)
            self.assertTrue(guard.requested)
            self.assertEqual(guard.signal_names, ("SIGINT",))
            self.assertEqual(received, [])
        self.assertEqual(signal.getsignal(signal.SIGINT), previous)
        self.assertEqual(received, [signal.SIGINT])


if __name__ == "__main__":
    unittest.main()
