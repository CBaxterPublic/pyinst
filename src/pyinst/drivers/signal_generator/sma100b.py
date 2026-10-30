from pyinst.instruments import SignalGenerator
from pyinst.drivers.base import ScpiInstrument
from pyinst.drivers.utils import query_bool, validate_frequency


class SMA100B(ScpiInstrument, SignalGenerator):
    """Rohde & Schwarz SMA100B analog signal generator."""

    idn_model = "SMA100B"
    min_frequency_hz = 8e3
    # Largest frequency option (B140); units with a lower option reject higher
    # values themselves.
    max_frequency_hz = 40e9

    @property
    def frequency(self) -> float:
        return float(self.query("SOUR:FREQ?"))

    @frequency.setter
    def frequency(self, value: float) -> None:
        validate_frequency(self, value)
        self.write(f"SOUR:FREQ {value:g}")

    @property
    def power(self) -> float:
        return float(self.query("SOUR:POW?"))

    @power.setter
    def power(self, value: float) -> None:
        self.write(f"SOUR:POW {value:g}")

    @property
    def output_enabled(self) -> bool:
        return query_bool(self, "OUTP:STAT?")

    @output_enabled.setter
    def output_enabled(self, value: bool) -> None:
        self.write(f"OUTP:STAT {1 if value else 0}")
