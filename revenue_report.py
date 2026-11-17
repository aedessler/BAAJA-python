"""Port of revenueReport.m."""
import numpy as np

from common import comparison_bar_chart, fprintf, print_increase

MEAN_FMT = '\tMean = $%.3g billion (%.2g%%).\n'
CI_FMT = '\t95%% confidence interval = $[%.3g, %.3g] billion ([%.2g, %.2g]%%).\n'


def revenue_report(Rc, bRc, Rfe, bRfe, Rfp, bRfp, figure_number, to_save, outdir='.'):
    """Report revenue outcomes in the baseline and alternative scenarios.

    Inputs:
        Rc, bRc    clean electricity revenue, baseline and under BAAJA, billion $
        Rfe, bRfe  fossil electricity revenue, baseline and under BAAJA, billion $
        Rfp, bRfp  fossil fuel production revenue, baseline and under BAAJA, billion $
        figure_number  number of the figure to plot into (0 -> no plots)
        to_save        whether to save the plot
        outdir         folder for the saved plot
    """
    fprintf('-------------------------------- ANNUAL REVENUE --------------------------------\n')
    print_increase('Increase in clean electricity revenue:\n', Rc, bRc, MEAN_FMT, CI_FMT)
    print_increase('Increase in fossil fuel electricity revenue:\n', Rfe, bRfe, MEAN_FMT, CI_FMT)
    print_increase('Increase in fossil fuel production revenue:\n', Rfp, bRfp, MEAN_FMT, CI_FMT)
    print_increase('Increase in total fossil fuel revenue:\n', Rfp + Rfe, bRfp + bRfe, MEAN_FMT, CI_FMT)

    # revenue ratio
    fprintf('Mean increase in fossil fuel revenue per unit mean increase in clean electricity revenue: %.3g.\n',
            np.mean(bRfp + bRfe - Rfp - Rfe) / np.mean(bRc - Rc))

    # revenue probabilities
    fprintf('Probability that revenues increase for fossil fuel production: %.3g%%.', 100 * np.mean(bRfp > Rfp))
    fprintf(' Fossil fuel electricity generation: %.3g%%. ', 100 * np.mean(bRfe > Rfe))
    fprintf(' Clean electricity generation: %.3g%%.\n', 100 * np.mean(bRc > Rc))
    fprintf('Probability that revenue increases are higher for fossil fuels than for clean electricity: %.3g%%.\n',
            100 * np.mean(bRfp + bRfe - Rfp - Rfe > bRc - Rc))

    # revenue plot
    if figure_number > 0:
        comparison_bar_chart(
            figure_number,
            baseline=[Rfp, Rfe, Rc],
            samples=[bRfp, bRfe, bRc],
            xticklabels=['Fossil fuel production', 'Fossil fuel electricity', 'Clean electricity'],
            ylabel=r'Annual revenue (\$ billions)',
            filename='revenue.png', to_save=to_save, outdir=outdir)
