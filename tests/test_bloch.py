"""Direct verification of the core Bloch physics -- mirrors the manual checks
done on the JS prototype (exact 90x rotation, T1/T2 decay rates, pulse duration
formula) so the Python port is held to the same rigor."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import numpy as np
from visuspin.physics.bloch import Ensemble, step, apply_pulse, run_free_precession, apply_dfs_sweep

def test_90x_pulse_on_resonance():
    ens = Ensemble.from_gaussian_offsets(60, sigma_rad_per_ms=0.0)  # all on-resonance
    dur = apply_pulse(ens, flip_deg=90, axis_phase_deg=0, nu1_khz=25, shape="hard")
    sx, sy, sz = ens.sum_m()
    assert abs(sx) < 1e-9 and abs(sy - (-1.0)) < 1e-9 and abs(sz) < 1e-9, (sx, sy, sz)
    expected_us = (np.pi/2) / (2*np.pi*25000) * 1e6
    assert abs(dur*1000 - expected_us) < 1e-6, (dur*1000, expected_us)
    print("PASS 90x on-resonance: M -> (0,-1,0), duration matches analytic formula")

def test_180x_and_180y_signs():
    ens = Ensemble.from_gaussian_offsets(1, sigma_rad_per_ms=0.0)
    ens.mx[:] = 0; ens.my[:] = 0; ens.mz[:] = 1
    apply_pulse(ens, 180, 0, nu1_khz=25, shape="hard")
    assert abs(ens.mx[0]) < 1e-6 and abs(ens.my[0]) < 1e-6 and abs(ens.mz[0]+1) < 1e-6
    ens2 = Ensemble.from_gaussian_offsets(1, sigma_rad_per_ms=0.0)
    ens2.mx[:] = 0; ens2.my[:] = 0; ens2.mz[:] = 1
    apply_pulse(ens2, 180, 90, nu1_khz=25, shape="hard")
    assert abs(ens2.mx[0]) < 1e-6 and abs(ens2.my[0]) < 1e-6 and abs(ens2.mz[0]+1) < 1e-6
    print("PASS 180x/180y both correctly invert +z -> -z")

def test_T2_T1_decay_rates():
    ens = Ensemble.from_gaussian_offsets(200, sigma_rad_per_ms=0.0)  # no dephasing -> pure T1/T2
    apply_pulse(ens, 90, 0, nu1_khz=25, shape="hard")
    T1, T2 = 700.0, 300.0
    out = run_free_precession(ens, duration_ms=300, T1_ms=T1, T2_ms=T2, n_samples=300)
    mxy_pred = np.exp(-out["t"]/T2)
    mz_pred = 1 - np.exp(-out["t"]/T1)
    assert np.max(np.abs(out["mxy"] - mxy_pred)) < 1e-8
    assert np.max(np.abs(out["mz"] - mz_pred)) < 1e-8
    print("PASS T2/T1 decay exactly matches analytic exp(-t/T2), 1-exp(-t/T1)")

def test_dephasing_develops_and_matches_T2star_regime():
    sigma = 0.08  # rad/ms
    ens = Ensemble.from_gaussian_offsets(400, sigma_rad_per_ms=sigma, seed=7)
    apply_pulse(ens, 90, 0, nu1_khz=25, shape="hard")
    T1, T2 = 5000.0, 5000.0  # long, so decay is dominated by dephasing not relaxation
    T2star = 1/(1/T2 + sigma/2)
    out = run_free_precession(ens, duration_ms=2*T2star, T1_ms=T1, T2_ms=T2, n_samples=400)
    # observed decay should be much faster than intrinsic T2 (since isochromats dephase)
    assert out["mxy"][-1] < np.exp(-out["t"][-1]/T2) * 0.5
    print(f"PASS dephasing: observed Mxy({out['t'][-1]:.0f}ms)={out['mxy'][-1]:.3f} "
          f"<< exp(-t/T2)={np.exp(-out['t'][-1]/T2):.3f} (T2* effect confirmed)")

def test_ct_selective_enhancement_gives_shorter_pulse():
    ens1 = Ensemble.from_gaussian_offsets(10, sigma_rad_per_ms=0.0)
    d_normal = apply_pulse(ens1, 90, 0, nu1_khz=25, shape="hard", enhancement=1.0)
    ens2 = Ensemble.from_gaussian_offsets(10, sigma_rad_per_ms=0.0)
    d_enhanced = apply_pulse(ens2, 90, 0, nu1_khz=25, shape="hard", enhancement=3.0)  # I=5/2 CT
    assert abs(d_enhanced - d_normal/3.0) < 1e-9
    sx, sy, sz = ens2.sum_m()
    assert abs(sy+1) < 1e-9  # still a clean 90 deg rotation, just faster
    print("PASS CT-selective enhancement=3.0 gives exactly 1/3 the pulse duration, same clean rotation")

def test_dfs_produces_substantial_inversion():
    # Adiabaticity requires nu1 << sweep range (a realistic DFS regime -- a
    # relatively weak, slowly-swept B1 traversing a wide frequency range one
    # local resonance at a time). nu1 ~ sweep range, tried first, gave poor
    # inversion (~0.73) because a strong B1 comparable to the whole sweep
    # range just produces ordinary Rabi nutation, not a sequence of adiabatic
    # passages -- a test-parameter lesson, not a code bug: the corrected
    # regime below satisfies the Landau-Zener adiabatic limit by ~19 e-foldings.
    ens = Ensemble.from_gaussian_offsets(200, sigma_rad_per_ms=1.5, seed=3)
    apply_dfs_sweep(ens, duration_ms=20, nu1_khz=2, sweep_range_khz=20.0)
    sx, sy, sz = ens.sum_m()
    assert sz < -0.7, f"expected substantial adiabatic inversion, got mz={sz}"
    print(f"PASS DFS sweep (nu1 << sweep range, proper adiabatic regime): mz={sz:.3f}")

def test_dfs_fails_when_not_adiabatic():
    # Sanity check on the failure mode itself: nu1 >= sweep range should NOT
    # give clean inversion (confirms the adiabaticity boundary is real, not
    # that the passing test above is a coincidence).
    ens = Ensemble.from_gaussian_offsets(200, sigma_rad_per_ms=1.5, seed=3)
    apply_dfs_sweep(ens, duration_ms=20, nu1_khz=10, sweep_range_khz=3.0)
    sx, sy, sz = ens.sum_m()
    assert sz > -0.5, f"expected the NON-adiabatic regime to fail to invert, got mz={sz}"
    print(f"PASS non-adiabatic regime (nu1 ~ sweep range) correctly fails to invert: mz={sz:.3f}")

if __name__ == "__main__":
    test_90x_pulse_on_resonance()
    test_180x_and_180y_signs()
    test_T2_T1_decay_rates()
    test_dephasing_develops_and_matches_T2star_regime()
    test_ct_selective_enhancement_gives_shorter_pulse()
    test_dfs_produces_substantial_inversion()
    test_dfs_fails_when_not_adiabatic()
    print("\nALL BLOCH PHYSICS TESTS PASSED")
