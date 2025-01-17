from typing import Iterator

import numpy as np

from ocean_optics.usb2000plus import DeviceNotFoundError, OceanOpticsUSB2000Plus

__all__ = ["DeviceNotFoundError", "SpectroscopyExperiment"]


class SpectroscopyExperiment:
    def __init__(self) -> None:
        self.device = OceanOpticsUSB2000Plus()

    def get_spectrum(self) -> tuple[np.ndarray, np.ndarray]:
        """Record a spectrum.

        Returns:
            A tuple of `np.ndarrays` with wavelength, intensity data. The
            wavelengths are in nanometers but the intensity is in arbitrary
            units (but should be calibrated so that different devices yield the
            same output).
        """
        return self.device.get_spectrum()

    def integrate_spectrum(self, count: int) -> Iterator[tuple[np.ndarray, np.ndarray]]:
        """Record a spectrum by integrating over multiple measurements.

        Record an integrated spectrum using the spectrometer. Multiple measurements
        are taken and they are summed to increase the signal to noise ratio. The
        results are displayed in a graph in the terminal. There are various options
        for other forms of output. The unit of intensity is arbitrary.

        Args:
            count: The number of measurements to perform.

        Yields:
            A tuple of `np.ndarrays` with wavelength, intensity data. The
            wavelengths are in nanometers but the intensity is in arbitrary
            units (but should be calibrated so that different devices yield the
            same output).
        """

        all_spectra = []
        for _ in range(count):
            wavelengths, intensities = self.device.get_spectrum()
            all_spectra.append(intensities)
            yield wavelengths, np.sum(all_spectra, axis=0)

    def set_integration_time(self, integration_time: int) -> None:
        """Set device integration time.

        The integration time is how long the device collects photons to measure
        the spectrum.

        Args:
            integration_time: The desired integration time in microseconds.
        """
        self.device.set_integration_time(integration_time)
