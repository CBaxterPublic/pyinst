from abc import ABC, abstractmethod
from typing import Sequence


class PowerSupplyChannel(ABC):
    """Common controls provided by a power-supply output channel."""

    @property
    @abstractmethod
    def voltage(self) -> float:
        """Voltage setpoint (V)."""

    @voltage.setter
    @abstractmethod
    def voltage(self, value: float) -> None:
        ...

    @property
    @abstractmethod
    def current(self) -> float:
        """Current setpoint (A)."""

    @current.setter
    @abstractmethod
    def current(self, value: float) -> None:
        ...

    @property
    @abstractmethod
    def output_enabled(self) -> bool:
        """Whether the channel output is enabled."""

    @output_enabled.setter
    @abstractmethod
    def output_enabled(self, value: bool) -> None:
        ...


class PowerSupply(ABC):
    """A power supply exposing one or more output channels."""

    @abstractmethod
    def channels(self) -> Sequence[PowerSupplyChannel]:
        """Return the output channels in instrument order."""
