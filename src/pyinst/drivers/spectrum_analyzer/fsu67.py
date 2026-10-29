import numpy as np

from pyinst.instruments import SpectrumAnalyzer
from pyinst.drivers.base import ScpiInstrument


class FSU67(ScpiInstrument, SpectrumAnalyzer):
    """Rohde & Schwarz FSU67 spectrum analyzer."""

    idn_model = "FSU"
    min_frequency_hz = 20.0
    max_frequency_hz = 67e9

    @property
    def averaging_count(self) -> int:
        if not self.query_bool("SENS:AVER:STAT?"):
            return 1
        return int(self.query("SENS:AVER:COUN?"))

    @averaging_count.setter
    def averaging_count(self, value: int) -> None:
        if isinstance(value, bool) or not isinstance(value, int) or value < 1:
            raise ValueError("averaging_count must be a positive integer")
        with self.lock:
            if value == 1:
                self.write("SENS:AVER:STAT OFF")
                return
            self.write(f"SENS:AVER:COUN {value}")
            self.write("SENS:AVER:STAT ON")

    @property
    def center_frequency(self) -> float:
        return float(self.query("FREQ:CENT?"))

    @center_frequency.setter
    def center_frequency(self, value: float) -> None:
        self._validate_frequency(value)
        self.write(f"FREQ:CENT {value:g}")

    @property
    def span(self) -> float:
        return float(self.query("FREQ:SPAN?"))

    @span.setter
    def span(self, value: float) -> None:
        self.write(f"FREQ:SPAN {value:g}")

    @property
    def reference_level(self) -> float:
        return float(self.query("DISP:TRAC:Y:RLEV?"))

    @reference_level.setter
    def reference_level(self, value: float) -> None:
        self.write(f"DISP:TRAC:Y:RLEV {value:g}")

    def get_trace(self) -> tuple[np.ndarray, np.ndarray]:
        with self.lock:
            units = self.query("UNIT:POW?").upper()
            if units != "DBM":
                raise RuntimeError(f"Trace units are {units!r}; set UNIT:POW DBM")
            self.write("FORM:DATA ASC")
            self.write("INIT:CONT OFF")
            self.write("INIT:IMM")
            self.query("*OPC?")
            start = float(self.query("FREQ:STAR?"))
            stop = float(self.query("FREQ:STOP?"))
            response = self.query("TRAC? TRACE1")

        levels = np.array(response.split(","), dtype=float)
        if levels.size < 2:
            raise ValueError(f"Unexpected trace response: {response!r}")
        return np.linspace(start, stop, levels.size), levels
