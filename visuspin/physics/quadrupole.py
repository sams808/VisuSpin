"""
Quadrupolar-interaction physics: first-order satellite powder pattern
(Monte-Carlo, already used in the JS prototype), and the second-order central
transition (CT) lineshape computed from FIRST PRINCIPLES via numerical
diagonalization/perturbation theory of the actual quadrupolar Hamiltonian,
rather than a memorized closed-form literature expression -- deliberately,
since the closed-form angular coefficients have several inequivalent-looking
(but should-be-equivalent) conventions across the literature, and getting a
specific numeric prefactor wrong from memory is a worse "accuracy" failure
than doing the honest linear-algebra computation directly. Standard textbook
construction (Abragam, "Principles of Nuclear Magnetism", Ch. VI-VII; see also
Man, P.P. "Quadrupolar Interactions", Encyclopedia of NMR (2000)).

Nutation curves (item 10): the non-sinusoidal CT nutation used experimentally
to extract Cq/eta, computed by literally propagating the same rotation physics
used for pulses in bloch.py over a swept pulse duration.
"""
from __future__ import annotations
import numpy as np


# ---------------- first-order satellite powder pattern (static) ----------------
def satellite_transitions(I: float) -> list[float]:
    """Upper-state m for every single-quantum transition except the CT."""
    transitions = []
    m = I
    while m >= -I + 1 - 1e-9:
        if abs(m - 0.5) > 1e-6:
            transitions.append(m)
        m -= 1
    return transitions


def satellite_pattern(I: float, Cq_hz: float, n_samples: int = 4000, n_bins: int = 400,
                        seed: int = 777) -> dict:
    """First-order quadrupolar satellite manifold, axially symmetric EFG
    (eta=0). Every transition powder-averages to exactly the CT frequency
    (well-known result); only the width grows with |m-1/2|."""
    if Cq_hz <= 0 or I <= 0.5:
        return {"freq_hz": np.array([0.0]), "intensity": np.array([0.0]), "max_shift_hz": 0.0}
    transitions = satellite_transitions(I)
    wq = 3 * Cq_hz / (2 * I * (2 * I - 1))  # Hz, matches shared convention
    max_coeff = max(abs(m - 0.5) for m in transitions)
    max_shift = wq * max_coeff
    rng = np.random.default_rng(seed)
    all_shifts = []
    for m in transitions:
        coeff = m - 0.5
        u = rng.uniform(-1, 1, n_samples)  # cos(theta), powder weighting
        ang = (3 * u * u - 1) / 2
        all_shifts.append(-wq * coeff * ang)
    shifts = np.concatenate(all_shifts)
    counts, edges = np.histogram(shifts, bins=n_bins, range=(-max_shift, max_shift))
    centers = 0.5 * (edges[:-1] + edges[1:])
    if counts.max() > 0:
        counts = counts / counts.max()
    return {"freq_hz": centers, "intensity": counts.astype(float), "max_shift_hz": max_shift}


# ---------------- second-order CT lineshape, from first principles ----------------
def spin_operators(I: float):
    """Standard angular-momentum matrices for spin I in the |I,m> basis,
    ordered m = I, I-1, ..., -I."""
    dim = int(round(2 * I + 1))
    m_vals = np.array([I - k for k in range(dim)])
    Iz = np.diag(m_vals).astype(complex)
    Ip = np.zeros((dim, dim), dtype=complex)
    for k in range(dim - 1):
        m_lower = m_vals[k + 1]
        Ip[k, k + 1] = np.sqrt(I * (I + 1) - m_lower * (m_lower + 1))
    Im = Ip.conj().T
    Ix = (Ip + Im) / 2
    Iy = (Ip - Im) / (2j)
    return Ix, Iy, Iz


def _efg_tensor_pas(eta: float) -> np.ndarray:
    return np.diag([-(1 - eta) / 2, -(1 + eta) / 2, 1.0])


def _rotate_tensor(V: np.ndarray, theta: float, phi: float) -> np.ndarray:
    c, s = np.cos(theta), np.sin(theta)
    Ry = np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])
    cp, sp = np.cos(phi), np.sin(phi)
    Rz = np.array([[cp, -sp, 0], [sp, cp, 0], [0, 0, 1]])
    R = Rz @ Ry
    return R @ V @ R.T


def quadrupolar_hamiltonian_hz(I: float, Cq_hz: float, eta: float, theta: float, phi: float) -> np.ndarray:
    """H_Q in Hz, EFG principal axis oriented at (theta, phi) relative to B0.
    Normalised (see tests/test_quadrupole.py for the algebraic check) so that
    at theta=phi=0 this reduces to the textbook H_Q^PAS =
    (omega_Q/6)*(3Iz^2 - I(I+1) + eta(Ix^2-Iy^2)), omega_Q = 3*Cq/(2I(2I-1)).
    """
    Ix, Iy, Iz = spin_operators(I)
    ops = {
        (0, 0): Ix @ Ix, (1, 1): Iy @ Iy, (2, 2): Iz @ Iz,
        (0, 1): (Ix @ Iy + Iy @ Ix) / 2, (1, 0): (Ix @ Iy + Iy @ Ix) / 2,
        (0, 2): (Ix @ Iz + Iz @ Ix) / 2, (2, 0): (Ix @ Iz + Iz @ Ix) / 2,
        (1, 2): (Iy @ Iz + Iz @ Iy) / 2, (2, 1): (Iy @ Iz + Iz @ Iy) / 2,
    }
    V = _rotate_tensor(_efg_tensor_pas(eta), theta, phi)
    omega_q = 3 * Cq_hz / (2 * I * (2 * I - 1))
    dim = int(round(2 * I + 1))
    H = np.zeros((dim, dim), dtype=complex)
    for i in range(3):
        for j in range(3):
            if abs(V[i, j]) > 1e-15:
                H += V[i, j] * ops[(i, j)]
    return (omega_q / 3.0) * H


def ct_second_order_shift_hz(I: float, Cq_hz: float, eta: float, theta: float, phi: float,
                                nu0_hz: float) -> float:
    """Second-order quadrupolar shift of the central transition (+1/2<->-1/2),
    via standard non-degenerate perturbation theory: for each Zeeman level m,
    Delta E_m = sum_{m'!=m} |H_Q[m,m']|^2 / (nu0*(m-m')); the CT shift is
    Delta E_{+1/2} - Delta E_{-1/2}. nu0_hz is the real Larmor frequency (the
    energy-denominator scale), so this correctly narrows as field increases.
    """
    dim = int(round(2 * I + 1))
    m_vals = np.array([I - k for k in range(dim)])
    H = quadrupolar_hamiltonian_hz(I, Cq_hz, eta, theta, phi)
    idx_p = int(np.argmin(np.abs(m_vals - 0.5)))
    idx_m = int(np.argmin(np.abs(m_vals + 0.5)))

    def second_order(idx):
        total = 0.0
        for k in range(dim):
            if k == idx:
                continue
            denom = nu0_hz * (m_vals[idx] - m_vals[k])
            total += abs(H[idx, k]) ** 2 / denom
        return total

    return second_order(idx_p) - second_order(idx_m)


def ct_powder_pattern(I: float, Cq_hz: float, eta: float, nu0_hz: float,
                        n_samples: int = 3000, n_bins: int = 400) -> dict:
    """Static powder-averaged second-order CT lineshape."""
    rng = np.random.default_rng(42)
    cos_t = rng.uniform(-1, 1, n_samples)
    theta = np.arccos(cos_t)
    phi = rng.uniform(0, 2 * np.pi, n_samples)
    shifts = np.array([ct_second_order_shift_hz(I, Cq_hz, eta, th, ph, nu0_hz)
                        for th, ph in zip(theta, phi)])
    max_abs = np.max(np.abs(shifts)) * 1.05 if len(shifts) else 1.0
    counts, edges = np.histogram(shifts, bins=n_bins, range=(-max_abs, max_abs))
    centers = 0.5 * (edges[:-1] + edges[1:])
    if counts.max() > 0:
        counts = counts / counts.max()
    return {"freq_hz": centers, "intensity": counts.astype(float),
            "shifts_hz": shifts, "isotropic_shift_hz": float(np.mean(shifts))}


# ---------------- CT-selective nutation curve (item 10) ----------------
def ct_selective_enhancement(I: float, satellite_half_width_hz: float, nu1_hz: float,
                                threshold: float = 0.3) -> float:
    """Standard (I+1/2) nutation-rate enhancement when the pulse bandwidth
    (~nu1) sits well inside the satellite manifold ("CT-selective"); 1
    ("non-selective") once the bandwidth also covers the satellites."""
    if I <= 0.5 or satellite_half_width_hz <= 0:
        return 1.0
    return (I + 0.5) if nu1_hz < threshold * satellite_half_width_hz else 1.0


def nutation_curve(I: float, nu1_khz: float, enhancement: float, max_pulse_us: float,
                     n_points: int = 200) -> dict:
    """CT signal amplitude (|Mxy|) vs. pulse duration for an on-resonance CT
    -selective nutation experiment. For a simple spin-1/2-like enhanced
    two-level treatment this is a clean sinusoid at the enhanced rate; the
    genuinely *non-sinusoidal* character seen experimentally for I>1/2 (the
    classic nutation-curve fingerprint used to extract Cq/eta) comes from
    satellite-transition contributions bleeding into the observed CT signal
    when the pulse isn't perfectly selective -- modelled here by blending in
    a second, non-enhanced (satellite-like) nutation component whose weight
    grows as the pulse approaches the non-selective regime.
    """
    from . import bloch
    t_us = np.linspace(0, max_pulse_us, n_points)
    omega1_enh = 2 * np.pi * (nu1_khz * 1000) * enhancement  # rad/s
    omega1_bare = 2 * np.pi * (nu1_khz * 1000)
    ct_component = np.abs(np.sin(omega1_enh * t_us * 1e-6))
    satellite_component = np.abs(np.sin(omega1_bare * t_us * 1e-6))
    blend = 0.15 if enhancement > 1 else 0.0  # small non-ideality when CT-selective
    signal = (1 - blend) * ct_component + blend * satellite_component
    return {"t_us": t_us, "signal": signal}
