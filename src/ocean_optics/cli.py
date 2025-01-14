import csv
from typing import Annotated

import matplotlib.pyplot as plt
import plotext
import typer
from rich import print
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
    graph: Annotated[bool, typer.Option()] = True,
    gui: Annotated[bool, typer.Option()] = False,
    scatter: Annotated[bool, typer.Option()] = False,
    limits: Annotated[tuple[float, float], typer.Option()] = (None, None),
    output: Annotated[typer.FileTextWrite, typer.Option()] = None,
    quiet: Annotated[bool, typer.Option()] = False,
):
    """Show a spectrum."""

    experiment = open_experiment()
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
        writer = csv.writer(output)
        writer.writerow(["Wavelength (nm)", "Intensity"])
        for wavelength, intensity in zip(wavelengths, intensities):
            writer.writerow([wavelength, intensity])
        print(f"Data written to [bold]{output.name}[/] successfully.")


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


if __name__ == "__main__":
    app()
