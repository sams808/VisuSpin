import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

from common import page_header, lesson_header, key_takeaway, term, predict_then_reveal, next_lesson
from visuspin.physics.disorder import gaussian_shift_distribution, combine_shift_components

st.set_page_config(page_title="VisuSpin — Network Connectivity", page_icon="🧊", layout="wide")
page_header("Lesson 14: Network Connectivity & Qn Speciation")
lesson_header(
    "Lesson 14 of 24",
    "N4 tells us how many borons are 4-coordinate. It doesn't say how the network is connected.",
    "Two glasses could have identical N4 but completely different network structures — one a "
    "well-connected 3D network, the other full of isolated, dead-end fragments. How does NMR "
    "tell them apart?",
)

st.markdown(
    f"""
For network-forming tetrahedra (SiO₄, PO₄, BO₄⁻), the key structural
descriptor is {term("Qn", "a tetrahedral site with n bridging oxygens (shared with another network-former) and (4-n) non-bridging oxygens (terminated at a modifier cation)")}:
Q4 is fully polymerized (every corner shared, like pure silica glass), Q0 is
fully isolated (every corner terminates at a modifier). Each extra bridging
oxygen shifts the isotropic ³¹P or ²⁹Si shift by a remarkably consistent
amount — which is how NMR reads off the degree of network polymerization
directly from a 1D spectrum.
"""
)

st.subheader("Building a Qⁿ spectrum")
st.markdown("Illustrative, literature-typical ²⁹Si shift ranges (not a specific measured dataset) — adjust each Qⁿ population and watch the spectrum change.")

qn_shifts = {"Q0": -70.0, "Q1": -79.0, "Q2": -88.0, "Q3": -98.0, "Q4": -110.0}
cols = st.columns(5)
pops = {}
for col, (label, default) in zip(cols, [("Q0", 0), ("Q1", 5), ("Q2", 30), ("Q3", 45), ("Q4", 20)]):
    with col:
        pops[label] = st.slider(label, 0, 100, default, 1, key=f"pop_{label}")
linewidth = st.slider("Linewidth per site (ppm, disorder broadening)", 1.0, 8.0, 3.0, 0.5)

with predict_then_reveal("Q2 and Q3 are only ~10 ppm apart, each already several ppm wide. Will they always resolve as two clean peaks?"):
    total = max(sum(pops.values()), 1)
    n_base = 8000
    components = []
    for label, shift in qn_shifts.items():
        n = max(30, int(n_base * pops[label] / total))
        components.append(gaussian_shift_distribution(shift, linewidth, n_samples=n))
    combined = combine_shift_components(components, n_bins=600, freq_range=(-140, -50))
    fig, ax = plt.subplots(figsize=(8, 3.6))
    ax.plot(combined["freq_hz"], combined["intensity"], color="#5b46e5")
    for label, shift in qn_shifts.items():
        if pops[label] > 0:
            ax.axvline(shift, color="gray", linestyle=":", linewidth=0.8)
            ax.text(shift, 1.02, label, ha="center", fontsize=9)
    ax.set_xlabel("29Si shift (ppm)"); ax.set_ylabel("Intensity"); ax.invert_xaxis(); ax.set_ylim(0, 1.15)
    st.pyplot(fig); plt.close(fig)
    st.write(
        "Not always — push the linewidth up (more structural disorder) or bring two populations "
        "close together, and adjacent Qⁿ peaks blur into one shoulder-less hump. When that "
        "happens, a 1D shift spectrum alone can't tell you the individual populations."
    )

st.subheader("Shift tells you *how much*, not *what's next to what*")
st.markdown(
    """
Even a perfectly resolved Qⁿ spectrum only gives you **populations** — how
much Q2, how much Q3 — not **connectivity** — whether a given Q3 site's
bridging oxygens actually connect to another Q3, or to a Q2, or a Q4. Two
network topologies can have identical Qⁿ populations while being structurally
very different (a homogeneous network of all-Q3-connected-to-Q3, versus
clustered domains of Q4-rich and Q2-rich regions).

Telling these apart needs a technique that's sensitive to *which sites are
near which* — a homonuclear through-space correlation experiment. That's
exactly what **Lesson 16 (DQ-SQ)** does: it correlates a spin with its
close neighbors directly, turning "how much of each Qⁿ" into "which Qⁿ sites
actually neighbor which."
"""
)

key_takeaway(
    "Qⁿ speciation from isotropic shift gives the network's degree of polymerization (how much "
    "of each connectivity type is present) — genuinely powerful, but it's a population count, not "
    "a map of the network. Distinguishing a homogeneous network from a phase-separated one with "
    "the same Qⁿ populations needs a connectivity-sensitive experiment, not just a sharper 1D spectrum."
)

next_lesson("Lesson 15 — Quantification Pitfalls", "pages/15_Quantification_Pitfalls.py")
