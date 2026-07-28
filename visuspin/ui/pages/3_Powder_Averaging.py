import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

from common import page_header
from visuspin.physics.csa import csa_shift
from visuspin.physics.powder import powder_visualization_data

st.set_page_config(page_title="VisuSpin — Powder Averaging", page_icon="🌐", layout="wide")
page_header("Powder Averaging (3D)", "Which crystallite orientations build which part of a powder pattern")

with st.sidebar:
    st.subheader("CSA tensor (used as the example interaction)")
    delta_iso = st.slider("δ_iso (ppm)", -200.0, 200.0, 0.0, 1.0)
    delta_aniso = st.slider("Anisotropy Δδ (ppm)", -300.0, 300.0, 100.0, 1.0)
    eta_csa = st.slider("Asymmetry η", 0.0, 1.0, 0.4, 0.01)
    n_points = st.slider("Crystallites sampled", 200, 5000, 1200, 100)
    elev = st.slider("View elevation", 0, 90, 20, 5)
    azim = st.slider("View azimuth", 0, 360, -60, 10)

data = powder_visualization_data(lambda ct, p: csa_shift(ct, p, delta_iso, delta_aniso, eta_csa), n_samples=n_points)

col1, col2 = st.columns([1.1, 1])
with col1:
    fig = plt.figure(figsize=(6, 6))
    ax = fig.add_subplot(111, projection="3d")
    sca = ax.scatter(data["x"], data["y"], data["z"], c=data["shift"], cmap="coolwarm", s=8)
    ax.set_xlim(-1, 1); ax.set_ylim(-1, 1); ax.set_zlim(-1, 1)
    ax.set_xlabel("x"); ax.set_ylabel("y"); ax.set_zlabel("z (B0 direction in the crystallite frame)")
    ax.view_init(elev=elev, azim=azim)
    fig.colorbar(sca, ax=ax, shrink=0.6, label="Shift (ppm)")
    ax.set_title("Each point = one crystallite's B0 orientation,\ncoloured by its single-crystal shift")
    st.pyplot(fig); plt.close(fig)

with col2:
    fig2, ax2 = plt.subplots(figsize=(6, 3))
    ax2.plot(data["hist_freq"], data["hist_intensity"], color="#5b46e5")
    ax2.set_xlabel("Chemical shift (ppm)"); ax2.set_ylabel("Intensity"); ax2.invert_xaxis()
    ax2.set_title("Resulting powder pattern")
    st.pyplot(fig2); plt.close(fig2)
    st.markdown(
        """
        **Reading the two plots together:** the red/blue poles of the sphere
        (θ≈0, where B0 is near the tensor's unique axis) map onto the
        outermost edges of the powder pattern; the equatorial band (θ≈90°)
        maps onto the pattern's more probable, higher-intensity region — the
        classic reason CSA/dipolar/first-order-quadrupolar powder patterns
        are edge-weighted rather than Gaussian-shaped: far more of the
        sphere's *area* lies near the equator than near the poles.
        """
    )

st.caption(
    "Orientations are sampled uniformly over the unit sphere (visuspin.physics.powder); "
    "shift(θ,φ) uses the same Haeberlen-convention CSA formula as the Lineshapes page."
)
