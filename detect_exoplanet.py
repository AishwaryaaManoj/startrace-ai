
import numpy as np
from astropy.timeseries import BoxLeastSquares


def detect_transit(time, flux):
    """Search a validated light curve for periodic transit-like dips."""

    time = np.asarray(time, dtype=float)
    flux = np.asarray(flux, dtype=float)

    if len(time) < 20 or len(time) != len(flux):
        raise ValueError("Need at least 20 matching time and flux values.")

    if not np.all(np.isfinite(time)) or not np.all(np.isfinite(flux)):
        raise ValueError("Input contains invalid values.")

    order = np.argsort(time)
    time = time[order]
    flux = flux[order]

    if np.ptp(time) <= 0:
        raise ValueError("Time values must span a positive range.")

    # Normalize brightness around 1.0
    median_flux = np.median(flux)
    if median_flux == 0:
        raise ValueError("Median flux must not be zero.")

    normalized_flux = flux / median_flux

    # Search for transit periods
    model = BoxLeastSquares(time, normalized_flux)
    periods = np.linspace(0.5, min(20, np.ptp(time) / 2), 2000)
    durations = np.linspace(0.02, 0.1, 10)

    result = model.power(periods, durations)

    best = np.argmax(result.power)

    return {
        "period": float(result.period[best]),
        "duration": float(result.duration[best]),
        "transit_depth": float(result.depth[best]),
        "power": float(result.power[best]),
        "time": time,
        "normalized_flux": normalized_flux,
        "result": result,
    }


if __name__ == "__main__":
    # Generate a test light curve with a known repeating transit.
    # This checks the algorithm; it is not a real planet discovery.
    rng = np.random.default_rng(42)

    time = np.linspace(0, 30, 3000)
    true_period = 3.0
    phase = ((time - 0.5 + true_period / 2) % true_period) - true_period / 2

    flux = np.ones_like(time)
    flux[np.abs(phase) < 0.08] -= 0.02
    flux += rng.normal(0, 0.001, len(time))

    candidate = detect_transit(time, flux)

    print("EXOPLANET HUNTER: TRANSIT DETECTION")
    print("=" * 40)
    print(f"Expected test period: {true_period:.3f} days")
    print(f"Detected period:      {candidate['period']:.3f} days")
    print(f"Estimated depth:      {candidate['transit_depth']:.5f}")
    print(f"BLS power:            {candidate['power']:.5f}")
