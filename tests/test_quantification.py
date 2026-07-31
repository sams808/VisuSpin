"""Verification of the saturation-recovery formula against known limits."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import numpy as np
from visuspin.physics.quantification import saturation_recovery_signal

def test_zero_delay_gives_zero_signal():
    assert saturation_recovery_signal(0.0, 500.0) == 0.0
    print("PASS recycle_delay=0 gives exactly zero signal")

def test_long_delay_gives_full_signal():
    s = saturation_recovery_signal(10000.0, 500.0)
    assert abs(s - 1.0) < 1e-8
    print(f"PASS recycle_delay >> T1 gives signal -> 1.0 (got {s:.6f})")

def test_delay_equal_to_T1_ln2_gives_half_signal():
    T1 = 500.0
    s = saturation_recovery_signal(T1 * np.log(2), T1)
    assert abs(s - 0.5) < 1e-8
    print(f"PASS recycle_delay = T1*ln(2) gives exactly half signal (got {s:.6f})")

def test_shorter_T1_recovers_faster_at_fixed_delay():
    delay = 200.0
    fast = saturation_recovery_signal(delay, T1_ms=100.0)
    slow = saturation_recovery_signal(delay, T1_ms=2000.0)
    assert fast > slow
    print(f"PASS at a fixed short recycle delay, short-T1 site ({fast:.3f}) recovers more "
          f"fully than long-T1 site ({slow:.3f}) -- the source of T1-saturation bias")

if __name__ == "__main__":
    test_zero_delay_gives_zero_signal()
    test_long_delay_gives_full_signal()
    test_delay_equal_to_T1_ln2_gives_half_signal()
    test_shorter_T1_recovers_faster_at_fixed_delay()
    print("\nALL QUANTIFICATION TESTS PASSED")
