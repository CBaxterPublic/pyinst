from abc import ABC, abstractmethod

import numpy as np


class SpectrumAnalyzer(ABC):
    """Common controls provided by a spectrum analyzer."""

    @property
    @abstractmethod
    def min_frequency_hz(self) -> float:
        """Minimum supported analyzer frequency in Hz."""

    @property
    @abstractmethod
    def max_frequency_hz(self) -> float:
        """Maximum supported analyzer frequency in Hz."""

    @property
    @abstractmethod
    def averaging_count(self) -> int:
        """Number of sweeps to average; 1 disables averaging."""

    @averaging_count.setter
    @abstractmethod
    def averaging_count(self, value: int) -> None:
        ...

    @property
    @abstractmethod
    def center_frequency(self) -> float:
        """Center frequency in Hz."""

    @center_frequency.setter
    @abstractmethod
    def center_frequency(self, value: float) -> None:
        ...

    @property
    @abstractmethod
    def span(self) -> float:
        """Frequency span in Hz."""

    @span.setter
    @abstractmethod
    def span(self, value: float) -> None:
        ...

    @property
    @abstractmethod
    def reference_level(self) -> float:
        """Display reference level in dBm."""

    @reference_level.setter
    @abstractmethod
    def reference_level(self, value: float) -> None:
        ...

    @abstractmethod
    def get_trace(self) -> tuple[np.ndarray, np.ndarray]:
        """Sweep and return ``(frequencies_hz, levels_dbm)`` float arrays for the active trace.

        Blocks until a complete sweep (including all averages) has finished.
        """
