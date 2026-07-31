"""Verification of the DQ-SQ correlation map: peak placement for auto-peaks
(a spin coupled to a chemically-identical neighbor) vs cross-peaks (distinct
shifts), and correct reuse of HMQC's transfer-efficiency function."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import numpy as np
from visuspin.physics.dqsq import dqsq_spectrum
from visuspin.physics.hmqc import mq_transfer_efficiency, optimal_tau_ms

def test_auto_peak_lands_on_the_dq_diagonal():
    # a spin coupled to a chemically identical neighbor (same shift) should
    # give exactly one peak, at (F1=2*shift, F2=shift) -- on the diagonal
    D = 3000.0
    tau = optimal_tau_ms(D)
    pairs = [{"shift_a_hz": 1000.0, "shift_b_hz": 1000.0, "amplitude": 1.0}]
    spec = dqsq_spectrum(pairs, D, tau, linewidth_hz=40.0, n_points=300)
    idx = np.unravel_index(np.argmax(spec["intensity"]), spec["intensity"].shape)
    f1_peak, f2_peak = spec["f1_hz"][idx[0]], spec["f2_hz"][idx[1]]
    assert abs(f1_peak - 2000.0) < 25, f"expected F1~2000, got {f1_peak}"
    assert abs(f2_peak - 1000.0) < 25, f"expected F2~1000, got {f2_peak}"
    assert abs(f1_peak - 2 * f2_peak) < 25, "auto-peak should land on the F1=2*F2 diagonal"
    print(f"PASS auto-peak (identical neighbor shifts) lands on the DQ diagonal at "
          f"(F1={f1_peak:.0f}, F2={f2_peak:.0f}) = (2xF2, F2)")

def test_cross_peak_gives_two_symmetric_off_diagonal_peaks():
    D = 3000.0
    tau = optimal_tau_ms(D)
    pairs = [{"shift_a_hz": -800.0, "shift_b_hz": 600.0, "amplitude": 1.0}]
    spec = dqsq_spectrum(pairs, D, tau, linewidth_hz=40.0, n_points=300)
    dq_expected = -800.0 + 600.0
    # find both local maxima along the DQ row nearest dq_expected
    f1_idx = np.argmin(np.abs(spec["f1_hz"] - dq_expected))
    row = spec["intensity"][f1_idx, :]
    peaks_f2 = []
    for i in range(2, len(row) - 2):
        if row[i] > 0.3 * row.max() and row[i] >= row[i - 1] and row[i] >= row[i + 1]:
            peaks_f2.append(spec["f2_hz"][i])
    assert len(peaks_f2) == 2, f"expected 2 cross-peaks at F1~{dq_expected}, found {len(peaks_f2)}"
    found = sorted(peaks_f2)
    assert abs(found[0] - (-800.0)) < 25 and abs(found[1] - 600.0) < 25
    print(f"PASS distinct-shift pair gives two cross-peaks at F2={found[0]:.0f} and F2={found[1]:.0f}, "
          f"both at F1={dq_expected:.0f} (the DQ sum)")

def test_reuses_hmqc_transfer_efficiency_exactly():
    D, tau = 2500.0, 0.15
    pairs = [{"shift_a_hz": 100.0, "shift_b_hz": 100.0, "amplitude": 1.0}]
    spec = dqsq_spectrum(pairs, D, tau)
    assert spec["efficiency"] == mq_transfer_efficiency(D, tau)
    print(f"PASS dqsq_spectrum's efficiency ({spec['efficiency']:.4f}) is exactly "
          f"hmqc.mq_transfer_efficiency's output -- same underlying physics, reused not duplicated")

if __name__ == "__main__":
    test_auto_peak_lands_on_the_dq_diagonal()
    test_cross_peak_gives_two_symmetric_off_diagonal_peaks()
    test_reuses_hmqc_transfer_efficiency_exactly()
    print("\nALL DQ-SQ TESTS PASSED")
