import typer
from rich import print
from rich.table import Table

from ocean_optics.spectroscopy import DeviceNotFoundError, SpectroscopyExperiment

app = typer.Typer()


@app.command()
def check():
    try:
        experiment = SpectroscopyExperiment()
    except DeviceNotFoundError:
        print("[red]No compatible device found.")
    else:
        print("[green]Device is connected and available.")


@app.command()
def spectrum():
    try:
        experiment = SpectroscopyExperiment()
    except DeviceNotFoundError:
        print("No compatible device found.")

    wavelengths, intensities = experiment.get_spectrum()
    table = Table("Wavelength (nm)", "Intensity")
    for wavelength, intensity in zip(wavelengths, intensities):
        table.add_row(f"{wavelength:.1f}", f"{intensity:.1f}")
    print(table)


if __name__ == "__main__":
    app()
