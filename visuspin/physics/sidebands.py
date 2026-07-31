"""
MAS spinning-sideband intensities, computed by direct numerical simulation
rather than the classic Herzfeld & Berger (J. Chem. Phys. 73, 6021 (1980))
closed-form Bessel-function series -- deliberately, for the same reason as
the second-order quadrupolar module: the closed-form coefficients have
several different-looking literature conventions, and a geometric simulation
sidesteps needing to recall one exactly.

Method: for each of many powder-sampled crystallite orientations (PAS-to-
rotor Euler angles beta, gamma), rotate the interaction tensor from its own
principal axis frame into the rotor frame, then into the lab frame via the
magic angle (54.74 deg) plus the *time-dependent* rotor spin phase. Only the
lab-frame zz-component of the tensor couples to B0 in the secular (high-field)
approximation, for CSA, first-order quadrupolar, and dipolar alike. Summing
exp(i*phase(t)) over the powder for many rotor periods and Fourier transforming
gives the sideband spectrum directly, with intensities emerging from the
simulation rather than a separate formula.
"""
from __future__ import annotations
import numpy as np

MAGIC_ANGLE_RAD = np.radians(54.7356)


def _rotation_matrix(alpha: float, beta: float, gamma: float) -> np.ndarray:
    """Z-Y-Z Euler rotation matrix (active rotation of the frame)."""
    ca, sa = np.cos(alpha), np.sin(alpha)
    cb, sb = np.cos(beta), np.sin(beta)
    cg, sg = np.cos(gamma), np.sin(gamma)
    Rz1 = np.array([[ca, -sa, 0], [sa, ca, 0], [0, 0, 1]])
    Ry = np.array([[cb, 0, sb], [0, 1, 0], [-sb, 0, cb]])
    Rz2 = np.array([[cg, -sg, 0], [sg, cg, 0], [0, 0, 1]])
    return Rz2 @ Ry @ Rz1


def _axially_symmetric_tensor(delta_aniso: float) -> np.ndarray:
    """Traceless axially-symmetric tensor, PAS z-axis carries the anisotropy
    (eta=0 case; shared by first-order quadrupolar satellites)."""
    return np.diag([-delta_aniso / 2, -delta_aniso / 2, delta_aniso])


def _biaxial_tensor(delta_aniso: float, eta: float) -> np.ndarray:
    dzz = delta_aniso
    dxx = -delta_aniso / 2 * (1 + eta)
    dyy = -delta_aniso / 2 * (1 - eta)
    return np.diag([dxx, dyy, dzz])


def mas_sideband_spectrum(delta_aniso_hz: float, eta: float, nu_rot_hz: float,
                            n_powder: int = 500, n_time_per_period: int = 64,
                            n_periods: int = 48, t2_star_s: float | None = None,
                            normalize: bool = True) -> dict:
    """Simulated MAS sideband spectrum for a single anisotropic interaction
    (CSA-like: use delta_aniso_hz/eta directly; for a first-order quadrupolar
    satellite transition, pass its own delta_aniso_hz = wq*(m-1/2) and eta=0
    per transition, and sum the resulting spectra).

    Returns dict with freq_hz (centred on the isotropic/CT frequency) and
    intensity (normalised to the centreband = 1 at nu_rot -> infinity limit,
    unless normalize=False -- pass that when comparing absolute intensities
    across two different calls with the same n_powder, e.g. to show that
    equal true populations with different anisotropy give different
    apparent centreband heights; each call's raw signal is already averaged
    consistently over n_powder isochromats before this final step).
    """
    if nu_rot_hz <= 0:
        raise ValueError("nu_rot_hz must be > 0; use the static powder pattern for nu_rot=0")
    rng = np.random.default_rng(55)
    cos_beta = rng.uniform(-1, 1, n_powder)
    beta = np.arccos(cos_beta)
    gamma = rng.uniform(0, 2 * np.pi, n_powder)

    V_pas = _biaxial_tensor(delta_aniso_hz, eta)
    tr = 1.0 / nu_rot_hz
    total_time = n_periods * tr
    n_total = n_periods * n_time_per_period
    t = np.linspace(0, total_time, n_total, endpoint=False)
    dt = t[1] - t[0]

    signal = np.zeros(n_total, dtype=complex)
    for b, g in zip(beta, gamma):
        R_pas_to_rotor = _rotation_matrix(0.0, b, g)
        V_rotor = R_pas_to_rotor @ V_pas @ R_pas_to_rotor.T
        # Rather than rotate the (time-independent) tensor into the lab frame
        # at every instant, keep V_rotor fixed and instead express the *lab
        # z-axis* (B0 direction) in rotor-frame coordinates as a function of
        # time -- physically, the spinning rotor "sees" B0 precess around its
        # own axis on a cone of half-angle = the magic angle, at the rotor
        # frequency. Derivation: v_rotor(t) = Rz(-w_r t) @ Ry(-theta_m) @ (0,0,1),
        # which gives the closed form below (verified by direct expansion).
        # The scalar v_rotor(t) . V_rotor . v_rotor(t) is then exactly the
        # tensor's component along the instantaneous B0 direction.
        rotor_phase = 2 * np.pi * nu_rot_hz * t
        cb2, sb2 = np.cos(MAGIC_ANGLE_RAD), np.sin(MAGIC_ANGLE_RAD)
        cg2, sg2 = np.cos(rotor_phase), np.sin(rotor_phase)
        lab_z_x = -cg2 * sb2
        lab_z_y = sg2 * sb2
        lab_z_z = np.full_like(t, cb2)
        lab_z = np.stack([lab_z_x, lab_z_y, lab_z_z], axis=-1)
        Vzz_t = np.einsum("ti,ij,tj->t", lab_z, V_rotor, lab_z)
        phase = 2 * np.pi * np.cumsum(Vzz_t) * dt
        env = np.exp(-t / t2_star_s) if t2_star_s else 1.0
        signal += np.exp(1j * phase) * env

    signal /= n_powder
    spectrum = np.fft.fftshift(np.fft.fft(signal))
    freq = np.fft.fftshift(np.fft.fftfreq(n_total, d=dt))
    mag = np.abs(spectrum)
    if normalize and mag.max() > 0:
        mag = mag / mag.max()
    return {"freq_hz": freq, "intensity": mag}
