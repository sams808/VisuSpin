<p align="center">
  <img src="assets/logo.svg" alt="VisuSpin" width="360">
</p>

<p align="center"><em>An interactive teaching toolkit for solid-state NMR spin physics.</em></p>

---

VisuSpin is a set of interactive, physically-grounded simulations for
teaching solid-state (and general) NMR spin dynamics. Every plot is computed
live from the actual underlying physics — exact per-isochromat Bloch
integration, first-principles spin-operator diagonalization, or direct
numerical powder/rotor simulation — from the parameters you choose, not from
pre-rendered pictures.

## What's inside

| Page | What it teaches |
|---|---|
| **Relaxation Explorer** | T1/T2/T2\* Bloch simulation: real nuclide table, finite pulses, CT-selective & DFS excitation, MAS |
| **Lineshapes** | CSA, dipolar Pake pattern, 1st/2nd-order quadrupolar CT, MAS sidebands |
| **Powder Averaging (3D)** | Which crystallite orientations build which part of a powder pattern |
| **MQMAS** | Why correlating a multiple-quantum dimension removes 2nd-order quadrupolar broadening |
| **HMQC** | 2D heteronuclear correlation via J- or D-mediated coherence transfer |
| **Multiplets & Decoupling** | J-multiplets collapsing under heteronuclear decoupling |
| **Nutation & CT-Selectivity** | Non-sinusoidal quadrupolar nutation, (I+1/2) enhancement, DFS adiabatic sweeps |
| **Pulse Sequence Composer** | Build sequences (Hahn echo, CPMG, REDOR, CP, spin-lock, DFS, ...) block by block, Scratch-style, with live timing diagrams |

## Install (Windows, for students)

1. Download or `git clone` this repository.
2. In the VisuSpin folder, right-click **`scripts\install.ps1`** → **Run with PowerShell**.
   (If Windows blocks it, open PowerShell in that folder and run
   `powershell -ExecutionPolicy Bypass -File scripts\install.ps1` instead.)
3. Double-click **`run_visuspin.bat`** to launch the app — it opens in your browser.

The installer creates a self-contained virtual environment (`.venv`) inside
the project folder; it never touches your system Python.

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
                # cross-polarization, MQMAS — each independently unit-tested
  sequences/    # block-based pulse-sequence engine (Pulse, Delay, Loop,
                # SpinLock, Acquire, Recouple, CrossPolarize, DFSSweep) +
                # named presets + timing-diagram renderer
  ui/           # Streamlit pages — thin views over visuspin.physics /
                # visuspin.sequences, no physics logic of its own
tests/          # one test file per physics module, run directly with
                # `python tests/test_*.py` (or via pytest)
scripts/        # install.ps1 / update.ps1 (see above)
assets/         # logo, icon
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
docstring for exactly why, verified directly rather than assumed). Every such
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
