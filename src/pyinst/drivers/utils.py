"""Helpers shared by SCPI driver implementations."""


def query_bool(instrument, command: str) -> bool:
    """Query ``command`` on ``instrument`` and parse a 1/0 or ON/OFF reply."""
    response = instrument.query(command).upper()
    if response in {"1", "ON"}:
        return True
    if response in {"0", "OFF"}:
        return False
    raise ValueError(f"Unexpected boolean response to {command!r}: {response!r}")


def validate_frequency(instrument, value: float) -> None:
    """Raise ValueError if ``value`` is outside the instrument's frequency range."""
    if not instrument.min_frequency_hz <= value <= instrument.max_frequency_hz:
        raise ValueError(
            f"Frequency {value:g} Hz is outside the supported range "
            f"{instrument.min_frequency_hz:g}..{instrument.max_frequency_hz:g} Hz"
        )
