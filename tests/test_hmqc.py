"""Verification of the HMQC transfer-efficiency function and 2D correlation map."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import numpy as np
from visuspin.physics.hmqc import mq_transfer_efficiency, optimal_tau_ms, hmqc_spectrum

def test_transfer_efficiency_zero_at_tau_zero_and_one_over_J():
    J = 140.0  # Hz, typical 1-bond CH J-coupling
    assert abs(mq_transfer_efficiency(J, 0.0)) < 1e-9
    assert abs(mq_transfer_efficiency(J, 1000.0 / J)) < 1e-9
    print(f"PASS transfer efficiency is exactly zero at tau=0 and tau=1/J={1000/J:.3f} ms")

def test_transfer_efficiency_maximal_at_optimal_tau():
    J = 140.0
    tau_opt = optimal_tau_ms(J)
    eff = mq_transfer_efficiency(J, tau_opt)
    assert abs(eff - 1.0) < 1e-9, f"expected efficiency 1.0 at tau_opt, got {eff}"
    assert abs(tau_opt - 1000.0/(2*J)) < 1e-9
    print(f"PASS transfer efficiency = {eff:.6f} (exactly 1.0) at optimal tau={tau_opt:.3f} ms = 1/(2J)")

def test_dipolar_coupling_uses_same_function_different_scale():
    # D-HMQC: a much larger effective coupling (kHz-scale recoupled dipolar)
    # means the optimal tau is much shorter than for a J-coupled pair
    D_hz = 3000.0
    J_hz = 140.0
    assert optimal_tau_ms(D_hz) < optimal_tau_ms(J_hz) / 10
    print(f"PASS D-coupling (large, {D_hz} Hz) needs a much shorter optimal tau "
          f"({optimal_tau_ms(D_hz):.4f} ms) than J-coupling ({optimal_tau_ms(J_hz):.3f} ms)")

def test_2d_spectrum_peaks_land_at_correct_shifts():
    sites = [{"shift_i_hz": 500.0, "shift_s_hz": -1200.0, "amplitude": 1.0},
             {"shift_i_hz": -800.0, "shift_s_hz": 600.0, "amplitude": 0.6}]
    J = 140.0
    tau = optimal_tau_ms(J)
    spec = hmqc_spectrum(sites, J, tau, f1_range_hz=(-2000, 2000), f2_range_hz=(-2000, 2000),
                           linewidth_hz=50, n_points=300)
    assert abs(spec["efficiency"] - 1.0) < 1e-9
    peak_idx = np.unravel_index(np.argmax(spec["intensity"]), spec["intensity"].shape)
    f1_peak = spec["f1_hz"][peak_idx[0]]
    f2_peak = spec["f2_hz"][peak_idx[1]]
    assert abs(f1_peak - (-1200.0)) < 20, f"F1 peak at {f1_peak}, expected near -1200"
    assert abs(f2_peak - 500.0) < 20, f"F2 peak at {f2_peak}, expected near 500 (largest-amplitude site)"
    print(f"PASS 2D HMQC peak found at (F1={f1_peak:.0f}, F2={f2_peak:.0f}) Hz, "
          f"matches the larger-amplitude site's (shift_s, shift_i) = (-1200, 500)")

def test_zero_tau_gives_no_correlation_signal():
    sites = [{"shift_i_hz": 100.0, "shift_s_hz": 100.0, "amplitude": 1.0}]
    spec = hmqc_spectrum(sites, 140.0, 0.0, n_points=100)
    assert np.max(spec["intensity"]) < 1e-9
    print("PASS tau=0 correctly produces zero HMQC signal (no time for MQ coherence to develop)")

if __name__ == "__main__":
    test_transfer_efficiency_zero_at_tau_zero_and_one_over_J()
    test_transfer_efficiency_maximal_at_optimal_tau()
    test_dipolar_coupling_uses_same_function_different_scale()
    test_2d_spectrum_peaks_land_at_correct_shifts()
    test_zero_tau_gives_no_correlation_signal()
    print("\nALL HMQC TESTS PASSED")
