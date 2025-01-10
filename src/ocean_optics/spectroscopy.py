import numpy as np

from ocean_optics.usb2000plus import DeviceNotFoundError, OceanOpticsUSB2000Plus


class SpectroscopyExperiment:
    def __init__(self) -> None:
        self.device = OceanOpticsUSB2000Plus()

    def get_spectrum(self) -> tuple[np.ndarray, np.ndarray]:
        return self.device.get_spectrum()
