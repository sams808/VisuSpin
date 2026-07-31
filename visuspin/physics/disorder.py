"""
Disorder models for amorphous/glassy materials: the Czjzek and extended-
Czjzek distributions of quadrupolar parameters (Cq, eta), plus a Gaussian
isotropic-shift disorder model for amorphous line broadening.

The Czjzek model's closed-form probability density has several numeric
prefactors that are easy to misquote (the same risk flagged in
quadrupole.py) -- so rather than quoting it, this module derives the
distribution directly from its one physical assumption: in a structurally
disordered solid, the electric field gradient at a given site has no
preferred orientation or shape, i.e. its 5 independent tensor components
are i.i.d. Gaussian. Generate many such random tensors, diagonalize each,
read off its own Cq and eta -- the resulting numerical distribution IS the
Czjzek distribution, by construction, with no formula to misquote.

References: Czjzek, G. et al. "Atomic coordination and the distribution of
electric field gradients in amorphous solids." Phys. Rev. B 23, 2513
(1981). Extended model: Le Caer, G., Bureau, B. & Massiot, D. "An extension
of the Czjzek model for the distribution of electric field gradients in
disordered solids...". J. Phys.: Condens. Matter 22, 065402 (2010).
"""
from __future__ import annotations
import numpy as np


def _random_traceless_symmetric_tensors(rng: np.random.Generator, n: int, scale: float) -> np.ndarray:
    """n random traceless symmetric 3x3 tensors; the 5 independent
    components (2 diagonal d.o.f. after the traceless constraint, 3
    off-diagonal) are each i.i.d. Gaussian(0, scale). Shape (n, 3, 3)."""
    vxx = rng.normal(0, scale, n)
    vyy = rng.normal(0, scale, n)
    vzz = -(vxx + vyy)
    vxy = rng.normal(0, scale, n)
    vxz = rng.normal(0, scale, n)
    vyz = rng.normal(0, scale, n)
    T = np.zeros((n, 3, 3))
    T[:, 0, 0], T[:, 1, 1], T[:, 2, 2] = vxx, vyy, vzz
    T[:, 0, 1] = T[:, 1, 0] = vxy
    T[:, 0, 2] = T[:, 2, 0] = vxz
    T[:, 1, 2] = T[:, 2, 1] = vyz
    return T


def _cq_eta_from_tensors(T: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Diagonalize each tensor and read off (Cq, eta) using the standard EFG
    convention |Vzz| >= |Vyy| >= |Vxx| (Cq directly proportional to Vzz in
    these dimensionless tensor units; eta = |Vxx-Vyy|/|Vzz|)."""
    eigvals = np.linalg.eigvalsh(T)  # ascending, shape (n, 3)
    idx = np.argsort(-np.abs(eigvals), axis=1)
    sorted_vals = np.take_along_axis(eigvals, idx, axis=1)
    Vzz, Vyy, Vxx = sorted_vals[:, 0], sorted_vals[:, 1], sorted_vals[:, 2]
    Cq = Vzz
    eta = np.clip(np.abs(Vxx - Vyy) / np.abs(Vzz), 0, 1)
    return Cq, eta


def czjzek_cq_eta_samples(sigma: float, n_samples: int = 20000, seed: int = 123) -> dict:
    """Pure (fully disordered) Czjzek Cq/eta samples. `sigma` sets the width
    (same units as Cq, e.g. MHz) of the underlying Gaussian tensor-component
    distribution."""
    rng = np.random.default_rng(seed)
    T = _random_traceless_symmetric_tensors(rng, n_samples, scale=sigma)
    Cq, eta = _cq_eta_from_tensors(T)
    return {"Cq": np.abs(Cq), "eta": eta}


def extended_czjzek_cq_eta_samples(Cq0: float, eta0: float, rho: float,
                                      n_samples: int = 20000, seed: int = 123) -> dict:
    """Extended Czjzek: a fixed reference tensor (Cq0, eta0 -- the average,
    crystalline-like local environment) plus an added random Czjzek-type
    disorder tensor whose width is `rho` times |Cq0| -- so rho is a
    dimensionless disorder fraction: rho=0 gives a single sharp (Cq0, eta0);
    rho >> 1 makes the reference negligible and the distribution approaches
    pure Czjzek. (This specific rho-as-fraction-of-Cq0 parametrization is a
    convenience choice for this teaching tool, not a claim of matching one
    specific paper's normalization exactly.)"""
    rng = np.random.default_rng(seed)
    Vzz0 = Cq0
    Vxx0 = -Vzz0 * (1 + eta0) / 2
    Vyy0 = -Vzz0 * (1 - eta0) / 2
    T_ref = np.diag([Vxx0, Vyy0, Vzz0])
    disorder_scale = rho * abs(Cq0) if Cq0 != 0 else rho
    T_disorder = _random_traceless_symmetric_tensors(rng, n_samples, scale=disorder_scale)
    T_total = T_ref[None, :, :] + T_disorder
    Cq, eta = _cq_eta_from_tensors(T_total)
    return {"Cq": np.abs(Cq), "eta": eta}


def gaussian_shift_distribution(delta_iso_mean: float, sigma_shift: float,
                                   n_samples: int = 20000, seed: int = 321) -> np.ndarray:
    """Amorphous isotropic-shift disorder: site-to-site variation in the
    local chemical environment gives a Gaussian spread of isotropic shifts
    around a mean, independent of (and layered on top of) any CSA/
    quadrupolar anisotropy each site also has."""
    rng = np.random.default_rng(seed)
    return rng.normal(delta_iso_mean, sigma_shift, n_samples)


def glass_ct_shifts(I: float, Cq_or_sigma: float, eta0: float, rho: float, nu0_hz: float,
                       shift_sigma_hz: float = 0.0, n_samples: int = 4000,
                       use_extended: bool = True) -> tuple[np.ndarray, dict]:
    """Raw per-site 2nd-order CT shift samples for a disordered site (see
    glass_ct_powder_pattern for the histogrammed version). Exposed
    separately so several coordination-environment components can be
    combined by concatenating raw samples (see combine_shift_components)
    rather than summing pre-normalized histograms."""
    from .quadrupole import ct_second_order_shift_hz
    if use_extended:
        cqeta = extended_czjzek_cq_eta_samples(Cq_or_sigma, eta0, rho, n_samples=n_samples)
    else:
        cqeta = czjzek_cq_eta_samples(Cq_or_sigma, n_samples=n_samples)
    rng = np.random.default_rng(999)
    cos_t = rng.uniform(-1, 1, n_samples)
    theta = np.arccos(cos_t)
    phi = rng.uniform(0, 2 * np.pi, n_samples)
    shifts = np.array([
        ct_second_order_shift_hz(I, cq, eta, th, ph, nu0_hz)
        for cq, eta, th, ph in zip(cqeta["Cq"], cqeta["eta"], theta, phi)
    ])
    if shift_sigma_hz > 0:
        shifts = shifts + gaussian_shift_distribution(0.0, shift_sigma_hz, n_samples=n_samples)
    return shifts, cqeta


def glass_ct_powder_pattern(I: float, Cq_or_sigma: float, eta0: float, rho: float, nu0_hz: float,
                               shift_sigma_hz: float = 0.0, n_samples: int = 4000, n_bins: int = 400,
                               use_extended: bool = True) -> dict:
    """CT powder pattern for a disordered (glassy) site: combines a
    Czjzek/extended-Czjzek distribution of (Cq, eta) with ordinary powder
    orientation averaging and (optionally) an amorphous Gaussian isotropic-
    shift spread -- reusing the exact same first-principles 2nd-order CT
    perturbation-theory calculation as the crystalline case
    (visuspin.physics.quadrupole.ct_second_order_shift_hz). The only change
    from the crystalline lineshape is that Cq and eta are themselves random
    per site instead of fixed; rho=0 (or a vanishingly small sigma) recovers
    the ordinary single-crystallite-value crystalline pattern exactly.
    """
    shifts, cqeta = glass_ct_shifts(I, Cq_or_sigma, eta0, rho, nu0_hz, shift_sigma_hz, n_samples, use_extended)
    max_abs = np.max(np.abs(shifts)) * 1.05 if len(shifts) else 1.0
    counts, edges = np.histogram(shifts, bins=n_bins, range=(-max_abs, max_abs))
    centers = 0.5 * (edges[:-1] + edges[1:])
    if counts.max() > 0:
        counts = counts / counts.max()
    return {"freq_hz": centers, "intensity": counts.astype(float), "cq_eta_samples": cqeta}


def combine_shift_components(shift_arrays: list[np.ndarray], n_bins: int = 500,
                                freq_range: tuple[float, float] | None = None) -> dict:
    """Combine several coordination-environment components' raw shift
    samples (e.g. from glass_ct_shifts, or plain Gaussian-shift arrays) into
    one population-weighted spectrum: give each component's array a length
    proportional to its population fraction before calling this, and the
    combined histogram will reflect that weighting automatically."""
    combined = np.concatenate(shift_arrays)
    if freq_range is None:
        max_abs = np.max(np.abs(combined)) * 1.05 if len(combined) else 1.0
        freq_range = (-max_abs, max_abs)
    counts, edges = np.histogram(combined, bins=n_bins, range=freq_range)
    centers = 0.5 * (edges[:-1] + edges[1:])
    if counts.max() > 0:
        counts = counts / counts.max()
    return {"freq_hz": centers, "intensity": counts.astype(float)}
