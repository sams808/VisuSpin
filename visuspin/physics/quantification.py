"""
Quantification pitfalls: the practical gotchas that make peak areas/heights
NOT directly proportional to true site populations unless accounted for.
Reuses visuspin.physics.cp (CP transfer bias) and visuspin.physics.sidebands
(sideband intensity redistribution) directly; the only new physics here is
the T1 saturation-recovery signal.
"""
from __future__ import annotations
import numpy as np


def saturation_recovery_signal(recycle_delay_ms: float, T1_ms: float) -> float:
    """Fraction of full equilibrium magnetization available at the start of
    a scan after only `recycle_delay_ms` of T1 recovery since the last
    pulse: M(t)/M0 = 1 - exp(-t/T1). A recycle delay much shorter than T1
    systematically undercounts that site relative to faster-relaxing ones."""
    return 1.0 - np.exp(-recycle_delay_ms / T1_ms)
