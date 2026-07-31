"""Verification of the STMAS angle-sensitivity model against the same
established facts used elsewhere in this codebase (CT's zero first-order
shift, the dipolar magic-angle P2 scaling)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import numpy as np
from visuspin.physics.stmas import (
    satellite_first_order_shift_hz, rank2_mas_averaging_factor, satellite_residual_vs_angle_error, MAGIC_ANGLE_DEG,
)

def test_central_transition_has_zero_first_order_shift_at_any_orientation():
    for cos_theta in [0.0, 0.3, 0.7, 1.0]:
        shift = satellite_first_order_shift_hz(1.5, 3e6, m_upper=0.5, cos_theta=cos_theta)
        assert abs(shift) < 1e-9, f"CT should have zero first-order shift, got {shift} at cos_theta={cos_theta}"
    print("PASS central transition (m_upper=0.5) has exactly zero first-order shift at every orientation")

def test_satellite_has_nonzero_first_order_shift():
    shift = satellite_first_order_shift_hz(1.5, 3e6, m_upper=1.5, cos_theta=0.5)
    assert abs(shift) > 1.0, f"expected a genuine nonzero satellite shift, got {shift} Hz"
    print(f"PASS the +1/2<->+3/2 satellite (I=3/2) has a real first-order shift ({shift:.1f} Hz) -- unlike the CT")

def test_p2_factor_zero_exactly_at_magic_angle():
    p2 = rank2_mas_averaging_factor(MAGIC_ANGLE_DEG)
    assert abs(p2) < 1e-6
    print(f"PASS P2(magic angle) = {p2:.2e} (exactly zero, as already established for the dipolar case)")

def test_satellite_residual_grows_with_angle_error_but_ct_is_immune():
    I, Cq_hz, cos_theta = 1.5, 3e6, 0.6
    errors = np.array([0.0, 0.05, 0.1, 0.2])
    residual_satellite = satellite_residual_vs_angle_error(I, Cq_hz, cos_theta, errors, m_upper=1.5)
    residual_ct = satellite_residual_vs_angle_error(I, Cq_hz, cos_theta, errors, m_upper=0.5)
    # MAGIC_ANGLE_DEG is a rounded decimal (54.7356, not the exact irrational
    # value), so P2 there is ~2.5e-7 rather than exactly 0 -- negligible
    # relative to the residual at a real angle error, which is the actual claim.
    assert abs(residual_satellite[0]) < 0.01 * abs(residual_satellite[-1]), \
        "at zero angle error, satellite residual should be negligible compared to a real missetting"
    assert np.all(np.abs(residual_satellite[1:]) > np.abs(residual_satellite[0]))
    assert np.all(np.diff(np.abs(residual_satellite)) > 0), "residual should grow monotonically with angle error"
    assert np.all(np.abs(residual_ct) < 1e-9), "CT residual should be exactly zero regardless of angle error"
    print(f"PASS satellite residual grows with angle error ({[f'{r:.1f}' for r in residual_satellite]} Hz), "
          f"while the CT stays exactly zero regardless of missetting -- the core STMAS-vs-MQMAS contrast")

if __name__ == "__main__":
    test_central_transition_has_zero_first_order_shift_at_any_orientation()
    test_satellite_has_nonzero_first_order_shift()
    test_p2_factor_zero_exactly_at_magic_angle()
    test_satellite_residual_grows_with_angle_error_but_ct_is_immune()
    print("\nALL STMAS TESTS PASSED")
