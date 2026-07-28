"""
Powder-averaging utilities: sampling crystallite orientations uniformly over
the unit sphere (or a suitable irreducible fraction), and turning a per-
orientation frequency function into a histogram (static powder lineshape).

For an axially symmetric interaction (no dependence on the azimuthal angle
phi), sampling cos(theta) uniformly on [-1, 1] alone gives the correct
solid-angle-weighted orientation distribution. For a general (biaxial, eta!=0)
interaction, both theta and phi matter and we sample the full sphere.
"""
from __future__ import annotations
import numpy as np


def sample_axially_symmetric(n: int, rng: np.random.Generator) -> np.ndarray:
    """cos(theta), uniform on [-1, 1] -- correct powder weighting when the
    interaction only depends on theta (eta = 0)."""
    return rng.uniform(-1.0, 1.0, n)


def sample_full_sphere(n: int, rng: np.random.Generator) -> tuple[np.ndarray, np.ndarray]:
    """(cos(theta), phi) uniformly distributed over the sphere -- needed when
    the interaction depends on the asymmetry parameter eta (biaxial case)."""
    cos_theta = rng.uniform(-1.0, 1.0, n)
    phi = rng.uniform(0.0, 2 * np.pi, n)
    return cos_theta, phi


def histogram_pattern(values: np.ndarray, n_bins: int = 400,
                        value_range: tuple[float, float] | None = None) -> tuple[np.ndarray, np.ndarray]:
    """Bin a set of sampled frequency/shift values into a normalised (0-1
    peak) lineshape. Returns (bin_centers, intensity)."""
    if value_range is None:
        vmax = np.max(np.abs(values)) if len(values) else 1.0
        value_range = (-vmax, vmax)
    counts, edges = np.histogram(values, bins=n_bins, range=value_range)
    centers = 0.5 * (edges[:-1] + edges[1:])
    if counts.max() > 0:
        counts = counts / counts.max()
    return centers, counts.astype(float)


def orientation_marker(cos_theta: float, phi: float = 0.0) -> np.ndarray:
    """Unit vector for a single crystallite orientation, for the 3D
    powder-averaging visualizer (module 9)."""
    sin_theta = np.sqrt(max(0.0, 1 - cos_theta ** 2))
    return np.array([sin_theta * np.cos(phi), sin_theta * np.sin(phi), cos_theta])


def powder_visualization_data(shift_fn, n_samples: int = 2000, seed: int = 13,
                                 n_bins: int = 300) -> dict:
    """3D powder-averaging teaching data: samples crystallite orientations
    over the full sphere, evaluates `shift_fn(cos_theta, phi) -> shift`
    (e.g. visuspin.physics.csa.csa_shift) at each one, and returns both the
    3D unit-vector coordinates (for a colour-mapped sphere scatter) and the
    resulting powder histogram -- so a UI can show, side by side, *which*
    crystallite orientations produce *which* part of the powder pattern."""
    rng = np.random.default_rng(seed)
    cos_theta, phi = sample_full_sphere(n_samples, rng)
    sin_theta = np.sqrt(np.clip(1 - cos_theta ** 2, 0.0, 1.0))
    x = sin_theta * np.cos(phi)
    y = sin_theta * np.sin(phi)
    z = cos_theta
    shift = shift_fn(cos_theta, phi)
    hist_x, hist_y = histogram_pattern(shift, n_bins=n_bins)
    return {"x": x, "y": y, "z": z, "shift": shift, "hist_freq": hist_x, "hist_intensity": hist_y}
