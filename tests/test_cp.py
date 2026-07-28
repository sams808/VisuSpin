"""Verification of the CP buildup/decay curve against known limiting behaviour."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import numpy as np
from visuspin.physics.cp import cp_buildup_curve

def test_fast_transfer_gives_near_pure_T1rho_I_decay():
    # T_IS << T1rho_I -> magnetisation transfers almost instantly, then just
    # decays with T1rho_I from (almost) full amplitude
    t1rho_i = 15.0
    out = cp_buildup_curve(t_is_ms=0.05, t1rho_i_ms=t1rho_i, contact_max_ms=30, n_points=600)
    assert out["valid_regime"]
    t, m = out["t_ms"], out["m_s"]
    # away from the very start (t >> T_IS), should match exp(-t/T1rho_I) closely
    mask = t > 1.0
    predicted = np.exp(-t[mask] / t1rho_i)
    resid = np.max(np.abs(m[mask] - predicted))
    assert resid < 0.03, f"residual {resid} too large vs pure T1rho_I decay"
    print(f"PASS fast-transfer CP curve matches exp(-t/T1rho_I) away from t=0, max residual {resid:.4f}")

def test_initial_slope_positive_in_valid_regime():
    out = cp_buildup_curve(t_is_ms=2.0, t1rho_i_ms=15.0, contact_max_ms=20, n_points=2000)
    assert out["valid_regime"]
    t, m = out["t_ms"], out["m_s"]
    assert m[5] > m[1] > 0, "signal should build up from zero at short contact times"
    assert out["optimal_contact_ms"] > 0
    print(f"PASS buildup regime: signal rises from 0, optimal contact time = {out['optimal_contact_ms']:.2f} ms, "
          f"peak = {out['peak_signal']:.3f}")

def test_slow_transfer_flagged_invalid():
    out = cp_buildup_curve(t_is_ms=20.0, t1rho_i_ms=10.0, contact_max_ms=20)
    assert not out["valid_regime"], "T_IS >= T1rho_I should be flagged as outside the standard CP regime"
    print("PASS T_IS >= T1rho_I correctly flagged as outside the standard CP transfer regime")

if __name__ == "__main__":
    test_fast_transfer_gives_near_pure_T1rho_I_decay()
    test_initial_slope_positive_in_valid_regime()
    test_slow_transfer_flagged_invalid()
    print("\nALL CP TESTS PASSED")
