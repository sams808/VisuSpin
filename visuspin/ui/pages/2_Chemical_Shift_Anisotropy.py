import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

from common import page_header, lesson_header, key_takeaway, term, predict_then_reveal, next_lesson
from visuspin.physics.csa import csa_shift, csa_powder_pattern, principal_values
from visuspin.physics.powder import powder_visualization_data

st.set_page_config(page_title="VisuSpin — Chemical Shift Anisotropy", page_icon="📈", layout="wide")
page_header("Lesson 2: Chemical Shift Anisotropy")
lesson_header(
    "Lesson 2 of 11",
    "Why does a solid powder turn one sharp peak into a broad hump?",
    "In solution, a compound gives one sharp peak per chemical environment. Take the exact "
    "same compound as a powdered solid — same molecule, same electrons — and that peak "
    "smears into a broad, oddly-shaped hump. Nothing about the chemistry changed. What did?",
)

st.markdown(
    """
In a liquid, molecules tumble millions of times per second, so each nucleus
experiences every possible orientation *averaged together* almost instantly
— one clean number, one sharp peak. In a solid, molecules are frozen in
place. And it turns out the local magnetic shielding a nucleus feels
genuinely **depends on which way its molecule is pointing** relative to B0
— the electron cloud around it isn't a perfect sphere, so it shields the
nucleus more along some molecular directions than others. This orientation
dependence is called **chemical shift anisotropy (CSA)**.
"""
)

st.subheader("1. One crystallite, one orientation, one sharp peak")
st.markdown("Pick an orientation of a single tiny crystal relative to B0, and you still get a single, sharp line — just at a shift that depends on that orientation.")
c1, c2 = st.columns([1, 1.5])
with c1:
    delta_iso = st.slider("δ_iso (ppm)", -50.0, 50.0, 0.0, 1.0)
    delta_aniso = st.slider("Anisotropy Δδ (ppm)", 20.0, 300.0, 120.0, 1.0)
    eta_csa = st.slider("Asymmetry η", 0.0, 1.0, 0.3, 0.01)
    theta_deg = st.slider("Crystal orientation θ (deg from B0)", 0, 180, 0, 1)
    phi_deg = st.slider("Crystal orientation φ (deg)", 0, 360, 0, 1)
    dzz, dxx, dyy = principal_values(delta_iso, delta_aniso, eta_csa)
with c2:
    shift_here = csa_shift(np.array([np.cos(np.radians(theta_deg))]), np.array([np.radians(phi_deg)]),
                             delta_iso, delta_aniso, eta_csa)[0]
    span = max(abs(dzz - delta_iso), abs(dxx - delta_iso), abs(dyy - delta_iso)) * 1.3 + 5
    freqs = np.linspace(delta_iso - span, delta_iso + span, 400)
    single_line = np.exp(-((freqs - shift_here) ** 2) / (2 * 1.5 ** 2))
    fig0, ax0 = plt.subplots(figsize=(6, 3))
    ax0.plot(freqs, single_line, color="#5b46e5")
    ax0.set_xlabel("Shift (ppm)"); ax0.set_ylabel("Intensity"); ax0.invert_xaxis()
    ax0.set_title(f"Single-crystal shift at this orientation: {shift_here:.1f} ppm")
    st.pyplot(fig0); plt.close(fig0)

with predict_then_reveal("Rotate the crystal (drag θ from 0° to 90°) without touching δ_iso/Δδ/η. Does the peak move?"):
    st.write(
        f"Yes — from {csa_shift(np.array([1.0]), np.array([0.0]), delta_iso, delta_aniso, eta_csa)[0]:.1f} ppm "
        f"at θ=0° to {csa_shift(np.array([0.0]), np.array([0.0]), delta_iso, delta_aniso, eta_csa)[0]:.1f} ppm at "
        f"θ=90°, φ=0°. Same nucleus, same molecule, same electrons — the *only* thing that changed "
        f"is which way it's pointing relative to B0. That's the entire anisotropy in a nutshell."
    )

st.subheader("2. A powder: every orientation, all at once")
st.markdown(
    """
A real powder sample has ~10²⁰ tiny crystallites, oriented in every possible
direction with equal probability. Each one gives its own sharp line at its
own orientation-dependent shift — and the spectrum we record is the sum of
*all of them at once*.
"""
)
n_points = st.slider("Crystallites sampled (for the 3D picture)", 300, 4000, 1500, 100)
data = powder_visualization_data(lambda ct, p: csa_shift(ct, p, delta_iso, delta_aniso, eta_csa), n_samples=n_points)
pat = csa_powder_pattern(delta_iso, delta_aniso, eta_csa)

col1, col2 = st.columns(2)
with col1:
    fig1 = plt.figure(figsize=(5.5, 5.5))
    ax1 = fig1.add_subplot(111, projection="3d")
    sca = ax1.scatter(data["x"], data["y"], data["z"], c=data["shift"], cmap="coolwarm", s=6)
    ax1.set_xlabel("x"); ax1.set_ylabel("y"); ax1.set_zlabel("B0 direction, in the crystal's own frame")
    fig1.colorbar(sca, ax=ax1, shrink=0.6, label="Shift (ppm)")
    ax1.set_title("Every crystallite's B0 orientation,\ncoloured by its own single-crystal shift")
    st.pyplot(fig1); plt.close(fig1)
with col2:
    fig2, ax2 = plt.subplots(figsize=(6, 5.5))
    ax2.plot(pat["shift"], pat["intensity"], color="#5b46e5")
    ax2.set_xlabel("Shift (ppm)"); ax2.set_ylabel("Intensity"); ax2.invert_xaxis()
    ax2.set_title("The powder pattern: the sum over every orientation")
    st.pyplot(fig2); plt.close(fig2)

key_takeaway(
    "The powder pattern's sharp edges come from the rare orientations where B0 lines up with "
    "a principal axis of the shift tensor (the poles of the sphere); the higher, broader middle "
    "comes from the equatorial band, simply because far more of a sphere's surface area sits "
    "near the equator than near either pole. Nothing exotic — it's a solid-angle-weighting effect, "
    "the same reason more of Earth's surface is near the equator than near the poles."
)

next_lesson("Lesson 3 — Dipolar Coupling", "pages/3_Dipolar_Coupling.py")
