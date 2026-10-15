
import pandas as pd
from validate_data import validate_lightcurve
from detect_exoplanet import detect_transit

print("EXOPLANET HUNTER - REAL NASA DATA TEST")
print("=" * 45)

# Load NASA data
df = pd.read_csv("data/kepler10_lightcurve.csv")
print("Loaded observations:", len(df))

# Validator returns: cleaned data, errors, warnings
clean_df, errors, warnings = validate_lightcurve(df)

if errors:
    print("\nValidation errors:")
    for error in errors:
        print("-", error)
    raise SystemExit("STOP: Please fix validation errors.")

print("\nData validation PASSED!")
print("Valid observations:", len(clean_df))

if warnings:
    print("\nValidation warnings:")
    for warning in warnings:
        print("-", warning)

# Run the existing BLS transit detector
print("\nRunning transit detection...")
result = detect_transit(
    clean_df["time"].to_numpy(),
    clean_df["flux"].to_numpy()
)



print("\nTRANSIT DETECTION RESULTS")
print("=" * 45)
print(f"Candidate period: {result['period']:.6f} days")
print(f"Transit duration: {result['duration']:.4f} days")
print(f"Transit depth: {result['transit_depth']:.8f}")
print(f"BLS power: {result['power']:.10g}")

print("\nInterpretation:")
print("A candidate period was found.")
print("This result alone does not confirm an exoplanet.")
print("Further observations and signal-strength checks are needed.")

