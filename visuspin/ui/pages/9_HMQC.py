import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

from common import page_header, lesson_header, key_takeaway, term, predict_then_reveal, next_lesson
from visuspin.physics.hmqc import mq_transfer_efficiency, optimal_tau_ms, hmqc_spectrum

st.set_page_config(page_title="VisuSpin — HMQC", page_icon="🔀", layout="wide")
page_header("Lesson 9: HMQC")
lesson_header(
    "Lesson 9 of 11",
    "How do you prove which atoms are bonded, or which are just close together?",
    "Lessons 3 and 8 showed two completely different couplings can link two different "
    "nuclei: through-space (dipolar) or through-bond (J). Can either be turned into a map "
    "of exactly which atoms are linked to which?",
)

st.markdown(
    f"""
**HMQC** (Heteronuclear Multiple-Quantum Correlation) does exactly that. Two
different nuclei — say ¹H (I) and ¹³C (S) — briefly form a shared,
two-spin coherence *only if they're coupled*. Let that coherence evolve for
a moment, then convert it back, and you get a 2D spectrum with a peak at
(shift_S, shift_I) **only** for pairs that are actually coupled. Uncoupled
pairs — everything else in the molecule — simply don't show up at all.
"""
)

st.subheader("1. Why a delay τ, and how long should it be?")
st.markdown(
    f"""
The shared coherence doesn't exist instantly — it has to build up, and the
rate it builds at is set by the coupling strength. Wait the delay τ, and the
transfer efficiency follows {term("sin(πcτ)", "the standard INEPT-style coherence-transfer function, c = the coupling constant in Hz")}.
"""
)
coupling_type = st.radio("Coherence-transfer mechanism", ["J (through-bond, scalar)", "D (through-space, dipolar/recoupled)"])
if coupling_type.startswith("J"):
    coupling_hz = st.slider("J coupling (Hz)", 1.0, 300.0, 140.0, 1.0)
else:
    coupling_hz = st.slider("Recoupled D (Hz)", 50.0, 8000.0, 2000.0, 50.0)
tau_opt = optimal_tau_ms(coupling_hz)

with predict_then_reveal("At τ=0, is there any correlation signal at all? And does making τ longer and longer keep helping forever?"):
    tau_axis = np.linspace(0, 2 * tau_opt, 300)
    eff_axis = np.array([mq_transfer_efficiency(coupling_hz, t) for t in tau_axis])
    fig, ax = plt.subplots(figsize=(7, 3))
    ax.plot(tau_axis, eff_axis, color="#5b46e5")
    ax.axvline(tau_opt, color="gray", linestyle="--", linewidth=1, label=f"optimum τ={tau_opt:.4f} ms")
    ax.set_xlabel("τ (ms)"); ax.set_ylabel("Transfer efficiency"); ax.legend()
    st.pyplot(fig); plt.close(fig)
    st.write(
        f"Zero signal at τ=0 (no time for any coherence to form), rising to a maximum at "
        f"τ = 1/(2×coupling) = {tau_opt:.4f} ms, then falling back down — push τ too far and "
        f"you actually lose signal again. Every real HMQC experiment is tuned around this optimum."
    )

tau_ms = st.slider("Fixed delay τ (ms) for the 2D map below", 0.0, max(2 * tau_opt, 0.01), float(tau_opt),
                     max(tau_opt / 100, 1e-4), format="%.4f")
with predict_then_reveal("D-coupling is typically much stronger than long-range J-coupling. Does that mean the optimal τ is shorter or longer for D?"):
    st.write(
        f"Shorter — optimal τ = 1/(2×coupling) shrinks as the coupling grows. A strong recoupled "
        f"dipolar coupling (~kHz) needs a delay of tens of microseconds; a weak long-range "
        f"J-coupling (~Hz-tens of Hz) needs milliseconds. Whichever mechanism you use sets the "
        f"whole experiment's timescale."
    )

st.subheader("2. The 2D correlation map")
st.markdown("Which nuclei show up in the map is entirely determined by which pairs are actually coupled — add or remove sites below.")
default_sites = [
    {"shift_i_hz": 500.0, "shift_s_hz": -1200.0, "amplitude": 1.0},
    {"shift_i_hz": -800.0, "shift_s_hz": 600.0, "amplitude": 0.7},
]
sites_df = st.data_editor(default_sites, num_rows="dynamic", key="hmqc_sites")
sites = [s for s in sites_df if all(k in s and s[k] is not None for k in ("shift_i_hz", "shift_s_hz"))]
for s in sites:
    s.setdefault("amplitude", 1.0)
if sites:
    spec = hmqc_spectrum(sites, coupling_hz, tau_ms, linewidth_hz=60.0, n_points=250)
    fig2, ax2 = plt.subplots(figsize=(6.5, 5.5))
    cf = ax2.contourf(spec["f2_hz"], spec["f1_hz"], spec["intensity"], levels=20, cmap="viridis")
    ax2.set_xlabel("F2 — I shift (Hz, direct)"); ax2.set_ylabel("F1 — S shift (Hz, indirect)")
    fig2.colorbar(cf, ax=ax2, label="Intensity")
    st.pyplot(fig2); plt.close(fig2)
else:
    st.info("Add at least one correlated site in the table above.")

key_takeaway(
    "HMQC turns 'these two nuclei are coupled' into 'these two nuclei show up at the same "
    "point in a 2D spectrum' — using J-coupling maps out bonding connectivity, using D-coupling "
    "maps out spatial proximity, and both rely on the exact same sin(πcτ) build-up mechanism, "
    "just tuned to a very different timescale."
)

next_lesson("Lesson 10 — Pulse Sequence Composer", "pages/10_Pulse_Sequence_Composer.py")
