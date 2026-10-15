import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(
    page_title="STARTRACE AI | Exoplanet Hunter",
    page_icon="🔭",
    layout="wide"
)

st.markdown("""
<style>
.stApp {
    background: #080d19;
    color: #edf3ff;
}
[data-testid="stSidebar"] {
    background: #10182a;
}
h1, h2, h3 {
    color: #72e5d3;
}
div[data-testid="stMetric"] {
    background: #131e32;
    border: 1px solid #263751;
    border-radius: 12px;
    padding: 15px;
}
.stButton > button {
    background: #72e5d3;
    color: #07111b;
    border-radius: 10px;
    font-weight: bold;
    border: none;
}
</style>
""", unsafe_allow_html=True)

st.sidebar.title("🔭 STARTRACE AI")
st.sidebar.caption("EXOPLANET HUNTER")
st.sidebar.divider()

scenario = st.sidebar.selectbox(
    "Select a signal",
    ["Transit Signal", "Random Noise", "Ambiguous Signal"]
)

uploaded = st.sidebar.file_uploader(
    "Upload stellar data (CSV)",
    type=["csv"]
)

def make_sample(scenario):
    rng = np.random.default_rng(42)
    time = np.linspace(0, 10, 600)
    flux = 1 + rng.normal(0, 0.0015, len(time))

    if scenario == "Transit Signal":
        phase = np.mod(time + 0.18, 2.7)
        flux[(phase > 1.296) & (phase < 1.431)] -= 0.012
    elif scenario == "Ambiguous Signal":
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

try:
    if uploaded:
        data = pd.read_csv(uploaded)
        data.columns = [
            str(c).strip().lower().replace(" ", "_")
            for c in data.columns
        ]

        if not {"time", "flux"}.issubset(data.columns):
            st.error("Your CSV must contain columns named time and flux.")
            st.stop()

        data = data[["time", "flux"]].copy()
        data["time"] = pd.to_numeric(data["time"], errors="coerce")
        data["flux"] = pd.to_numeric(data["flux"], errors="coerce")
        data = data.replace([np.inf, -np.inf], np.nan).dropna()
        data = data.sort_values("time")

        if len(data) < 10:
            st.error("Please upload at least 10 valid rows.")
            st.stop()
    else:
        data = make_sample(scenario)

except Exception as e:
    st.error(f"Unable to read the file: {e}")
    st.stop()

median_flux = data["flux"].median()

if not np.isfinite(median_flux) or median_flux == 0:
    st.error("The flux data cannot be normalized.")
    st.stop()

data["relative_flux"] = data["flux"] / median_flux

st.subheader("Mission Overview")
c1, c2, c3, c4 = st.columns(4)

c1.metric("Observations", f"{len(data):,}")
c2.metric(
    "Time Coverage",
    f"{data['time'].max() - data['time'].min():.2f} days"
)
c3.metric("Median Flux", f"{median_flux:.5f}")
c4.metric("Dataset", "Uploaded CSV" if uploaded else "Demo Data")

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
        hovertemplate="Time: %{x:.3f} days<br>Flux: %{y:.6f}<extra></extra>"
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
    "Investigate possible dips in stellar brightness. "
    "A dip alone does not confirm an exoplanet."
)

if st.button("Run Candidate Analysis"):
    st.info(
        "The frontend is working! Your teammate can connect "
        "the real detection algorithm here."
    )

st.divider()

c1, c2, c3 = st.columns(3)
c1.markdown("### 🔭 Observe")
c1.write("Visualize stellar brightness over time.")
c2.markdown("### 🧪 Investigate")
c2.write("Look for repeated brightness dips.")
c3.markdown("### ✅ Validate")
c3.write("Check evidence before identifying a candidate.")

st.caption(
    "STARTRACE AI · Hackathon prototype · "
    "Synthetic demo data are illustrative, not real observations."
)