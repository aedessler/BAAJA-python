"""Port of energyReport.m."""
import numpy as np

from common import comparison_bar_chart, fprintf, print_increase

MEAN_FMT = '\tMean = %.3g EJ (%.2g%%).\n'
CI_FMT = '\t95%% confidence interval = [%.3g, %.3g] EJ ([%.2g, %.2g]%%).\n'


def energy_report(E, bE, C, bC, P, bP, D, bD, X, bX, figure_number, to_save, outdir='.'):
    """Report energy outcomes in the baseline and alternative scenarios.

    Inputs:
        E, bE   total electricity generation, baseline and under BAAJA, EJ
        C, bC   clean electricity generation, baseline and under BAAJA, EJ
        P, bP   total fossil fuel production, baseline and under BAAJA, EJ
        D, bD   total domestic fossil fuel direct use, baseline and under BAAJA, EJ
        X, bX   fossil fuel exports, baseline and under BAAJA, EJ
        figure_number  number of the figure to plot into (0 -> no plots)
        to_save        whether to save the plot
        outdir         folder for the saved plot
    """
    fprintf('-------------------------------- ANNUAL ENERGY --------------------------------\n')
    print_increase('Increase in clean electricity generation:\n', C, bC, MEAN_FMT, CI_FMT)
    print_increase('Increase in fossil fuel electricity generation:\n', E - C, bE - bC, MEAN_FMT, CI_FMT)
    print_increase('Increase in total electricity generation:\n', E, bE, MEAN_FMT, CI_FMT)
    print_increase('Increase in fossil fuel production:\n', P, bP, MEAN_FMT, CI_FMT)
    print_increase('Increase in fossil fuel direct use:\n', D, bD, MEAN_FMT, CI_FMT)
    print_increase('Increase in fossil fuel exports:\n', X, bX, MEAN_FMT, CI_FMT)

    # energy probabilities
    fprintf('Probability that clean generation increases: %.3g%%.', 100 * np.mean(bC > C))
    fprintf(' Fossil fuel electricity generation: %.3g%%. ', 100 * np.mean(bE - bC > E - C))
    fprintf(' Total generation: %.3g%%.\n', 100 * np.mean(bE > E))
    fprintf('Probability that generation increases are higher for clean than fossil fuel electricity: %.3g%%.\n',
            100 * np.mean(bC - C > bE - bC - (E - C)))
    fprintf('Probability that domestic fossil fuel use (direct + electricity) increases: %.3g%%.\n',
            100 * np.mean(bP - bX > P - X))
    fprintf('Probability that fossil fuel exports increase: %.3g%%.\n', 100 * np.mean(bX > X))

    # electricity plot
    if figure_number > 0:
        comparison_bar_chart(
            figure_number,
            baseline=[E - C, C],
            samples=[bE - bC, bC],
            xticklabels=['Fossil fuel', 'Clean'],
            ylabel='Annual electricity generation (EJ)',
            filename='generation.png', to_save=to_save, outdir=outdir)
