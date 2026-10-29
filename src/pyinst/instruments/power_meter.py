from abc import ABC, abstractmethod
from typing import Sequence


class PowerMeterChannel(ABC):
    """Measurement API for one power-meter input channel."""

    @property
    @abstractmethod
    def frequency(self) -> float:
        """Calibration frequency in Hz."""

    @frequency.setter
    @abstractmethod
    def frequency(self, value: float) -> None:
        ...

    @property
    @abstractmethod
    def averaging_count(self) -> int:
        """Number of readings to average; 1 disables averaging."""

    @averaging_count.setter
    @abstractmethod
    def averaging_count(self, value: int) -> None:
        """Set a positive averaging count supported by the instrument."""

    @abstractmethod
    def measure_power_dbm(self) -> float:
        """Measure the input power and return it in dBm."""
        ...


class PowerMeter(ABC):
    """A power meter exposing one or more input channels."""

    @property
    @abstractmethod
    def channel_count(self) -> int:
        """Number of channels available."""

    @abstractmethod
    def channels(self) -> Sequence[PowerMeterChannel]:
        """Return the input channels in instrument order."""
