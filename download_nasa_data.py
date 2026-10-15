
import lightkurve as lk
import pandas as pd
from pathlib import Path

def download_nasa_data():
    print("EXOPLANET HUNTER - NASA DATA DOWNLOAD")
    print("=" * 40)
    print("Searching for Kepler-10 observations...")

    try:
        results = lk.search_lightcurve(
            "Kepler-10",
            mission="Kepler",
            cadence="long"
        )

        if len(results) == 0:
            print("No observations found.")
            return

        print(f"Found {len(results)} available data products.")
        print("Downloading the first available observation...")

        # Start with one observation to keep the download manageable.
        light_curve = results[0].download(
            quality_bitmask="default"
        )

        if light_curve is None:
            print("Download returned no data.")
            return

        light_curve = light_curve.remove_nans().normalize()

        data = pd.DataFrame({
            "time": light_curve.time.value,
            "flux": light_curve.flux.value
        })

        data = data.replace([float("inf"), float("-inf")], pd.NA)
        data = data.dropna()
        data = data.sort_values("time")
        data = data.drop_duplicates(subset="time")

        if len(data) < 20:
            print("Not enough valid observations for analysis.")
            return

        output_dir = Path("data")
        output_dir.mkdir(parents=True, exist_ok=True)

        output_file = output_dir / "kepler10_lightcurve.csv"
        data.to_csv(output_file, index=False)

        print("\nDOWNLOAD SUCCESSFUL!")
        print("-" * 40)
        print("Source: NASA Kepler mission archive")
        print("Target: Kepler-10")
        print("Valid observations:", len(data))
        print(
            "Time range:",
            round(data["time"].min(), 4),
            "to",
            round(data["time"].max(), 4)
        )
        print("Saved file:", output_file.resolve())
        print("\nFirst five rows:")
        print(data.head().to_string(index=False))

    except Exception as error:
        print("\nDOWNLOAD FAILED")
        print("Error:", error)
        print(
            "Check your internet connection. "
            "Your synthetic demo is still available."
        )


if __name__ == "__main__":
    download_nasa_data()
