import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

from common import page_header, lesson_header, key_takeaway, term, predict_then_reveal, next_lesson
from visuspin.physics.sidebands import mas_sideband_spectrum

st.set_page_config(page_title="VisuSpin — Magic-Angle Spinning", page_icon="📈", layout="wide")
page_header("Lesson 5: Magic-Angle Spinning")
lesson_header(
    "Lesson 5 of 11",
    "CSA, dipolar coupling, first-order quadrupolar broadening — one fix for all three?",
    "The last three lessons all found the exact same magic number, 54.74°, where the "
    "broadening vanishes. Is that a coincidence, and can we actually exploit it?",
)

st.markdown(
    """
It's not a coincidence. CSA (Lesson 2) and dipolar splitting (Lesson 3) both
depend on orientation through the identical factor, **(3cos²θ − 1)**, where θ
is the angle between some fixed molecular direction and B0. That factor is
exactly zero at θ = 54.7356° — the **magic angle**.

Physically spinning the *entire sample* — not the molecules, the whole
rotor — around an axis tilted at the magic angle relative to B0 means every
crystallite's *effective* θ gets rapidly averaged through a full circle
around that angle. If the spinning is fast enough, the time-averaged
(3cos²θ − 1) factor each crystallite feels goes to zero, for every
crystallite, regardless of its own fixed orientation. This is
**{}**.
""".format(term("magic-angle spinning (MAS)", "MAS — spinning the sample at 54.74° to B0, fast, to average away first-order anisotropic broadening"))
)

st.subheader("How fast is 'fast enough'?")
st.markdown("Simulated directly by rotating the interaction tensor through an actual rotor period (not a textbook formula) — watch what a CSA-broadened powder pattern does as the spin rate increases.")
delta_aniso = st.slider("CSA anisotropy (Hz)", 500.0, 20000.0, 4000.0, 100.0)
eta_mas = st.slider("Asymmetry η", 0.0, 1.0, 0.3, 0.01)
nu_rot_khz = st.slider("MAS rate (kHz)", 0.5, 100.0, 5.0, 0.5)

with predict_then_reveal("At a slow spin rate (a few kHz), does the spectrum become one sharp line, or something messier?"):
    spec = mas_sideband_spectrum(delta_aniso, eta_mas, nu_rot_khz * 1000)
    fig, ax = plt.subplots(figsize=(7.5, 3.2))
    ax.plot(spec["freq_hz"], spec["intensity"], color="#c05621")
    ax.set_xlabel("Frequency (Hz)"); ax.set_ylabel("Intensity")
    ax.set_title(f"MAS at {nu_rot_khz:.1f} kHz")
    st.pyplot(fig); plt.close(fig)
    st.markdown(
        f"""
        A forest of extra sharp lines — **spinning sidebands** — spaced at exactly the spin rate
        ({nu_rot_khz*1000:.0f} Hz apart), flanking a true centreband at the isotropic shift. Each
        sideband is a genuine artifact of the spinning not being fast enough to fully outrun the
        interaction. Push the MAS rate slider up past the anisotropy value above, and watch them
        collapse into the sidebands disappearing and a single sharp centreband taking over.
        """
    )

key_takeaway(
    "MAS doesn't average away anisotropic broadening instantly — it averages it away over each "
    "full rotor period. Spin faster than the interaction's own frequency scale (in Hz) and you "
    "get one sharp line; spin slower, and you get a sideband pattern that still encodes the full "
    "static anisotropy, just resolved into a comb of sharp lines instead of one broad hump."
)

st.subheader("What MAS can't fix")
st.markdown(
    """
Recall Lesson 4's second-order quadrupolar broadening. It comes from a
fundamentally different kind of angular dependence — not a simple
(3cos²θ − 1) term, but a mix of *two* different angular functions. Spinning
at the magic angle zeros out one of them, but **not the other**: a residual,
genuinely anisotropic broadening survives on the central transition even
under arbitrarily fast MAS. This is precisely why ²³Na, ²⁷Al, and other
quadrupolar-nucleus spectra can still look stubbornly broad even on a
modern, fast-spinning probe — and it's the motivation for the next lesson,
which uses a completely different (two-dimensional) trick to finish the job.
"""
)

next_lesson("Lesson 6 — MQMAS", "pages/6_MQMAS.py")
