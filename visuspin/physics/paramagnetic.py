"""
Paramagnetic NMR: Fermi-contact and pseudocontact shifts, and paramagnetic
relaxation enhancement (PRE). Implements the well-established SCALING LAWS
(Curie 1/T temperature dependence; the same (3cos^2(theta)-1) geometric
factor already used for CSA and dipolar coupling; 1/r^6 PRE distance
falloff) rather than deriving absolute shift/rate values from hyperfine
coupling constants and g-tensors from scratch -- the scaling laws are
simple, non-controversial physics; the absolute prefactors (A_hyperfine,
g-values) are exactly the kind of easily-misquoted numeric detail this
codebase avoids trusting to memory elsewhere. Shifts/rates here are
expressed relative to a user-supplied reference value at a reference
temperature/distance.

References: Bertini, I., Luchinat, C. & Parigi, G. "Solution NMR of
Paramagnetic Molecules." Elsevier (2001); Solomon, I. "Relaxation Processes
in a System of Two Spins." Phys. Rev. 99, 559 (1955); Bloembergen, N.
"Proton Relaxation Times in Paramagnetic Solutions." J. Chem. Phys. 27, 572
(1957).
"""
from __future__ import annotations
import numpy as np


def curie_law_factor(T_kelvin, T_ref_kelvin: float = 298.15):
    """Curie-law temperature scaling, relative to a reference temperature:
    exactly T_ref/T (an unpaired electron's population difference, and so
    every shift/coupling that derives from it, scales as 1/T)."""
    return T_ref_kelvin / np.asarray(T_kelvin, dtype=float)


def contact_shift_ppm(delta_ref_ppm: float, T_kelvin, T_ref_kelvin: float = 298.15):
    """Fermi-contact shift at T, given its value at a reference temperature
    (Curie-law 1/T scaling; isotropic -- no geometric/orientation
    dependence, since it comes from spin density delocalized onto the
    nucleus through bonds, not a through-space interaction)."""
    return delta_ref_ppm * curie_law_factor(T_kelvin, T_ref_kelvin)


def pseudocontact_shift_ppm(delta_ref_ppm: float, theta_rad, T_kelvin, T_ref_kelvin: float = 298.15):
    """Pseudocontact (dipolar, through-space) shift: the same
    (3cos^2(theta)-1)/2 orientation factor already used for CSA
    (visuspin.physics.csa) and dipolar coupling
    (visuspin.physics.dipolar.dipolar_splitting_hz), combined with Curie-law
    1/T scaling. delta_ref_ppm is the shift's magnitude at theta=0 and
    T=T_ref."""
    ang = (3 * np.cos(np.asarray(theta_rad, dtype=float)) ** 2 - 1) / 2
    return delta_ref_ppm * ang * curie_law_factor(T_kelvin, T_ref_kelvin)


def pre_rate_hz(rate_ref_hz: float, r_angstrom, r_ref_angstrom: float = 3.0):
    """Paramagnetic relaxation enhancement rate (added to 1/T1 or 1/T2),
    given its value at a reference electron-nucleus distance: scales as
    1/r^6, the dominant qualitative feature of the Solomon-Bloembergen
    dipolar relaxation mechanism (the full theory also has a
    correlation-time-dependent spectral density factor, omitted here as a
    disclosed simplification -- see module docstring)."""
    r = np.asarray(r_angstrom, dtype=float)
    return rate_ref_hz * (r_ref_angstrom / r) ** 6
