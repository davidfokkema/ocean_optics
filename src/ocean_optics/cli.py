import csv
import pathlib
from typing import Annotated

import matplotlib.pyplot as plt
import numpy as np
import plotext
import typer
from rich import print
from rich.progress import track
from rich.table import Table

from ocean_optics.spectroscopy import DeviceNotFoundError, SpectroscopyExperiment

app = typer.Typer()


@app.command()
def check():
    """Check if a compatible device can be found."""
    try:
        SpectroscopyExperiment()
    except DeviceNotFoundError:
        print("[red]No compatible device found.")
    else:
        print("[green]Device is connected and available.")


@app.command()
def spectrum(
    int_time: Annotated[
        int,
        typer.Option(
            "--int-time",
            "-t",
            help="Set the integration time of the device in microseconds.",
        ),
    ] = 100_000,
    graph: Annotated[
        bool,
        typer.Option(
            help="""Plot the spectrum in a graph in the terminal. If --no-graph
                 is used, display the resuls in a table instead.""",
        ),
    ] = True,
    gui: Annotated[bool, typer.Option(help="Use a GUI to show the graph.")] = False,
    scatter: Annotated[
        bool,
        typer.Option(
            "--scatter", "-s", help="Use a scatter plot instead of a line plot."
        ),
    ] = False,
    limits: Annotated[
        tuple[float, float], typer.Option(help="Restrict wavelengths to (min, max).")
    ] = (None, None),
    output: Annotated[
        typer.FileTextWrite,
        typer.Option("--output", "-o", help="Write the results to a CSV file."),
    ] = None,
    quiet: Annotated[
        bool, typer.Option("--quiet", "-q", help="Don't show any console output.")
    ] = False,
):
    """Record a spectrum.

    Record a spectrum using the spectrometer, displaying the results in a graph
    in the terminal. There are various options for other forms of output. The
    unit of intensity is arbitrary.
    """

    experiment = open_experiment()
    experiment.set_integration_time(int_time)
    wavelengths, intensities = experiment.get_spectrum()

    xmin, xmax = limits
    if limits != (None, None):
        mask = (xmin <= wavelengths) & (wavelengths <= xmax)
        wavelengths = wavelengths[mask]
        intensities = intensities[mask]

    if not quiet:
        if graph:
            if gui:
                if scatter:
                    plt.scatter(wavelengths, intensities, marker=".")
                else:
                    plt.plot(wavelengths, intensities)
                plt.xlim(xmin, xmax)
                plt.xlabel("Wavelength (nm)")
                plt.ylabel("Intensity")
                plt.show()
            else:
                plotext.theme("clear")
                if scatter:
                    plotext.scatter(wavelengths, intensities, marker="braille")
                else:
                    plotext.plot(wavelengths, intensities, marker="braille")
                plotext.xlim(xmin, xmax)
                plotext.xlabel("Wavelength (nm)")
                plotext.ylabel("Intensity")
                plotext.show()
        else:
            rich_table = Table("Wavelength (nm)", "Intensity")
            for wavelength, intensity in zip(wavelengths, intensities):
                rich_table.add_row(f"{wavelength:.1f}", f"{intensity:.1f}")
            print(rich_table)

    if output:
        save_spectrum(output, wavelengths, intensities)


@app.command()
def integrate(
    count: Annotated[
        int, typer.Option("--count", "-c", help="Number of measurements to perform.")
    ] = 10,
    int_time: Annotated[
        int,
        typer.Option(
            "--int-time",
            "-t",
            help="Set the integration time of the device in microseconds.",
        ),
    ] = 100_000,
    graph: Annotated[
        bool,
        typer.Option(
            help="Plot the spectrum in a graph in the terminal.",
        ),
    ] = True,
    scatter: Annotated[
        bool,
        typer.Option(
            "--scatter", "-s", help="Use a scatter plot instead of a line plot."
        ),
    ] = False,
    limits: Annotated[
        tuple[float, float], typer.Option(help="Restrict wavelengths to (min, max).")
    ] = (None, None),
    output: Annotated[
        typer.FileTextWrite,
        typer.Option("--output", "-o", help="Write the results to a CSV file."),
    ] = None,
):
    """Record a spectrum by integrating over multiple measurements.

    Record an integrated spectrum using the spectrometer. Multiple measurements
    are taken and they are summed to increase the signal to noise ratio. The
    results are displayed in a graph in the terminal. There are various options
    for other forms of output. The unit of intensity is arbitrary.
    """
    experiment = open_experiment()
    experiment.set_integration_time(int_time)
    xmin, xmax = limits

    plotext.theme("clear")
    plotext.xlim(xmin, xmax)
    plotext.xlabel("Wavelength (nm)")
    plotext.ylabel("Intensity")
    for wavelengths, intensities in track(
        experiment.integrate_spectrum(count), total=count, description="Taking data..."
    ):
        if limits != (None, None):
            mask = (xmin <= wavelengths) & (wavelengths <= xmax)
            wavelengths = wavelengths[mask]
            intensities = intensities[mask]

        if graph:
            plotext.clear_data()
            if scatter:
                plotext.scatter(wavelengths, intensities, marker="braille")
            else:
                plotext.plot(wavelengths, intensities, marker="braille")
            plotext.show()

    if output:
        save_spectrum(output, wavelengths, intensities)


def open_experiment():
    """Open the spectroscopy experiment.

    Connect to an available spectropy device.

    Raises:
        typer.Abort: An error occured opening the experiment.

    Returns:
        An `ocean_optics.Spectroscopy` instance.
    """
    try:
        experiment = SpectroscopyExperiment()
    except DeviceNotFoundError:
        print("[red]No compatible device found.")
        raise typer.Abort()
    return experiment


def save_spectrum(
    path: pathlib.Path, wavelengths: np.ndarray, intensities: np.ndarray
) -> None:
    """Save spectrum data to a file as CSV.

    Args:
        path: The path of the output file.
        wavelengths: The wavelength values.
        intensities: The intensity data.
    """
    writer = csv.writer(path)
    writer.writerow(["Wavelength (nm)", "Intensity"])
    for wavelength, intensity in zip(wavelengths, intensities):
        writer.writerow([wavelength, intensity])
    print(f"Data written to [bold]{path.name}[/] successfully.")


if __name__ == "__main__":
    app()
