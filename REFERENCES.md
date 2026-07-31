# References

The literature behind every simulation in VisuSpin, organized by module. Where
a formula is genuinely contested or easy to misquote from memory (e.g. the
second-order quadrupolar lineshape, MAS sideband intensities), VisuSpin
computes it from first principles instead of a closed-form literature
coefficient — see the relevant module docstring for that reasoning. The
references below are cited either because VisuSpin *implements* the specific
result, or because they're the right entry point for a student who wants the
full derivation.

## Foundational texts

- Abragam, A. *Principles of Nuclear Magnetism*. Oxford University Press, 1961. (Ch. VI–VII: quadrupolar interactions)
- Levitt, M.H. *Spin Dynamics: Basics of Nuclear Magnetic Resonance*, 2nd ed. Wiley, 2008. (Ch. 5 and throughout: general product-operator/relaxation formalism)
- Duer, M.J. *Introduction to Solid-State NMR Spectroscopy*. Blackwell, 2004.
- Man, P.P. "Quadrupolar Interactions." *Encyclopedia of Analytical Chemistry* (2000); also "Quadrupole Couplings in Nuclear Magnetic Resonance, General." *Encyclopedia of NMR* (2000).

## Relaxation & pulses (`physics/bloch.py`, `ui/pages/1_Relaxation_Explorer.py`)

- Bloch, F. "Nuclear Induction." *Phys. Rev.* **70**, 460 (1946). (The Bloch equations themselves)
- Harris, R.K. et al. "NMR nomenclature: nuclear spin properties and conventions for chemical shifts." *Pure Appl. Chem.* **73**, 1795 (2001). (Gyromagnetic ratios used in `nuclides.py`)

## Quadrupolar nuclei: CT-selectivity, DFS, nutation (`physics/quadrupole.py`, `physics/bloch.py`, `ui/pages/7_Nutation_CT_Selectivity.py`)

- Iuga, D., Schäfer, H., Verhagen, R. & Kentgens, A.P.M. "Population and coherence transfer induced by double frequency sweeps in half-integer quadrupolar spin systems." *J. Magn. Reson.* **147**, 192 (2000). (DFS adiabatic passage)
- Abragam, *Principles of Nuclear Magnetism* (above), for the (I+1/2) central-transition nutation enhancement and second-order perturbation-theory framework VisuSpin's own diagonalization reproduces numerically.

## MAS sidebands (`physics/sidebands.py`)

- Herzfeld, J. & Berger, A.E. "Sideband intensities in NMR spectra of samples spinning at the magic angle." *J. Chem. Phys.* **73**, 6021 (1980). (The classic closed-form result; VisuSpin instead simulates the rotor-period tensor rotation directly — see the module docstring for why.)

## Chemical shift anisotropy (`physics/csa.py`)

- Haeberlen, U. *High Resolution NMR in Solids: Selective Averaging*. Academic Press, 1976. (The Haeberlen convention used throughout)

## Dipolar coupling & REDOR (`physics/dipolar.py`, `sequences/presets.py`)

- Gullion, T. & Schaefer, J. "Rotational-Echo Double-Resonance NMR." *J. Magn. Reson.* **81**, 196 (1989). (REDOR)
- Pake, G.E. "Nuclear Resonance Absorption in Hydrated Crystals: Fine Structure of the Proton Line." *J. Chem. Phys.* **16**, 327 (1948). (The Pake doublet)

## Cross-polarization & spin-lock (`physics/cp.py`, `sequences/blocks.py`)

- Hartmann, S.R. & Hahn, E.L. "Nuclear Double Resonance in the Rotating Frame." *Phys. Rev.* **128**, 2042 (1962). (Hartmann–Hahn matching)
- Pines, A., Gibby, M.G. & Waugh, J.S. "Proton-enhanced NMR of dilute spins in solids." *J. Chem. Phys.* **59**, 569 (1973). (CP buildup/decay kinetics)
- Look, D.C. & Lowe, I.J. "Nuclear Magnetic Dipole–Dipole Relaxation Along the Static and Rotating Magnetic Fields." *J. Chem. Phys.* **44**, 2995 (1966). (T1ρ / spin-lock relaxation)

## Echo sequences (`sequences/presets.py`)

- Hahn, E.L. "Spin Echoes." *Phys. Rev.* **80**, 580 (1950). (Hahn echo)
- Carr, H.Y. & Purcell, E.M. "Effects of Diffusion on Free Precession in Nuclear Magnetic Resonance Experiments." *Phys. Rev.* **94**, 630 (1954).
- Meiboom, S. & Gill, D. "Modified Spin-Echo Method for Measuring Nuclear Relaxation Times." *Rev. Sci. Instrum.* **29**, 688 (1958). (Together: CPMG)

## HMQC & coherence transfer (`physics/hmqc.py`)

- Bax, A., Griffey, R.H. & Hawkins, B.L. "Correlation of proton and nitrogen-15 chemical shifts by multiple quantum NMR." *J. Magn. Reson.* **55**, 301 (1983). (Solution-NMR HMQC origin)
- Cavadini, S., Antonijevic, S., Lupulescu, A. & Bodenhausen, G. "Indirect detection of nitrogen-14 in solid-state NMR spectroscopy." *J. Magn. Reson.* **182**, 168 (2006). (Solid-state D-/J-HMQC sequence VisuSpin's composer implements)
- Morris, G.A. & Freeman, R. "Enhancement of nuclear magnetic resonance signals by polarization transfer." *J. Am. Chem. Soc.* **101**, 760 (1979). (The sin(πJτ) transfer-efficiency function reused for both J- and D-HMQC)

## J-coupling multiplets & decoupling (`physics/decoupling.py`)

- Karplus, M. & Pople, J.A. "Theory of Carbon NMR Chemical Shifts in Conjugated Molecules." *J. Chem. Phys.* **38**, 2803 (1963). (General multiplet-counting result underlying the binomial multiplet)
- Levitt, *Spin Dynamics* (above), Ch. 5, for the standard treatment of heteronuclear decoupling.

## MQMAS (`physics/mqmas.py`)

- Frydman, L. & Harwood, J.S. "Isotropic Spectra of Half-Integer Quadrupolar Spins from Bidimensional Magic-Angle Spinning NMR." *J. Am. Chem. Soc.* **117**, 5367 (1995). (The original MQMAS experiment)
- Amoureux, J.P., Fernandez, C. & Steuernagel, S. "Z-Filtering in MQMAS NMR." *J. Magn. Reson. A* **123**, 116 (1996). (The shear-ratio formula VisuSpin cites directly, having confirmed by direct computation that a naive rotor-averaged re-derivation from the static formula does *not* reproduce it — see `mqmas.py`'s module docstring and `tests/test_mqmas.py`)

## Disorder & the Czjzek model (`physics/disorder.py`)

- Czjzek, G. et al. "Atomic coordination and the distribution of electric field gradients in amorphous solids." *Phys. Rev. B* **23**, 2513 (1981). (VisuSpin derives the distribution numerically from its defining assumption — random traceless symmetric EFG tensors — rather than quoting the closed-form density; a memorized closed-form marginal was checked against the simulation while building this and found wrong, caught rather than shipped, see `tests/test_disorder.py`.)
- Le Caër, G., Bureau, B. & Massiot, D. "An extension of the Czjzek model for the distribution of electric field gradients in disordered solids and an application to NMR spectra of ⁷¹Ga in chalcogenide glasses." *J. Phys.: Condens. Matter* **22**, 065402 (2010). (Extended Czjzek model)

## DQ-SQ homonuclear correlation (`physics/dqsq.py`)

- Feike, M. et al. "Broadband Multiple-Quantum NMR Spectroscopy." *J. Magn. Reson. A* **122**, 214 (1996). (BABA recoupling)
- Hohwy, M. et al. "Broadband dipolar recoupling in the nuclear magnetic resonance of rotating solids: A compensated C7 pulse sequence." *J. Chem. Phys.* **108**, 2686 (1998). (POST-C7 recoupling)

## STMAS (`physics/stmas.py`)

- Gan, Z. "Isotropic NMR spectra of half-integer quadrupolar nuclei using satellite transitions and magic-angle spinning." *J. Am. Chem. Soc.* **122**, 3242 (2000).

## Variable-temperature NMR & exchange dynamics (`physics/dynamics.py`)

- Gutowsky, H.S. & Holm, C.H. "Rate Processes and Nuclear Magnetic Resonance Spectra. II. Hindered Internal Rotation of Amides." *J. Chem. Phys.* **25**, 1228 (1956).
- McConnell, H.M. "Reaction Rates by Nuclear Magnetic Resonance." *J. Chem. Phys.* **28**, 430 (1958). (VisuSpin simulates 2-site exchange by direct Monte Carlo — stochastic site-jumping under the ordinary Bloch equations — rather than the classical closed-form lineshape, verified against both the slow- and fast-exchange limits.)

## Paramagnetic NMR (`physics/paramagnetic.py`)

- Bertini, I., Luchinat, C. & Parigi, G. *Solution NMR of Paramagnetic Molecules*. Elsevier, 2001.
- Solomon, I. "Relaxation Processes in a System of Two Spins." *Phys. Rev.* **99**, 559 (1955).
- Bloembergen, N. "Proton Relaxation Times in Paramagnetic Solutions." *J. Chem. Phys.* **27**, 572 (1957). (Together: the Solomon-Bloembergen theory behind PRE; VisuSpin implements the well-established 1/r⁶ and Curie 1/T scaling laws rather than deriving absolute shifts/rates from hyperfine constants and g-tensors.)

## Software / testing tools used during development

- Streamlit (`streamlit.io`) — the UI framework VisuSpin is built on.
- NumPy, Matplotlib — numerical simulation and plotting.
