#!/usr/bin/env python3
"""Experimental PIC16F877A CPU/UART emulator for preserved Bixby firmware.

This is a reverse-engineering harness, not a safety-qualified appliance model.
It implements the complete 35-instruction mid-range PIC14 core plus the small
set of PIC16F877A peripheral behaviors needed to explore startup, EEPROM reads,
and UART receive/transmit paths.  Analog, timer, watchdog, and external-I/O
behavior is deliberately synthetic.

The project command probes disposable in-memory copies of the preserved
firmware images and writes evidence under reverse-engineering/firmware/emulation.
Its write experiments modify only cloned RAM and synthetic EEPROM.  It never
connects to a stove, never modifies a source HEX file, and excludes the
``CW0FC4`` reset/loader value.
"""

from __future__ import annotations

import argparse
import copy
import csv
import json
from collections import Counter, defaultdict, deque
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable, Iterable, Mapping


try:
    from firmware_pipeline import (
        CW_EXIT_PC,
        CW_HANDLER_MATRIX,
        CW_SEMANTICS,
        CR_HANDLER_MATRIX,
        STATE_DISPATCH_PC,
        IHexImage,
        TELEMETRY_PATHS,
        decode_pic14,
        parse_ihex,
        region_for_word,
    )
except ModuleNotFoundError:
    from tools.firmware_pipeline import (  # type: ignore[no-redef]
        CW_EXIT_PC,
        CW_HANDLER_MATRIX,
        CW_SEMANTICS,
        CR_HANDLER_MATRIX,
        STATE_DISPATCH_PC,
        IHexImage,
        TELEMETRY_PATHS,
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
SFR_PORTA = 0x005
SFR_PORTB = 0x006
SFR_PORTC = 0x007
SFR_PORTD = 0x008
SFR_PORTE = 0x009
SFR_PCLATH = 0x00A
SFR_INTCON = 0x00B
SFR_PIR1 = 0x00C
SFR_PIR2 = 0x00D
SFR_TMR1L = 0x00E
SFR_TMR1H = 0x00F
SFR_TMR2 = 0x011
SFR_SSPBUF = 0x013
SFR_RCSTA = 0x018
SFR_TXREG = 0x019
SFR_RCREG = 0x01A
SFR_ADRESH = 0x01E
SFR_ADCON0 = 0x01F
SFR_TRISA = 0x085
SFR_TRISB = 0x086
SFR_TRISC = 0x087
SFR_TRISD = 0x088
SFR_TRISE = 0x089
SFR_PIE1 = 0x08C
SFR_SSPCON2 = 0x091
SFR_PR2 = 0x092
SFR_TXSTA = 0x098
SFR_SPBRG = 0x099
SFR_ADRESL = 0x09E
SFR_ADCON1 = 0x09F
SFR_EEDATA = 0x10C
SFR_EEADR = 0x10D
SFR_EECON1 = 0x18C
SFR_EECON2 = 0x18D

INTCON_T0IF = 2
INTCON_PEIE = 6
INTCON_GIE = 7
PIR1_TMR1IF = 0
PIR1_TMR2IF = 1
PIR1_TXIF = 4
PIR1_RCIF = 5
PIE1_RCIE = 5


PORT_NAMES = {
    SFR_PORTA: "PORTA",
    SFR_PORTB: "PORTB",
    SFR_PORTC: "PORTC",
    SFR_PORTD: "PORTD",
    SFR_PORTE: "PORTE",
}
PORT_ADDRESS_BY_NAME = {name: address for address, name in PORT_NAMES.items()}
TRIS_BY_PORT = {
    SFR_PORTA: SFR_TRISA,
    SFR_PORTB: SFR_TRISB,
    SFR_PORTC: SFR_TRISC,
    SFR_PORTD: SFR_TRISD,
    SFR_PORTE: SFR_TRISE,
}
SFR_NAMES = {
    SFR_INDF: "INDF",
    SFR_TMR0: "TMR0",
    SFR_PCL: "PCL",
    SFR_STATUS: "STATUS",
    SFR_FSR: "FSR",
    **PORT_NAMES,
    SFR_PCLATH: "PCLATH",
    SFR_INTCON: "INTCON",
    SFR_PIR1: "PIR1",
    SFR_PIR2: "PIR2",
    SFR_TMR1L: "TMR1L",
    SFR_TMR1H: "TMR1H",
    SFR_TMR2: "TMR2",
    SFR_SSPBUF: "SSPBUF",
    SFR_RCSTA: "RCSTA",
    SFR_TXREG: "TXREG",
    SFR_RCREG: "RCREG",
    SFR_ADRESH: "ADRESH",
    SFR_ADCON0: "ADCON0",
    SFR_TRISA: "TRISA",
    SFR_TRISB: "TRISB",
    SFR_TRISC: "TRISC",
    SFR_TRISD: "TRISD",
    SFR_TRISE: "TRISE",
    SFR_PIE1: "PIE1",
    SFR_SSPCON2: "SSPCON2",
    SFR_PR2: "PR2",
    SFR_TXSTA: "TXSTA",
    SFR_SPBRG: "SPBRG",
    SFR_ADRESL: "ADRESL",
    SFR_ADCON1: "ADCON1",
    SFR_EEDATA: "EEDATA",
    SFR_EEADR: "EEADR",
    SFR_EECON1: "EECON1",
    SFR_EECON2: "EECON2",
}


def memory_name(address: int | None) -> str:
    if address is None:
        return "NULL_INDF"
    return SFR_NAMES.get(address, f"RAM_0x{address:03X}")


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


@dataclass(frozen=True, slots=True)
class MemoryAccess:
    step: int
    pc: int
    action: str
    address: int | None
    name: str
    value: int
    via: str


@dataclass(frozen=True, slots=True)
class MemoryChange:
    step: int
    pc: int
    address: int | None
    name: str
    before: int
    after: int
    via: str


class PIC16F877A:
    """Instruction-accurate core with deterministic lightweight peripherals."""

    def __init__(
        self,
        image: IHexImage,
        *,
        fast_forward_delays: bool = True,
        data_eeprom: Mapping[int, int] | bytes | bytearray | memoryview | None = None,
        gpio_inputs: Mapping[int | str, int] | None = None,
        adc_inputs: Mapping[int, int] | None = None,
    ):
        self.words = {
            address: word & 0x3FFF
            for address, word in image.words.items()
            if region_for_word(address) == "program"
        }
        image_eeprom = {
            address - 0x2100: word & 0xFF
            for address, word in image.words.items()
            if region_for_word(address) == "eeprom"
        }
        self.eeprom = {address: 0xFF for address in range(0x100)}
        self.eeprom.update(image_eeprom)
        if data_eeprom is not None:
            if isinstance(data_eeprom, Mapping):
                supplied = data_eeprom.items()
            else:
                supplied = enumerate(bytes(data_eeprom))
            for address, value in supplied:
                if not 0 <= address <= 0xFF or not 0 <= value <= 0xFF:
                    raise ValueError("data EEPROM addresses and values must be bytes")
                self.eeprom[address] = value
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
        self.port_inputs = {address: 0 for address in PORT_NAMES}
        if gpio_inputs:
            for port, value in gpio_inputs.items():
                self.set_gpio_port(port, value)
        self.adc_inputs = {channel: 0 for channel in range(8)}
        if adc_inputs:
            for channel, value in adc_inputs.items():
                self.set_adc_input(channel, value)
        self.memory_trace_enabled = False
        self.memory_accesses: list[MemoryAccess] = []
        self.memory_changes: list[MemoryChange] = []
        self._instruction_pc = 0
        self.ram[SFR_STATUS] = (1 << STATUS_TO) | (1 << STATUS_PD)
        self.ram[SFR_PIR1] = 1 << PIR1_TXIF
        self.ram[SFR_PR2] = 0xFF

    def clone(self) -> "PIC16F877A":
        """Clone a deterministic booted state for an independent probe."""

        return copy.deepcopy(self)

    def set_gpio_port(self, port: int | str, value: int, *, mask: int = 0xFF) -> None:
        """Set synthetic external pin levels without changing output latches."""

        if isinstance(port, str):
            try:
                address = PORT_ADDRESS_BY_NAME[port.upper()]
            except KeyError as exc:
                raise ValueError(f"unknown GPIO port {port!r}") from exc
        else:
            address = port
        if address not in PORT_NAMES:
            raise ValueError(f"0x{address:03X} is not a modeled GPIO port")
        if not 0 <= value <= 0xFF or not 0 <= mask <= 0xFF:
            raise ValueError("GPIO value and mask must be bytes")
        previous = self.port_inputs[address]
        self.port_inputs[address] = (previous & ~mask) | (value & mask)

    def set_gpio_bit(self, port: int | str, bit: int, high: bool) -> None:
        if not 0 <= bit <= 7:
            raise ValueError("GPIO bit must be from 0 through 7")
        self.set_gpio_port(port, (1 << bit) if high else 0, mask=1 << bit)

    def set_adc_input(self, channel: int, value: int) -> None:
        if not 0 <= channel <= 7:
            raise ValueError("ADC channel must be from 0 through 7")
        if not 0 <= value <= 0x3FF:
            raise ValueError("ADC input must be a 10-bit value")
        self.adc_inputs[channel] = value

    def begin_memory_trace(self) -> None:
        self.memory_accesses.clear()
        self.memory_changes.clear()
        self.memory_trace_enabled = True

    def end_memory_trace(self) -> tuple[list[MemoryAccess], list[MemoryChange]]:
        self.memory_trace_enabled = False
        return list(self.memory_accesses), list(self.memory_changes)

    def _record_access(
        self, action: str, address: int | None, value: int, via: str
    ) -> None:
        if self.memory_trace_enabled:
            self.memory_accesses.append(
                MemoryAccess(
                    self.steps,
                    self._instruction_pc,
                    action,
                    address,
                    memory_name(address),
                    value & 0xFF,
                    via,
                )
            )

    def _record_change(
        self, address: int | None, before: int, after: int, via: str
    ) -> None:
        if self.memory_trace_enabled and before != after:
            self.memory_changes.append(
                MemoryChange(
                    self.steps,
                    self._instruction_pc,
                    address,
                    memory_name(address),
                    before & 0xFF,
                    after & 0xFF,
                    via,
                )
            )

    @property
    def status(self) -> int:
        return self.ram[SFR_STATUS]

    @status.setter
    def status(self, value: int) -> None:
        before = self.ram[SFR_STATUS]
        self.ram[SFR_STATUS] = value & 0xFF
        self._record_change(SFR_STATUS, before, self.ram[SFR_STATUS], "alu-flag")

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
        if address in PORT_NAMES:
            # PIC port reads return physical pin levels for inputs and the
            # output latch for outputs.  Keep external levels separate from
            # the latch so virtual switch changes cannot overwrite outputs.
            tris = self.ram[TRIS_BY_PORT[address]]
            latch = self.ram[address]
            return (latch & ~tris) | (self.port_inputs[address] & tris)
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
            address = self._resolve_indirect()
            via = "indirect"
        else:
            address = effective
            via = "direct"
        value = self._read_effective(address)
        self._record_access("read", address, value, via)
        return value

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
            if value & 0x02:
                ee_address = self.ram[SFR_EEADR]
                if value & 0x04:  # WREN
                    before = self.eeprom.get(ee_address, 0xFF)
                    ee_value = self.ram[SFR_EEDATA]
                    self.eeprom[ee_address] = ee_value
                    self.ram[SFR_PIR2] |= 1 << 4  # EEIF
                    self.events.append(
                        TraceEvent(
                            self.steps,
                            "eeprom_write",
                            self.pc,
                            ee_value,
                            f"EEPROM[0x{ee_address:02X}] 0x{before:02X}->0x{ee_value:02X}",
                        )
                    )
                else:
                    self.events.append(
                        TraceEvent(
                            self.steps,
                            "eeprom_write_rejected",
                            self.pc,
                            self.ram[SFR_EEDATA],
                            "WR requested while WREN was clear",
                        )
                    )
                # The physical part clears WR when the programming cycle
                # completes.  Complete it immediately in this deterministic
                # offline model so the firmware's WR polling loop can return.
                self.ram[address] &= ~0x02
            return
        if address == SFR_ADCON0:
            self.ram[address] = value
            if value & 0x04:  # GO/DONE: complete a deterministic conversion.
                channel = (value >> 3) & 0x07
                sample = self.adc_inputs[channel]
                if self.ram[SFR_ADCON1] & 0x80:  # ADFM: right justified.
                    self.ram[SFR_ADRESH] = (sample >> 8) & 0x03
                    self.ram[SFR_ADRESL] = sample & 0xFF
                else:
                    self.ram[SFR_ADRESH] = (sample >> 2) & 0xFF
                    self.ram[SFR_ADRESL] = (sample & 0x03) << 6
                self.ram[SFR_PIR1] |= 1 << 6  # ADIF
                self.events.append(
                    TraceEvent(
                        self.steps,
                        "adc_sample",
                        self.pc,
                        sample,
                        f"AN{channel}=0x{sample:03X}",
                    )
                )
            self.ram[address] &= ~0x04
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
            address = self._resolve_indirect()
            via = "indirect"
        else:
            address = effective
            via = "direct"
        before = 0 if address is None else self.ram[address]
        self._record_access("write", address, value, via)
        self._write_effective(address, value)
        after = 0 if address is None else self.ram[address]
        self._record_change(address, before, after, via)

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
        self._instruction_pc = current_pc
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
        "2.02-pickit-bootloader",
        "2.02/extracted/Bixby_0202_260827_PICkit.hex",
        b"\xEA",
        "binary bootloader identify probe",
    ),
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


APPLICATION_SPECS = (
    (
        "2.02",
        "2.02/extracted/Bixby_0202_260827_PICkit.hex",
        4,
    ),
    (
        "2.06",
        "2.06/extracted/Bixby_02060021_Downloader.hex",
        5,
    ),
    (
        "2.70",
        "2.70/extracted/Bixby_0270_070206.hex",
        7,
    ),
    (
        "2.71",
        "2.71/extracted/Bixby_0271_080315.hex",
        7,
    ),
)

RESPONSE_FORMATTERS = {
    "2.02": 0x12B7,
    "2.06": 0x1265,
    "2.70": 0x1352,
    "2.71": 0x132F,
}

CHECKSUM_END_BY_FORMAT = {
    0: 0x4B,
    1: 0x4B,
    2: 0x4C,
    3: 0x4C,
    4: 0x69,
    5: 0x9A,
    7: 0xFF,
}

VOLATILE_SFRS = frozenset(
    (SFR_TMR0, SFR_TMR1L, SFR_TMR1H, SFR_TMR2, SFR_PIR1, SFR_INTCON)
)


@dataclass(slots=True)
class RequestExecution:
    start_step: int
    request: bytes
    response: bytes
    steps: int
    error: str | None
    handler_seen: bool
    formatter_seen: bool
    accesses: list[MemoryAccess]
    changes: list[MemoryChange]
    net_changes: list[tuple[int, int, int]]
    events: list[TraceEvent]


@dataclass(slots=True)
class SilentWriteExecution:
    start_step: int
    request: bytes
    response: bytes
    steps: int
    error: str | None
    handler_seen: bool
    exit_seen: bool
    accesses: list[MemoryAccess]
    changes: list[MemoryChange]
    net_changes: list[tuple[int, int, int]]
    eeprom_changes: list[tuple[int, int, int]]
    events: list[TraceEvent]


@dataclass(slots=True)
class TelemetrySlotExecution:
    version: str
    index: int
    response: bytes
    steps: int
    error: str | None
    sender_seen: bool
    accesses: list[MemoryAccess]
    changes: list[MemoryChange]
    events: list[TraceEvent]


def calculate_fixture_checksum(data_format: int, data: bytes | bytearray) -> int:
    """Implement the BixCheck add-then-ROL16 configuration checksum."""

    try:
        end = CHECKSUM_END_BY_FORMAT[data_format]
    except KeyError as exc:
        raise ValueError(f"unsupported data format {data_format}") from exc
    if len(data) < end + 1:
        raise ValueError(f"format {data_format} requires EEPROM through 0x{end:02X}")
    checksum = 0
    for value in data[0x02 : end + 1]:
        checksum = (checksum + value) & 0xFFFF
        checksum = ((checksum << 1) | (checksum >> 15)) & 0xFFFF
    return checksum


def synthetic_controller_eeprom(data_format: int) -> bytes:
    """Build an obvious, deterministic, checksum-valid 256-byte lab fixture."""

    data = bytearray(((address * 0x25) + 0x5A) & 0xFF for address in range(0x100))
    data[0x02] = data_format
    data[0x03:0x0B] = b"EMU00001"
    data[0x0B:0x13] = b"01012000"
    data[0x13:0x23] = b"OPENMAXFIRE-LAB "
    checksum = calculate_fixture_checksum(data_format, data)
    data[0x00] = checksum >> 8
    data[0x01] = checksum & 0xFF
    return bytes(data)


def response_value(response: bytes) -> int | None:
    """Return the data byte from a six-character addressed response."""

    line = response.rstrip(b"\r\n")
    if len(line) != 6:
        return None
    try:
        return int(line[4:6], 16)
    except ValueError:
        return None


def execute_request(
    cpu: PIC16F877A,
    request: bytes,
    *,
    step_limit: int,
    handler_pc: int | None = None,
    formatter_pc: int | None = None,
    trace_entire_request: bool = False,
) -> RequestExecution:
    """Execute one request and optionally isolate its register handler."""

    start_step = cpu.steps
    tx_before = len(cpu.tx_bytes)
    events_before = len(cpu.events)
    accesses: list[MemoryAccess] = []
    changes: list[MemoryChange] = []
    net_changes: list[tuple[int, int, int]] = []
    handler_seen = False
    formatter_seen = False
    trace_started = False
    ram_before: bytes | None = None
    error: str | None = None
    if cpu.memory_trace_enabled:
        cpu.end_memory_trace()
    if trace_entire_request:
        ram_before = bytes(cpu.ram)
        cpu.begin_memory_trace()
        trace_started = True
    cpu.queue_uart(request)
    completed = False
    try:
        for _ in range(step_limit):
            if (
                handler_pc is not None
                and not handler_seen
                and cpu.pc == handler_pc
            ):
                handler_seen = True
                ram_before = bytes(cpu.ram)
                cpu.begin_memory_trace()
                trace_started = True
            if (
                trace_started
                and handler_seen
                and formatter_pc is not None
                and cpu.pc == formatter_pc
            ):
                accesses, changes = cpu.end_memory_trace()
                trace_started = False
                formatter_seen = True
                assert ram_before is not None
                net_changes = [
                    (address, before, after)
                    for address, (before, after) in enumerate(
                        zip(ram_before, bytes(cpu.ram), strict=True)
                    )
                    if before != after
                ]
            cpu.step()
            if b"\n" in bytes(cpu.tx_bytes[tx_before:]):
                completed = True
                break
        if not completed:
            error = f"no LF response within {step_limit} modeled instructions"
    except EmulationError as exc:
        error = str(exc)
    finally:
        if trace_started:
            accesses, changes = cpu.end_memory_trace()
            if ram_before is not None:
                net_changes = [
                    (address, before, after)
                    for address, (before, after) in enumerate(
                        zip(ram_before, bytes(cpu.ram), strict=True)
                    )
                    if before != after
                ]
    return RequestExecution(
        start_step=start_step,
        request=request,
        response=bytes(cpu.tx_bytes[tx_before:]),
        steps=cpu.steps - start_step,
        error=error,
        handler_seen=handler_seen,
        formatter_seen=formatter_seen,
        accesses=accesses,
        changes=changes,
        net_changes=net_changes,
        events=list(cpu.events[events_before:]),
    )


def execute_silent_write(
    cpu: PIC16F877A,
    request: bytes,
    *,
    step_limit: int,
    handler_pc: int,
    exit_pc: int,
) -> SilentWriteExecution:
    """Execute one six-byte C write through its real silent handler.

    C-unit writes normally emit no response, so waiting for LF incorrectly
    classifies successful writes as timeouts.  This bounded offline helper
    starts tracing at the statically verified handler entry and treats the
    common parser exit as completion.  A response such as the CW0D ``I\n`` is
    captured but is not required.
    """

    if len(request) != 6 or request[:2] != b"CW":
        raise ValueError("silent C write must have the form CWxxyy")
    start_step = cpu.steps
    tx_before = len(cpu.tx_bytes)
    events_before = len(cpu.events)
    handler_seen = False
    exit_seen = False
    tracing = False
    ram_before: bytes | None = None
    eeprom_before = dict(cpu.eeprom)
    accesses: list[MemoryAccess] = []
    changes: list[MemoryChange] = []
    net_changes: list[tuple[int, int, int]] = []
    error: str | None = None
    if cpu.memory_trace_enabled:
        cpu.end_memory_trace()
    cpu.queue_uart(request)
    try:
        for _ in range(step_limit):
            if not handler_seen and cpu.pc == handler_pc:
                handler_seen = True
                ram_before = bytes(cpu.ram)
                cpu.begin_memory_trace()
                tracing = True
            if handler_seen and cpu.pc == exit_pc:
                exit_seen = True
                break
            cpu.step()
        if not handler_seen:
            error = f"handler 0x{handler_pc:04X} not reached within {step_limit} instructions"
        elif not exit_seen:
            error = f"handler did not reach silent exit 0x{exit_pc:04X} within {step_limit} instructions"
    except EmulationError as exc:
        error = str(exc)
    finally:
        if tracing:
            accesses, changes = cpu.end_memory_trace()
        if ram_before is not None:
            net_changes = [
                (address, before, after)
                for address, (before, after) in enumerate(
                    zip(ram_before, bytes(cpu.ram), strict=True)
                )
                if before != after
            ]
    eeprom_changes = [
        (address, eeprom_before.get(address, 0xFF), cpu.eeprom.get(address, 0xFF))
        for address in sorted(set(eeprom_before) | set(cpu.eeprom))
        if eeprom_before.get(address, 0xFF) != cpu.eeprom.get(address, 0xFF)
    ]
    return SilentWriteExecution(
        start_step=start_step,
        request=request,
        response=bytes(cpu.tx_bytes[tx_before:]),
        steps=cpu.steps - start_step,
        error=error,
        handler_seen=handler_seen,
        exit_seen=exit_seen,
        accesses=accesses,
        changes=changes,
        net_changes=net_changes,
        eeprom_changes=eeprom_changes,
        events=list(cpu.events[events_before:]),
    )


def execute_telemetry_slot(
    cpu: PIC16F877A,
    version: str,
    index: int,
    *,
    step_limit: int = 20_000,
) -> TelemetrySlotExecution:
    """Force one periodic telemetry producer slot in an isolated CPU clone.

    This is a synthetic entry-point experiment, not a cadence model.  It
    preserves the booted RAM/EEPROM fixture, sets only the periodic slot index,
    and enters the statically identified producer block with the bank/page
    state used by the real main-loop jump.
    """

    try:
        path = TELEMETRY_PATHS[version]
    except KeyError as exc:
        raise ValueError(f"unknown firmware version {version!r}") from exc
    if not 0 <= index <= path["last_index"]:
        raise ValueError(
            f"{version} periodic telemetry index must be 0x00..0x{path['last_index']:02X}"
        )
    cpu.pc = path["block_entry"]
    cpu.stack.clear()
    cpu.sleeping = False
    cpu.ram[SFR_PCLATH] = 0x08
    cpu.status &= ~((1 << STATUS_RP0) | (1 << STATUS_RP1))
    cpu.ram[path["index_ram"]] = index
    start_step = cpu.steps
    tx_before = len(cpu.tx_bytes)
    events_before = len(cpu.events)
    cpu.begin_memory_trace()
    sender_seen = False
    error: str | None = None
    try:
        for executed in range(1, step_limit + 1):
            if cpu.pc == path["t_sender"]:
                sender_seen = True
            cpu.step()
            emitted = bytes(cpu.tx_bytes[tx_before:])
            requested_prefix = f"T{index:02x}".encode("ascii")
            if any(
                line.lower().startswith(requested_prefix.lower())
                for line in emitted.split(b"\n")[:-1]
            ):
                break
        else:
            executed = step_limit
            error = f"no complete T frame within {step_limit} instructions"
    except EmulationError as exc:
        executed = cpu.steps - start_step
        error = str(exc)
    accesses, changes = cpu.end_memory_trace()
    return TelemetrySlotExecution(
        version=version,
        index=index,
        response=bytes(cpu.tx_bytes[tx_before:]),
        steps=executed,
        error=error,
        sender_seen=sender_seen,
        accesses=accesses,
        changes=changes,
        events=list(cpu.events[events_before:]),
    )


def read_cr_registers(
    cpu: PIC16F877A,
    registers: Iterable[int],
    *,
    step_limit: int,
) -> tuple[dict[int, int | None], list[str]]:
    values: dict[int, int | None] = {}
    errors: list[str] = []
    for register in registers:
        if not 0 <= register <= 0x0E:
            raise ValueError("CR register must be in the range 0x00 through 0x0E")
        request = f"CR{register:02X}".encode("ascii")
        # Stop-on-LF leaves the firmware only one instruction past its final
        # TXREG write.  Clone the settled state for every query so a following
        # command cannot arrive before the parser returns to its idle state.
        result = execute_request(cpu.clone(), request, step_limit=step_limit)
        values[register] = response_value(result.response)
        if result.error:
            errors.append(f"{request.decode()}: {result.error}")
    return values, errors


def read_cr_snapshot(
    cpu: PIC16F877A, *, step_limit: int
) -> tuple[dict[int, int | None], list[str]]:
    return read_cr_registers(cpu, range(0x0F), step_limit=step_limit)


def changed_bits(before: int, after: int) -> str:
    mask = before ^ after
    return ",".join(str(bit) for bit in range(8) if mask & (1 << bit))


def write_csv_rows(
    path: Path, fieldnames: tuple[str, ...], rows: Iterable[Mapping[str, object]]
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def ascii_preview(data: bytes | bytearray) -> str:
    return "".join(chr(value) if 0x20 <= value <= 0x7E else f"\\x{value:02X}" for value in data)


def requested_telemetry_line(response: bytes, index: int) -> bytes:
    """Select the requested T slot when a producer emits other T lines first."""

    prefix = f"T{index:02x}".encode("ascii").lower()
    return next(
        (
            line
            for line in response.splitlines()
            if line.lower().startswith(prefix)
        ),
        b"",
    )


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
            "Tight DECFSZ/GOTO-self delay loops are fast-forwarded while "
            "preserving their terminal register state.",
            "GPIO and ADC inputs are synthetic; external mux hardware, motors, "
            "watchdog, and electrical behavior are not modeled.",
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


def run_deep_project(
    repo_root: Path,
    boot_steps: int,
    probe_steps: int,
) -> dict[str, object]:
    """Run exhaustive offline probes and write machine-readable evidence."""

    firmware_root = repo_root / "reverse-engineering" / "firmware"
    destination = firmware_root / "emulation" / "deep"
    destination.mkdir(parents=True, exist_ok=True)
    settle_steps = max(10_000, min(50_000, boot_steps))

    fixtures = {
        data_format: synthetic_controller_eeprom(data_format)
        for data_format in sorted({item[2] for item in APPLICATION_SPECS})
    }
    fixture_rows: list[dict[str, object]] = []
    fixture_metadata: list[dict[str, object]] = []
    for data_format, fixture in fixtures.items():
        checksum = calculate_fixture_checksum(data_format, fixture)
        endpoint = CHECKSUM_END_BY_FORMAT[data_format]
        fixture_metadata.append(
            {
                "data_format": data_format,
                "checksum": f"0x{checksum:04X}",
                "checksum_storage": f"{fixture[0]:02X} {fixture[1]:02X}",
                "checksum_endpoint": f"0x{endpoint:02X}",
                "serial": fixture[0x03:0x0B].decode("ascii"),
                "production_date": fixture[0x0B:0x13].decode("ascii"),
                "model": fixture[0x13:0x23].decode("ascii").rstrip(),
            }
        )
        for address, value in enumerate(fixture):
            if address < 0x02:
                role = "stored checksum"
            elif address == 0x02:
                role = "data format"
            elif 0x03 <= address <= 0x0A:
                role = "synthetic serial"
            elif 0x0B <= address <= 0x12:
                role = "synthetic production date"
            elif 0x13 <= address <= 0x22:
                role = "synthetic model"
            else:
                role = "deterministic lab pattern"
            fixture_rows.append(
                {
                    "data_format": f"0x{data_format:02X}",
                    "address": f"0x{address:02X}",
                    "value": f"0x{value:02X}",
                    "ascii": chr(value) if 0x20 <= value <= 0x7E else "",
                    "checksum_covered": "yes" if 0x02 <= address <= endpoint else "no",
                    "role": role,
                }
            )
    write_csv_rows(
        destination / "controller-eeprom-fixtures.csv",
        ("data_format", "address", "value", "ascii", "checksum_covered", "role"),
        fixture_rows,
    )

    booted: dict[str, PIC16F877A] = {}
    parsed_images: dict[str, IHexImage] = {}
    formats: dict[str, int] = {}
    images: dict[str, str] = {}
    for version, relative, data_format in APPLICATION_SPECS:
        path = firmware_root / relative
        image = parse_ihex(path.read_bytes())
        cpu = PIC16F877A(
            image,
            data_eeprom=fixtures[data_format],
        )
        if version == "2.02":
            # The older startup path enters a synchronous CCP1-timed actuator
            # initialization loop that the lightweight peripheral model does
            # not yet advance.  Stop immediately before its first state-family
            # dispatch and seed the same 0x20 cold/off family observed on the
            # live controller.  Commands queued at this boundary pass through
            # the real UART ISR, parser, dispatchers, and response formatter.
            for _ in range(boot_steps):
                if cpu.pc == STATE_DISPATCH_PC[version]:
                    cpu.ram[0x04C] = 0x20
                    break
                cpu.step()
            else:
                raise EmulationError(
                    "2.02 did not reach its first state dispatch within "
                    f"{boot_steps} modeled instructions"
                )
        else:
            cpu.run(boot_steps)
        cpu.events.clear()
        cpu.recent.clear()
        cpu.pc_hits.clear()
        booted[version] = cpu
        parsed_images[version] = image
        formats[version] = data_format
        images[version] = path.name

    cr_rows: list[dict[str, object]] = []
    access_rows: list[dict[str, object]] = []
    watch_rows: list[dict[str, object]] = []
    net_change_rows: list[dict[str, object]] = []
    dependencies: dict[
        tuple[str, str, int | None, str], dict[str, object]
    ] = defaultdict(lambda: {"count": 0, "values": set(), "pcs": set(), "vias": set()})

    for version, _relative, _data_format in APPLICATION_SPECS:
        for register, handler_pc in enumerate(CR_HANDLER_MATRIX[version]):
            request = f"CR{register:02X}".encode("ascii")
            cpu = booted[version].clone()
            result = execute_request(
                cpu,
                request,
                step_limit=probe_steps,
                handler_pc=handler_pc,
                formatter_pc=RESPONSE_FORMATTERS[version],
            )
            value = response_value(result.response)
            cr_rows.append(
                {
                    "version": version,
                    "image": images[version],
                    "request": request.decode("ascii"),
                    "response": ascii_preview(result.response),
                    "response_hex": result.response.hex(" ").upper(),
                    "value": "" if value is None else f"0x{value:02X}",
                    "handler_pc": f"0x{handler_pc:04X}",
                    "formatter_pc": f"0x{RESPONSE_FORMATTERS[version]:04X}",
                    "handler_seen": "yes" if result.handler_seen else "no",
                    "formatter_seen": "yes" if result.formatter_seen else "no",
                    "steps": result.steps,
                    "reads": sum(item.action == "read" for item in result.accesses),
                    "writes": sum(item.action == "write" for item in result.accesses),
                    "watchpoint_changes": len(result.changes),
                    "net_changes": len(result.net_changes),
                    "error": result.error or "",
                }
            )
            for ordinal, item in enumerate(result.accesses, start=1):
                address_text = "" if item.address is None else f"0x{item.address:03X}"
                access_rows.append(
                    {
                        "version": version,
                        "request": request.decode("ascii"),
                        "ordinal": ordinal,
                        "command_step": item.step - result.start_step,
                        "pc": f"0x{item.pc:04X}",
                        "action": item.action,
                        "address": address_text,
                        "name": item.name,
                        "value": f"0x{item.value:02X}",
                        "via": item.via,
                    }
                )
                if item.action == "read":
                    dependency = dependencies[
                        (version, request.decode("ascii"), item.address, item.name)
                    ]
                    dependency["count"] = int(dependency["count"]) + 1
                    dependency["values"].add(item.value)  # type: ignore[union-attr]
                    dependency["pcs"].add(item.pc)  # type: ignore[union-attr]
                    dependency["vias"].add(item.via)  # type: ignore[union-attr]
            for ordinal, item in enumerate(result.changes, start=1):
                watch_rows.append(
                    {
                        "version": version,
                        "request": request.decode("ascii"),
                        "ordinal": ordinal,
                        "command_step": item.step - result.start_step,
                        "pc": f"0x{item.pc:04X}",
                        "address": "" if item.address is None else f"0x{item.address:03X}",
                        "name": item.name,
                        "before": f"0x{item.before:02X}",
                        "after": f"0x{item.after:02X}",
                        "changed_bits": changed_bits(item.before, item.after),
                        "via": item.via,
                    }
                )
            for address, before, after in result.net_changes:
                net_change_rows.append(
                    {
                        "version": version,
                        "request": request.decode("ascii"),
                        "address": f"0x{address:03X}",
                        "name": memory_name(address),
                        "before": f"0x{before:02X}",
                        "after": f"0x{after:02X}",
                        "changed_bits": changed_bits(before, after),
                        "volatile": "yes" if address in VOLATILE_SFRS else "no",
                    }
                )

    dependency_rows: list[dict[str, object]] = []
    for (version, request, address, name), detail in sorted(
        dependencies.items(),
        key=lambda item: (item[0][0], item[0][1], -1 if item[0][2] is None else item[0][2]),
    ):
        dependency_rows.append(
            {
                "version": version,
                "request": request,
                "address": "" if address is None else f"0x{address:03X}",
                "name": name,
                "read_count": detail["count"],
                "values": " ".join(
                    f"0x{value:02X}" for value in sorted(detail["values"])  # type: ignore[arg-type]
                ),
                "pcs": " ".join(
                    f"0x{pc:04X}" for pc in sorted(detail["pcs"])  # type: ignore[arg-type]
                ),
                "via": " ".join(sorted(detail["vias"])),  # type: ignore[arg-type]
            }
        )

    write_csv_rows(
        destination / "cr-read-matrix.csv",
        (
            "version", "image", "request", "response", "response_hex", "value",
            "handler_pc", "formatter_pc", "handler_seen", "formatter_seen", "steps",
            "reads", "writes", "watchpoint_changes", "net_changes", "error",
        ),
        cr_rows,
    )
    write_csv_rows(
        destination / "cr-handler-accesses.csv",
        (
            "version", "request", "ordinal", "command_step", "pc", "action",
            "address", "name", "value", "via",
        ),
        access_rows,
    )
    write_csv_rows(
        destination / "cr-handler-dependencies.csv",
        ("version", "request", "address", "name", "read_count", "values", "pcs", "via"),
        dependency_rows,
    )
    write_csv_rows(
        destination / "cr-handler-watchpoints.csv",
        (
            "version", "request", "ordinal", "command_step", "pc", "address",
            "name", "before", "after", "changed_bits", "via",
        ),
        watch_rows,
    )
    write_csv_rows(
        destination / "cr-handler-net-changes.csv",
        (
            "version", "request", "address", "name", "before", "after",
            "changed_bits", "volatile",
        ),
        net_change_rows,
    )

    # Exercise every C-unit write dispatcher on an independent clone.  Values
    # mirror harmless service-software examples where those are known.  CW0F
    # deliberately uses 0x00: the 0xC4 reset/loader key is never queued here.
    write_values = {
        0x00: 0x00,
        0x01: 0x00,
        0x02: 0x00,
        0x03: 0x00,
        0x04: 0xA5,
        0x05: 0x00,
        0x06: 0x00,
        0x07: 0x00,
        0x08: 0x32,
        0x09: 0x40,
        0x0A: 0x00,
        0x0B: 0x20,
        0x0C: 0x00,
        0x0D: 0x00,
        0x0E: 0x14,
        0x0F: 0x00,
    }
    write_step_limit = max(20_000, min(probe_steps, 50_000))
    cw_rows: list[dict[str, object]] = []
    cw_net_rows: list[dict[str, object]] = []
    cw_eeprom_rows: list[dict[str, object]] = []
    cw_accesses: dict[tuple[object, ...], dict[str, object]] = defaultdict(
        lambda: {"count": 0, "values": set(), "pcs": set()}
    )
    cw_changes: dict[tuple[object, ...], dict[str, object]] = defaultdict(
        lambda: {"count": 0, "before": set(), "after": set(), "pcs": set()}
    )
    for version, _relative, _data_format in APPLICATION_SPECS:
        for register, handler_pc in enumerate(CW_HANDLER_MATRIX[version]):
            value = write_values[register]
            request = f"CW{register:02X}{value:02X}".encode("ascii")
            result = execute_silent_write(
                booted[version].clone(),
                request,
                step_limit=write_step_limit,
                handler_pc=handler_pc,
                exit_pc=CW_EXIT_PC[version],
            )
            modeled_nonreturn = register in (0x05, 0x0A)
            semantic, description, evidence = CW_SEMANTICS[register]
            eeprom_events = [
                item for item in result.events if item.kind == "eeprom_write"
            ]
            cw_rows.append(
                {
                    "version": version,
                    "image": images[version],
                    "request": request.decode("ascii"),
                    "register": f"0x{register:02X}",
                    "value": f"0x{value:02X}",
                    "semantic": semantic,
                    "description": description,
                    "evidence": evidence,
                    "handler_pc": f"0x{handler_pc:04X}",
                    "exit_pc": f"0x{CW_EXIT_PC[version]:04X}",
                    "expected_model_status": (
                        "long actuator path may not return"
                        if modeled_nonreturn
                        else "normal silent exit"
                    ),
                    "response": ascii_preview(result.response),
                    "response_hex": result.response.hex(" ").upper(),
                    "handler_seen": "yes" if result.handler_seen else "no",
                    "exit_seen": "yes" if result.exit_seen else "no",
                    "steps": result.steps,
                    "reads": sum(item.action == "read" for item in result.accesses),
                    "writes": sum(item.action == "write" for item in result.accesses),
                    "watchpoint_changes": len(result.changes),
                    "net_changes": len(result.net_changes),
                    "eeprom_write_events": len(eeprom_events),
                    "eeprom_net_changes": len(result.eeprom_changes),
                    "error": result.error or "",
                }
            )
            for item in result.accesses:
                key = (
                    version,
                    request.decode("ascii"),
                    item.action,
                    item.address,
                    item.name,
                    item.via,
                )
                detail = cw_accesses[key]
                detail["count"] = int(detail["count"]) + 1
                detail["values"].add(item.value)  # type: ignore[union-attr]
                detail["pcs"].add(item.pc)  # type: ignore[union-attr]
            for item in result.changes:
                key = (
                    version,
                    request.decode("ascii"),
                    item.address,
                    item.name,
                    item.via,
                )
                detail = cw_changes[key]
                detail["count"] = int(detail["count"]) + 1
                detail["before"].add(item.before)  # type: ignore[union-attr]
                detail["after"].add(item.after)  # type: ignore[union-attr]
                detail["pcs"].add(item.pc)  # type: ignore[union-attr]
            for address, before, after in result.net_changes:
                cw_net_rows.append(
                    {
                        "version": version,
                        "request": request.decode("ascii"),
                        "address": f"0x{address:03X}",
                        "name": memory_name(address),
                        "before": f"0x{before:02X}",
                        "after": f"0x{after:02X}",
                        "changed_bits": changed_bits(before, after),
                        "volatile": "yes" if address in VOLATILE_SFRS else "no",
                    }
                )
            for item in eeprom_events:
                cw_eeprom_rows.append(
                    {
                        "version": version,
                        "request": request.decode("ascii"),
                        "command_step": item.step - result.start_step,
                        "pc": f"0x{item.pc:04X}",
                        "kind": item.kind,
                        "value": "" if item.value is None else f"0x{item.value:02X}",
                        "detail": item.detail,
                    }
                )

    cw_access_rows: list[dict[str, object]] = []
    for (version, request, action, address, name, via), detail in sorted(
        cw_accesses.items(),
        key=lambda item: (
            str(item[0][0]), str(item[0][1]), str(item[0][2]),
            -1 if item[0][3] is None else int(item[0][3]), str(item[0][5]),
        ),
    ):
        cw_access_rows.append(
            {
                "version": version,
                "request": request,
                "action": action,
                "address": "" if address is None else f"0x{address:03X}",
                "name": name,
                "via": via,
                "count": detail["count"],
                "values": " ".join(
                    f"0x{value:02X}" for value in sorted(detail["values"])  # type: ignore[arg-type]
                ),
                "pcs": " ".join(
                    f"0x{pc:04X}" for pc in sorted(detail["pcs"])  # type: ignore[arg-type]
                ),
            }
        )
    cw_change_rows: list[dict[str, object]] = []
    for (version, request, address, name, via), detail in sorted(
        cw_changes.items(),
        key=lambda item: (
            str(item[0][0]), str(item[0][1]),
            -1 if item[0][2] is None else int(item[0][2]), str(item[0][4]),
        ),
    ):
        cw_change_rows.append(
            {
                "version": version,
                "request": request,
                "address": "" if address is None else f"0x{address:03X}",
                "name": name,
                "via": via,
                "count": detail["count"],
                "before_values": " ".join(
                    f"0x{value:02X}" for value in sorted(detail["before"])  # type: ignore[arg-type]
                ),
                "after_values": " ".join(
                    f"0x{value:02X}" for value in sorted(detail["after"])  # type: ignore[arg-type]
                ),
                "pcs": " ".join(
                    f"0x{pc:04X}" for pc in sorted(detail["pcs"])  # type: ignore[arg-type]
                ),
            }
        )
    write_csv_rows(
        destination / "cw-write-matrix.csv",
        (
            "version", "image", "request", "register", "value", "semantic",
            "description", "evidence", "handler_pc", "exit_pc",
            "expected_model_status", "response", "response_hex", "handler_seen",
            "exit_seen", "steps", "reads", "writes", "watchpoint_changes",
            "net_changes", "eeprom_write_events", "eeprom_net_changes", "error",
        ),
        cw_rows,
    )
    write_csv_rows(
        destination / "cw-handler-access-summary.csv",
        ("version", "request", "action", "address", "name", "via", "count", "values", "pcs"),
        cw_access_rows,
    )
    write_csv_rows(
        destination / "cw-handler-change-summary.csv",
        (
            "version", "request", "address", "name", "via", "count",
            "before_values", "after_values", "pcs",
        ),
        cw_change_rows,
    )
    write_csv_rows(
        destination / "cw-handler-net-changes.csv",
        (
            "version", "request", "address", "name", "before", "after",
            "changed_bits", "volatile",
        ),
        cw_net_rows,
    )
    write_csv_rows(
        destination / "cw-eeprom-events.csv",
        ("version", "request", "command_step", "pc", "kind", "value", "detail"),
        cw_eeprom_rows,
    )

    # Bypass only the periodic cadence gate and enter each producer slot on a
    # clone.  This preserves the actual producer and UART sender code while
    # making every slot reproducible without wall-clock or sensor hardware.
    telemetry_rows: list[dict[str, object]] = []
    telemetry_accesses: dict[tuple[object, ...], dict[str, object]] = defaultdict(
        lambda: {"count": 0, "values": set(), "pcs": set()}
    )
    for version, _relative, _data_format in APPLICATION_SPECS:
        path = TELEMETRY_PATHS[version]
        for index in range(path["last_index"] + 1):
            result = execute_telemetry_slot(
                booted[version].clone(), version, index, step_limit=write_step_limit
            )
            lines = [line for line in result.response.splitlines() if line]
            t_line = requested_telemetry_line(result.response, index)
            dw_line = next((line for line in lines if line.startswith(b"DW")), b"")
            t_index: int | None = None
            t_value: int | None = None
            aux_index: int | None = None
            aux_value: int | None = None
            try:
                if len(t_line) == 5:
                    t_index = int(t_line[1:3], 16)
                    t_value = int(t_line[3:5], 16)
                if len(dw_line) == 6:
                    aux_index = int(dw_line[2:4], 16)
                    aux_value = int(dw_line[4:6], 16)
            except ValueError:
                pass
            value_write_pcs = sorted(
                {
                    item.pc
                    for item in result.accesses
                    if item.action == "write" and item.address == path["value_ram"]
                }
            )
            aux_write_pcs = sorted(
                {
                    item.pc
                    for item in result.accesses
                    if item.action == "write" and item.address == path["aux_value_ram"]
                }
            )
            telemetry_rows.append(
                {
                    "version": version,
                    "index": f"0x{index:02X}",
                    "block_entry": f"0x{path['block_entry']:04X}",
                    "sender_pc": f"0x{path['t_sender']:04X}",
                    "response": ascii_preview(result.response),
                    "response_hex": result.response.hex(" ").upper(),
                    "t_frame": t_line.decode("ascii", errors="replace"),
                    "t_index": "" if t_index is None else f"0x{t_index:02X}",
                    "t_value": "" if t_value is None else f"0x{t_value:02X}",
                    "aux_frame": dw_line.decode("ascii", errors="replace"),
                    "aux_index": "" if aux_index is None else f"0x{aux_index:02X}",
                    "aux_value": "" if aux_value is None else f"0x{aux_value:02X}",
                    "value_ram": f"0x{path['value_ram']:03X}",
                    "value_write_pcs": " ".join(f"0x{pc:04X}" for pc in value_write_pcs),
                    "aux_value_ram": f"0x{path['aux_value_ram']:03X}",
                    "aux_write_pcs": " ".join(f"0x{pc:04X}" for pc in aux_write_pcs),
                    "sender_seen": "yes" if result.sender_seen else "no",
                    "steps": result.steps,
                    "reads": sum(item.action == "read" for item in result.accesses),
                    "writes": sum(item.action == "write" for item in result.accesses),
                    "error": result.error or "",
                }
            )
            for item in result.accesses:
                key = (
                    version,
                    index,
                    item.action,
                    item.address,
                    item.name,
                    item.via,
                )
                detail = telemetry_accesses[key]
                detail["count"] = int(detail["count"]) + 1
                detail["values"].add(item.value)  # type: ignore[union-attr]
                detail["pcs"].add(item.pc)  # type: ignore[union-attr]
    telemetry_access_rows: list[dict[str, object]] = []
    for (version, index, action, address, name, via), detail in sorted(
        telemetry_accesses.items(),
        key=lambda item: (
            str(item[0][0]), int(item[0][1]), str(item[0][2]),
            -1 if item[0][3] is None else int(item[0][3]), str(item[0][5]),
        ),
    ):
        telemetry_access_rows.append(
            {
                "version": version,
                "index": f"0x{int(index):02X}",
                "action": action,
                "address": "" if address is None else f"0x{int(address):03X}",
                "name": name,
                "via": via,
                "count": detail["count"],
                "values": " ".join(
                    f"0x{value:02X}" for value in sorted(detail["values"])  # type: ignore[arg-type]
                ),
                "pcs": " ".join(
                    f"0x{pc:04X}" for pc in sorted(detail["pcs"])  # type: ignore[arg-type]
                ),
            }
        )
    write_csv_rows(
        destination / "telemetry-slot-matrix.csv",
        (
            "version", "index", "block_entry", "sender_pc", "response",
            "response_hex", "t_frame", "t_index", "t_value", "aux_frame",
            "aux_index", "aux_value", "value_ram", "value_write_pcs",
            "aux_value_ram", "aux_write_pcs", "sender_seen", "steps", "reads",
            "writes", "error",
        ),
        telemetry_rows,
    )
    write_csv_rows(
        destination / "telemetry-producer-access-summary.csv",
        ("version", "index", "action", "address", "name", "via", "count", "values", "pcs"),
        telemetry_access_rows,
    )

    eeprom_read_rows: list[dict[str, object]] = []
    for version, _relative, data_format in APPLICATION_SPECS:
        fixture = fixtures[data_format]
        for address in range(0x100):
            request = f"AR{address:02X}".encode("ascii")
            # A response is complete when its final LF enters TXREG, one
            # instruction before the parser returns to idle. Reusing that
            # exact CPU boundary for the next request can eventually fill the
            # older 2.02 receive ring and create a harness-only timeout. Each
            # EEPROM address is an independent probe, so start it from the
            # same settled boot fixture just as the CR matrix does.
            result = execute_request(
                booted[version].clone(), request, step_limit=probe_steps
            )
            actual = response_value(result.response)
            eeprom_events = [item for item in result.events if item.kind == "eeprom_read"]
            eeprom_read_rows.append(
                {
                    "version": version,
                    "data_format": f"0x{data_format:02X}",
                    "request": request.decode("ascii"),
                    "response": ascii_preview(result.response),
                    "response_hex": result.response.hex(" ").upper(),
                    "address": f"0x{address:02X}",
                    "expected": f"0x{fixture[address]:02X}",
                    "actual": "" if actual is None else f"0x{actual:02X}",
                    "match": "yes" if actual == fixture[address] else "no",
                    "eeprom_read_events": len(eeprom_events),
                    "event_details": " | ".join(item.detail for item in eeprom_events),
                    "steps": result.steps,
                    "error": result.error or "",
                }
            )
    write_csv_rows(
        destination / "a-unit-eeprom-reads.csv",
        (
            "version", "data_format", "request", "response", "response_hex",
            "address", "expected", "actual", "match", "eeprom_read_events",
            "event_details", "steps", "error",
        ),
        eeprom_read_rows,
    )

    gpio_input_rows: list[dict[str, object]] = []
    gpio_scenario_rows: list[dict[str, object]] = []
    gpio_effect_rows: list[dict[str, object]] = []
    for version, _relative, _data_format in APPLICATION_SPECS:
        base = booted[version]
        for port_address, port_name in PORT_NAMES.items():
            tris = base.ram[TRIS_BY_PORT[port_address]]
            for bit in range(8):
                gpio_input_rows.append(
                    {
                        "version": version,
                        "port": port_name,
                        "bit": bit,
                        "direction": "input" if tris & (1 << bit) else "output",
                        "tris": f"0x{tris:02X}",
                        "output_latch": f"0x{base.ram[port_address]:02X}",
                    }
                )
        baseline_cpu = base.clone()
        baseline_cpu.run(settle_steps)
        baseline_values, baseline_errors = read_cr_snapshot(
            baseline_cpu, step_limit=probe_steps
        )
        for port_address, port_name in PORT_NAMES.items():
            tris = base.ram[TRIS_BY_PORT[port_address]]
            for bit in range(8):
                if not tris & (1 << bit):
                    continue
                cpu = base.clone()
                cpu.set_gpio_bit(port_address, bit, True)
                cpu.run(settle_steps)
                values, errors = read_cr_snapshot(cpu, step_limit=probe_steps)
                changed = [
                    register
                    for register in range(0x0F)
                    if values[register] != baseline_values[register]
                ]
                gpio_scenario_rows.append(
                    {
                        "version": version,
                        "stimulus": f"{port_name}{bit}=1",
                        "port": port_name,
                        "bit": bit,
                        "settle_steps": settle_steps,
                        "changed_registers": " ".join(
                            f"CR{register:02X}" for register in changed
                        ),
                        "changed_count": len(changed),
                        "baseline_errors": " | ".join(baseline_errors),
                        "stimulus_errors": " | ".join(errors),
                    }
                )
                for register in changed:
                    before = baseline_values[register]
                    after = values[register]
                    gpio_effect_rows.append(
                        {
                            "version": version,
                            "stimulus": f"{port_name}{bit}=1",
                            "port": port_name,
                            "bit": bit,
                            "register": f"CR{register:02X}",
                            "baseline": "" if before is None else f"0x{before:02X}",
                            "stimulated": "" if after is None else f"0x{after:02X}",
                            "changed_bits": (
                                "" if before is None or after is None
                                else changed_bits(before, after)
                            ),
                        }
                    )
    write_csv_rows(
        destination / "gpio-input-matrix.csv",
        ("version", "port", "bit", "direction", "tris", "output_latch"),
        gpio_input_rows,
    )
    write_csv_rows(
        destination / "gpio-scenarios.csv",
        (
            "version", "stimulus", "port", "bit", "settle_steps",
            "changed_registers", "changed_count", "baseline_errors", "stimulus_errors",
        ),
        gpio_scenario_rows,
    )
    write_csv_rows(
        destination / "gpio-effects.csv",
        (
            "version", "stimulus", "port", "bit", "register", "baseline",
            "stimulated", "changed_bits",
        ),
        gpio_effect_rows,
    )

    adc_scenario_rows: list[dict[str, object]] = []
    adc_effect_rows: list[dict[str, object]] = []
    adc_levels = (0x100, 0x200, 0x300, 0x3FF)
    for version, _relative, data_format in APPLICATION_SPECS:
        base = booted[version]
        baseline_cpu = base.clone()
        baseline_values, baseline_errors = read_cr_registers(
            baseline_cpu, (0x09, 0x0A), step_limit=probe_steps
        )
        for channel in range(8):
            for level in adc_levels:
                # These images take their modeled analog samples during the
                # reset/startup sequence.  Apply each value before reset and
                # replay the same number of instructions for a fair diff.
                cpu = PIC16F877A(
                    parsed_images[version],
                    data_eeprom=fixtures[data_format],
                    adc_inputs={channel: level},
                )
                cpu.run(boot_steps)
                sample_events = [
                    item
                    for item in cpu.events
                    if item.kind == "adc_sample" and item.detail.startswith(f"AN{channel}=")
                ]
                values, errors = read_cr_registers(
                    cpu, (0x09, 0x0A), step_limit=probe_steps
                )
                changed = [
                    register
                    for register in (0x09, 0x0A)
                    if values[register] != baseline_values[register]
                ]
                adc_scenario_rows.append(
                    {
                        "version": version,
                        "channel": f"AN{channel}",
                        "input_10bit": f"0x{level:03X}",
                        "sample_events_during_boot": len(sample_events),
                        "boot_steps": boot_steps,
                        "changed_registers": " ".join(
                            f"CR{register:02X}" for register in changed
                        ),
                        "changed_count": len(changed),
                        "baseline_errors": " | ".join(baseline_errors),
                        "stimulus_errors": " | ".join(errors),
                    }
                )
                for register in changed:
                    before = baseline_values[register]
                    after = values[register]
                    adc_effect_rows.append(
                        {
                            "version": version,
                            "channel": f"AN{channel}",
                            "input_10bit": f"0x{level:03X}",
                            "register": f"CR{register:02X}",
                            "baseline": "" if before is None else f"0x{before:02X}",
                            "stimulated": "" if after is None else f"0x{after:02X}",
                            "changed_bits": (
                                "" if before is None or after is None
                                else changed_bits(before, after)
                            ),
                        }
                    )
    write_csv_rows(
        destination / "adc-scenarios.csv",
        (
            "version", "channel", "input_10bit", "sample_events_during_boot",
            "boot_steps", "changed_registers", "changed_count", "baseline_errors",
            "stimulus_errors",
        ),
        adc_scenario_rows,
    )
    write_csv_rows(
        destination / "adc-effects.csv",
        (
            "version", "channel", "input_10bit", "register", "baseline",
            "stimulated", "changed_bits",
        ),
        adc_effect_rows,
    )

    adc_sources: dict[str, set[str]] = defaultdict(set)
    for row in adc_effect_rows:
        adc_sources[str(row["register"])].add(str(row["channel"]))
    signal_rows = (
        {
            "signal": "front-panel buttons",
            "protocol_source": "CR01",
            "encoding": "none=00, ON=02, OFF=01, UP=04, DOWN=08",
            "pic_source": (
                "RD3 active-low return; RD2 selects the button bank and RD6:RD5 "
                "select OFF/ON/UP/DOWN; debounced into RAM 0x53"
            ),
            "evidence": (
                "identical firmware mux scanner in 2.06/2.70/2.71 plus BixCheck "
                "AnalyzeInteractiveResult"
            ),
            "confidence": "high static mapping; not live-validated",
        },
        {
            "signal": "burn-drive motor limit switch",
            "protocol_source": "CR02 bit 0",
            "encoding": "opposite states; physical polarity not established",
            "pic_source": (
                "RD3 active-high external-input mux return; slot 0 selected by "
                "RD7=1 and RD6:RD5=00"
            ),
            "evidence": (
                "firmware mux scanner plus BixCheck plate-motor-off predicate and "
                "9067-0404 board diagram label"
            ),
            "confidence": "high static mapping; not live-validated",
        },
        {
            "signal": "unassigned external-input mux slot",
            "protocol_source": "CR02 bit 1",
            "encoding": "logical state only; function and polarity unknown",
            "pic_source": (
                "RD3 active-high external-input mux return; slot 1 selected by "
                "RD7=1 and RD6:RD5=01"
            ),
            "evidence": "identical firmware mux scanner in 2.06/2.70/2.71",
            "confidence": "high transport mapping; physical function unresolved",
        },
        {
            "signal": "exhaust-fan sensor (J10)",
            "protocol_source": "CR05",
            "encoding": (
                "TMR0 falling-edge count sampled every 30 RB0 external-interrupt "
                "ticks; 0xFF denotes counter overflow"
            ),
            "pic_source": "RA4/T0CKI -> TMR0 -> RAM 0x34",
            "evidence": (
                "identical firmware counter/latch path in 2.06/2.70/2.71, "
                "BixCheck exhaust-test CR05 predicates, and 9067-0404 diagram J10 label"
            ),
            "confidence": (
                "high static mapping; engineering conversion and installed-board "
                "routing not live-validated"
            ),
        },
        {
            "signal": "feeder-wheel sensor (J9)",
            "protocol_source": "CR02 bit 4 and CR07",
            "encoding": (
                "RD0 current state in CR02.4; elapsed RB0 ticks for an RD0 "
                "high-then-low cycle, shifted right four, in CR07"
            ),
            "pic_source": (
                "RD0 edge state; RB1 gates RAM 0x47:0x46 counter; latched in "
                "RAM 0x45:0x44"
            ),
            "evidence": (
                "identical firmware edge/counter path in 2.06/2.70/2.71, "
                "BixCheck feeder-test CR07 predicate, and 9067-0404 diagram J9 label"
            ),
            "confidence": (
                "high static mapping; polarity, tick duration, and installed-board "
                "routing not live-validated"
            ),
        },
        {
            "signal": "firebox door",
            "protocol_source": "CR02 bit 5",
            "encoding": "open=1, closed=0",
            "pic_source": "RD1",
            "evidence": "BixCheck checkout mask cross-referenced to firmware/GPIO trace",
            "confidence": "high offline mapping; not live-validated",
        },
        {
            "signal": "ash drawer",
            "protocol_source": "CR02 bit 6",
            "encoding": "open=1, closed=0",
            "pic_source": "RD4",
            "evidence": "BixCheck checkout mask cross-referenced to firmware/GPIO trace",
            "confidence": "high offline mapping; not live-validated",
        },
        {
            "signal": "thermostat",
            "protocol_source": "CR06 bit 2",
            "encoding": "open/closed are opposite states",
            "pic_source": "RB4",
            "evidence": "BixCheck checkout mask cross-referenced to firmware/GPIO trace",
            "confidence": "high pin/bit mapping; polarity awaits live validation",
        },
        {
            "signal": "fuel-select switch",
            "protocol_source": "CR02 bit 2",
            "encoding": "1=Fuel A/corn, 0=Fuel B/wood",
            "pic_source": (
                "RD3 active-high external-input mux return; slot 2 selected by "
                "RD7=1 and RD6:RD5=10"
            ),
            "evidence": (
                "firmware mux scanner and 0x30 Fuel A/B configuration-bank offset, "
                "opposite BixCheck predicates, and 9067-0404 board diagram label"
            ),
            "confidence": "high static mapping and polarity; not live-validated",
        },
        {
            "signal": "fan potentiometer",
            "protocol_source": "CR09",
            "encoding": "low<=03, detent=79..86, high>FB in BixCheck checkout",
            "pic_source": " ".join(sorted(adc_sources.get("CR09", set()))) or "not resolved",
            "evidence": "BixCheck thresholds plus synthetic ADC differential",
            "confidence": "high register mapping; ADC channel depends on modeled result",
        },
        {
            "signal": "feed potentiometer",
            "protocol_source": "CR0A",
            "encoding": "low<=03, detent=79..86, high>FB in BixCheck checkout",
            "pic_source": " ".join(sorted(adc_sources.get("CR0A", set()))) or "not resolved",
            "evidence": "BixCheck thresholds plus synthetic ADC differential",
            "confidence": "high register mapping; ADC channel depends on modeled result",
        },
    )
    write_csv_rows(
        destination / "signal-map.csv",
        (
            "signal", "protocol_source", "encoding", "pic_source", "evidence", "confidence",
        ),
        signal_rows,
    )

    cr_errors = [row for row in cr_rows if row["error"]]
    eeprom_mismatches = [row for row in eeprom_read_rows if row["match"] != "yes"]
    cw_expected_nonreturns = [
        row for row in cw_rows
        if row["expected_model_status"] == "long actuator path may not return"
        and row["exit_seen"] != "yes"
    ]
    cw_unexpected_errors = [
        row for row in cw_rows
        if row["expected_model_status"] == "normal silent exit" and row["error"]
    ]
    telemetry_errors = [row for row in telemetry_rows if row["error"]]
    summary: dict[str, object] = {
        "schema": 1,
        "status": "experimental offline emulation",
        "generated_by": "tools/pic14_emulator.py project",
        "boot_steps": boot_steps,
        "probe_step_limit": probe_steps,
        "synthetic_settle_steps": settle_steps,
        "firmware_versions": [item[0] for item in APPLICATION_SPECS],
        "cr_commands_executed": len(cr_rows),
        "cr_handlers_reached": sum(row["handler_seen"] == "yes" for row in cr_rows),
        "cr_formatters_reached": sum(row["formatter_seen"] == "yes" for row in cr_rows),
        "cr_errors": len(cr_errors),
        "handler_access_records": len(access_rows),
        "handler_read_dependencies": len(dependency_rows),
        "watchpoint_records": len(watch_rows),
        "handler_net_change_records": len(net_change_rows),
        "cw_commands_executed": len(cw_rows),
        "cw_handlers_reached": sum(row["handler_seen"] == "yes" for row in cw_rows),
        "cw_normal_exits_reached": sum(row["exit_seen"] == "yes" for row in cw_rows),
        "cw_expected_modeled_nonreturns": len(cw_expected_nonreturns),
        "cw_unexpected_errors": len(cw_unexpected_errors),
        "cw_handler_access_summaries": len(cw_access_rows),
        "cw_handler_change_summaries": len(cw_change_rows),
        "cw_handler_net_change_records": len(cw_net_rows),
        "cw_eeprom_write_events": len(cw_eeprom_rows),
        "write_probe_step_limit": write_step_limit,
        "telemetry_slots_executed": len(telemetry_rows),
        "telemetry_senders_reached": sum(
            row["sender_seen"] == "yes" for row in telemetry_rows
        ),
        "telemetry_frames_completed": sum(bool(row["t_frame"]) for row in telemetry_rows),
        "telemetry_errors": len(telemetry_errors),
        "telemetry_producer_access_summaries": len(telemetry_access_rows),
        "a_unit_reads_executed": len(eeprom_read_rows),
        "a_unit_read_mismatches": len(eeprom_mismatches),
        "gpio_input_scenarios": len(gpio_scenario_rows),
        "gpio_effect_records": len(gpio_effect_rows),
        "adc_scenarios": len(adc_scenario_rows),
        "adc_effect_records": len(adc_effect_rows),
        "fixture_metadata": fixture_metadata,
        "adc_register_sources": {
            register: sorted(channels) for register, channels in sorted(adc_sources.items())
        },
        "limitations": [
            "GPIO and ADC stimuli are synthetic logical values, not electrical models.",
            "The RD3 multiplexer is represented only as a pin level; external "
            "selection-aware hardware is not modeled.",
            "Signal names come from cross-referencing BixCheck masks, firmware data "
            "flow, and a related-board 9067-0404 diagram; they remain unvalidated "
            "on serial 5215's reported 9067-0604 board.",
            "The EEPROM fixture is conspicuously synthetic and contains no owner "
            "or stove calibration data.",
            "C-unit writes execute only in disposable CPU clones with synthetic "
            "RAM/EEPROM; no source image or physical controller is modified.",
            "CW0F is absent from the 2.02/format-04 dispatcher. In later "
            "firmware it is probed only with value 0x00; the state-changing "
            "0xC4 reset/loader key is explicitly excluded.",
            "CW05 and CW0A enter long actuator/timer paths that do not return in "
            "the bounded peripheral model; this is a model limitation, not a "
            "firmware failure.",
            "Telemetry slots are entered directly after synthetic boot. Producer "
            "and UART code are real firmware, but periodic cadence/gating is not modeled.",
            "The 2.02 fixture stops at its first state dispatch and seeds the "
            "live-observed 0x20 cold/off family because the emulator does not "
            "yet advance the firmware's synchronous CCP1 actuator-init wait.",
            "TMR0 is advanced synthetically per modeled instruction; no timing or "
            "sensor-rate conclusion should be drawn from emulator step counts.",
        ],
    }
    (destination / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(
        "deep: "
        f"{summary['cr_handlers_reached']}/{summary['cr_commands_executed']} CR handlers; "
        f"{summary['cw_normal_exits_reached']}/{summary['cw_commands_executed']} CW exits "
        f"({summary['cw_expected_modeled_nonreturns']} expected modeled non-returns); "
        f"{summary['telemetry_frames_completed']}/{summary['telemetry_slots_executed']} telemetry slots; "
        f"{summary['a_unit_reads_executed'] - summary['a_unit_read_mismatches']}"
        f"/{summary['a_unit_reads_executed']} EEPROM reads matched; "
        f"{summary['gpio_effect_records']} GPIO and {summary['adc_effect_records']} ADC effects"
    )
    return summary


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
    run_deep_project(repo_root, boot_steps, probe_steps)
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
