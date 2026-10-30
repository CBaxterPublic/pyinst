import threading
import weakref
import pyvisa
from typing import Protocol

_locks_guard = threading.Lock()
_connection_locks: dict[tuple, threading.RLock] = {}


def _canonical_name(name: str) -> str:
    try:
        return pyvisa.rname.to_canonical_name(name).casefold()
    except Exception:
        return name.strip().casefold()


def _connection_lock(address: str | None = None, session=None) -> threading.RLock:
    """Return the lock shared by every instrument object on one connection.

    Objects are on the same connection when they use the same VISA resource
    name, however it is spelled, or the same session object. Commands from them
    must not interleave, so they share one lock.
    """
    name = getattr(session, "resource_name", None)
    if not isinstance(name, str):
        name = address
    if name:
        key = ("name", _canonical_name(name))
    else:
        key = ("session", id(session))
    with _locks_guard:
        lock = _connection_locks.get(key)
        if lock is None:
            lock = _connection_locks[key] = threading.RLock()
            if key[0] == "session":
                try:
                    weakref.finalize(session, _connection_locks.pop, key, None)
                except TypeError:
                    pass  # not weak-referenceable: the entry lives for the process
        return lock


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
        # Shared per connection (resource name or session); see _connection_lock().
        self.lock = (
            _connection_lock(address, session)
            if address or session is not None
            else threading.RLock()
        )

    @property
    def connected(self) -> bool:
        return self._session is not None

    def connect(self):
        """Open the configured VISA resource and validate its identity."""
        if self.connected:
            return self
        if not self.address:
            raise ValueError("An instrument address is required to connect")

        self.lock = _connection_lock(self.address)
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