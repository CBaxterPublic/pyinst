"""Instrument role interfaces."""

from .power_supply import PowerSupply, PowerSupplyChannel
from .power_meter import PowerMeter, PowerMeterChannel
from .signal_generator import SignalGenerator
from .spectrum_analyzer import SpectrumAnalyzer

__all__ = [
    "PowerMeter",
    "PowerMeterChannel",
    "PowerSupply",
    "PowerSupplyChannel",
    "SignalGenerator",
    "SpectrumAnalyzer",
]
