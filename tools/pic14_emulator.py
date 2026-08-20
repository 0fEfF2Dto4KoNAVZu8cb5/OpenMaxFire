#!/usr/bin/env python3
"""Experimental PIC16F877A CPU/UART emulator for preserved Bixby firmware.

This is a reverse-engineering harness, not a safety-qualified appliance model.
It implements the complete 35-instruction mid-range PIC14 core plus the small
set of PIC16F877A peripheral behaviors needed to explore startup, EEPROM reads,
and UART receive/transmit paths.  Analog, timer, watchdog, and external-I/O
behavior is deliberately synthetic.

The project command performs read-only probes against copies of the preserved
firmware images and writes evidence under reverse-engineering/firmware/emulation.
It never connects to a stove and never modifies the source HEX files.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, deque
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable, Iterable


try:
    from firmware_pipeline import IHexImage, decode_pic14, parse_ihex, region_for_word
except ModuleNotFoundError:
    from tools.firmware_pipeline import (  # type: ignore[no-redef]
        IHexImage,
        decode_pic14,
        parse_ihex,
        region_for_word,
    )


STATUS_C = 0
STATUS_DC = 1
STATUS_Z = 2
STATUS_PD = 3
STATUS_TO = 4
STATUS_RP0 = 5
STATUS_RP1 = 6
STATUS_IRP = 7

SFR_INDF = 0x000
SFR_TMR0 = 0x001
SFR_PCL = 0x002
SFR_STATUS = 0x003
SFR_FSR = 0x004
SFR_PCLATH = 0x00A
SFR_INTCON = 0x00B
SFR_PIR1 = 0x00C
SFR_TMR1L = 0x00E
SFR_TMR1H = 0x00F
SFR_TMR2 = 0x011
SFR_SSPBUF = 0x013
SFR_RCSTA = 0x018
SFR_TXREG = 0x019
SFR_RCREG = 0x01A
SFR_ADCON0 = 0x01F
SFR_PIE1 = 0x08C
SFR_SSPCON2 = 0x091
SFR_PR2 = 0x092
SFR_TXSTA = 0x098
SFR_SPBRG = 0x099
SFR_EEDATA = 0x10C
SFR_EEADR = 0x10D
SFR_EECON1 = 0x18C

INTCON_T0IF = 2
INTCON_PEIE = 6
INTCON_GIE = 7
PIR1_TMR1IF = 0
PIR1_TMR2IF = 1
PIR1_TXIF = 4
PIR1_RCIF = 5
PIE1_RCIE = 5


class EmulationError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class TraceEvent:
    step: int
    kind: str
    pc: int
    value: int | None
    detail: str


@dataclass(frozen=True, slots=True)
class InstructionTrace:
    step: int
    pc: int
    word: int
    mnemonic: str
    operands: str
    w: int
    status: int


class PIC16F877A:
    """Instruction-accurate core with deterministic lightweight peripherals."""

    def __init__(self, image: IHexImage, *, fast_forward_delays: bool = True):
        self.words = {
            address: word & 0x3FFF
            for address, word in image.words.items()
            if region_for_word(address) == "program"
        }
        self.eeprom = {
            address - 0x2100: word & 0xFF
            for address, word in image.words.items()
            if region_for_word(address) == "eeprom"
        }
        self.ram = bytearray(0x200)
        self.w = 0
        self.pc = 0
        self.stack: list[int] = []
        self.steps = 0
        self.sleeping = False
        self.rx_queue: deque[int] = deque()
        self.tx_bytes = bytearray()
        self.events: list[TraceEvent] = []
        self.recent: deque[InstructionTrace] = deque(maxlen=1024)
        self.pc_hits: Counter[int] = Counter()
        self.fast_forward_delays = fast_forward_delays
        self.accelerated_delay_loops = 0
        self.ram[SFR_STATUS] = (1 << STATUS_TO) | (1 << STATUS_PD)
        self.ram[SFR_PIR1] = 1 << PIR1_TXIF
        self.ram[SFR_PR2] = 0xFF

    @property
    def status(self) -> int:
        return self.ram[SFR_STATUS]

    @status.setter
    def status(self, value: int) -> None:
        self.ram[SFR_STATUS] = value & 0xFF

    def _flag(self, bit: int) -> bool:
        return bool(self.status & (1 << bit))

    def _set_flag(self, bit: int, enabled: bool) -> None:
        if enabled:
            self.status |= 1 << bit
        else:
            self.status &= ~(1 << bit)

    def _set_z(self, value: int) -> None:
        self._set_flag(STATUS_Z, (value & 0xFF) == 0)

    def _resolve_direct(self, file_register: int) -> int:
        file_register &= 0x7F
        if file_register in (0x00, 0x02, 0x03, 0x04, 0x0A, 0x0B):
            return file_register
        if 0x70 <= file_register <= 0x7F:
            return file_register
        bank = (self.status >> STATUS_RP0) & 0x03
        return (bank << 7) | file_register

    def _resolve_indirect(self) -> int | None:
        fsr = self.ram[SFR_FSR]
        if fsr == 0:
            return None
        return (((self.status >> STATUS_IRP) & 1) << 8) | fsr

    def _read_effective(self, address: int | None) -> int:
        if address is None:
            return 0
        if address == SFR_PCL:
            return self.pc & 0xFF
        if address == SFR_PIR1:
            value = self.ram[address] | (1 << PIR1_TXIF)
            if self.rx_queue:
                value |= 1 << PIR1_RCIF
            else:
                value &= ~(1 << PIR1_RCIF)
            return value
        if address == SFR_RCREG:
            if not self.rx_queue:
                return self.ram[address]
            value = self.rx_queue.popleft()
            self.ram[address] = value
            self.events.append(
                TraceEvent(self.steps, "uart_rx", self.pc, value, "RCREG read")
            )
            return value
        return self.ram[address]

    def read_file(self, file_register: int) -> int:
        effective = self._resolve_direct(file_register)
        if effective == SFR_INDF:
            return self._read_effective(self._resolve_indirect())
        return self._read_effective(effective)

    def _write_effective(self, address: int | None, value: int) -> None:
        if address is None:
            return
        value &= 0xFF
        if address == SFR_PCL:
            self.ram[address] = value
            self.pc = (((self.ram[SFR_PCLATH] & 0x1F) << 8) | value) & 0x1FFF
            return
        if address == SFR_TXREG:
            self.ram[address] = value
            self.tx_bytes.append(value)
            self.events.append(
                TraceEvent(self.steps, "uart_tx", self.pc, value, "TXREG write")
            )
            return
        if address == SFR_SSPBUF:
            self.ram[address] = value
            self.ram[SFR_PIR1] |= 1 << 3  # SSPIF: byte transfer completed
            return
        if address == SFR_EECON1:
            self.ram[address] = value
            if value & 0x01:
                ee_address = self.ram[SFR_EEADR]
                ee_value = self.eeprom.get(ee_address, 0xFF)
                self.ram[SFR_EEDATA] = ee_value
                self.ram[address] &= ~0x01
                self.events.append(
                    TraceEvent(
                        self.steps,
                        "eeprom_read",
                        self.pc,
                        ee_value,
                        f"EEPROM[0x{ee_address:02X}]",
                    )
                )
            return
        if address == SFR_ADCON0:
            self.ram[address] = value & ~0x04
            return
        if address == SFR_SSPCON2:
            # Model an attached, immediately acknowledging I2C device.  The
            # hardware clears SEN/RSEN/PEN/RCEN/ACKEN when each bus operation
            # completes; retaining these bits deadlocks startup polling loops.
            self.ram[address] = value & ~0x1F
            if value & 0x08:  # RCEN: synthesize one byte from the I2C peripheral.
                self.ram[SFR_SSPBUF] = 0x40
            self.ram[SFR_PIR1] |= 1 << 3
            self.events.append(
                TraceEvent(self.steps, "i2c_complete", self.pc, value, "SSPCON2 command")
            )
            return
        self.ram[address] = value

    def write_file(self, file_register: int, value: int) -> None:
        effective = self._resolve_direct(file_register)
        if effective == SFR_INDF:
            self._write_effective(self._resolve_indirect(), value)
        else:
            self._write_effective(effective, value)

    def _write_destination(self, file_register: int, destination_file: bool, value: int) -> None:
        value &= 0xFF
        if destination_file:
            self.write_file(file_register, value)
        else:
            self.w = value

    def _push(self, value: int) -> None:
        if len(self.stack) == 8:
            self.stack.pop(0)
        self.stack.append(value & 0x1FFF)

    def _pop(self) -> int:
        if not self.stack:
            raise EmulationError(f"hardware stack underflow at PC 0x{self.pc:04X}")
        return self.stack.pop()

    def queue_uart(self, data: bytes | bytearray | memoryview) -> None:
        self.rx_queue.extend(bytes(data))
        if data:
            self.sleeping = False

    def _interrupt_pending(self) -> bool:
        intcon = self.ram[SFR_INTCON]
        if not intcon & (1 << INTCON_GIE):
            return False
        core_sources = ((intcon >> 3) & (intcon & 0x07)) != 0
        peripheral_sources = bool(
            intcon & (1 << INTCON_PEIE)
            and self._read_effective(SFR_PIR1) & self.ram[SFR_PIE1]
        )
        return core_sources or peripheral_sources

    def _tick_peripherals(self) -> None:
        old = self.ram[SFR_TMR0]
        self.ram[SFR_TMR0] = (old + 1) & 0xFF
        if old == 0xFF:
            self.ram[SFR_INTCON] |= 1 << INTCON_T0IF

        timer1 = self.ram[SFR_TMR1L] | (self.ram[SFR_TMR1H] << 8)
        timer1 = (timer1 + 1) & 0xFFFF
        self.ram[SFR_TMR1L] = timer1 & 0xFF
        self.ram[SFR_TMR1H] = timer1 >> 8
        if timer1 == 0:
            self.ram[SFR_PIR1] |= 1 << PIR1_TMR1IF

        timer2 = (self.ram[SFR_TMR2] + 1) & 0xFF
        self.ram[SFR_TMR2] = timer2
        if timer2 == self.ram[SFR_PR2]:
            self.ram[SFR_PIR1] |= 1 << PIR1_TMR2IF

    def _branch_target(self, low_11: int) -> int:
        return (((self.ram[SFR_PCLATH] & 0x18) << 8) | low_11) & 0x1FFF

    def step(self) -> InstructionTrace:
        if self._interrupt_pending():
            self._push(self.pc)
            self.ram[SFR_INTCON] &= ~(1 << INTCON_GIE)
            self.events.append(
                TraceEvent(self.steps, "interrupt", self.pc, None, "enabled interrupt source")
            )
            self.pc = 0x0004
        if self.sleeping and not self.rx_queue:
            self.steps += 1
            self._tick_peripherals()
            trace = InstructionTrace(
                self.steps, self.pc, 0x0063, "sleep", "", self.w, self.status
            )
            self.recent.append(trace)
            return trace

        current_pc = self.pc
        try:
            word = self.words[current_pc]
        except KeyError as exc:
            raise EmulationError(f"execution reached unmapped word 0x{current_pc:04X}") from exc
        decoded = decode_pic14(word)
        if decoded.kind == "unknown":
            raise EmulationError(f"unknown instruction 0x{word:04X} at 0x{current_pc:04X}")
        self.pc = (self.pc + 1) & 0x1FFF
        self.steps += 1
        self.pc_hits[current_pc] += 1

        mnemonic = decoded.mnemonic
        f = word & 0x7F
        destination_file = bool(word & 0x80)
        skip = False

        if mnemonic == "nop":
            pass
        elif mnemonic == "return":
            self.pc = self._pop()
        elif mnemonic == "retfie":
            self.pc = self._pop()
            self.ram[SFR_INTCON] |= 1 << INTCON_GIE
        elif mnemonic == "option":
            self.ram[0x081] = self.w
        elif mnemonic.startswith("tris"):
            port = int(decoded.operands, 16)
            self.ram[0x080 | port] = self.w
        elif mnemonic == "sleep":
            self.sleeping = True
            self._set_flag(STATUS_PD, False)
            self._set_flag(STATUS_TO, True)
        elif mnemonic == "clrwdt":
            self._set_flag(STATUS_PD, True)
            self._set_flag(STATUS_TO, True)
        elif mnemonic == "movwf":
            self.write_file(f, self.w)
        elif mnemonic == "clrw":
            self.w = 0
            self._set_z(0)
        elif mnemonic == "clrf":
            self.write_file(f, 0)
            self._set_z(0)
        elif mnemonic in {
            "subwf", "decf", "iorwf", "andwf", "xorwf", "addwf", "movf",
            "comf", "incf", "decfsz", "rrf", "rlf", "swapf", "incfsz",
        }:
            if mnemonic == "decfsz" and destination_file and self.fast_forward_delays:
                next_word = self.words.get(self.pc)
                if next_word is not None:
                    next_instruction = decode_pic14(next_word)
                    if (
                        next_instruction.mnemonic == "goto"
                        and self._branch_target(next_word & 0x07FF) == current_pc
                    ):
                        self.write_file(f, 1)
                        self.accelerated_delay_loops += 1
            source = self.read_file(f)
            if mnemonic == "subwf":
                result = source - self.w
                self._set_flag(STATUS_C, source >= self.w)
                self._set_flag(STATUS_DC, (source & 0x0F) >= (self.w & 0x0F))
                result &= 0xFF
                self._set_z(result)
            elif mnemonic == "decf":
                result = (source - 1) & 0xFF
                self._set_z(result)
            elif mnemonic == "iorwf":
                result = source | self.w
                self._set_z(result)
            elif mnemonic == "andwf":
                result = source & self.w
                self._set_z(result)
            elif mnemonic == "xorwf":
                result = source ^ self.w
                self._set_z(result)
            elif mnemonic == "addwf":
                total = source + self.w
                self._set_flag(STATUS_C, total > 0xFF)
                self._set_flag(STATUS_DC, (source & 0x0F) + (self.w & 0x0F) > 0x0F)
                result = total & 0xFF
                self._set_z(result)
            elif mnemonic == "movf":
                result = source
                self._set_z(result)
            elif mnemonic == "comf":
                result = (~source) & 0xFF
                self._set_z(result)
            elif mnemonic == "incf":
                result = (source + 1) & 0xFF
                self._set_z(result)
            elif mnemonic == "decfsz":
                result = (source - 1) & 0xFF
                skip = result == 0
            elif mnemonic == "rrf":
                old_carry = int(self._flag(STATUS_C))
                self._set_flag(STATUS_C, bool(source & 1))
                result = ((old_carry << 7) | (source >> 1)) & 0xFF
            elif mnemonic == "rlf":
                old_carry = int(self._flag(STATUS_C))
                self._set_flag(STATUS_C, bool(source & 0x80))
                result = ((source << 1) | old_carry) & 0xFF
            elif mnemonic == "swapf":
                result = ((source << 4) | (source >> 4)) & 0xFF
            elif mnemonic == "incfsz":
                result = (source + 1) & 0xFF
                skip = result == 0
            else:
                raise AssertionError(mnemonic)
            self._write_destination(f, destination_file, result)
        elif mnemonic in ("bcf", "bsf", "btfsc", "btfss"):
            bit = (word >> 7) & 7
            value = self.read_file(f)
            if mnemonic == "bcf":
                self.write_file(f, value & ~(1 << bit))
            elif mnemonic == "bsf":
                self.write_file(f, value | (1 << bit))
            elif mnemonic == "btfsc":
                skip = not bool(value & (1 << bit))
            else:
                skip = bool(value & (1 << bit))
        elif mnemonic == "call":
            self._push(self.pc)
            self.pc = self._branch_target(word & 0x07FF)
        elif mnemonic == "goto":
            self.pc = self._branch_target(word & 0x07FF)
        elif mnemonic == "movlw":
            self.w = word & 0xFF
        elif mnemonic == "retlw":
            self.w = word & 0xFF
            self.pc = self._pop()
        elif mnemonic in ("iorlw", "andlw", "xorlw"):
            literal = word & 0xFF
            if mnemonic == "iorlw":
                self.w |= literal
            elif mnemonic == "andlw":
                self.w &= literal
            else:
                self.w ^= literal
            self.w &= 0xFF
            self._set_z(self.w)
        elif mnemonic == "sublw":
            literal = word & 0xFF
            result = literal - self.w
            self._set_flag(STATUS_C, literal >= self.w)
            self._set_flag(STATUS_DC, (literal & 0x0F) >= (self.w & 0x0F))
            self.w = result & 0xFF
            self._set_z(self.w)
        elif mnemonic == "addlw":
            literal = word & 0xFF
            total = self.w + literal
            self._set_flag(STATUS_C, total > 0xFF)
            self._set_flag(STATUS_DC, (self.w & 0x0F) + (literal & 0x0F) > 0x0F)
            self.w = total & 0xFF
            self._set_z(self.w)
        else:
            raise EmulationError(f"unimplemented instruction {mnemonic} at 0x{current_pc:04X}")

        if skip:
            self.pc = (self.pc + 1) & 0x1FFF
        self._tick_peripherals()
        trace = InstructionTrace(
            self.steps,
            current_pc,
            word,
            mnemonic,
            decoded.operands,
            self.w,
            self.status,
        )
        self.recent.append(trace)
        return trace

    def run(self, limit: int, until: Callable[["PIC16F877A"], bool] | None = None) -> int:
        executed = 0
        while executed < limit:
            self.step()
            executed += 1
            if until is not None and until(self):
                break
        return executed


PROBE_SPECS = (
    (
        "2.06-downloader",
        "2.06/extracted/Bixby_02060021_Downloader.hex",
        b"CR00",
        "ASCII read probe",
    ),
    (
        "2.06-pickit-bootloader",
        "2.06/extracted/Bixby_02060021_PICkit.hex",
        b"\xEA",
        "binary bootloader identify probe",
    ),
    (
        "2.70",
        "2.70/extracted/Bixby_0270_070206.hex",
        b"CR00",
        "ASCII read probe",
    ),
    (
        "2.71",
        "2.71/extracted/Bixby_0271_080315.hex",
        b"CR00",
        "ASCII read probe",
    ),
)


def ascii_preview(data: bytes | bytearray) -> str:
    return "".join(chr(value) if 0x20 <= value <= 0x7E else f"\\x{value:02X}" for value in data)


def probe_image(
    path: Path,
    label: str,
    probe: bytes,
    description: str,
    *,
    boot_steps: int = 250_000,
    probe_steps: int = 500_000,
) -> tuple[dict[str, object], list[InstructionTrace], list[TraceEvent]]:
    image = parse_ihex(path.read_bytes())
    cpu = PIC16F877A(image)
    error: str | None = None
    try:
        cpu.run(boot_steps)
        tx_before = len(cpu.tx_bytes)
        events_before = len(cpu.events)
        cpu.queue_uart(probe)
        expected_end = b"\xEB" if probe == b"\xEA" else b"\n"
        cpu.run(
            probe_steps,
            until=lambda state: expected_end in bytes(state.tx_bytes[tx_before:]),
        )
    except EmulationError as exc:
        error = str(exc)
        tx_before = 0
        events_before = 0
    output = bytes(cpu.tx_bytes[tx_before:])
    events = cpu.events[events_before:]
    summary: dict[str, object] = {
        "schema": 1,
        "emulator": "tools/pic14_emulator.py",
        "status": "experimental",
        "label": label,
        "image": path.name,
        "probe_description": description,
        "probe_hex": probe.hex(" ").upper(),
        "probe_ascii": ascii_preview(probe),
        "boot_steps_requested": boot_steps,
        "probe_steps_limit": probe_steps,
        "steps_executed": cpu.steps,
        "final_pc": f"0x{cpu.pc:04X}",
        "rx_bytes_remaining": len(cpu.rx_queue),
        "tx_hex": output.hex(" ").upper(),
        "tx_ascii": ascii_preview(output),
        "uart_rx_events": sum(item.kind == "uart_rx" for item in events),
        "uart_tx_events": sum(item.kind == "uart_tx" for item in events),
        "interrupt_events": sum(item.kind == "interrupt" for item in events),
        "accelerated_delay_loops": cpu.accelerated_delay_loops,
        "eeprom_read_events": sum(item.kind == "eeprom_read" for item in events),
        "error": error,
        "top_pc_hits": [
            {"pc": f"0x{pc:04X}", "count": count}
            for pc, count in cpu.pc_hits.most_common(20)
        ],
        "limitations": [
            "Peripheral timing is synthetic and is not cycle-accurate.",
            "Tight DECFSZ/GOTO-self delay loops are fast-forwarded while preserving their terminal register state.",
            "Analog inputs, external switches, motors, watchdog, and electrical behavior are not modeled.",
            "A successful software trace does not establish hardware safety or live compatibility.",
        ],
    }
    return summary, list(cpu.recent), events


def write_probe_artifacts(
    destination: Path,
    label: str,
    summary: dict[str, object],
    trace: Iterable[InstructionTrace],
    events: Iterable[TraceEvent],
) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    (destination / f"{label}-summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    with (destination / f"{label}-recent-trace.csv").open(
        "w", encoding="utf-8", newline=""
    ) as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=("step", "pc", "word", "mnemonic", "operands", "w", "status"),
        )
        writer.writeheader()
        for item in trace:
            row = asdict(item)
            row.update(
                pc=f"0x{item.pc:04X}",
                word=f"0x{item.word:04X}",
                w=f"0x{item.w:02X}",
                status=f"0x{item.status:02X}",
            )
            writer.writerow(row)
    with (destination / f"{label}-events.csv").open(
        "w", encoding="utf-8", newline=""
    ) as handle:
        writer = csv.DictWriter(
            handle, fieldnames=("step", "kind", "pc", "value", "detail")
        )
        writer.writeheader()
        for item in events:
            row = asdict(item)
            row.update(
                pc=f"0x{item.pc:04X}",
                value="" if item.value is None else f"0x{item.value:02X}",
            )
            writer.writerow(row)


def run_project(repo_root: Path, boot_steps: int, probe_steps: int) -> list[dict[str, object]]:
    firmware_root = repo_root / "reverse-engineering" / "firmware"
    destination = firmware_root / "emulation"
    summaries: list[dict[str, object]] = []
    for label, relative, probe, description in PROBE_SPECS:
        path = firmware_root / relative
        # The PICkit image only listens for 0xEA during its reset-time
        # bootloader window, so queue that byte before executing reset.
        selected_boot_steps = 0 if probe == b"\xEA" else boot_steps
        summary, trace, events = probe_image(
            path,
            label,
            probe,
            description,
            boot_steps=selected_boot_steps,
            probe_steps=probe_steps,
        )
        write_probe_artifacts(destination, label, summary, trace, events)
        summaries.append(summary)
        print(f"{label}: {summary['tx_ascii']!r}; error={summary['error']!r}")
    (destination / "summary.json").write_text(
        json.dumps(summaries, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return summaries


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    project = subparsers.add_parser("project", help="probe all preserved firmware generations")
    project.add_argument("--repo-root", type=Path, default=Path.cwd())
    project.add_argument("--boot-steps", type=int, default=250_000)
    project.add_argument("--probe-steps", type=int, default=500_000)
    probe = subparsers.add_parser("probe", help="probe one Intel HEX image")
    probe.add_argument("hex", type=Path)
    probe.add_argument("--label", default="standalone")
    probe.add_argument("--bytes", default="43523030", help="probe bytes as hex")
    probe.add_argument("--boot-steps", type=int, default=250_000)
    probe.add_argument("--probe-steps", type=int, default=500_000)
    probe.add_argument("--output", type=Path)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.command == "project":
        run_project(args.repo_root.resolve(), args.boot_steps, args.probe_steps)
        return 0
    probe = bytes.fromhex(args.bytes)
    summary, trace, events = probe_image(
        args.hex, args.label, probe, "standalone probe",
        boot_steps=args.boot_steps, probe_steps=args.probe_steps,
    )
    if args.output:
        write_probe_artifacts(args.output, args.label, summary, trace, events)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
