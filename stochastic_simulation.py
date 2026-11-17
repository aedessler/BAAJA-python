"""Port of stochasticSimulation.m."""
import numpy as np

from common import fprintf
from trirnd import trirnd


def stochastic_simulation(acLow, acHigh, aeLow, aeHigh, apLow, apHigh, b, eSig,
                          E, C, P, D, N, to_report, rng=None):
    """Monte Carlo simulation of energy flows in an alternate-history 2025 with BAAJA in full effect.

    Inputs:
        acLow, acHigh  low/high value of clean electricity relative change scalar
        aeLow, aeHigh  low/high value of electricity demand relative change scalar
        apLow, apHigh  low/high value of fossil fuel production relative change scalar
                       (indicator of BAAJA overall effectiveness)
        b              parameter estimates from least-squares fit
        eSig           standard error from least-squares fit
        E              baseline total electricity generation, EJ
        C              baseline clean electricity generation, EJ
        P              baseline total fossil fuel production, EJ
        D              baseline total domestic fossil fuel direct use, EJ
        N              number of Monte Carlo samples
        to_report      whether to issue text reports
        rng            numpy random Generator (default: a fresh, unseeded one)

    Returns (each a length-N array):
        bE  total electricity generation under BAAJA, EJ
        bC  clean electricity generation under BAAJA, EJ
        bP  fossil fuel production under BAAJA, EJ
        bD  domestic fossil fuel direct use under BAAJA, EJ
    """
    rng = np.random.default_rng() if rng is None else rng
    N = int(N)

    # random number generation of relative change scalars (same draw order as MATLAB)
    ac = trirnd(acLow, acHigh, N, rng)  # clean electricity
    ae = (aeLow + (aeHigh - aeLow) / (acHigh - acLow) * (ac - acLow)
          + 0.01 * trirnd(-1, 1, N, rng))  # electricity generation
    ap = trirnd(apLow, apHigh, N, rng)  # fossil fuel production
    ad = 1 + b[0] + b[1] * (ap - 1) + eSig * rng.standard_normal(N)  # domestic fossil fuel direct use

    # report
    if to_report:
        fprintf('Mean ac = %.4g, ae = %.4g, ap = %.4g, ad = %.4g.\n',
                np.mean(ac), np.mean(ae), np.mean(ap), np.mean(ad))
        fprintf('Probability that ac < 1: %.3g%%.\n', 100 * np.mean(ac < 1))
        fprintf('Probability that ae < 1: %.3g%%.\n', 100 * np.mean(ae < 1))

    # simulation
    bE = ae * E  # total electricity generation, EJ
    bC = ac * C  # clean electricity generation, EJ
    bP = ap * P  # fossil fuel production, EJ
    bD = ad * D  # domestic fossil fuel direct use, EJ

    return bE, bC, bP, bD
