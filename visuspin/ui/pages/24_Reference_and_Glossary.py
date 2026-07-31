import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st

from common import page_header, lesson_header
from visuspin.physics.nuclides import NUCLIDES, nu0_hz

st.set_page_config(page_title="VisuSpin — Reference & Glossary", page_icon="📚", layout="wide")
page_header("Lesson 24: Reference & Glossary")
lesson_header(
    "Lesson 24 of 24 — appendix",
    "A place to look things up without re-reading a whole lesson.",
    "Every term introduced across the previous 24 lessons, a Hz↔ppm converter, and typical "
    "parameter ranges to sanity-check your own data against.",
)

st.subheader("Hz ↔ ppm converter")
st.caption("Different lessons use whichever unit is most natural for that interaction (Hz for couplings/rates, ppm for shifts) — use this to convert between them for a specific nuclide and field.")
c1, c2, c3 = st.columns(3)
with c1:
    symbol = st.selectbox("Nuclide", list(NUCLIDES.keys()), index=list(NUCLIDES.keys()).index("1H"))
    nuc = NUCLIDES[symbol]
with c2:
    b0 = st.slider("B0 (T)", 1.0, 20.0, 9.4, 0.1)
    nu0 = nu0_hz(nuc, b0)
    st.caption(f"ν0 = {nu0/1e6:.3f} MHz")
with c3:
    mode = st.radio("Convert", ["Hz → ppm", "ppm → Hz"])
    if mode == "Hz → ppm":
        hz_val = st.number_input("Value (Hz)", value=100.0)
        st.metric("In ppm", f"{hz_val / (nu0 * 1e-6):.4f}")
    else:
        ppm_val = st.number_input("Value (ppm)", value=1.0)
        st.metric("In Hz", f"{ppm_val * nu0 * 1e-6:.2f}")

st.divider()
st.subheader("Typical parameter ranges (illustrative, not a specific measured dataset)")
st.markdown(
    """
| Nucleus | Typical context | Cq range | η range | Typical T1 |
|---|---|---|---|---|
| ¹H | organics, hydroxyls | — (spin 1/2) | — | ms – s |
| ¹³C | organics, carbonates | — (spin 1/2) | — | s – minutes (slow without dipolar relaxation partners) |
| ²⁹Si | silicate glasses/minerals | — (spin 1/2) | — | tens of seconds – minutes |
| ³¹P | phosphate glasses | — (spin 1/2) | — | seconds – minutes |
| ⁷Li | oxide/battery materials | 0.02–0.2 MHz (weak) | 0–1 | ms – s |
| ¹¹B | BO₃ (trigonal) | 2.4–2.7 MHz | 0.1–0.3 | ms – s |
| ¹¹B | BO₄ (tetrahedral) | 0–0.5 MHz | 0–1 | ms – s |
| ²³Na | oxide/silicate glasses | 0.5–3.5 MHz | 0–1 | ms – s |
| ²⁷Al | AlIV/V/VI in glasses | 0.5–10 MHz | 0–1 | ms – s |
| ¹⁷O | bridging/non-bridging oxygen | 2–10 MHz | 0–1 | ms – s (often needs isotopic enrichment) |

Quadrupolar nuclei with **large Cq** (e.g. ¹⁷O, some ²⁷Al environments) can be difficult to
excite/detect uniformly (Lesson 4, 7) — always cross-check a real value against a proper
reference before treating it as a firm constraint.
"""
)

st.divider()
st.subheader("Glossary")
GLOSSARY = {
    "Magnetization (M)": "The bulk, measurable sum of many nuclear magnetic moments (Lesson 0).",
    "Larmor frequency (ν0)": "A nucleus's natural precession rate around B0: ν0 = γB0/2π (Lesson 0).",
    "T1": "Longitudinal (spin-lattice) relaxation time — how fast equilibrium Mz returns (Lesson 0).",
    "T2": "Transverse relaxation time — the true, irreversible decay of observable signal (Lesson 0, 1).",
    "T2*": "The FID's observed decay time; always <= T2, since it also includes reversible field-inhomogeneity dephasing (Lesson 1).",
    "CSA": "Chemical shift anisotropy — orientation-dependent shielding (Lesson 2).",
    "Dipolar coupling": "Direct, through-space magnetic coupling between two nuclei (Lesson 3).",
    "Quadrupolar interaction": "The electric-quadrupole/EFG coupling unique to spin > 1/2 nuclei (Lesson 4).",
    "Magic angle": "54.7356° — the spinning axis angle that zeros first-order anisotropic (rank-2) broadening (Lesson 5).",
    "MQMAS": "2D experiment correlating a multiple-quantum coherence with the CT to remove residual 2nd-order quadrupolar broadening (Lesson 6).",
    "STMAS": "MQMAS alternative correlating a satellite transition with the CT instead (Lesson 17).",
    "CT-selective": "A pulse narrow enough to excite only the central transition, giving an (I+1/2) nutation-rate enhancement (Lesson 7).",
    "DFS": "Double frequency sweep — an adiabatic transfer boosting central-transition signal (Lesson 7).",
    "J-coupling": "Scalar, through-bond, isotropic coupling mediated by bonding electrons (Lesson 8).",
    "HMQC": "2D heteronuclear correlation via J- or D-mediated coherence transfer (Lesson 9).",
    "Czjzek model": "The distribution of (Cq, η) that follows from assuming a completely disordered (no preferred shape) electric field gradient (Lesson 12).",
    "Extended Czjzek model": "Czjzek disorder added on top of a fixed reference (Cq0, η0), for partial/intermediate disorder (Lesson 12).",
    "Qⁿ": "A network-forming tetrahedral site with n bridging oxygens (Lesson 14).",
    "N4": "The fraction of 4-coordinate boron in a borate glass (Lesson 13).",
    "DQ-SQ": "Homonuclear double-quantum/single-quantum correlation revealing spatial proximity (Lesson 16).",
    "PASS/TOSS": "Pulse sequences separating true isotropic shifts from MAS spinning sidebands (Lesson 18).",
    "PRE": "Paramagnetic relaxation enhancement — a 1/r^6 distance-dependent relaxation boost near an unpaired electron (Lesson 20).",
    "GIPAW-DFT": "A DFT method for computing EFG/shielding tensors directly from a periodic crystal structure (Lesson 21).",
}
for term_name, definition in GLOSSARY.items():
    st.markdown(f"**{term_name}** — {definition}")
