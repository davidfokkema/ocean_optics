import typer

from ocean_optics.spectroscopy import DeviceNotFoundError, SpectroscopyExperiment

app = typer.Typer()


@app.command()
def check():
    try:
        experiment = SpectroscopyExperiment()
    except DeviceNotFoundError:
        print("No compatible device found.")
    else:
        print("Device is connected and available.")


if __name__ == "__main__":
    app()
