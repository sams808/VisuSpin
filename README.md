<p align="center">
  <img src="assets/logo.svg" alt="VisuSpin" width="360">
</p>

<p align="center"><em>An interactive teaching toolkit for solid-state NMR spin physics.</em></p>

---

VisuSpin is a guided, 25-lesson path through solid-state NMR spin physics,
built for students with **no prior NMR background** and extending into
real materials-science applications (disordered/glassy materials,
quantification, dynamics). Every plot is computed live from the actual
underlying physics — exact per-isochromat Bloch integration, first-
principles spin-operator diagonalization, direct numerical powder/rotor
simulation, or direct Monte Carlo (disorder, exchange dynamics) — from the
parameters you choose, not from pre-rendered pictures. Each lesson opens
with a concrete motivating question, builds the idea up one step at a time,
and asks you to predict what a plot will show *before* revealing it, then
hands over the full explorer once the concept has landed.

## Part 1: Foundations

| # | Lesson | What it teaches |
|---|---|---|
| 0 | **NMR Fundamentals** | Magnetization, precession, RF pulses, T1/T2, the FID, and the Fourier transform |
| 1 | **Relaxation Explorer** | Why the same sample decays two different ways — T2 vs. T2*, and how an echo tells them apart |
| 2 | **Chemical Shift Anisotropy** | Why a solid powder turns one sharp solution-NMR peak into a broad hump |
| 3 | **Dipolar Coupling** | Two nearby nuclei as tiny bar magnets — the Pake doublet, and a 1/r³ distance ruler |
| 4 | **Quadrupolar Interactions** | Why ²³Na, ²⁷Al, ¹¹B and friends look so different from ¹H — and why higher field narrows their lines |
| 5 | **Magic-Angle Spinning** | One trick, spinning at 54.74°, that erases CSA, dipolar, and first-order quadrupolar broadening at once |
| 6 | **MQMAS** | The 2D trick that finishes the job MAS alone can't |
| 7 | **Nutation & CT-Selectivity** | Exciting quadrupolar nuclei efficiently, and boosting signal further with DFS |
| 8 | **J-Coupling & Decoupling** | The one coupling that doesn't care about orientation — and how to switch it off on purpose |
| 9 | **HMQC** | Turning "these nuclei are coupled" into a 2D map of exactly which atoms are linked to which |
| 10 | **Pulse Sequence Composer** | Capstone: build Hahn echo, CPMG, REDOR, CP and more from the same handful of primitives |

## Part 2: Materials Science Applications

| # | Lesson | What it teaches |
|---|---|---|
| 12 | **Disorder & the Czjzek Model** | Why glasses give distributions of Cq/η instead of one crystalline value |
| 13 | **Real Spectra: Glass Case Studies** | Illustrative ²⁷Al (AlIV/V/VI) and ¹¹B (BO₃/BO₄, the "N4" anomaly) worked examples |
| 14 | **Network Connectivity & Qⁿ Speciation** | Why Qⁿ shift trends give populations but not connectivity |
| 15 | **Quantification Pitfalls** | CP bias, T1 saturation, and spinning-sideband redistribution |
| 16 | **DQ-SQ Homonuclear Correlation** | Which sites actually neighbor which — answers Lesson 14's cliffhanger |
| 17 | **STMAS vs. MQMAS** | A more sensitive MQMAS alternative, and why it demands a near-perfect magic angle |
| 18 | **PASS/TOSS Sideband Separation** | Untangling overlapping sidebands from several sites without spinning faster |
| 19 | **Variable-Temperature NMR** | Motional narrowing, coalescence, and Arrhenius-activated dynamics/phase transitions |
| 20 | **Paramagnetic NMR** | Contact/pseudocontact shifts and PRE — nuisance or deliberate structural probe |
| 21 | **NMR Crystallography & DFT** | Bridging DFT-computed Cq/η/CSA tensors to the spectra this app simulates |
| 22 | **Choosing Your Experiment** | A question-driven guide to the whole app |
| 23 | **Spectral Fitting Workshop** | Fit a mystery spectrum by hand; see why a good R² isn't the whole story |
| 24 | **Reference & Glossary** | Hz↔ppm converter, typical Cq/η/T1 ranges, every term defined across the app |

Go in order the first time through; after that, jump to any lesson from the
sidebar as a reference.

There's also a **Live Vector Explorer** — a real-time, 60fps animated
companion to Lesson 1, built as a single self-contained HTML/JS file (no
Python, no Streamlit) and reachable both as a page inside the app and as a
standalone double-click launch (see below).

## Install (Windows, for students)

1. Download or `git clone` this repository.
2. In the VisuSpin folder, right-click **`scripts\install.ps1`** → **Run with PowerShell**.
   (If Windows blocks it, open PowerShell in that folder and run
   `powershell -ExecutionPolicy Bypass -File scripts\install.ps1` instead.)
3. Double-click **`run_visuspin.bat`** to launch the full app — it opens in your browser.
   Or double-click **`run_visuspin_live.bat`** to open just the Live Vector
   Explorer directly, with no Python/Streamlit involved at all.

The installer creates a self-contained virtual environment (`.venv`) inside
the project folder; it never touches your system Python. `run_visuspin_live.bat`
doesn't need the installer or the virtual environment at all — it just opens
an HTML file in your browser.

### Updating

Right-click **`scripts\update.ps1`** → **Run with PowerShell** (or run it the
same way as `install.ps1` above). This pulls the latest version from GitHub
and refreshes dependencies. Requires the folder to be a `git clone` of this
repository (not a plain zip download) — instructors distributing a git clone
to a shared drive get this for free.

## Running manually (any OS)

```bash
pip install -r requirements.txt
streamlit run visuspin/ui/Home.py
```

## Project layout

```
visuspin/
  physics/      # the actual spin physics — Bloch equations, quadrupolar
                # perturbation theory, CSA/dipolar/MAS lineshapes, HMQC,
                # cross-polarization, MQMAS, Czjzek/extended-Czjzek disorder,
                # DQ-SQ, STMAS, exchange dynamics, paramagnetic scaling laws
                # — each independently unit-tested
  sequences/    # block-based pulse-sequence engine (Pulse, Delay, Loop,
                # SpinLock, Acquire, Recouple, CrossPolarize, DFSSweep) +
                # named presets + timing-diagram renderer
  ui/           # Streamlit pages (pages/0_..24_*.py, one per lesson, plus
                # 11_Live_Vector_Explorer.py) — thin views + narrative over
                # visuspin.physics/visuspin.sequences, no physics logic of its own
  classic/      # live_vector_explorer.html — standalone real-time JS/canvas
                # companion tool, embedded into page 11 and launchable directly
tests/          # one test file per physics module, run directly with
                # `python tests/test_*.py` (or via pytest)
scripts/        # install.ps1 / update.ps1 (see above)
assets/         # logo.svg/icon.svg (source vectors), icon.ico (multi-res
                # Windows app/shortcut icon), icon.png (512x512, cross-platform)
run_visuspin.bat        # launches the full Streamlit app
run_visuspin_live.bat   # launches just the Live Vector Explorer, no Python needed
```

## Scope & honesty about simplifications

Some interactions are computed from first principles precisely *because*
their closed-form literature coefficients are easy to misquote (the
second-order quadrupolar CT lineshape, MAS sideband intensities) — VisuSpin
diagonalizes the actual Hamiltonian / simulates the actual rotor period
instead. A few modules intentionally use disclosed simplifications where a
fully rigorous treatment is out of scope for a teaching tool (e.g. the MQMAS
shear ratio uses the standard literature closed-form value rather than a
from-scratch Floquet derivation — see `visuspin/physics/mqmas.py`'s
docstring for exactly why, verified directly rather than assumed). The same
approach carries through Part 2: the Czjzek disorder model is derived
numerically from its own defining assumption (diagonalizing random EFG
tensors) rather than a memorized closed-form density — one such memorized
formula was checked against the simulation while building this and found
wrong, caught rather than shipped (see `tests/test_disorder.py`). Similarly,
paramagnetic NMR (Lesson 20) implements the well-established scaling laws
(Curie 1/T, 1/r⁶ PRE falloff) rather than absolute values from hyperfine
constants, and PASS/TOSS (Lesson 18) shows the practical before/after
outcome rather than simulating the pulse-sequence mechanism itself. Every
simplification is disclosed in the relevant module's docstring and in
`REFERENCES.md`, rather than silently overclaiming research-grade accuracy.

## Testing

```bash
python tests/test_bloch.py
python tests/test_quadrupole.py
# ... etc, one per module — each is self-contained and prints PASS/FAIL
```

## License

MIT — see `LICENSE`.
