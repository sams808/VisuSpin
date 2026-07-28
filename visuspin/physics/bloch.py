"""
Per-isochromat Bloch-equation simulator in the rotating frame.

Physics (identical to the verified VisuSpin/t1t2_explorer JS tool):

    dMx/dt =  dw*My - Mx/T2
    dMy/dt = -dw*Mx - My/T2
    dMz/dt = -(Mz - M0)/T1

for each isochromat independently, where `dw` is that isochromat's own
resonance offset (rad/ms). Because this ODE is linear with piecewise-constant
`dw` and relaxation times, it has an EXACT closed-form solution per step
(rotation about z at rate dw, combined with independent T1/T2 exponential
decay) -- so evolution is exact, not an Euler/RK4 approximation, and has zero
numerical drift regardless of step size.

Pulses are finite-duration effective-field rotations (B1 + the isochromat's
own offset), applied via the Rodrigues rotation formula -- not idealised
instantaneous flips -- so off-resonance isochromats genuinely tip along a
different axis than on-resonance ones (real pulse-imperfection physics).
"""
from __future__ import annotations

import numpy as np
from dataclasses import dataclass, field


@dataclass
class Ensemble:
    """N independent isochromats. All arrays have shape (N,)."""
    n: int
    dw: np.ndarray        # static (non-spinning) offset, rad/ms
    phi: np.ndarray        # random rotor phase at t=0, rad (used only under MAS)
    mx: np.ndarray = field(default=None)
    my: np.ndarray = field(default=None)
    mz: np.ndarray = field(default=None)
    m0: float = 1.0

    def __post_init__(self):
        if self.mx is None:
            self.mx = np.zeros(self.n)
        if self.my is None:
            self.my = np.zeros(self.n)
        if self.mz is None:
            self.mz = np.full(self.n, self.m0)

    @classmethod
    def from_gaussian_offsets(cls, n: int, sigma_rad_per_ms: float, seed: int = 1234,
                                m0: float = 1.0) -> "Ensemble":
        rng = np.random.default_rng(seed)
        dw = rng.normal(0.0, sigma_rad_per_ms, n) if sigma_rad_per_ms > 0 else np.zeros(n)
        phi = np.random.default_rng(seed + 1).uniform(0, 2 * np.pi, n)
        return cls(n=n, dw=dw, phi=phi, m0=m0)

    def sum_m(self) -> tuple[float, float, float]:
        """The vector sum (mean) magnetisation -- the actual observable."""
        return float(self.mx.mean()), float(self.my.mean()), float(self.mz.mean())

    def copy(self) -> "Ensemble":
        return Ensemble(self.n, self.dw.copy(), self.phi.copy(),
                          self.mx.copy(), self.my.copy(), self.mz.copy(), self.m0)


def step(ens: Ensemble, dt_ms: float, t_ms: float, T1_ms: float, T2_ms: float,
         mas_rate_khz: float = 0.0) -> None:
    """Advance the ensemble in place by dt_ms of free precession + relaxation.

    Under MAS, each isochromat's static offset is treated as the anisotropic
    part of its shift and modulated at the rotor rate (single-harmonic
    cos(omega_r t + phi) -- a simplified stand-in for the real two-harmonic
    (3cos^2(theta(t))-1) modulation of a spinning powder). This is exact for
    the static (non-spinning) case and a disclosed simplification under MAS.
    """
    if dt_ms <= 0:
        return
    decay_t2 = np.exp(-dt_ms / T2_ms)
    decay_t1 = np.exp(-dt_ms / T1_ms)

    if mas_rate_khz > 0:
        t_mid = t_ms + dt_ms / 2
        phase0 = 2 * np.pi * mas_rate_khz * t_mid
        dw_eff = ens.dw * np.cos(phase0 + ens.phi)
    else:
        dw_eff = ens.dw

    theta = dw_eff * dt_ms
    c, s = np.cos(theta), np.sin(theta)
    mx0, my0 = ens.mx, ens.my
    ens.mx = (mx0 * c + my0 * s) * decay_t2
    ens.my = (my0 * c - mx0 * s) * decay_t2
    ens.mz = ens.m0 + (ens.mz - ens.m0) * decay_t1


def run_free_precession(ens: Ensemble, duration_ms: float, T1_ms: float, T2_ms: float,
                          mas_rate_khz: float = 0.0, t0_ms: float = 0.0,
                          n_samples: int = 200) -> dict:
    """Evolve for `duration_ms`, recording `n_samples` snapshots of the vector
    sum (for plotting time traces). Returns dict of arrays: t, mz, mxy, mx, my."""
    dt = duration_ms / max(n_samples, 1)
    ts, mzs, mxys, mxs, mys = [], [], [], [], []
    t = t0_ms
    for _ in range(n_samples):
        step(ens, dt, t, T1_ms, T2_ms, mas_rate_khz)
        t += dt
        sx, sy, sz = ens.sum_m()
        ts.append(t); mzs.append(sz); mxys.append(np.hypot(sx, sy)); mxs.append(sx); mys.append(sy)
    return {"t": np.array(ts), "mz": np.array(mzs), "mxy": np.array(mxys),
            "mx": np.array(mxs), "my": np.array(mys)}


def rodrigues(m: np.ndarray, axis: np.ndarray, theta) -> np.ndarray:
    """Rotate vector(s) m (shape (...,3)) about unit axis (shape (...,3)) by
    angle theta (scalar or shape (...)). Standard Rodrigues rotation formula:
        m' = m*cos(theta) + (axis x m)*sin(theta) + axis*(axis.m)*(1-cos(theta))
    """
    c = np.cos(theta)[..., None] if np.ndim(theta) else np.cos(theta)
    s = np.sin(theta)[..., None] if np.ndim(theta) else np.sin(theta)
    dot = np.sum(axis * m, axis=-1, keepdims=True)
    cross = np.cross(axis, m)
    return m * c + cross * s + axis * dot * (1 - c)


def apply_pulse(ens: Ensemble, flip_deg: float, axis_phase_deg: float, nu1_khz: float,
                 shape: str = "hard", enhancement: float = 1.0, n_steps: int = 200) -> float:
    """Apply a finite-duration B1 pulse via the full effective-field rotation
    (B1 + each isochromat's own offset dw), in place. Returns the real pulse
    duration in ms.

    shape: "hard" (rectangular, constant amplitude) or "soft" (sin^2 envelope,
    which averages to exactly 0.5 of the peak amplitude over the pulse).
    enhancement: CT-selective nutation-rate enhancement factor (I+1/2 for a
    half-integer quadrupolar CT when the pulse bandwidth is much narrower than
    the satellite manifold; 1 otherwise). See ct_selective_enhancement().
    """
    flip_rad = np.radians(flip_deg)
    omega1_peak = 2 * np.pi * (nu1_khz * 1000) * enhancement  # rad/s
    avg_factor = 0.5 if shape == "soft" else 1.0
    duration_s = flip_rad / (omega1_peak * avg_factor)
    duration_ms = duration_s * 1000
    dt_ms = duration_ms / n_steps

    axis_phase = np.radians(axis_phase_deg)
    bx0, by0 = np.cos(axis_phase), np.sin(axis_phase)

    m = np.stack([ens.mx, ens.my, ens.mz], axis=-1)  # (N, 3)
    bz = ens.dw  # rad/ms, per isochromat -- constant across the pulse
    for s_idx in range(n_steps):
        frac = (s_idx + 0.5) / n_steps
        amp = np.sin(np.pi * frac) ** 2 if shape == "soft" else 1.0
        w1_ms = (omega1_peak * amp) / 1000  # rad/ms, scalar (same B1 for every isochromat)
        bx, by = bx0 * w1_ms, by0 * w1_ms
        bmag = np.sqrt(bx ** 2 + by ** 2 + bz ** 2)
        bmag_safe = np.where(bmag < 1e-12, 1.0, bmag)
        axis = np.stack([np.full_like(bz, bx), np.full_like(bz, by), bz], axis=-1) / bmag_safe[..., None]
        theta = bmag * dt_ms
        m = rodrigues(m, axis, theta)
    ens.mx, ens.my, ens.mz = m[..., 0], m[..., 1], m[..., 2]
    return duration_ms


def apply_dfs_sweep(ens: Ensemble, duration_ms: float, nu1_khz: float, sweep_range_khz: float,
                     n_steps: int = 240) -> None:
    """Double frequency sweep: constant-amplitude pulse whose RF frequency is
    linearly swept across +/-sweep_range_khz. Each isochromat crosses resonance
    (bz = dw - rf_offset(t) = 0) at a different instant during the sweep --
    the real adiabatic-passage mechanism DFS relies on to transfer satellite
    population into the central transition (Iuga et al., J. Magn. Reson. 147,
    192 (2000)).
    """
    omega1 = 2 * np.pi * (nu1_khz * 1000)  # rad/s
    dt_ms = duration_ms / n_steps
    w1_ms = omega1 / 1000
    m = np.stack([ens.mx, ens.my, ens.mz], axis=-1)
    for s_idx in range(n_steps):
        frac = (s_idx + 0.5) / n_steps
        rf_offset_rad_ms = 2 * np.pi * sweep_range_khz * (1 - 2 * frac)
        bz = ens.dw - rf_offset_rad_ms
        bmag = np.sqrt(w1_ms ** 2 + bz ** 2)
        axis = np.stack([np.full_like(bz, w1_ms), np.zeros_like(bz), bz], axis=-1) / bmag[..., None]
        theta = bmag * dt_ms
        m = rodrigues(m, axis, theta)
    ens.mx, ens.my, ens.mz = m[..., 0], m[..., 1], m[..., 2]
