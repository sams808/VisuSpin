import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

from common import page_header, lesson_header, key_takeaway, term, predict_then_reveal, next_lesson
from visuspin.physics.paramagnetic import contact_shift_ppm, pseudocontact_shift_ppm, pre_rate_hz

st.set_page_config(page_title="VisuSpin — Paramagnetic NMR", page_icon="🧲", layout="wide")
page_header("Lesson 20: Paramagnetic NMR")
lesson_header(
    "Lesson 20 of 24",
    "A trace of Fe3+ or a rare-earth dopant can devastate a spectrum — or become a powerful probe.",
    "An unpaired electron's magnetic moment is about 658 times a proton's. Even weak coupling to "
    "one has an outsized effect on nearby nuclei. What are the actual mechanisms, and can they be "
    "put to use rather than just avoided?",
)

st.markdown(
    """
Three distinct mechanisms, each with its own signature:

- **Fermi contact shift** — unpaired electron spin density delocalized onto
  the nucleus through chemical bonds. Isotropic (no orientation dependence),
  falls off fast with bonding distance, and follows Curie's law (∝ 1/T).
- **Pseudocontact shift** — a through-space dipolar interaction with the
  ion's (anisotropic) induced moment. Same (3cos²θ−1) geometric factor
  you've now seen for CSA and dipolar coupling — but can reach nuclei much
  farther away than the contact mechanism.
- **PRE (paramagnetic relaxation enhancement)** — the fluctuating electron
  moment is a hugely efficient relaxation pathway, falling off as 1/r⁶.
"""
)

st.subheader("Contact shift: Curie's law")
c1, c2 = st.columns([1, 1.5])
with c1:
    delta_ref = st.slider("Reference contact shift at 298 K (ppm)", 5.0, 300.0, 80.0, 5.0)
with c2:
    T_range = np.linspace(200, 500, 200)
    shifts = contact_shift_ppm(delta_ref, T_range)
    fig, ax = plt.subplots(figsize=(6.5, 3.2))
    ax.plot(T_range, shifts, color="#5b46e5")
    ax.set_xlabel("Temperature (K)"); ax.set_ylabel("Contact shift (ppm)")
    st.pyplot(fig); plt.close(fig)

with predict_then_reveal("Does the contact shift extrapolate to zero as T -> infinity, or level off at some nonzero value?"):
    st.write(
        "It extrapolates to exactly zero — Curie's law is a pure 1/T dependence with no offset, "
        "because it comes directly from the electron's thermal spin polarization, which vanishes "
        "at infinite temperature. A real system's *additional* temperature-independent shift, if "
        "any, signals a different mechanism (e.g. Van Vleck paramagnetism) layered on top."
    )

st.subheader("Pseudocontact shift: the same geometric factor, again")
theta_deg = st.slider("Angle θ between the electron-nucleus vector and B0 (deg)", 0, 90, 20, 1)
delta_pc_ref = st.slider("Reference pseudocontact magnitude (ppm, at θ=0)", 5.0, 100.0, 40.0, 5.0)
shift_pc = pseudocontact_shift_ppm(delta_pc_ref, np.radians(theta_deg), T_kelvin=298.15)
st.metric("Pseudocontact shift at this orientation", f"{shift_pc:.2f} ppm")
st.caption("Try θ = 54.74° — the same magic angle that zeroed CSA and dipolar splittings zeros this too.")

st.subheader("PRE: a distance ruler, or a way to lose your signal")
c3, c4 = st.columns([1, 1.5])
with c3:
    rate_ref = st.slider("Reference PRE rate at 3 Å (Hz)", 10.0, 5000.0, 500.0, 10.0)
with c4:
    r_range = np.linspace(2.5, 15, 200)
    rates = pre_rate_hz(rate_ref, r_range, r_ref_angstrom=3.0)
    fig2, ax2 = plt.subplots(figsize=(6.5, 3.2))
    ax2.semilogy(r_range, rates, color="#c05621")
    ax2.set_xlabel("Distance from paramagnetic center (Å)"); ax2.set_ylabel("PRE rate (Hz, log scale)")
    st.pyplot(fig2); plt.close(fig2)

with predict_then_reveal("Given the 1/r^6 falloff, would you expect PRE to be a broad-brush effect over many angstroms, or a short-range 'switch'?"):
    st.write(
        "A short-range switch — 1/r⁶ is an extremely steep falloff, so nuclei within a couple of "
        "Å of a paramagnetic center are often broadened into invisibility, while nuclei even "
        "modestly farther away are barely affected. This steepness is exactly what makes PRE such "
        "a precise (if short-ranged) distance probe when it's usable at all."
    )

key_takeaway(
    "Paramagnetic effects are usually treated as a nuisance — trace transition-metal or "
    "rare-earth impurities can broaden or shift signals unpredictably — but the same three "
    "mechanisms (contact, pseudocontact, PRE) are deliberately exploited as structural probes "
    "when the paramagnetic center's location is itself of interest, precisely because they're so "
    "much larger and more distance/geometry-sensitive than any purely diamagnetic interaction."
)

next_lesson("Lesson 21 — NMR Crystallography & the DFT Bridge", "pages/21_NMR_Crystallography_DFT.py")
