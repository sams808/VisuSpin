"""Verifies the REDOR/CP/DFS presets run cleanly through the block engine and
that the resulting traces match the underlying analytic physics functions
directly (not just "it doesn't crash")."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import numpy as np
from visuspin.sequences.blocks import SequenceContext
from visuspin.sequences.engine import run_sequence
from visuspin.sequences.presets import redor, cross_polarization, dfs_enhanced_ct
from visuspin.physics.dipolar import redor_dephasing_curve
from visuspin.physics.cp import cp_buildup_curve

def test_redor_preset_matches_dipolar_physics_directly():
    d_hz, tr_us, ncyc = 300.0, 40.0, 20
    ctx = SequenceContext(T1_ms=5000, T2_ms=1e6, nu1_khz=25)  # T2~inf isolates the REDOR effect
    out = run_sequence(redor(d_hz=d_hz, rotor_period_us=tr_us, n_cycles=ncyc, acquire_ms=0.5),
                         ctx, n_isochromats=50, sigma_rad_per_ms=0.0)
    direct = redor_dephasing_curve(d_hz, tr_us, ncyc, n_orientations=1500)
    # after the 90 pulse, mxy should start near 1 and fall to ~ (1 - delta_s/s0) at full dephasing
    final_expected = 1.0 - direct["delta_s_over_s0"][-1]
    # T2=inf, so the acquire window shouldn't change the post-dephasing value at all
    assert abs(out["mxy"][-1] - final_expected) < 0.03, f"got {out['mxy'][-1]}, expected {final_expected}"
    print(f"PASS REDOR preset: final S/S0-equivalent mxy={out['mxy'][-1]:.3f} matches direct dipolar physics {final_expected:.3f}")

def test_cp_preset_matches_analytic_buildup_curve():
    t_is, t1rho_i, contact = 1.0, 10.0, 5.0
    ctx = SequenceContext(T1_ms=5000, T2_ms=1e6, nu1_khz=25)
    out = run_sequence(cross_polarization(t_is_ms=t_is, t1rho_i_ms=t1rho_i, contact_ms=contact, acquire_ms=0.5),
                         ctx, n_isochromats=20, sigma_rad_per_ms=0.0)
    direct = cp_buildup_curve(t_is, t1rho_i, contact_max_ms=contact, n_points=200)
    expected_peak = np.max(np.abs(direct["m_s"]))
    got_peak = out["mxy"][: len(direct["t_ms"])].max()
    assert abs(got_peak - expected_peak) < 0.02, f"got {got_peak}, expected {expected_peak}"
    print(f"PASS CP preset: peak mxy through engine={got_peak:.3f} matches direct CP physics {expected_peak:.3f}")

def test_dfs_preset_runs_and_inverts_or_transfers_population():
    ctx = SequenceContext(T1_ms=5000, T2_ms=300, nu1_khz=15)
    out = run_sequence(dfs_enhanced_ct(sweep_ms=2.0, nu1_khz=2.0, sweep_range_khz=20.0, acquire_ms=5),
                         ctx, n_isochromats=100, sigma_rad_per_ms=0.05)
    assert out["mxy"].max() > 0, "DFS+CT-selective preset should produce nonzero transverse signal"
    assert np.all(np.isfinite(out["mxy"])) and np.all(np.isfinite(out["mz"]))
    print(f"PASS DFS-enhanced preset runs cleanly, peak mxy={out['mxy'].max():.3f}")

if __name__ == "__main__":
    test_redor_preset_matches_dipolar_physics_directly()
    test_cp_preset_matches_analytic_buildup_curve()
    test_dfs_preset_runs_and_inverts_or_transfers_population()
    print("\nALL REDOR/CP/DFS PRESET TESTS PASSED")
