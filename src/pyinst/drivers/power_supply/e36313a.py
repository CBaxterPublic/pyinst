from pyinst.drivers.power_supply.e3631xx import E3631xx


class E36313A(E3631xx):
    """Keysight E36313A triple-output DC power supply."""

    idn_model = "E36313A"

    @property
    def channel_count(self) -> int:
        return 3
