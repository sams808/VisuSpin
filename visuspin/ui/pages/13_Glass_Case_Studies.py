import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

from common import page_header, lesson_header, key_takeaway, term, predict_then_reveal, next_lesson
from visuspin.physics.nuclides import NUCLIDES, nu0_hz
from visuspin.physics.disorder import glass_ct_shifts, combine_shift_components

st.set_page_config(page_title="VisuSpin — Glass Case Studies", page_icon="🧊", layout="wide")
page_header("Lesson 13: Real Spectra — Glass Case Studies")
lesson_header(
    "Lesson 13 of 24",
    "A real glass spectrum rarely shows one clean hump. What are we actually looking at?",
    "27Al and 11B MAS spectra of real glasses routinely show several overlapping features side "
    "by side. Are those separate compounds, or something else entirely?",
)

st.markdown(
    """
They're usually the **same nucleus in structurally distinct coordination
environments**, each broadened by its own Czjzek-type disorder (Lesson 12),
summed together. The two case studies below use **illustrative, literature-
typical parameter ranges** (not a specific measured dataset) to show how
that sum builds the spectra glass scientists actually see.
"""
)

st.subheader("Case study 1: ²⁷Al coordination in an aluminosilicate glass")
st.markdown(
    "Aluminum in a glass network can sit in 4-, 5-, or 6-fold oxygen coordination "
    f"({term('AlIV / AlV / AlVI', 'four-, five-, and six-coordinate aluminum, each a structurally distinct network site')}), "
    "each with its own typical shift and quadrupolar coupling."
)
b0_al = st.slider("B0 (T)", 1.0, 20.0, 14.1, 0.1, key="b0_al")
nu0_al = nu0_hz(NUCLIDES["27Al"], b0_al)

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown("**AlIV** (4-coord.)")
    pop_4 = st.slider("Population (%)", 0, 100, 70, 1, key="pop4")
    shift_4 = st.slider("δ_iso (ppm)", 40.0, 90.0, 62.0, 1.0, key="shift4")
    cq_4 = st.slider("Cq0 (MHz)", 1.0, 12.0, 6.0, 0.1, key="cq4")
with c2:
    st.markdown("**AlV** (5-coord.)")
    pop_5 = st.slider("Population (%)", 0, 100, 8, 1, key="pop5")
    shift_5 = st.slider("δ_iso (ppm)", 20.0, 50.0, 35.0, 1.0, key="shift5")
    cq_5 = st.slider("Cq0 (MHz)", 0.5, 8.0, 3.0, 0.1, key="cq5")
with c3:
    st.markdown("**AlVI** (6-coord.)")
    pop_6 = st.slider("Population (%)", 0, 100, 22, 1, key="pop6")
    shift_6 = st.slider("δ_iso (ppm)", -10.0, 20.0, 4.0, 1.0, key="shift6")
    cq_6 = st.slider("Cq0 (MHz)", 0.2, 5.0, 1.5, 0.1, key="cq6")

with predict_then_reveal("AlV is often the smallest population (a few percent). Will it show up as a clear peak, or hide as a subtle shoulder?"):
    total_pop = max(pop_4 + pop_5 + pop_6, 1)
    n_base = 6000
    components = []
    for shift_ppm, cq, pop in [(shift_4, cq_4, pop_4), (shift_5, cq_5, pop_5), (shift_6, cq_6, pop_6)]:
        n = max(50, int(n_base * pop / total_pop))
        shifts_hz, _ = glass_ct_shifts(1.5, cq * 1e6, 0.3, rho=0.25, nu0_hz=nu0_al, n_samples=n)
        shift_offset_hz = shift_ppm * 1e-6 * nu0_al
        components.append(shifts_hz + shift_offset_hz)
    combined = combine_shift_components(components, n_bins=600)
    fig, ax = plt.subplots(figsize=(8, 3.6))
    ax.plot(combined["freq_hz"] / (1e-6 * nu0_al), combined["intensity"], color="#5b46e5")
    ax.set_xlabel("Shift (ppm)"); ax.set_ylabel("Intensity"); ax.invert_xaxis()
    ax.set_title(f"Simulated 27Al MAS spectrum: {pop_4}% AlIV / {pop_5}% AlV / {pop_6}% AlVI")
    st.pyplot(fig); plt.close(fig)
    csv_data = "shift_ppm,intensity\n" + "\n".join(
        f"{s:.4f},{i:.6f}" for s, i in zip(combined["freq_hz"] / (1e-6 * nu0_al), combined["intensity"])
    )
    st.download_button("Download this spectrum as CSV", csv_data, file_name="al27_glass_spectrum.csv", mime="text/csv")
    st.write(
        "Depends entirely on the balance of population **and** linewidth — a small population "
        "with a narrow line can still be clearly visible, while a similarly small population with "
        "a broad, heavily quadrupolar-broadened line can vanish into the baseline between its "
        "neighbors. Try dragging AlV's population toward zero and back, or widening its Cq0."
    )

st.subheader("Case study 2: ¹¹B and the borate 'anomaly' — BO₃ ↔ BO₄")
st.markdown(
    """
Boron in oxide glasses converts between 3-coordinate **BO₃** (trigonal, planar)
and 4-coordinate **BO₄** (tetrahedral) as network modifiers are added — the
fraction in 4-coordination is universally called **N4** in glass science.
The two environments look dramatically different in ¹¹B NMR: BO₃'s planar,
asymmetric geometry gives it a *large* Cq (strongly quadrupolar-broadened),
while BO₄'s near-tetrahedral symmetry gives it a *small* Cq (narrow line).
"""
)
b0_b = st.slider("B0 (T)", 1.0, 20.0, 9.4, 0.1, key="b0_b")
nu0_b = nu0_hz(NUCLIDES["11B"], b0_b)
c4, c5 = st.columns(2)
with c4:
    n4 = st.slider("N4 (fraction 4-coordinate, %)", 0, 100, 35, 1)
with c5:
    st.caption(f"BO3 population: {100-n4}% · BO4 population: {n4}%")

with predict_then_reveal("BO4 has a much smaller Cq than BO3. At equal population, would BO4's peak look narrow-and-tall, or broad-and-short, compared to BO3?"):
    n_base_b = 6000
    n_bo3 = max(50, int(n_base_b * (100 - n4) / 100))
    n_bo4 = max(50, int(n_base_b * n4 / 100))
    shifts_bo3, _ = glass_ct_shifts(1.5, 2.6e6, 0.15, rho=0.2, nu0_hz=nu0_b, n_samples=n_bo3)
    shifts_bo4, _ = glass_ct_shifts(1.5, 0.3e6, 0.2, rho=0.3, nu0_hz=nu0_b, n_samples=n_bo4)
    shifts_bo3 = shifts_bo3 + 15.0 * 1e-6 * nu0_b
    shifts_bo4 = shifts_bo4 + 0.5 * 1e-6 * nu0_b
    combined_b = combine_shift_components([shifts_bo3, shifts_bo4], n_bins=600)
    fig2, ax2 = plt.subplots(figsize=(8, 3.6))
    ax2.plot(combined_b["freq_hz"] / (1e-6 * nu0_b), combined_b["intensity"], color="#c05621")
    ax2.set_xlabel("Shift (ppm)"); ax2.set_ylabel("Intensity"); ax2.invert_xaxis()
    ax2.set_title(f"Simulated 11B MAS spectrum: N4 = {n4}%")
    st.pyplot(fig2); plt.close(fig2)
    st.write(
        "Narrow-and-tall: the same number of spins packed into a much smaller frequency range "
        "produces a taller peak. This is exactly why **N4 can't be read directly off peak "
        "heights** — a proper population estimate needs to integrate the *area* of each "
        "component, not compare their heights (foreshadowing the fitting workshop, Lesson 23)."
    )

key_takeaway(
    "Every 'extra hump' in a real glass spectrum is a population of structurally distinct sites, "
    "each with its own Czjzek-broadened lineshape. Visually estimating site fractions from peak "
    "height is unreliable whenever linewidths differ between sites — which, in a glass, they "
    "almost always do."
)

next_lesson("Lesson 14 — Network Connectivity & Qn Speciation", "pages/14_Network_Connectivity.py")
