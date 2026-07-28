"""Runs an ordered list of Block objects through a fresh isochromat ensemble
and stitches together the resulting trace for plotting."""
from __future__ import annotations
import numpy as np

from ..physics.bloch import Ensemble
from .blocks import Block, SequenceContext, TraceSegment


def run_sequence(blocks: list[Block], ctx: SequenceContext, n_isochromats: int = 60,
                    sigma_rad_per_ms: float = 0.05, seed: int = 1234) -> dict:
    ens = Ensemble.from_gaussian_offsets(n_isochromats, sigma_rad_per_ms, seed=seed)
    t = 0.0
    all_t, all_mz, all_mxy, labels = [], [], [], []
    for b in blocks:
        segs = b.run(ens, ctx, t)
        for s in segs:
            all_t.append(s.t_ms); all_mz.append(s.mz); all_mxy.append(s.mxy)
            labels.append((t, b.label()))
        t += b.duration_estimate_ms(ctx)
    t_arr = np.concatenate(all_t) if all_t else np.array([0.0])
    mz_arr = np.concatenate(all_mz) if all_mz else np.array([1.0])
    mxy_arr = np.concatenate(all_mxy) if all_mxy else np.array([0.0])
    return {"t_ms": t_arr, "mz": mz_arr, "mxy": mxy_arr, "block_starts": labels,
            "total_duration_ms": t, "final_ensemble": ens}
