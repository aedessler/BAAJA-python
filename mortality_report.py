"""Port of mortalityReport.m."""
import numpy as np

from common import Q1, Q2, comparison_bar_chart, fprintf, quantile


def mortality_report(MV, bMV, ML, bML, figure_number, to_save, outdir='.'):
    """Report mortality outcomes in the baseline and alternative scenarios.

    Inputs:
        MV, bMV  American mortality attributable to fossil fuel air pollution
                 (Vohra et al.), baseline and under BAAJA, thousand lives
        ML, bML  American mortality attributable to fossil fuel air pollution
                 (Lelieveld et al.), baseline and under BAAJA, thousand lives
        figure_number  number of the figure to plot into (0 -> no plots)
        to_save        whether to save the plot
        outdir         folder for the saved plot
    """
    mortality911 = 2.977  # number of American deaths on 9/11, thousands
    fprintf('-------------------------------- ANNUAL MORTALITY --------------------------------\n')
    for name, M, bM in [('Vohra et al.', MV, bMV), ('Lelieveld et al.', ML, bML)]:
        fprintf('Increase in American mortality attributable to fossil fuel air pollution (%s):\n', name)
        fprintf('\tMean = %.3g thousand lives (%.2g%%).\n',
                np.mean(bM) - M, 100 * (np.mean(bM) / M - 1))
        fprintf('\tEquivalent to %.3g 9/11s.\n', np.mean(bM - M) / mortality911)
        dLow, dHigh = quantile(bM - M, [Q1, Q2])
        sLow, sHigh = quantile(bM, [Q1, Q2])
        fprintf('\t95%% confidence interval = [%.3g, %.3g] thousand lives ([%.2g, %.2g]%%).\n',
                dLow, dHigh, 100 * (sLow / M - 1), 100 * (sHigh / M - 1))

    # mortality probability
    fprintf('Probability that mortality from fossil fuel air pollution increases: %.3g%%.\n',
            100 * np.mean(bML > ML))

    # mortality plot
    if figure_number > 0:
        comparison_bar_chart(
            figure_number,
            baseline=[MV, ML],
            samples=[bMV, bML],
            xticklabels=['Vohra et al. mortality intensity', 'Lelieveld et al. mortality intensity'],
            ylabel='Annual domestic mortality attributable to\nfossil fuel air pollution (thousand lives)',
            filename='mortality.png', to_save=to_save, outdir=outdir)
