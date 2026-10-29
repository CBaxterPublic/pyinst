from pyinst.instruments import SignalGenerator
from pyinst.drivers.base import ScpiInstrument


class N5181A(ScpiInstrument, SignalGenerator):
    """Keysight N5181A MXG analog signal generator."""

    idn_model = "N5181A"
    min_frequency_hz = 9e3
    max_frequency_hz = 6e9

    @property
    def frequency(self) -> float:
        return float(self.query("SOUR:FREQ?"))

    @frequency.setter
    def frequency(self, value: float) -> None:
        self._validate_frequency(value)
        self.write(f"SOUR:FREQ {value:g}")

    @property
    def power(self) -> float:
        return float(self.query("SOUR:POW?"))

    @power.setter
    def power(self, value: float) -> None:
        self.write(f"SOUR:POW {value:g}")

    @property
    def output_enabled(self) -> bool:
        return self.query_bool("OUTP:STAT?")

    @output_enabled.setter
    def output_enabled(self, value: bool) -> None:
        self.write(f"OUTP:STAT {1 if value else 0}")
