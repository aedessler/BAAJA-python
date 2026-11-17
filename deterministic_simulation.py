"""Port of deterministicSimulation.m."""
import numpy as np


def deterministic_simulation(acLow, acHigh, aeLow, aeHigh, apLow, apHigh, b, E, C, P, D, n):
    """Deterministic sweep of energy flows in an alternate-history 2025 with BAAJA in full effect.

    The clean electricity scalar ac is swept over n points (an n x 1 column) and
    the fossil fuel production scalar ap takes its low, middle, and high values
    (a 1 x 3 row). Quantities that combine the two broadcast to n x 3, exactly
    as MATLAB's implicit expansion does in the original.

    Inputs:
        acLow, acHigh  low/high value of clean electricity relative change scalar
        aeLow, aeHigh  low/high value of electricity demand relative change scalar
        apLow, apHigh  low/high value of fossil fuel production relative change scalar
        b              parameter estimates from least-squares fit
        E, C, P, D     baseline total electricity, clean electricity, fossil fuel
                       production, and domestic fossil fuel direct use, EJ
        n              number of data points to sweep

    Returns:
        ac  clean electricity generation relative change scalar, n x 1
        ae  total electricity generation relative change scalar, n x 1
        ap  fossil fuel production relative change scalar, 1 x 3
        ad  domestic fossil fuel direct use relative change scalar, 1 x 3
        bE  total electricity generation under BAAJA, EJ, n x 1
        bC  clean electricity generation under BAAJA, EJ, n x 1
        bP  fossil fuel production under BAAJA, EJ, 1 x 3
        bD  domestic fossil fuel direct use under BAAJA, EJ, 1 x 3
    """
    # relative change scalars
    ac = np.linspace(acLow, acHigh, int(n))[:, np.newaxis]  # clean electricity generation
    ae = aeLow + (aeHigh - aeLow) / (acHigh - acLow) * (ac - acLow)  # total electricity generation
    ap = np.array([[apLow, (apLow + apHigh) / 2, apHigh]])  # fossil fuel production
    ad = 1 + b[0] + b[1] * (ap - 1)  # domestic fossil fuel direct use

    # simulation
    bE = ae * E  # total electricity generation, EJ
    bC = ac * C  # clean electricity generation, EJ
    bP = ap * P  # fossil fuel production, EJ
    bD = ad * D  # domestic fossil fuel direct use, EJ

    return ac, ae, ap, ad, bE, bC, bP, bD
