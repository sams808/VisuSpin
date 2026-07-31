import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

from common import page_header, lesson_header, key_takeaway, term, predict_then_reveal, next_lesson
from visuspin.physics.nuclides import NUCLIDES, nu0_hz
from visuspin.physics.quadrupole import ct_powder_pattern

st.set_page_config(page_title="VisuSpin — NMR Crystallography & DFT", page_icon="🧮", layout="wide")
page_header("Lesson 21: NMR Crystallography & the DFT Bridge")
lesson_header(
    "Lesson 21 of 24",
    "Every lineshape in this app needs Cq, η, and shift tensors as input. Where do real numbers come from?",
    "Before you've even run the NMR experiment — or when a material won't grow single crystals "
    "or give a clean diffraction pattern at all — how do you get a testable prediction for what "
    "the spectrum *should* look like?",
)

st.markdown(
    f"""
{term("GIPAW-DFT", "Gauge-Including Projector Augmented Wave density functional theory: computes the electric field gradient and chemical shielding tensors directly from a periodic crystal structure")}
calculates the electric field gradient tensor (→ Cq, η directly from its
principal values) and the shielding tensor (→ CSA parameters) for a given
atomic structure, no experiment required. This makes NMR a genuine
structure-validation tool: compute the expected spectrum for each candidate
structure, and see which one actually matches what you measured — exactly
the workflow behind **NMR crystallography**, and the approach used to solve
structures too disordered or fine-grained for diffraction to handle alone.
"""
)

st.subheader("Two candidate structures, one measured spectrum")
st.markdown("Imagine a DFT calculation on two candidate structures for the same material, differing only in a subtle local distortion.")
quad_nuclides = [s for s, n in NUCLIDES.items() if n.spin > 0.5 and n.is_half_integer_quadrupolar]
symbol = st.selectbox("Nuclide", quad_nuclides, index=quad_nuclides.index("27Al") if "27Al" in quad_nuclides else 0)
nuc = NUCLIDES[symbol]
b0 = st.slider("B0 (T)", 1.0, 20.0, 14.1, 0.1)
nu0 = nu0_hz(nuc, b0)

c1, c2 = st.columns(2)
with c1:
    st.markdown("**Candidate A (DFT)**")
    cq_a = st.slider("Cq (MHz)", 0.5, 10.0, 3.0, 0.1, key="cq_a")
    eta_a = st.slider("η", 0.0, 1.0, 0.2, 0.01, key="eta_a")
with c2:
    st.markdown("**Candidate B (DFT)**")
    cq_b = st.slider("Cq (MHz)", 0.5, 10.0, 3.4, 0.1, key="cq_b")
    eta_b = st.slider("η", 0.0, 1.0, 0.35, 0.01, key="eta_b")

with predict_then_reveal("Which is more likely to discriminate cleanly between two similar candidate structures: Cq/η, or the isotropic shift alone?"):
    pat_a = ct_powder_pattern(nuc.spin, cq_a * 1e6, eta_a, nu0)
    pat_b = ct_powder_pattern(nuc.spin, cq_b * 1e6, eta_b, nu0)
    fig, ax = plt.subplots(figsize=(7.5, 3.4))
    ax.plot(pat_a["freq_hz"], pat_a["intensity"], color="#5b46e5", label=f"Candidate A: Cq={cq_a} MHz, η={eta_a}")
    ax.plot(pat_b["freq_hz"], pat_b["intensity"], color="#c05621", label=f"Candidate B: Cq={cq_b} MHz, η={eta_b}")
    ax.set_xlabel("Frequency (Hz, from unperturbed CT)"); ax.set_ylabel("Intensity"); ax.legend(fontsize=8)
    st.pyplot(fig); plt.close(fig)
    st.write(
        "Cq/η, almost always. The electric field gradient is a very steep function of local bond "
        "angles and distances — a distortion too subtle to shift the isotropic chemical shift "
        "noticeably can still produce a clearly different quadrupolar lineshape. This is exactly "
        "why quadrupolar central-transition lineshapes (Lessons 4, 6, 12) are such a sensitive "
        "structural fingerprint, and why DFT-predicted Cq/η is often the deciding piece of "
        "evidence in NMR crystallography."
    )

st.subheader("The same bridge closes Lesson 12's loop, too")
st.markdown(
    """
Lesson 12's Czjzek model assumed a *purely statistical* distribution of
disorder — the honest, physically-motivated default when no atomistic
detail is available. When it is available (e.g. several structural
snapshots from an ab initio molecular-dynamics run, or a set of candidate
glass models), running the *same* GIPAW-DFT calculation on each snapshot
and collecting the resulting Cq/η values builds a distribution grounded in
actual atomistic structure, rather than an assumed statistical shape — the
natural next step once modeling resources allow it.
"""
)

key_takeaway(
    "DFT-computed NMR parameters turn 'structure' and 'spectrum' into a two-way bridge: predict a "
    "spectrum from a candidate structure to test it against experiment, or — when a family of "
    "structures is available (MD snapshots, candidate polymorphs) — build a genuinely structure-"
    "grounded disorder distribution instead of the statistical Czjzek default from Lesson 12."
)

next_lesson("Lesson 22 — Choosing Your Experiment", "pages/22_Choosing_Your_Experiment.py")
