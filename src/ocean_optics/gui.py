import sys

import pyqtgraph as pg
from PySide6 import QtWidgets
from PySide6.QtCore import Slot

from ocean_optics.spectroscopy import SpectroscopyExperiment

# PyQtGraph global options
pg.setConfigOption("background", "w")
pg.setConfigOption("foreground", "k")


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
        continuous_button = QtWidgets.QPushButton("Continuous")
        hbox.addWidget(continuous_button)

        # Slots and signals
        single_button.clicked.connect(self.single_measurement)

        # Open device
        self.experiment = SpectroscopyExperiment()

    @Slot()
    def single_measurement(self):
        wavelengths, intensities = self.experiment.get_spectrum()

        self.plot_widget.clear()
        self.plot_widget.plot(
            wavelengths, intensities, symbol=None, pen={"color": "k", "width": 5}
        )
        self.plot_widget.setLabel("left", "Intensity")
        self.plot_widget.setLabel("bottom", "Wavelength (nm)")
        self.plot_widget.setLimits(yMin=0)


def main():
    app = QtWidgets.QApplication(sys.argv)
    ui = UserInterface()
    ui.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
