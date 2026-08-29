"""Runtime guards for an uninterrupted firmware-programming window."""

from __future__ import annotations

import ctypes
import os
import platform
import shutil
import signal
import subprocess
import time
from collections.abc import Callable

from .errors import SafetyInterlockError


class SleepInhibitor:
    """Prevent automatic host sleep while a physical update is in progress.

    This cannot prevent loss of mains power, a forced shutdown, a closed laptop
    lid on every platform, or a process kill.  It removes the avoidable
    automatic-idle failure mode and fails closed if the operating system cannot
    establish an inhibitor.
    """

    def __init__(self, reason: str = "OpenMaxFire firmware update in progress"):
        if not isinstance(reason, str) or not reason.strip():
            raise ValueError("sleep-inhibitor reason must be non-empty")
        self.reason = reason.strip()
        self.backend: str | None = None
        self._process: subprocess.Popen[str] | None = None
        self._windows_active = False

    @property
    def active(self) -> bool:
        return self.backend is not None

    def ensure_active(self) -> None:
        """Fail if the acquired assertion disappeared before programming."""

        if self.backend is None:
            raise SafetyInterlockError("host sleep inhibitor is not active")
        if self._windows_active:
            return
        if self._process is None or self._process.poll() is not None:
            raise SafetyInterlockError(
                "host sleep inhibitor exited before flashing reached a safe boundary"
            )

    def __enter__(self) -> "SleepInhibitor":
        system = platform.system()
        if system == "Windows":
            # Microsoft documents ES_CONTINUOUS | ES_SYSTEM_REQUIRED as the
            # persistent request that keeps the system in its working state.
            flags = 0x80000000 | 0x00000001
            result = ctypes.windll.kernel32.SetThreadExecutionState(flags)  # type: ignore[attr-defined]
            if result == 0:
                raise SafetyInterlockError(
                    "Windows refused the required sleep-inhibition request"
                )
            self._windows_active = True
            self.backend = "windows.SetThreadExecutionState"
            return self

        if system == "Darwin":
            executable = "/usr/bin/caffeinate"
            if not os.path.isfile(executable):
                raise SafetyInterlockError(
                    "macOS sleep inhibitor /usr/bin/caffeinate is unavailable"
                )
            command = [executable, "-di", "-w", str(os.getpid())]
            backend = "macos.caffeinate"
        elif system == "Linux":
            inhibit = shutil.which("systemd-inhibit")
            sleeper = shutil.which("sleep")
            if inhibit is None or sleeper is None:
                raise SafetyInterlockError(
                    "Linux systemd-inhibit and sleep are required for live flashing"
                )
            command = [
                inhibit,
                "--what=sleep:shutdown:idle",
                "--who=OpenMaxFire",
                f"--why={self.reason}",
                "--mode=block",
                sleeper,
                "infinity",
            ]
            backend = "linux.systemd-inhibit"
        else:
            raise SafetyInterlockError(
                f"automatic sleep inhibition is not implemented for {system or 'this OS'}"
            )

        try:
            process = subprocess.Popen(
                command,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                text=True,
            )
        except OSError as exc:
            raise SafetyInterlockError(
                f"could not start the required host sleep inhibitor: {exc}"
            ) from exc
        # Both helpers remain running while their inhibitor is held.  A quick
        # exit means the OS rejected the request (for example, no logind bus).
        time.sleep(0.10)
        if process.poll() is not None:
            stderr = (process.stderr.read() if process.stderr is not None else "").strip()
            raise SafetyInterlockError(
                "the host sleep inhibitor exited before programming"
                + (f": {stderr}" if stderr else "")
            )
        self._process = process
        self.backend = backend
        return self

    def close(self) -> None:
        process = self._process
        self._process = None
        if process is not None:
            process.terminate()
            try:
                process.wait(timeout=2.0)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=2.0)
        if self._windows_active:
            ctypes.windll.kernel32.SetThreadExecutionState(0x80000000)  # type: ignore[attr-defined]
            self._windows_active = False
        self.backend = None

    def __exit__(self, exc_type, exc, traceback) -> None:
        self.close()


class DeferredTerminationSignals:
    """Defer ordinary terminal/process cancellation during Flash writes.

    The handler deliberately does not re-raise after the critical section.  A
    caller can inspect :attr:`requested` and report that cancellation was
    deferred until the controller reached a recoverable application state.
    SIGKILL, power loss, and operating-system failure remain outside software's
    control.
    """

    def __init__(self, callback: Callable[[int], None] | None = None):
        self.callback = callback
        self.received: list[int] = []
        self._previous: dict[int, object] = {}

    @property
    def requested(self) -> bool:
        return bool(self.received)

    @property
    def signal_names(self) -> tuple[str, ...]:
        return tuple(signal.Signals(item).name for item in self.received)

    def _handler(self, signum: int, _frame: object) -> None:
        # Keep the actual signal handler minimal. Console and journal I/O can
        # allocate, block, or re-enter code that the signal interrupted, so the
        # callback runs only after the protected loader exchange exits.
        self.received.append(signum)

    def __enter__(self) -> "DeferredTerminationSignals":
        candidates = [signal.SIGINT, signal.SIGTERM]
        if hasattr(signal, "SIGBREAK"):
            candidates.append(signal.SIGBREAK)  # type: ignore[attr-defined]
        try:
            for item in candidates:
                self._previous[item] = signal.getsignal(item)
                signal.signal(item, self._handler)
        except (OSError, RuntimeError, ValueError) as exc:
            for item, previous in self._previous.items():
                signal.signal(item, previous)
            self._previous.clear()
            raise SafetyInterlockError(
                "could not install cancellation deferral before programming"
            ) from exc
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        for item, previous in self._previous.items():
            signal.signal(item, previous)
        self._previous.clear()
        if self.callback is not None:
            for signum in self.received:
                try:
                    self.callback(signum)
                except Exception:
                    # A broken console or diagnostic callback must not obscure
                    # the loader result after the critical exchange.
                    pass


__all__ = ["DeferredTerminationSignals", "SleepInhibitor"]
