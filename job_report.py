"""Port of jobReport.m."""
import numpy as np

from common import comparison_bar_chart, fprintf, print_increase

MEAN_FMT = '\tMean = %.3g thousand (%.2g%%).\n'
CI_FMT = '\t95%% confidence interval = [%.3g, %.3g] thousand ([%.2g, %.2g]%%).\n'


def job_report(Jc, bJc, Jfe, bJfe, Jfp, bJfp, figure_number, to_save, outdir='.'):
    """Report job outcomes in the baseline and alternative scenarios.

    Inputs:
        Jc, bJc    clean electricity jobs, baseline and under BAAJA, thousands
        Jfe, bJfe  fossil electricity jobs, baseline and under BAAJA, thousands
        Jfp, bJfp  fossil fuel production jobs, baseline and under BAAJA, thousands
        figure_number  number of the figure to plot into (0 -> no plots)
        to_save        whether to save the plot
        outdir         folder for the saved plot
    """
    fprintf('-------------------------------- ANNUAL JOBS --------------------------------\n')
    print_increase('Increase in clean electricity jobs:\n', Jc, bJc, MEAN_FMT, CI_FMT)
    print_increase('Increase in fossil fuel electricity jobs:\n', Jfe, bJfe, MEAN_FMT, CI_FMT)
    print_increase('Increase in fossil fuel production jobs:\n', Jfp, bJfp, MEAN_FMT, CI_FMT)
    print_increase('Increase in total fossil fuel jobs:\n', Jfp + Jfe, bJfp + bJfe, MEAN_FMT, CI_FMT)

    # jobs ratio
    fprintf('Mean increase in fossil fuel jobs per unit mean increase in clean electricity jobs: %.3g.\n',
            np.mean(bJfp + bJfe - Jfp - Jfe) / np.mean(bJc - Jc))

    # jobs probabilities
    fprintf('Probability that jobs increase for fossil fuel production: %.3g%%.', 100 * np.mean(bJfp > Jfp))
    fprintf(' Fossil fuel electricity generation: %.3g%%. ', 100 * np.mean(bJfe > Jfe))
    fprintf(' Clean electricity generation: %.3g%%.\n', 100 * np.mean(bJc > Jc))
    fprintf('Probability that job increases are higher for fossil fuels than for clean electricity: %.3g%%.\n',
            100 * np.mean(bJfp + bJfe - Jfp - Jfe > bJc - Jc))

    # job plot
    if figure_number > 0:
        comparison_bar_chart(
            figure_number,
            baseline=[Jfp, Jfe, Jc],
            samples=[bJfp, bJfe, bJc],
            xticklabels=['Fossil fuel production', 'Fossil fuel electricity', 'Clean electricity'],
            ylabel='Annual jobs (thousands)',
            filename='jobs.png', to_save=to_save, outdir=outdir)
