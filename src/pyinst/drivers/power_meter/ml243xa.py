from __future__ import annotations

from abc import ABC, abstractmethod
from math import log10
from typing import Sequence

from pyinst.drivers.base import ScpiInstrument
from pyinst.instruments import PowerMeter, PowerMeterChannel


class ML243xAChannel(PowerMeterChannel):
    """One sensor input on an Anritsu ML243xA power meter."""

    def __init__(self, instrument: ML243xA, sensor: str) -> None:
        self.instrument = instrument
        self.sensor = sensor

    @property
    def frequency(self) -> float:
        response = self.instrument.query(f"CFFRQ? {self.sensor}")
        return float(response.rsplit(",", 1)[-1].strip())

    @frequency.setter
    def frequency(self, value: float) -> None:
        if not 9e3 <= value <= 122e9:
            raise ValueError("frequency must be between 9 kHz and 122 GHz")
        self.instrument.write(f"CFFRQ {self.sensor},{value:g}")

    @property
    def averaging_count(self) -> int:
        response = self.instrument.query(f"AVG? {self.sensor}")
        fields = response.split(",")
        if len(fields) != 3:
            raise ValueError(f"Unexpected averaging response: {response!r}")
        mode = fields[1].strip().upper()
        if mode == "OFF":
            return 1
        if mode in {"AUTO", "AUTOMATIC"}:
            raise RuntimeError("Automatic averaging has no fixed averaging count")
        return int(fields[2].strip())

    @averaging_count.setter
    def averaging_count(self, value: int) -> None:
        if isinstance(value, bool) or not isinstance(value, int) or not 1 <= value <= 512:
            raise ValueError("averaging_count must be an integer from 1 to 512")
        if value == 1:
            self.instrument.write(f"AVG {self.sensor},OFF")
        else:
            self.instrument.write(f"AVG {self.sensor},RPT,{value}")

    def _display_channel(self) -> int:
        for channel_number in range(1, 3):
            response = self.instrument.query(f"CHCFG? {channel_number}")
            configuration = response.rsplit(",", 1)[-1].strip().upper()
            if configuration == self.sensor:
                return channel_number
        raise RuntimeError(
            f"Sensor {self.sensor} is not directly assigned to a display channel; "
            "configure CHCFG before measuring"
        )

    def measure_power_dbm(self) -> float:
        with self.instrument.lock:
            channel_number = self._display_channel()
            units_response = self.instrument.query(f"CHUNIT? {channel_number}")
            units = units_response.rsplit(",", 1)[-1].strip().upper()
            response = self.instrument.query(f"TR2 {channel_number}")
            value = self._parse_measurement(response)

            if units == "DBM":
                return value
            if units == "W":
                if value < 0:
                    raise ValueError(f"Power meter returned negative power: {value} W")
                if value == 0:
                    return float("-inf")
                return 10 * log10(value * 1000)
            raise ValueError(
                f"Cannot convert display units {units!r} to dBm; set channel units to DBM or W"
            )

    @staticmethod
    def _parse_measurement(response: str) -> float:
        fields = response.replace(",", " ").split()
        for field in reversed(fields):
            try:
                return float(field)
            except ValueError:
                continue
        raise ValueError(f"Unexpected power measurement response: {response!r}")


class ML243xA(ScpiInstrument, PowerMeter, ABC):
    """Shared native-command implementation for Anritsu ML243xA meters."""

    @property
    @abstractmethod
    def channel_count(self) -> int:
        """Number of physical sensor inputs on the model."""

    def channels(self) -> Sequence[ML243xAChannel]:
        return tuple(
            ML243xAChannel(self, chr(ord("A") + index))
            for index in range(self.channel_count)
        )
