import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st

from common import page_header, lesson_header, key_takeaway

st.set_page_config(page_title="VisuSpin — Choosing Your Experiment", page_icon="🧭", layout="wide")
page_header("Lesson 22: Choosing Your Experiment")
lesson_header(
    "Lesson 22 of 24",
    "You have a material and a question. Which of the last 20 lessons do you actually reach for?",
    "Every technique in this app solves a specific problem. Organized by *technique name*, that's "
    "hard to search. Organized by *question*, it's a lookup.",
)

st.markdown("Pick the question closest to what you actually want to know:")

GUIDE = {
    "How many distinct sites are there, and in what proportion?":
        ("Real Spectra / Network Connectivity", "pages/13_Glass_Case_Studies.py",
         "Build the spectrum as a sum of known site types, then see Lesson 23 to fit real data the same way."),
    "Is a peak's height/area actually proportional to that site's population?":
        ("Quantification Pitfalls", "pages/15_Quantification_Pitfalls.py",
         "CP bias, T1 saturation, and sideband redistribution can all make height ≠ population."),
    "Is this material crystalline or does it show a distribution of local environments?":
        ("Disorder & the Czjzek Model", "pages/12_Disorder_and_Czjzek_Model.py",
         "Turns 'the line looks weirdly broad and asymmetric' into an actual disorder parameter."),
    "Are two site types actually bonded/adjacent, or just both present in the sample?":
        ("DQ-SQ Homonuclear Correlation", "pages/16_DQ_SQ_Correlation.py",
         "For the same nucleus. Use HMQC instead if the two sites are different nuclei."),
    "Are two *different* nuclei close together or bonded?":
        ("HMQC", "pages/9_HMQC.py",
         "J-coupling for bonded pairs, dipolar (D) coupling for through-space proximity."),
    "My quadrupolar nucleus has poor resolution even under fast MAS — now what?":
        ("MQMAS", "pages/6_MQMAS.py",
         "Or STMAS (Lesson 17) if sensitivity matters more than tolerance for a slightly-off magic angle."),
    "Something in my spectrum changes with temperature — what does that tell me?":
        ("Variable-Temperature NMR", "pages/19_Variable_Temperature_NMR.py",
         "Coalescence behavior can give you an activation energy for whatever's exchanging."),
    "I have overlapping sidebands from several sites and can't tell which belongs to which":
        ("PASS/TOSS", "pages/18_PASS_TOSS.py",
         "Separates true isotropic peaks from the sideband forest without needing to spin faster."),
    "A trace paramagnetic impurity is affecting my spectrum (or I want to use it as a probe)":
        ("Paramagnetic NMR", "pages/20_Paramagnetic_NMR.py",
         "Contact/pseudocontact shifts and PRE — usually a nuisance, sometimes a deliberate tool."),
    "I want to test whether a candidate structure actually matches my data":
        ("NMR Crystallography & DFT", "pages/21_NMR_Crystallography_DFT.py",
         "Compute the expected spectrum from a candidate structure and compare."),
    "I need to design or understand a specific pulse sequence":
        ("Pulse Sequence Composer", "pages/10_Pulse_Sequence_Composer.py",
         "Every named sequence is a composition of the same handful of primitives."),
    "I'm not sure yet — I just need the fundamentals":
        ("NMR Fundamentals", "pages/0_NMR_Fundamentals.py",
         "Start at the beginning: magnetization, precession, pulses, relaxation, the FID and FT."),
}

choice = st.selectbox("What do you want to find out?", list(GUIDE.keys()))
title, path, note = GUIDE[choice]
st.markdown(f"### → {title}")
st.caption(note)
try:
    st.page_link(path, label=f"Open: {title}", icon="➡️")
except Exception:
    st.caption(f"Open: {path}")

key_takeaway(
    "There's no single 'best' NMR technique — only the technique that answers the specific "
    "question in front of you. Naming your question precisely is usually most of the work; the "
    "technique choice tends to follow directly once you have."
)
