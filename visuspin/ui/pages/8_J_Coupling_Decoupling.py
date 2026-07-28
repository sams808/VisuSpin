import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import matplotlib.pyplot as plt
import streamlit as st

from common import page_header, lesson_header, key_takeaway, term, predict_then_reveal, next_lesson
from visuspin.physics.decoupling import multiplet_spectrum, decoupled_spectrum

st.set_page_config(page_title="VisuSpin — J-Coupling & Decoupling", page_icon="🔊", layout="wide")
page_header("Lesson 8: J-Coupling & Decoupling")
lesson_header(
    "Lesson 8 of 11",
    "Even in a perfectly uniform liquid, peaks split into doublets and triplets. Why?",
    "Every broadening mechanism so far (CSA, dipolar, quadrupolar) depends on orientation, and "
    "vanishes with fast enough tumbling or spinning. But solution-NMR multiplets don't go away "
    "no matter how fast the molecule tumbles. Something else is going on.",
)

st.markdown(
    f"""
{term("J-coupling", "scalar, through-bond coupling mediated by shared bonding electrons")}
is fundamentally different from everything in the last four lessons: it's
transmitted through chemical bonds via the shared electrons, not directly
through space — and critically, it does **not** depend on orientation at
all. Fast tumbling in solution can't average it away because there's nothing
anisotropic to average in the first place. It's every bit as present, and
just as informative, in a solid.
"""
)

st.subheader("1. Multiplets: splitting from neighboring spins")
c1, c2 = st.columns([1, 1.6])
with c1:
    J = st.slider("J coupling (Hz)", 5.0, 300.0, 140.0, 1.0)
    n_coupled = st.slider("Number of equivalent coupled I=1/2 neighbors", 0, 6, 1, 1)
    linewidth = st.slider("Natural linewidth (Hz)", 0.5, 50.0, 8.0, 0.5)
with c2:
    with predict_then_reveal("With 2 equivalent coupled neighbors, how many lines appear, and in what intensity ratio?"):
        coupled = multiplet_spectrum(J, n_coupled, linewidth_hz=linewidth) if n_coupled > 0 else None
        fig, ax = plt.subplots(figsize=(7, 3.2))
        if coupled is not None:
            ax.plot(coupled["freq_hz"], coupled["intensity"], color="#c05621")
        ax.set_xlabel("Frequency (Hz)"); ax.set_ylabel("Intensity")
        ax.set_title(f"{n_coupled} coupled spin(s), J={J:.0f} Hz")
        st.pyplot(fig); plt.close(fig)
        st.write(
            "n equivalent spin-1/2 neighbors split a peak into n+1 lines with binomial "
            "(Pascal's-triangle) intensities: 1:1 for one neighbor, 1:2:1 for two, 1:3:3:1 for "
            "three. Try the slider above — the count and the ratio both follow this exactly."
        )

st.subheader("2. Decoupling: removing it on purpose")
st.markdown(
    """
J-multiplets are informative, but they also make spectra harder to read —
especially when a rare nucleus like ¹³C is coupled to several nearby ¹H's at
once. **Heteronuclear decoupling** continuously irradiates the *other*
nucleus (e.g. ¹H) throughout acquisition, scrambling its spin state so fast
that the coupled nucleus only ever sees an *average* — collapsing the whole
multiplet back down to one line.
"""
)
residual = st.slider("Residual coupling / imperfect decoupling (Hz)", 0.0, 150.0, 0.0, 1.0,
                       help="0 = ideal decoupling. Larger values model finite RF field / off-resonance / decoupling-sequence mismatch as an added broadening.")
decoupled = decoupled_spectrum(linewidth_hz=linewidth, residual_coupling_hz=residual)
fig2, ax2 = plt.subplots(figsize=(7, 3.2))
ax2.plot(decoupled["freq_hz"], decoupled["intensity"], color="#5b46e5")
ax2.set_xlabel("Frequency (Hz)"); ax2.set_ylabel("Intensity")
ax2.set_title(f"Decoupled: effective linewidth {decoupled['effective_linewidth_hz']:.1f} Hz")
st.pyplot(fig2); plt.close(fig2)

key_takeaway(
    "J-coupling is the odd one out in these lessons: it's isotropic, so MAS and fast tumbling "
    "can't touch it — but it CAN be removed by actively scrambling the coupling partner's spin "
    "state (decoupling), a fundamentally different tool from anything used against CSA, dipolar, "
    "or quadrupolar broadening."
)
st.caption(
    "Imperfect decoupling is modelled here as broadening added in quadrature to the natural "
    "linewidth — a standard simplified picture, not a Floquet simulation of a specific sequence "
    "like TPPM/SPINAL-64 (see decoupling.py docstring)."
)

next_lesson("Lesson 9 — HMQC", "pages/9_HMQC.py")
