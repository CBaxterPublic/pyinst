from pyinst.drivers.power_meter.ml243xa import ML243xA


class ML2438A(ML243xA):
    """Anritsu ML2438A dual-sensor power meter."""

    idn_model = "ML2438A"

    @property
    def channel_count(self) -> int:
        return 2
