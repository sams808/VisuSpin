import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
from common import render_logo, lesson_link

st.set_page_config(page_title="VisuSpin", page_icon="🧲", layout="wide")

render_logo(320)
st.caption("An interactive teaching toolkit for solid-state NMR spin physics")
st.divider()

st.markdown(
    """
VisuSpin is a guided path through solid-state NMR spin physics, built for
students with **no prior NMR background**. Every plot on every page is
computed live from the actual underlying physics — Bloch-equation
integration, exact spin-operator diagonalization, or direct numerical powder
simulation — from the parameters you choose, not from pre-rendered pictures.

Each lesson opens with a concrete question, builds the idea up one step at a
time, and asks you to predict what a plot will show *before* revealing it —
then hands you the full explorer to play with once the concept has landed.
Go in order the first time through; after that, jump to any lesson from the
sidebar as a reference.
"""
)
st.divider()

st.subheader("Part 1: Foundations")

lesson_link("0", "NMR Fundamentals", "Magnetization, precession, RF pulses, T1/T2, the FID, and the Fourier transform.", "pages/0_NMR_Fundamentals.py")
lesson_link("1", "Relaxation Explorer", "Why the same sample decays two different ways — T2 vs. T2*, and how an echo tells them apart.", "pages/1_Relaxation_Explorer.py")
lesson_link("2", "Chemical Shift Anisotropy", "Why a solid powder turns one sharp solution-NMR peak into a broad hump.", "pages/2_Chemical_Shift_Anisotropy.py")
lesson_link("3", "Dipolar Coupling", "Two nearby nuclei as tiny bar magnets — the Pake doublet, and a distance ruler that scales as 1/r³.", "pages/3_Dipolar_Coupling.py")
lesson_link("4", "Quadrupolar Interactions", "Why 23Na, 27Al, 11B and friends look so different from 1H — and why higher field narrows their lines.", "pages/4_Quadrupolar_Interactions.py")
lesson_link("5", "Magic-Angle Spinning", "One trick, spinning at 54.74°, that erases CSA, dipolar, and first-order quadrupolar broadening at once.", "pages/5_Magic_Angle_Spinning.py")
lesson_link("6", "MQMAS", "The 2D trick that finishes the job MAS alone can't: removing residual quadrupolar broadening.", "pages/6_MQMAS.py")
lesson_link("7", "Nutation & CT-Selectivity", "Exciting quadrupolar nuclei efficiently, and boosting signal further with DFS.", "pages/7_Nutation_CT_Selectivity.py")
lesson_link("8", "J-Coupling & Decoupling", "The one coupling that doesn't care about orientation — and how to switch it off on purpose.", "pages/8_J_Coupling_Decoupling.py")
lesson_link("9", "HMQC", "Turning 'these nuclei are coupled' into a 2D map of exactly which atoms are linked to which.", "pages/9_HMQC.py")
lesson_link("10", "Pulse Sequence Composer", "Capstone: build Hahn echo, CPMG, REDOR, CP and more from the same handful of primitives.", "pages/10_Pulse_Sequence_Composer.py")

st.divider()
st.subheader("Part 2: Materials Science Applications")
st.caption("Real disordered materials, quantification, and the techniques that go beyond the Part 1 foundations.")

lesson_link("12", "Disorder & the Czjzek Model", "Why glasses give distributions of Cq/η instead of one crystalline value, and what that does to the lineshape.", "pages/12_Disorder_and_Czjzek_Model.py")
lesson_link("13", "Real Spectra: Glass Case Studies", "Illustrative 27Al (AlIV/V/VI) and 11B (BO3/BO4, the 'N4' anomaly) worked examples.", "pages/13_Glass_Case_Studies.py")
lesson_link("14", "Network Connectivity & Qn Speciation", "Why Qn shift trends give populations but not connectivity.", "pages/14_Network_Connectivity.py")
lesson_link("15", "Quantification Pitfalls", "CP bias, T1 saturation, and spinning-sideband redistribution — three reasons peak height ≠ population.", "pages/15_Quantification_Pitfalls.py")
lesson_link("16", "DQ-SQ Homonuclear Correlation", "Which sites actually neighbor which — answers Lesson 14's cliffhanger.", "pages/16_DQ_SQ_Correlation.py")
lesson_link("17", "STMAS vs. MQMAS", "A more sensitive alternative to MQMAS, and why it demands a nearly perfect magic angle.", "pages/17_STMAS.py")
lesson_link("18", "PASS/TOSS Sideband Separation", "Untangling overlapping sidebands from several sites without spinning faster.", "pages/18_PASS_TOSS.py")
lesson_link("19", "Variable-Temperature NMR", "Motional narrowing, coalescence, and Arrhenius-activated dynamics/phase transitions.", "pages/19_Variable_Temperature_NMR.py")
lesson_link("20", "Paramagnetic NMR", "Contact/pseudocontact shifts and PRE — a nuisance from trace dopants, or a deliberate structural probe.", "pages/20_Paramagnetic_NMR.py")
lesson_link("21", "NMR Crystallography & DFT", "Bridging DFT-computed Cq/η/CSA tensors to the spectra this app simulates.", "pages/21_NMR_Crystallography_DFT.py")
lesson_link("22", "Choosing Your Experiment", "A question-driven guide to the whole app — pick your goal, get the right lesson.", "pages/22_Choosing_Your_Experiment.py")
lesson_link("23", "Spectral Fitting Workshop", "Fit a mystery spectrum by hand and see why a good R² alone isn't the whole story.", "pages/23_Spectral_Fitting_Workshop.py")
lesson_link("24", "Reference & Glossary", "Hz↔ppm converter, typical Cq/η/T1 ranges, and every term defined across the app.", "pages/24_Reference_and_Glossary.py")

st.divider()
st.subheader("Companion tool")
lesson_link("Live", "Live Vector Explorer", "A real-time, 60fps animated companion to Lesson 1 — same physics, no clicking to recompute. "
             "Also runs standalone with no Python at all: double-click run_visuspin_live.bat.", "pages/11_Live_Vector_Explorer.py")

st.divider()
st.markdown(
    """
**How to run this app.** If you installed VisuSpin with the provided
`scripts/install.ps1`, use the `run_visuspin.bat` shortcut it created (or
`run_visuspin_live.bat` to jump straight to the standalone Live Vector
Explorer, no Streamlit required). To run manually:
`streamlit run visuspin/ui/Home.py` from the project root.

**Scope note.** VisuSpin is a *teaching* tool. Simple interactions (Bloch
relaxation, CSA, dipolar couplings, static 2nd-order quadrupolar lineshapes)
are computed from first principles. A few modules (REDOR/CP transfer curves,
MQMAS shearing, MAS sidebands) intentionally use disclosed simplifications —
each page and each function's docstring says exactly which, and why — rather
than silently overclaiming research-grade accuracy. See `REFERENCES.md` in
the repository for the literature behind every simulation.
"""
)
