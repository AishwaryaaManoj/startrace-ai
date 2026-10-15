import numpy as np
import pandas as pd


def validate_lightcurve(df):
    errors = []
    warnings = []

    # Check required columns
    required = {"time", "flux"}
    missing = required - set(df.columns)

    if missing:
        return None, [f"Missing required columns: {sorted(missing)}"], []

    # Convert values to numbers
    df = df.copy()
    df["time"] = pd.to_numeric(df["time"], errors="coerce")
    df["flux"] = pd.to_numeric(df["flux"], errors="coerce")

    # Remove missing and infinite values
    valid = (
        np.isfinite(df["time"]) &
        np.isfinite(df["flux"])
    )
    removed = int((~valid).sum())

    if removed:
        warnings.append(f"Removed {removed} invalid row(s).")

    df = df.loc[valid].copy()

    if len(df) < 20:
        errors.append("At least 20 valid observations are required.")

    # Check duplicate timestamps
    duplicates = int(df["time"].duplicated().sum())

    if duplicates:
        warnings.append(
            f"Removed {duplicates} duplicate timestamp row(s)."
        )
        df = df.drop_duplicates(subset="time", keep="first")

    # Sort chronologically
    df = df.sort_values("time").reset_index(drop=True)

    if len(df) < 20:
        errors.append("Too few unique observations remain.")

    if len(df) > 0:
        if df["time"].nunique() < 2:
            errors.append("Timestamps must span more than one time point.")
        elif df["time"].max() <= df["time"].min():
            errors.append("Invalid time range.")

        if (df["flux"] <= 0).any():
            warnings.append(
                "Some flux values are zero or negative; check the data."
            )

    if errors:
        return None, errors, warnings

    return df, errors, warnings


if __name__ == "__main__":
    # Built-in test data; no downloaded dataset is needed.
    sample = pd.DataFrame({
        "time": np.arange(100, dtype=float),
        "flux": 1.0 - 0.01 * np.sin(np.arange(100) / 5)
    })

    # Add one invalid row to test cleaning.
    sample.loc[10, "flux"] = np.nan

    cleaned, errors, warnings = validate_lightcurve(sample)

    print("TEST: Light-curve data validation")
    print("-" * 35)

    for warning in warnings:
        print("WARNING:", warning)

    for error in errors:
        print("ERROR:", error)

    if cleaned is not None:
        print("RESULT: PASS")
        print("Valid observations:", len(cleaned))
        print("Time range:", cleaned["time"].min(),
              "to", cleaned["time"].max())
    else:
        print("RESULT: FAIL")