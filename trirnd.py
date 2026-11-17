"""Port of trirnd.m."""
import numpy as np


def trirnd(a, c, size=None, rng=None):
    """Sample from the symmetric triangular distribution on [a, c].

    Inputs:
        a     the minimum of the support of the distribution
        c     the maximum of the support of the distribution
        size  output shape: an int N for N samples, or (m, n) for an m x n
              matrix (MATLAB's trirnd(a, c, m, n) is trirnd(a, c, (m, n)) here)
        rng   numpy random Generator (default: a fresh, unseeded one)

    Output:
        independent samples; the mode is the midpoint (a + c)/2
    """
    rng = np.random.default_rng() if rng is None else rng
    return rng.triangular(a, (a + c) / 2, c, size)
