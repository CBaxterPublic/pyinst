import threading
from typing import Protocol


class ScpiSession(Protocol):
    """Minimal command interface required by an SCPI driver."""

    def query(self, command: str) -> str: ...

    def write(self, command: str) -> object: ...


class ScpiInstrument:
    """Base class for SCPI instruments using an injected session or PyVISA."""

    idn_model: str | None = None

    def __init__(
        self,
        address: str | None = None,
        *,
        session: ScpiSession | None = None,
        visa_backend: str | None = None,
    ) -> None:
        self.address = address
        self.visa_backend = visa_backend
        self._session = session
        self._resource_manager = None
        self._owns_session = False
        # Re-entrant so multi-command operations can hold it across query()/write().
        self.lock = threading.RLock()

    @property
    def connected(self) -> bool:
        return self._session is not None

    def connect(self):
        """Open the configured VISA resource and validate its identity."""
        if self.connected:
            return self
        if not self.address:
            raise ValueError("An instrument address is required to connect")

        try:
            import pyvisa
        except ImportError as exc:
            raise RuntimeError(
                "PyVISA is required for hardware connections; install pyinst[visa]"
            ) from exc

        resource_manager = (
            pyvisa.ResourceManager(self.visa_backend)
            if self.visa_backend
            else pyvisa.ResourceManager()
        )
        self._resource_manager = resource_manager
        try:
            self._session = resource_manager.open_resource(self.address)
            self._owns_session = True
            if self.idn_model:
                identity = self.query("*IDN?")
                if self.idn_model.casefold() not in identity.casefold():
                    raise RuntimeError(
                        f"Expected {self.idn_model} at {self.address}; got {identity}"
                    )
        except Exception:
            self.disconnect()
            raise
        return self

    def query(self, command: str) -> str:
        if self._session is None:
            raise RuntimeError("Instrument is not connected")
        with self.lock:
            return str(self._session.query(command)).strip()

    def write(self, command: str):
        if self._session is None:
            raise RuntimeError("Instrument is not connected")
        with self.lock:
            return self._session.write(command)

    def query_bool(self, command: str) -> bool:
        response = self.query(command).upper()
        if response in {"1", "ON"}:
            return True
        if response in {"0", "OFF"}:
            return False
        raise ValueError(f"Unexpected boolean response to {command!r}: {response!r}")

    def _validate_frequency(self, value: float) -> None:
        if not self.min_frequency_hz <= value <= self.max_frequency_hz:
            raise ValueError(
                f"Frequency {value:g} Hz is outside the supported range "
                f"{self.min_frequency_hz:g}..{self.max_frequency_hz:g} Hz"
            )

    def disconnect(self) -> None:
        session = self._session
        resource_manager = self._resource_manager
        owns_session = self._owns_session
        self._session = None
        self._resource_manager = None
        self._owns_session = False

        if owns_session and session is not None:
            session.close()
        if resource_manager is not None:
            resource_manager.close()

    def __enter__(self):
        return self.connect()

    def __exit__(self, exc_type, exc_value, traceback):
        self.disconnect()