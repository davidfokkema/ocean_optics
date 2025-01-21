import sys

import numpy as np
import pyqtgraph as pg
from PySide6 import QtCore, QtWidgets
from PySide6.QtCore import Slot

from ocean_optics.spectroscopy import SpectroscopyExperiment

# PyQtGraph global options
pg.setConfigOption("background", "w")
pg.setConfigOption("foreground", "k")


class MeasurementWorker(QtCore.QThread):
    new_data = QtCore.Signal(tuple)
    stopped = False

    def setup(self, experiment: SpectroscopyExperiment) -> None:
        self.experiment = experiment

    def run(self) -> None: ...

    def stop(self) -> None:
        self.stopped = True


class IntegrateSpectrumWorker(MeasurementWorker):
    def setup(self, experiment: SpectroscopyExperiment, count: int) -> None:
        self.experiment = experiment
        self.count = count

    def run(self) -> None:
        self.stopped = False
        for wavelengths, intensities in self.experiment.integrate_spectrum(self.count):
            self.new_data.emit((wavelengths, intensities))
            if self.stopped:
                self.experiment.stopped = True


class ContinuousSpectrumWorker(MeasurementWorker):
    def run(self) -> None:
        self.stopped = False
        while True:
            wavelengths, intensities = self.experiment.get_spectrum()
            self.new_data.emit((wavelengths, intensities))
            if self.stopped:
                break


class UserInterface(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        # Build UI
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)

        vbox = QtWidgets.QVBoxLayout(central_widget)
        self.plot_widget = pg.PlotWidget()
        vbox.addWidget(self.plot_widget)
        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)

        single_button = QtWidgets.QPushButton("Single")
        hbox.addWidget(single_button)
        self.integrate_button = QtWidgets.QPushButton("Integrate")
        hbox.addWidget(self.integrate_button)
        self.continuous_button = QtWidgets.QPushButton("Continuous")
        hbox.addWidget(self.continuous_button)
        self.stop_button = QtWidgets.QPushButton("Stop", enabled=False)
        hbox.addWidget(self.stop_button)

        # Slots and signals
        single_button.clicked.connect(self.single_measurement)
        self.integrate_button.clicked.connect(self.integrate_spectrum)
        self.continuous_button.clicked.connect(self.continuous_spectrum)
        self.stop_button.clicked.connect(self.stop_measurement)

        # Open device
        self.experiment = SpectroscopyExperiment()

        # Workers
        self.integrate_spectrum_worker = IntegrateSpectrumWorker()
        self.integrate_spectrum_worker.new_data.connect(self.plot_new_data)
        self.integrate_spectrum_worker.finished.connect(self.worker_has_finished)
        self.continuous_spectrum_worker = ContinuousSpectrumWorker()
        self.continuous_spectrum_worker.new_data.connect(self.plot_new_data)
        self.continuous_spectrum_worker.finished.connect(self.worker_has_finished)

    @Slot()
    def single_measurement(self):
        wavelengths, intensities = self.experiment.get_spectrum()
        self.plot_data(wavelengths, intensities)

    @Slot()
    def integrate_spectrum(self) -> None:
        self.disable_measurement_buttons()
        self.integrate_spectrum_worker.setup(experiment=self.experiment, count=100)
        self.integrate_spectrum_worker.start()

    @Slot()
    def continuous_spectrum(self) -> None:
        self.disable_measurement_buttons()
        self.continuous_spectrum_worker.setup(experiment=self.experiment)
        self.continuous_spectrum_worker.start()

    @Slot()
    def stop_measurement(self) -> None:
        self.integrate_spectrum_worker.stop()
        self.continuous_spectrum_worker.stop()

    def disable_measurement_buttons(self) -> None:
        self.integrate_button.setEnabled(False)
        self.continuous_button.setEnabled(False)
        self.stop_button.setEnabled(True)

    @Slot()
    def worker_has_finished(self) -> None:
        self.integrate_button.setEnabled(True)
        self.continuous_button.setEnabled(True)
        self.stop_button.setEnabled(False)

    def plot_data(self, wavelengths, intensities):
        self.plot_widget.clear()
        self.plot_widget.plot(
            wavelengths, intensities, symbol=None, pen={"color": "k", "width": 5}
        )
        self.plot_widget.setLabel("left", "Intensity")
        self.plot_widget.setLabel("bottom", "Wavelength (nm)")
        self.plot_widget.setLimits(yMin=0)

    @Slot(tuple)
    def plot_new_data(self, data: tuple[np.ndarray, np.ndarray]) -> None:
        self.plot_data(data[0], data[1])


def main():
    app = QtWidgets.QApplication(sys.argv)
    ui = UserInterface()
    ui.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
