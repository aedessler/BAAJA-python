"""BAAJA: potential impacts of the Bipartisan American Affordability and Jobs Act.

Python port of BAAJA.m from https://github.com/kevinjkircher/BAAJA
(original MATLAB code by Kevin J. Kircher, Purdue University, kevinjkircher.com).

This script evaluates the potential economic and environmental impacts of the
Bipartisan American Affordability and Jobs Act draft text that was published on
September 30, 2026. It generates the figures and numerical estimates reported
in the write-up at kevinjkircher.com/baaja.

Command line:
    python baaja.py                  # text report + figures on screen, like running BAAJA.m
    python baaja.py --save --no-show # save the eight figures as 600-dpi PNGs instead
    python baaja.py --ac-low 1       # clean electricity range used in the current report
    python baaja.py -h               # all options

From Python:
    from baaja import run
    results = run(to_report=False, fig_num=0)
    results['sC']  # any variable BAAJA.m leaves in the MATLAB workspace
"""
import argparse

import numpy as np

from deterministic_simulation import deterministic_simulation
from energy_report import energy_report
from fit_direct_use_parameters import fit_direct_use_parameters
from greenhouse_gas_report import greenhouse_gas_report
from initialize_baseline_parameters import initialize_baseline_parameters
from job_report import job_report
from mortality_report import mortality_report
from revenue_report import revenue_report
from set_derived_parameters import set_derived_parameters
from stochastic_simulation import stochastic_simulation
from tradeoff_plots import tradeoff_plots
from tradeoff_report import tradeoff_report


def run(N=1e7, n=1e3, to_report=True, fig_num=1, to_save=False, outdir='.', seed=0,
        acLow=0.97, acHigh=1.1, aeLow=1, aeHigh=1.05, apLow=1.02, apHigh=1.08):
    """Run the full BAAJA analysis (the body of BAAJA.m).

    Inputs:
        N          number of independent Monte Carlo samples
        n          number of data points in the deterministic sweep
        to_report  whether to print the text reports (and draw the bar charts)
        fig_num    number of the first figure to plot into (0 -> no plots)
        to_save    whether to save figures as PNG files
        outdir     folder for saved figures
        seed       random seed (None -> different samples each run)
        acLow, acHigh  low/high value of clean electricity relative change scalar
        aeLow, aeHigh  low/high value of electricity demand relative change scalar
        apLow, apHigh  low/high value of fossil fuel production relative change scalar

    Returns a dict of every variable defined here, matching the names BAAJA.m
    leaves in the MATLAB workspace (s* = Monte Carlo samples, d* = deterministic sweep).
    """
    rng = np.random.default_rng(seed)

    # %% baseline: 2025 as it was
    # fundamental inputs
    (E,       # total electricity generation, EJ
     C,       # clean electricity generation, EJ
     eta,     # fleet-average fossil fuel electricity generation efficiency, dimensionless
     P,       # fossil fuel production, EJ
     D,       # domestic fossil fuel direct use, EJ
     lamd,    # carbon dioxide intensity of fossil fuel direct use, Gt/EJ
     lame,    # carbon dioxide intensity of fossil fuel electricity, Gt/EJ
     mu,      # methane intensity at GWP100 of fossil fuel production, CO2e Gt/EJ
     pif,     # average fossil fuel price, billion $/EJ
     pie,     # average wholesale electricity price, billion $/EJ
     gamc,    # job intensity of clean electricity generation, thousand jobs/EJ
     gamfe,   # job intensity of fossil fueled electricity generation, thousand jobs/EJ
     gamfp,   # job intensity of fossil fuel production, thousand jobs/EJ
     deltaV,  # mortality intensity attributable to fossil fuel air pollution from Vohra et al., thousand lives/EJ
     deltaL,  # mortality intensity attributable to fossil fuel air pollution from Lelieveld et al., thousand lives/EJ
     ) = initialize_baseline_parameters(to_report)

    # derived parameter values
    (X,     # fossil fuel exports, EJ
     Rc,    # clean electricity revenue, billion $
     Rfe,   # fossil electricity revenue, billion $
     Rfp,   # fossil fuel production revenue, billion $
     Jc,    # clean electricity jobs, thousands
     Jfe,   # fossil fueled electricity jobs, thousands
     Jfp,   # fossil fuel production jobs, thousands
     dCO2,  # CO2 emissions from domestic fossil fuel direct use, Gt
     eCO2,  # CO2 emissions from domestic fossil fuel electricity, Gt
     CH4,   # CO2e emissions from methane from fossil fuel production at GWP100, Gt CO2e
     xCO2,  # CO2 emissions associated with fossil fuel exports, Gt
     MV,    # mortality from US fossil fuel use based on Vohra et al., thousand lives
     ML,    # mortality from US fossil fuel use based on Lelieveld et al., thousand lives
     ) = set_derived_parameters(E, C, eta, P, D, lamd, lame, mu, pif, pie,
                                gamc, gamfe, gamfp, deltaV, deltaL)

    # %% alternative: 2025 as if BAAJA had been in full effect
    # regression relating domestic direct fossil fuel use to total fossil fuel production
    b, eSig = fit_direct_use_parameters(to_report, fig_num, to_save, outdir)

    # Monte Carlo simulation of energy flows
    sE, sC, sP, sD = stochastic_simulation(acLow, acHigh, aeLow, aeHigh, apLow, apHigh,
                                           b, eSig, E, C, P, D, N, to_report, rng)

    # derived parameter values
    (sX, sRc, sRfe, sRfp, sJc, sJfe, sJfp, sdCO2, seCO2, sCH4, sxCO2, sMV, sML
     ) = set_derived_parameters(sE, sC, eta, sP, sD, lamd, lame, mu, pif, pie,
                                gamc, gamfe, gamfp, deltaV, deltaL)

    # text reports and bar graphs
    if fig_num > 0:
        fig_num += 1
    if to_report:
        energy_report(E, sE, C, sC, P, sP, D, sD, X, sX, fig_num, to_save, outdir)
        if fig_num > 0:
            fig_num += 1
        revenue_report(Rc, sRc, Rfe, sRfe, Rfp, sRfp, fig_num, to_save, outdir)
        if fig_num > 0:
            fig_num += 1
        job_report(Jc, sJc, Jfe, sJfe, Jfp, sJfp, fig_num, to_save, outdir)
        if fig_num > 0:
            fig_num += 1
        greenhouse_gas_report(dCO2, sdCO2, eCO2, seCO2, CH4, sCH4, xCO2, sxCO2,
                              fig_num, to_save, outdir)
        if fig_num > 0:
            fig_num += 1
        mortality_report(MV, sMV, ML, sML, fig_num, to_save, outdir)
        if fig_num > 0:
            fig_num += 1
        tradeoff_report(Rc, sRc, MV, sMV, ML, sML, C, sC, dCO2, sdCO2, CH4, sCH4)

    # %% sensitivity of tradeoff parameters
    # deterministic simulation of energy flows, sweeping over fixed ranges
    ac, ae, ap, ad, dE, dC, dP, dD = deterministic_simulation(
        acLow, acHigh, aeLow, aeHigh, apLow, apHigh, b, E, C, P, D, n)

    # derived parameters
    (_, dRc, _, _, _, _, _, ddCO2, deCO2, dCH4, _, _, dML
     ) = set_derived_parameters(dE, dC, eta, dP, dD, lamd, lame, mu, pif, pie,
                                gamc, gamfe, gamfp, deltaV, deltaL)

    # tradeoff plots
    if fig_num > 0:
        tradeoff_plots(ac, ap, Rc, dRc, ML, dML, C, dC, dCO2, ddCO2, eCO2, deCO2, CH4, dCH4,
                       fig_num, to_save, outdir)

    results = dict(locals())
    del results['rng'], results['_']
    return results


def main(argv=None):
    parser = argparse.ArgumentParser(
        description='Python port of BAAJA.m: potential impacts of the Bipartisan '
                    'American Affordability and Jobs Act on US energy systems.')
    parser.add_argument('-N', '--samples', type=float, default=1e7,
                        help='number of Monte Carlo samples (default: 1e7, as in BAAJA.m)')
    parser.add_argument('--seed', type=int, default=0,
                        help='random seed (default: 0)')
    parser.add_argument('--ac-low', type=float, default=0.97,
                        help='low end of the clean electricity scalar a_c (default: 0.97, as in '
                             'BAAJA.m; the current version of the report uses 1)')
    parser.add_argument('--save', action='store_true',
                        help='save figures as 600-dpi PNG files (toSave = 1 in BAAJA.m)')
    parser.add_argument('--outdir', default='.',
                        help='folder for saved figures (default: current folder)')
    parser.add_argument('--no-plots', action='store_true',
                        help='make no figures (figNum = 0 in BAAJA.m)')
    parser.add_argument('--no-show', action='store_true',
                        help="don't open figure windows (use with --save)")
    parser.add_argument('--no-report', action='store_true',
                        help='skip the text reports and bar charts (toReport = 0 in BAAJA.m)')
    args = parser.parse_args(argv)

    if args.no_show:
        import matplotlib
        matplotlib.use('Agg')

    run(N=args.samples, seed=args.seed, acLow=args.ac_low,
        to_report=not args.no_report, fig_num=0 if args.no_plots else 1,
        to_save=args.save, outdir=args.outdir)

    if not args.no_plots and not args.no_show:
        import matplotlib.pyplot as plt
        plt.show()


if __name__ == '__main__':
    main()
