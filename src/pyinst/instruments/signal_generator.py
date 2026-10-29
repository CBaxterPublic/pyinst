from abc import ABC, abstractmethod


class SignalGenerator(ABC):
    """Common controls provided by a signal generator."""

    @property
    @abstractmethod
    def min_frequency_hz(self) -> float:
        """Minimum supported frequency in Hz."""

    @property
    @abstractmethod
    def max_frequency_hz(self) -> float:
        """Maximum supported frequency in Hz."""

    @property
    @abstractmethod
    def frequency(self) -> float:
        """Frequency in Hz."""

    @frequency.setter
    @abstractmethod
    def frequency(self, value: float) -> None:
        ...

    @property
    @abstractmethod
    def power(self) -> float:
        """Output power in dBm."""

    @power.setter
    @abstractmethod
    def power(self, value: float) -> None:
        ...

    @property
    @abstractmethod
    def output_enabled(self) -> bool:
        """Whether the RF output is enabled."""

    @output_enabled.setter
    @abstractmethod
    def output_enabled(self, value: bool) -> None:
        ...
