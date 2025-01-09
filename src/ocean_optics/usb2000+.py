import time
from dataclasses import dataclass

import numpy as np
import plotext as plt
import usb.core
import usb.util


@dataclass
class DeviceConfiguration:
    serial_number: str
    wavelength_calibration_coefficients: list[float]
    stray_light_constant: float
    nonlinearity_correction_coefficients: list[float]
    polynomial_order_nonlinearity_calibration: int
    optical_bench: str
    device_configuration: str


class OceanOpticsUSB2000Plus:
    INT_TIME: int = 100_000

    _config: DeviceConfiguration

    def __init__(self) -> None:
        self.device = usb.core.find(idVendor=0x2457, idProduct=0x101E)
        self.device.set_configuration()
        self.clear_buffers()

        # Initialize device
        self.device.write(0x01, b"\x01")
        # Set default integration time
        self.device.write(0x01, b"\x02" + int(self.INT_TIME).to_bytes(4, "little"))

        self._config = self.get_configuration()

    def clear_buffers(self) -> None:
        """Clear buffers by reading from both IN endpoints."""
        for endpoint in 0x81, 0x82:
            try:
                self.device.read(
                    endpoint=endpoint, size_or_buffer=1_000_000, timeout=100
                )
            except usb.core.USBTimeoutError:
                pass

    def get_configuration(self) -> DeviceConfiguration:
        """Get all configuration parameters.

        Returns:
            DeviceConfiguration: the configuration parameters.
        """
        serial = self._query_configuration_parameter(0)
        wavelength = [
            float(self._query_configuration_parameter(param)) for param in range(1, 5)
        ]
        stray_light = float(self._query_configuration_parameter(5))
        nonlinearity = [
            float(self._query_configuration_parameter(param)) for param in range(6, 14)
        ]
        polynomial = int(self._query_configuration_parameter(14))
        bench = self._query_configuration_parameter(15)
        dev_config = self._query_configuration_parameter(16)
        return DeviceConfiguration(
            serial_number=serial,
            wavelength_calibration_coefficients=wavelength,
            stray_light_constant=stray_light,
            nonlinearity_correction_coefficients=nonlinearity,
            polynomial_order_nonlinearity_calibration=polynomial,
            optical_bench=bench,
            device_configuration=dev_config,
        )

    def _query_configuration_parameter(self, index: int) -> str:
        """Query a configuration parameter.

        The indexes can be looked up in the data sheet. End users should call
        the `get_configuration()` method.

        Args:
            index (int): the requested configuration index.

        Returns:
            str: the value of the parameter as text.
        """
        command = b"\x05" + index.to_bytes(1)
        self.device.write(0x01, command)
        value: bytes = self.device.read(0x81, 17).tobytes()
        assert value[:2] == command
        # ignore everything after the first \x00 byte in the data range
        data = value[2 : value.find(b"\x00", 2)]
        return data.decode()

    def get_spectrum(self):
        data = self.get_raw_spectrum()
        x = np.arange(len(data))
        c = self._config.wavelength_calibration_coefficients
        # FIXME: check calibration
        # FIXME: read out autonulling information and scale accordingly
        x = c[0] + c[1] * x + c[2] * x**2 + c[3] * x**3
        return x[20:], data[20:]

    def get_raw_spectrum(self):
        self.device.write(0x01, b"\x09")
        # wait for measurement to complete, integration time is in microseconds.
        # FIXME: don't sleep, because the device will automatically acquire two
        # additional spectra which will be available sooner than acquiring a
        # fresh one.
        time.sleep(self.INT_TIME / 1_000_000)
        packets = []
        for _ in range(8):
            try:
                packets.append(self.device.read(0x82, 512, 100).tobytes())
            except usb.core.USBTimeoutError:
                break
        else:
            packets.append(self.device.read(0x82, 1, 100).tobytes())
        assert packets[-1][-1] == 0x69

        data = b"".join(packets[:-1])
        return np.frombuffer(data, dtype=np.uint16)

    def close(self) -> None:
        print("Shutting down.")
        self.device.write(0x01, b"\x04\x00\x00")
        print("Done.")


if __name__ == "__main__":
    dev = OceanOpticsUSB2000Plus()

    x, data = dev.get_spectrum()
    plt.clf()
    plt.plot(x, data)
    plt.show()

    print(x.shape)
    print(data.shape)

    print(dev.get_configuration())

    dev.device.write(0x01, b"\x09")
    dev.device.read(0x82, 512, 100).tobytes()

    dev.close()
