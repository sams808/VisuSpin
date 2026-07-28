import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
from common import render_logo, ACCENT

st.set_page_config(page_title="VisuSpin", page_icon="🧲", layout="wide")

render_logo(320)
st.caption("An interactive teaching toolkit for solid-state NMR spin physics")
st.divider()

st.markdown(
    """
VisuSpin is a set of interactive, physically-grounded simulations for
teaching solid-state (and general) NMR spin dynamics. Every plot on every
page is generated from the actual underlying spin physics — Bloch-equation
integration, exact spin-operator diagonalization, or direct numerical powder
simulation — computed live from the parameters you choose, not from
pre-rendered pictures.

**Use the page list in the left sidebar to jump between modules:**
"""
)

cols = st.columns(2)
with cols[0]:
    st.markdown(
        f"""
##### Relaxation & pulses
- **Relaxation Explorer** — T1/T2/T2\\* Bloch simulation, real nuclide table, finite pulses, CT-selective & DFS excitation, MAS sidebands
- **Nutation & CT-Selectivity** — quadrupolar nutation curves, (I+1/2) enhancement, DFS adiabatic sweeps

##### Lineshapes
- **Lineshapes** — CSA, dipolar Pake pattern, 1st/2nd-order quadrupolar CT, MAS sidebands
- **Powder Averaging (3D)** — see which crystallite orientations build which part of a powder pattern
- **MQMAS** — why correlating a multiple-quantum dimension removes 2nd-order quadrupolar broadening
""")
with cols[1]:
    st.markdown(
        f"""
##### Correlations & coupling
- **HMQC** — 2D heteronuclear correlation via J- or D-mediated coherence transfer
- **Multiplets & Decoupling** — J-multiplets collapsing under heteronuclear decoupling

##### Pulse sequences
- **Pulse Sequence Composer** — build sequences (Hahn echo, CPMG, REDOR, CP, spin-lock, DFS, ...) block by block, Scratch-style, with live timing diagrams and simulated signal traces
""")

st.divider()
st.markdown(
    """
**How to run this app.** If you installed VisuSpin with the provided
`scripts/install.ps1`, use the `run_visuspin.bat` shortcut it created. To run
manually: `streamlit run visuspin/ui/Home.py` from the project root.

**Scope note.** VisuSpin is a *teaching* tool. Simple interactions (Bloch
relaxation, CSA, dipolar couplings, static 2nd-order quadrupolar lineshapes)
are computed from first principles. A few modules (REDOR/CP transfer curves,
MQMAS shearing, MAS sidebands) intentionally use disclosed simplifications —
each page and each function's docstring says exactly which, and why — rather
than silently overclaiming research-grade accuracy. See `REFERENCES.md` in
the repository for the literature behind every simulation.
"""
)
