from pyinst.drivers.power_meter.ml243xa import ML243xA


class ML2437A(ML243xA):
    """Anritsu ML2437A single-sensor power meter."""

    idn_model = "ML2437A"

    @property
    def channel_count(self) -> int:
        return 1
