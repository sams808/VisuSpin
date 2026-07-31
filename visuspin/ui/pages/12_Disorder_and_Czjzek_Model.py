import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

from common import page_header, lesson_header, key_takeaway, term, predict_then_reveal, next_lesson
from visuspin.physics.nuclides import NUCLIDES, nu0_hz
from visuspin.physics.disorder import (
    czjzek_cq_eta_samples, extended_czjzek_cq_eta_samples, glass_ct_powder_pattern,
)
from visuspin.physics.quadrupole import ct_powder_pattern

st.set_page_config(page_title="VisuSpin — Disorder & the Czjzek Model", page_icon="🧊", layout="wide")
page_header("Lesson 12: Disorder & the Czjzek Model")
lesson_header(
    "Lesson 12 of 24 — Part 2: Materials Science",
    "A crystal gives one sharp line. The same atoms, melted into a glass, give a broad hump. Why?",
    "Lessons 4–6 treated Cq and η as fixed numbers. In a real glass, no two sites are quite "
    "identical. What actually happens to the physics once every site has a slightly different "
    "local environment?",
)

st.markdown(
    """
In a crystal, every site of a given type sees an essentially identical
local structure, so Cq and η take one sharp value. In a glass, the network
is frozen in a huge variety of slightly different local geometries — bond
angles and lengths that never quite repeat. The **Czjzek model** describes
the natural consequence of *total* structural disorder: if a site's electric
field gradient has no preferred orientation or shape at all, its 5
independent tensor components are just independent Gaussian random
numbers. Diagonalize a random tensor like that, and out comes a random Cq
and η — do it for thousands of "sites," and you get the whole distribution.
"""
)

st.subheader("1. What does 'no preferred shape' actually produce?")
sigma = st.slider("Disorder width σ (arbitrary Cq units)", 0.5, 5.0, 2.0, 0.1)
with predict_then_reveal("Would you expect the resulting η values to be spread evenly across [0,1], or clustered somewhere?"):
    out = czjzek_cq_eta_samples(sigma=sigma, n_samples=6000)
    fig0, (axa, axb) = plt.subplots(1, 2, figsize=(10, 3.6))
    axa.scatter(out["Cq"], out["eta"], s=3, alpha=0.25, color="#5b46e5")
    axa.set_xlabel("Cq"); axa.set_ylabel("η"); axa.set_title("Czjzek (Cq, η) samples")
    axb.hist(out["eta"], bins=30, color="#f0a83c")
    axb.set_xlabel("η"); axb.set_ylabel("count"); axb.set_title("η distribution")
    st.pyplot(fig0); plt.close(fig0)
    st.markdown(
        "Strongly clustered toward **high η** (close to 1) — axially symmetric environments "
        "(η≈0) are genuinely rare for a randomly-shaped EFG. This isn't an empirical fitting "
        "curve; it falls straight out of diagonalizing a tensor with no preferred shape."
    )

st.subheader("2. Dialing disorder: from crystal to glass")
st.markdown(
    "The **extended Czjzek model** adds a random Czjzek-type disorder tensor on top of a fixed "
    f"reference ({term('Cq0, η0', 'the mean, crystalline-like local environment')}), scaled by a "
    "disorder fraction ρ. ρ=0 is a perfect crystal; large ρ is a fully disordered glass."
)
c1, c2 = st.columns([1, 1.5])
with c1:
    quad_nuclides = [s for s, n in NUCLIDES.items() if n.spin > 0.5 and n.is_half_integer_quadrupolar]
    symbol = st.selectbox("Nuclide", quad_nuclides, index=quad_nuclides.index("27Al") if "27Al" in quad_nuclides else 0)
    nuc = NUCLIDES[symbol]
    b0 = st.slider("B0 (T)", 1.0, 20.0, 9.4, 0.1)
    Cq0 = st.slider("Reference Cq0 (MHz)", 0.5, 15.0, 4.0, 0.1)
    eta0 = st.slider("Reference η0", 0.0, 1.0, 0.2, 0.01)
    rho = st.slider("Disorder fraction ρ", 0.0, 1.5, 0.3, 0.01)
    nu0 = nu0_hz(nuc, b0)
with c2:
    ext = extended_czjzek_cq_eta_samples(Cq0, eta0, rho, n_samples=4000)
    fig1, ax1 = plt.subplots(figsize=(6.5, 4.2))
    ax1.scatter(ext["Cq"], ext["eta"], s=4, alpha=0.3, color="#c05621")
    ax1.axvline(Cq0, color="gray", linestyle="--", linewidth=1)
    ax1.axhline(eta0, color="gray", linestyle="--", linewidth=1)
    ax1.set_xlabel("Cq (MHz)"); ax1.set_ylabel("η")
    ax1.set_title(f"ρ={rho:.2f}: {'nearly a single point (crystal-like)' if rho < 0.05 else 'spreading around (Cq0, η0)'}")
    st.pyplot(fig1); plt.close(fig1)

st.subheader("3. What this does to the actual spectrum")
shift_sigma = st.slider("Amorphous isotropic-shift spread (Hz)", 0.0, 3000.0, 0.0, 50.0,
                          help="Site-to-site chemical-shift variation, layered on top of the quadrupolar disorder above.")
with predict_then_reveal("Compare a near-crystalline pattern (small ρ) to a glassy one (larger ρ). Same Cq0/η0 — does the lineshape just get wider, or change shape (symmetric hump vs. sharp-edged powder pattern)?"):
    crystal = ct_powder_pattern(nuc.spin, Cq0 * 1e6, eta0, nu0)
    glass = glass_ct_powder_pattern(nuc.spin, Cq0 * 1e6, eta0, rho, nu0, shift_sigma_hz=shift_sigma)
    fig2, ax2 = plt.subplots(figsize=(8, 3.4))
    ax2.plot(crystal["freq_hz"], crystal["intensity"], color="#5b46e5", label="crystal (ρ=0)")
    ax2.plot(glass["freq_hz"], glass["intensity"], color="#c05621", label=f"glass (ρ={rho:.2f})")
    ax2.set_xlabel("Frequency (Hz, from unperturbed CT)"); ax2.set_ylabel("Intensity"); ax2.legend()
    st.pyplot(fig2); plt.close(fig2)
    st.write(
        "Both wider **and** reshaped: the crystal's sharp-edged powder pattern (Lesson 4) washes "
        "out into a smoother, more symmetric-looking hump — the classic signature glass NMR "
        "spectroscopists use to spot a disordered site at a glance, well before doing any fitting."
    )

key_takeaway(
    "A glass's broad NMR line isn't just 'a crystalline line with extra broadening' — it's the "
    "sum of thousands of slightly different crystalline-like lines, each shifted by its own "
    "site's Cq, η, and isotropic shift. The Czjzek/extended-Czjzek model gives that sum a "
    "physically-motivated shape instead of an arbitrary fitting function."
)

next_lesson("Lesson 13 — Real Spectra: Glass Case Studies", "pages/13_Glass_Case_Studies.py")
