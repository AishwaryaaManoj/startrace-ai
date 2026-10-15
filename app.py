import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from pathlib import Path

# Project backend modules created earlier
try:
    from validate_data import validate_lightcurve
    from detect_exoplanet import detect_transit
    BACKEND_IMPORT_ERROR = None
except Exception as exc:
    validate_lightcurve = None
    detect_transit = None
    BACKEND_IMPORT_ERROR = str(exc)

st.set_page_config(
    page_title="STARTRACE AI | Exoplanet Hunter",
    page_icon="🔭",
    layout="wide"
)

st.markdown("""
<style>
/* Dark space theme with high-contrast, readable text */
.stApp, [data-testid="stAppViewContainer"] {
    background: #080d19;
    color: #f3f6ff;
}
[data-testid="stHeader"] { background: rgba(8, 13, 25, 0.96); }
[data-testid="stSidebar"] { background: #111b2e; }
[data-testid="stSidebar"] * { color: #e7edff !important; }

/* Main content text */
.stApp p, .stApp li, .stApp label, .stApp span,
.stApp small, .stApp .stMarkdown, [data-testid="stCaptionContainer"] {
    color: #e3eaff;
}
h1, h2, h3, h4, h5, h6,
.stApp h1, .stApp h2, .stApp h3 {
    color: #f5f7ff !important;
}
[data-testid="stMetricLabel"] p,
[data-testid="stMetricLabel"] {
    color: #c4d2f0 !important;
}
[data-testid="stMetricValue"] {
    color: #ffffff !important;
}
[data-testid="stMetric"] {
    background: #142139;
    border: 1px solid #2d4264;
    border-radius: 12px;
    padding: 15px;
}

/* Inputs and dropdowns */
.stSelectbox label, .stFileUploader label, .stTextInput label {
    color: #e7edff !important;
}
[data-baseweb="select"] > div {
    background: #182640 !important;
    border-color: #40577d !important;
}
[data-baseweb="select"] *, [data-baseweb="popover"] * {
    color: #f4f7ff !important;
}
input, textarea {
    color: #f4f7ff !important;
    background: #182640 !important;
}

/* Buttons */
.stButton > button, .stDownloadButton > button {
    background: #78e6d5;
    color: #07111b !important;
    border-radius: 10px;
    font-weight: 700;
    border: none;
}
.stButton > button:hover, .stDownloadButton > button:hover {
    background: #a0f3e7;
    color: #07111b !important;
}

/* Tables and notices */
[data-testid="stDataFrame"] {
    border: 1px solid #2d4264;
    border-radius: 8px;
}
[data-testid="stAlert"] p { color: #f3f6ff !important; }
hr { border-color: #293953 !important; }
</style>
""", unsafe_allow_html=True)

BASE_DIR = Path(__file__).resolve().parent
NASA_CSV = BASE_DIR / "data" / "kepler10_lightcurve.csv"

st.sidebar.title("🔭 STARTRACE AI")
st.sidebar.caption("EXOPLANET HUNTER")
st.sidebar.divider()

data_source = st.sidebar.selectbox(
    "Choose data source",
    ["NASA Kepler-10", "Demo Data", "Upload CSV"]
)

scenario = st.sidebar.selectbox(
    "Select a demo signal",
    ["Transit Signal", "Random Noise", "Ambiguous Signal"],
    disabled=(data_source != "Demo Data")
)

uploaded = None
if data_source == "Upload CSV":
    uploaded = st.sidebar.file_uploader(
        "Upload stellar data (CSV)",
        type=["csv"]
    )

def make_sample(scenario_name):
    rng = np.random.default_rng(42)
    time = np.linspace(0, 10, 600)
    flux = 1 + rng.normal(0, 0.0015, len(time))

    if scenario_name == "Transit Signal":
        phase = np.mod(time + 0.18, 2.7)
        flux[(phase > 1.296) & (phase < 1.431)] -= 0.012
    elif scenario_name == "Ambiguous Signal":
        phase = np.mod(time + 0.18, 2.7)
        flux[(phase > 1.296) & (phase < 1.431)] -= 0.004
        flux += 0.0015 * np.sin(time * 2.3)
    else:
        idx = rng.choice(len(time), 8, replace=False)
        flux[idx] -= rng.uniform(0.002, 0.008, 8)

    return pd.DataFrame({"time": time, "flux": flux})

st.markdown("""
# STARTRACE AI
### A signal hidden in the starlight

Explore stellar brightness and investigate tiny dips that
could reveal an orbiting exoplanet.
""")

st.divider()

# Load data according to the selected source
try:
    if data_source == "NASA Kepler-10":
        if not NASA_CSV.exists():
            st.error(
                "NASA dataset not found. Make sure this file exists: "
                "`data/kepler10_lightcurve.csv` inside your project folder."
            )
            st.stop()
        data = pd.read_csv(NASA_CSV)
        dataset_label = "NASA Kepler-10"
    elif data_source == "Upload CSV":
        if uploaded is None:
            st.info("Upload a CSV file from the sidebar to continue.")
            st.stop()
        data = pd.read_csv(uploaded)
        dataset_label = "Uploaded CSV"
    else:
        data = make_sample(scenario)
        dataset_label = f"Demo: {scenario}"

    data.columns = [
        str(c).strip().lower().replace(" ", "_")
        for c in data.columns
    ]

    if not {"time", "flux"}.issubset(data.columns):
        st.error("Your CSV must contain columns named `time` and `flux`.")
        st.stop()

    data = data[["time", "flux"]].copy()
    data["time"] = pd.to_numeric(data["time"], errors="coerce")
    data["flux"] = pd.to_numeric(data["flux"], errors="coerce")
    data = data.replace([np.inf, -np.inf], np.nan).dropna()
    data = data.sort_values("time").drop_duplicates(subset=["time"])

    if len(data) < 20:
        st.error("At least 20 valid observations are required.")
        st.stop()

except Exception as exc:
    st.error(f"Unable to load the selected data: {exc}")
    st.stop()

# Run the project's validator if available
if validate_lightcurve is not None:
    try:
        validated = validate_lightcurve(data)
        if isinstance(validated, tuple) and len(validated) == 3:
            clean_data, validation_errors, validation_warnings = validated
        else:
            st.error("validate_lightcurve returned an unexpected result.")
            st.stop()

        if validation_errors:
            for message in validation_errors:
                st.error(str(message))
            st.stop()

        for message in validation_warnings:
            st.warning(str(message))

        data = clean_data.copy()
    except Exception as exc:
        st.error(f"Data validation failed: {exc}")
        st.stop()
else:
    st.warning(
        "Backend validation module could not be imported. "
        "The dashboard loaded the data using basic checks only. "
        f"Import detail: {BACKEND_IMPORT_ERROR}"
    )

median_flux = data["flux"].median()
if not np.isfinite(median_flux) or median_flux == 0:
    st.error("The flux data cannot be normalized.")
    st.stop()

data["relative_flux"] = data["flux"] / median_flux

st.subheader("Mission Overview")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Observations", f"{len(data):,}")
c2.metric("Time Coverage", f"{data['time'].max() - data['time'].min():.2f} days")
c3.metric("Median Flux", f"{median_flux:.5f}")
c4.metric("Dataset", dataset_label)

st.divider()
left, right = st.columns([2, 1])

with left:
    st.subheader("🌌 Stellar Light Curve")
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=data["time"],
        y=data["relative_flux"],
        mode="lines",
        line=dict(color="#72e5d3", width=1.5),
        hovertemplate="Time: %{x:.3f} days<br>Relative flux: %{y:.6f}<extra></extra>"
    ))
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#080d19",
        plot_bgcolor="#0c1424",
        height=430,
        xaxis_title="Time (days)",
        yaxis_title="Relative brightness",
        showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("📊 Data Preview")
    st.dataframe(
        data[["time", "flux", "relative_flux"]].head(12),
        use_container_width=True,
        hide_index=True
    )
    st.download_button(
        "Download CSV",
        data=data[["time", "flux"]].to_csv(index=False),
        file_name="startrace_data.csv",
        mime="text/csv"
    )

st.divider()
st.subheader("🪐 Candidate Analysis")
st.write(
    "Run the Box Least Squares (BLS) algorithm on the selected light curve. "
    "A candidate signal is not proof of an exoplanet."
)

if detect_transit is None:
    st.error(
        "The detection backend could not be imported. Check that "
        "`detect_exoplanet.py` is in the same folder as `app.py` and that "
        "Astropy is installed. "
        + (f"Import detail: {BACKEND_IMPORT_ERROR}" if BACKEND_IMPORT_ERROR else "")
    )
else:
    if st.button("Run Candidate Analysis"):
        with st.spinner("Searching for possible repeating transit dips..."):
            try:
                result = detect_transit(
                    data["time"].to_numpy(dtype=float),
                    data["flux"].to_numpy(dtype=float)
                )
                if not isinstance(result, dict):
                    raise ValueError("Detection function did not return a result dictionary.")

                period = float(result["period"])
                duration = float(result["duration"])
                depth = float(result["transit_depth"])
                power = float(result["power"])

                st.success("BLS analysis completed.")
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Candidate Period", f"{period:.5f} days")
                m2.metric("Transit Duration", f"{duration:.4f} days")
                m3.metric("Transit Depth", f"{depth:.6f}")
                m4.metric("BLS Power", f"{power:.3e}")

                # Show phase-folded light curve using the detected candidate period.
                plot_time = np.asarray(result.get("time", data["time"]), dtype=float)
                normalized_flux = np.asarray(
                    result.get("normalized_flux", data["relative_flux"]), dtype=float
                )
                if period > 0 and len(plot_time) == len(normalized_flux):
                    phase = ((plot_time / period + 0.5) % 1.0) - 0.5
                    order = np.argsort(phase)
                    folded = go.Figure()
                    folded.add_trace(go.Scatter(
                        x=phase[order],
                        y=normalized_flux[order],
                        mode="markers",
                        marker=dict(color="#a78bfa", size=4, opacity=0.75),
                        hovertemplate="Phase: %{x:.3f}<br>Relative flux: %{y:.6f}<extra></extra>"
                    ))
                    folded.update_layout(
                        template="plotly_dark",
                        paper_bgcolor="#080d19",
                        plot_bgcolor="#0c1424",
                        height=350,
                        xaxis_title="Orbital phase",
                        yaxis_title="Normalized brightness",
                        showlegend=False
                    )
                    st.subheader("Phase-Folded Candidate Curve")
                    st.plotly_chart(folded, use_container_width=True)

                st.warning(
                    "This is a possible transit candidate, not a confirmed exoplanet. "
                    "The current Kepler-10 test has a weak signal, so its result needs "
                    "additional validation and better-quality or longer observations."
                )

                report = pd.DataFrame([{
                    "dataset": dataset_label,
                    "observations": len(data),
                    "candidate_period_days": period,
                    "transit_duration_days": duration,
                    "transit_depth": depth,
                    "bls_power": power,
                    "interpretation": "Candidate only; not confirmed"
                }])
                st.download_button(
                    "Download Candidate Report",
                    data=report.to_csv(index=False),
                    file_name="startrace_candidate_report.csv",
                    mime="text/csv"
                )

            except Exception as exc:
                st.error(
                    "Candidate analysis failed. Check that `detect_exoplanet.py` "
                    "matches the expected function interface. "
                    f"Details: {exc}"
                )

st.divider()
c1, c2, c3 = st.columns(3)
c1.markdown("### 🔭 Observe")
c1.write("Visualize stellar brightness over time.")
c2.markdown("### 🧪 Investigate")
c2.write("Search for repeated brightness dips using BLS.")
c3.markdown("### ✅ Validate")
c3.write("Review the evidence before identifying a candidate.")

st.caption(
    "STARTRACE AI · Hackathon prototype · "
    "Synthetic demo data are illustrative, not real observations."
)
