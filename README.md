# pyinst

`pyinst` provides shared instrument interfaces and SCPI drivers for laboratory
instruments. Drivers accept any session implementing `query()` and `write()`,
or can open a VISA resource when constructed with an address.

## Instrument Interfaces

- `SignalGenerator`: frequency, output power, and RF output state.
- `SpectrumAnalyzer`: center frequency, span, reference level, averaging
  count (`1` disables averaging), and `get_trace()`, which sweeps and returns
  `(frequencies_hz, levels_dbm)` as NumPy arrays.
- `PowerMeter`: channels with a settable calibration frequency in Hz, an
  averaging count (`1` disables averaging), and input power measurements in
  dBm. Concrete drivers validate the count against their instrument's limits.
- `PowerSupply`: access to channels implementing voltage, current, and output
  state controls.

Model-specific operations belong on the concrete driver rather than on these
shared interfaces.

Signal generators and spectrum analyzers expose `min_frequency_hz` and
`max_frequency_hz`. Their frequency setters reject values outside these
inclusive bounds before sending a command to the instrument.

## Drivers

- `E36313A`: Keysight E3631xx-family power supply with three output channels.
- `N5181A`: Keysight MXG analog signal generator.
- `SMA100B`: Rohde & Schwarz analog signal generator.
- `FSU67`: Rohde & Schwarz FSU spectrum analyzer.
- `ML2437A` and `ML2438A`: Anritsu single- and dual-sensor power meters.

`E3631xx` contains the shared channel-selection and voltage/current/output
commands. A model subclass supplies its `idn_model` and `channel_count`, so
future E3631xx models can reuse the implementation without duplicating channel
logic.

Driver source is grouped by instrument class under `pyinst.drivers`: power
meters, power supplies, signal generators, and spectrum analyzers each have
their own package. The ML243xA models share sensor configuration and measurement
logic; their sensor counts differ.

## Hardware connection

Install the optional VISA dependency with `python -m pip install -e '.[visa]'`
and configure a VISA backend. Connect explicitly or use the driver as a context
manager:

```python
from pyinst import N5181A

with N5181A("TCPIP0::192.0.2.10::inst0::INSTR") as generator:
  generator.frequency = 1e9
  generator.power = -10
  generator.output_enabled = True
```

For custom transports, pass an object with `query()` and `write()` as the
`session` argument.

## Development

```sh
python -m pip install -e .
```
