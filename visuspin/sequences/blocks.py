"""
Generic pulse-sequence building blocks -- the "Scratch for pulse sequences"
idea: Hahn echo, CPMG, spin-locking/T1rho, and DFS-based sequences are all just
different orderings/parameterisations of a handful of primitive blocks acting
on the same single-spin isochromat ensemble (visuspin.physics.bloch), rather
than bespoke code per named sequence.

Each block is a small dataclass with a `.run(ens, ctx)` method that advances
the ensemble in place and returns a list of TraceSegment for plotting/replay.
`ctx` is a SequenceContext carrying the shared parameters (T1, T2, nu1, MAS
rate, ...) so blocks stay lightweight and composable.
"""
from __future__ import annotations
from dataclasses import dataclass, field
import numpy as np

from ..physics import bloch


@dataclass
class SequenceContext:
    T1_ms: float
    T2_ms: float
    mas_rate_khz: float = 0.0
    nu1_khz: float = 25.0
    pulse_shape: str = "hard"
    enhancement: float = 1.0  # CT-selective nutation enhancement, if applicable


@dataclass
class TraceSegment:
    label: str
    t_ms: np.ndarray
    mz: np.ndarray
    mxy: np.ndarray


class Block:
    """Base class. `name` is shown in the composer palette; `params` lists
    (key, default, min, max, step, unit) tuples for auto-generated UI controls."""
    name = "block"
    params: list[tuple] = []

    def __init__(self, **kwargs):
        self.values = {k: kwargs.get(k, default) for (k, default, *_ ) in self.params}

    def run(self, ens: "bloch.Ensemble", ctx: SequenceContext, t0_ms: float) -> list[TraceSegment]:
        raise NotImplementedError

    def duration_estimate_ms(self, ctx: SequenceContext) -> float:
        return 0.0

    def label(self) -> str:
        return self.name


class Pulse(Block):
    name = "Pulse"
    params = [("flip_deg", 90.0, 0, 360, 1, "deg"),
              ("axis_deg", 0.0, 0, 360, 1, "deg (0=x, 90=y)")]

    def run(self, ens, ctx, t0_ms):
        bloch.apply_pulse(ens, self.values["flip_deg"], self.values["axis_deg"],
                            ctx.nu1_khz, ctx.pulse_shape, ctx.enhancement)
        sx, sy, sz = ens.sum_m()
        return [TraceSegment(f"{self.values['flip_deg']:.0f} deg pulse",
                                np.array([t0_ms]), np.array([sz]), np.array([np.hypot(sx, sy)]))]


class Delay(Block):
    name = "Delay"
    params = [("duration_ms", 5.0, 0.001, 5000, 0.1, "ms")]

    def run(self, ens, ctx, t0_ms):
        dur = self.values["duration_ms"]
        n = max(10, int(dur / max(ctx.T2_ms / 200, 0.01)))
        n = min(n, 4000)
        out = bloch.run_free_precession(ens, dur, ctx.T1_ms, ctx.T2_ms, ctx.mas_rate_khz,
                                           t0_ms=t0_ms, n_samples=n)
        return [TraceSegment("delay", out["t"], out["mz"], out["mxy"])]

    def duration_estimate_ms(self, ctx):
        return self.values["duration_ms"]


class Loop(Block):
    """Repeats a sub-list of blocks N times (CPMG echo trains, rotor-
    synchronised REDOR dephasing periods, ...)."""
    name = "Loop"
    params = [("n_repeats", 4, 1, 200, 1, "times")]

    def __init__(self, body: list[Block] | None = None, **kwargs):
        super().__init__(**kwargs)
        self.body = body or []

    def run(self, ens, ctx, t0_ms):
        segs = []
        t = t0_ms
        for _ in range(int(self.values["n_repeats"])):
            for b in self.body:
                new_segs = b.run(ens, ctx, t)
                segs.extend(new_segs)
                t += b.duration_estimate_ms(ctx)
        return segs

    def duration_estimate_ms(self, ctx):
        return self.values["n_repeats"] * sum(b.duration_estimate_ms(ctx) for b in self.body)

    def label(self):
        return f"Loop x{int(self.values['n_repeats'])}"


class SpinLock(Block):
    """Spin-locking for a T1rho measurement: magnetisation held along the
    effective B1 axis decays with time constant T1rho (set independently from
    T2, since rotating-frame relaxation probes different, typically slower,
    motions -- Look & Lowe, J. Chem. Phys. 44, 2995 (1966))."""
    name = "Spin-lock (T1rho)"
    params = [("duration_ms", 5.0, 0.01, 500, 0.1, "ms"),
              ("T1rho_ms", 20.0, 0.1, 5000, 0.1, "ms")]

    def run(self, ens, ctx, t0_ms):
        dur, t1rho = self.values["duration_ms"], self.values["T1rho_ms"]
        n = 100
        t = np.linspace(0, dur, n)
        sx0, sy0, sz0 = ens.sum_m()
        mxy0 = np.hypot(sx0, sy0)
        mxy = mxy0 * np.exp(-t / t1rho)
        scale = np.where(mxy0 > 1e-12, mxy / max(mxy0, 1e-12), 0.0)
        ens.mx *= np.exp(-dur / t1rho)
        ens.my *= np.exp(-dur / t1rho)
        return [TraceSegment("spin-lock", t + t0_ms, np.full(n, ens.mz.mean()), mxy)]

    def duration_estimate_ms(self, ctx):
        return self.values["duration_ms"]


class Acquire(Block):
    """Marks the acquisition window; doesn't change the physics, just tags
    the trace for the UI/diagram."""
    name = "Acquire"
    params = [("duration_ms", 20.0, 0.1, 2000, 0.1, "ms")]

    def run(self, ens, ctx, t0_ms):
        return Delay(duration_ms=self.values["duration_ms"]).run(ens, ctx, t0_ms)

    def duration_estimate_ms(self, ctx):
        return self.values["duration_ms"]


class Recouple(Block):
    """Rotor-synchronised dipolar recoupling period (REDOR: Gullion & Schaefer,
    J. Magn. Reson. 81, 196 (1989)). The single-isochromat Bloch ensemble used
    elsewhere has no heteronuclear-dipolar term, so this block does not evolve
    `ens` under a coupling Hamiltonian; instead it multiplies the ensemble's
    current transverse signal by the powder-averaged REDOR dephasing envelope
    S/S0(t) from visuspin.physics.dipolar.redor_dephasing_curve -- the same
    "swap in the analytic result" pattern used for CSA/quadrupolar/sideband
    lineshapes elsewhere in VisuSpin. Valid as the sole coherence-decay
    mechanism within a preset (not meant to be interleaved with unrelated
    free-precession segments in the same trace)."""
    name = "REDOR recoupling"
    params = [("d_hz", 200.0, 1, 5000, 1, "Hz"),
              ("rotor_period_us", 50.0, 1, 1000, 1, "us"),
              ("n_cycles", 32, 1, 400, 1, "rotor cycles")]

    def run(self, ens, ctx, t0_ms):
        from ..physics.dipolar import redor_dephasing_curve
        d_hz, tr_us, ncyc = self.values["d_hz"], self.values["rotor_period_us"], int(self.values["n_cycles"])
        curve = redor_dephasing_curve(d_hz, tr_us, ncyc, n_orientations=1500)
        sx0, sy0, sz0 = ens.sum_m()
        mxy0 = np.hypot(sx0, sy0)
        s_over_s0 = 1.0 - curve["delta_s_over_s0"]
        mxy = mxy0 * s_over_s0
        ens.mx = ens.mx * s_over_s0[-1]
        ens.my = ens.my * s_over_s0[-1]
        return [TraceSegment("REDOR dephasing", curve["dephasing_time_ms"] + t0_ms,
                                np.full(len(mxy), ens.mz.mean()), mxy)]

    def duration_estimate_ms(self, ctx):
        return self.values["n_cycles"] * self.values["rotor_period_us"] / 1000.0


class CrossPolarize(Block):
    """Hartmann-Hahn cross-polarization contact (Pines, Gibby & Waugh, J.
    Chem. Phys. 59, 569 (1973)). Generates the dilute-spin transverse signal
    directly from the analytic buildup/decay curve
    (visuspin.physics.cp.cp_buildup_curve) rather than evolving `ens` under a
    two-spin transfer Hamiltonian the single-isochromat model doesn't have."""
    name = "Cross-polarize"
    params = [("t_is_ms", 1.0, 0.01, 20, 0.01, "ms"),
              ("t1rho_i_ms", 10.0, 0.1, 500, 0.1, "ms"),
              ("contact_ms", 2.0, 0.01, 20, 0.01, "ms")]

    def run(self, ens, ctx, t0_ms):
        from ..physics.cp import cp_buildup_curve
        t_is, t1rho_i, contact = self.values["t_is_ms"], self.values["t1rho_i_ms"], self.values["contact_ms"]
        curve = cp_buildup_curve(t_is, t1rho_i, contact_max_ms=contact, n_points=200)
        m_final = curve["m_s"][-1]
        ens.mx = np.full(ens.n, m_final)
        ens.my = np.zeros(ens.n)
        return [TraceSegment("CP contact", curve["t_ms"] + t0_ms,
                                np.full(len(curve["m_s"]), ens.mz.mean()), np.abs(curve["m_s"]))]

    def duration_estimate_ms(self, ctx):
        return self.values["contact_ms"]


class DFSSweep(Block):
    """Double frequency sweep -- adiabatic satellite-to-central-transition
    population transfer for half-integer quadrupolar nuclei (Iuga et al., J.
    Magn. Reson. 147, 192 (2000)). Thin wrapper around
    visuspin.physics.bloch.apply_dfs_sweep."""
    name = "DFS sweep"
    params = [("duration_ms", 2.0, 0.01, 50, 0.01, "ms"),
              ("nu1_khz", 25.0, 0.1, 200, 0.1, "kHz"),
              ("sweep_range_khz", 100.0, 1, 2000, 1, "kHz")]

    def run(self, ens, ctx, t0_ms):
        from ..physics.bloch import apply_dfs_sweep
        apply_dfs_sweep(ens, self.values["duration_ms"], self.values["nu1_khz"], self.values["sweep_range_khz"])
        sx, sy, sz = ens.sum_m()
        return [TraceSegment("DFS sweep", np.array([t0_ms + self.values["duration_ms"]]),
                                np.array([sz]), np.array([np.hypot(sx, sy)]))]

    def duration_estimate_ms(self, ctx):
        return self.values["duration_ms"]
