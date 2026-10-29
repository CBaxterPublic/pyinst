from contextlib import contextmanager
from abc import ABC, abstractmethod
from typing import Sequence

from pyinst.instruments import PowerSupply, PowerSupplyChannel
from pyinst.drivers.base import ScpiInstrument


class E3631xxChannel(PowerSupplyChannel):
    """One output channel on a Keysight E3631xx power supply."""

    def __init__(self, instrument: "E3631xx", number: int) -> None:
        self.instrument = instrument
        self.number = number

    @contextmanager
    def _selected(self):
        """Hold the instrument lock with this channel selected."""
        with self.instrument.lock:
            self.instrument.write(f"INST:NSEL {self.number}")
            yield

    @property
    def voltage(self) -> float:
        with self._selected():
            return float(self.instrument.query("VOLT?"))

    @voltage.setter
    def voltage(self, value: float) -> None:
        with self._selected():
            self.instrument.write(f"VOLT {value:g}")

    @property
    def current(self) -> float:
        with self._selected():
            return float(self.instrument.query("CURR?"))

    @current.setter
    def current(self, value: float) -> None:
        with self._selected():
            self.instrument.write(f"CURR {value:g}")

    @property
    def output_enabled(self) -> bool:
        with self._selected():
            return self.instrument.query_bool("OUTP:STAT?")

    @output_enabled.setter
    def output_enabled(self, value: bool) -> None:
        with self._selected():
            self.instrument.write(f"OUTP:STAT {1 if value else 0}")


class E3631xx(ScpiInstrument, PowerSupply, ABC):
    """Shared SCPI implementation for Keysight E3631xx power supplies."""

    @property
    @abstractmethod
    def channel_count(self) -> int:
        """Number of independently selectable outputs."""

    def channels(self) -> Sequence[E3631xxChannel]:
        return tuple(
            E3631xxChannel(self, number)
            for number in range(1, self.channel_count + 1)
        )
