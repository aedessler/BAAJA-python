"""Port of greenhouseGasReport.m."""
import numpy as np

from common import comparison_bar_chart, fprintf, print_increase

MEAN_FMT = '\tMean = %.3g Gt (%.2g%%).\n'
CI_FMT = '\t95%% confidence interval = [%.3g, %.3g] Gt ([%.2g, %.2g]%%).\n'


def greenhouse_gas_report(dCO2, bdCO2, eCO2, beCO2, CH4, bCH4, xCO2, bxCO2,
                          figure_number, to_save, outdir='.'):
    """Report greenhouse gas outcomes in the baseline and alternative scenarios.

    Inputs:
        dCO2, bdCO2  domestic CO2 from fossil fuel direct use, baseline and under BAAJA, Gt
        eCO2, beCO2  domestic CO2 from fossil fuel electricity, baseline and under BAAJA, Gt
        CH4, bCH4    domestic CH4 from fossil fuel production, baseline and under BAAJA, Gt CO2e
        xCO2, bxCO2  CO2 associated with fossil fuel exports, baseline and under BAAJA, Gt
        figure_number  number of the figure to plot into (0 -> no plots)
        to_save        whether to save the plot
        outdir         folder for the saved plot
    """
    fprintf('-------------------------------- ANNUAL GREENHOUSE GASES --------------------------------\n')
    print_increase('Increase in domestic energy-related CO2 emissions from fossil fuel direct use:\n',
                   dCO2, bdCO2, MEAN_FMT, CI_FMT)
    print_increase('Increase in domestic energy-related CO2 emissions from fossil fuel electricity:\n',
                   eCO2, beCO2, MEAN_FMT, CI_FMT)
    print_increase('Increase in domestic CH4 emissions from fossil fuel production:\n',
                   CH4, bCH4, '\tMean = %.3g Gt CO2e at GWP100 (%.2g%%).\n', CI_FMT)
    print_increase('Increase in total domestic energy-related CO2e emissions:\n',
                   dCO2 + eCO2 + CH4, bdCO2 + beCO2 + bCH4, MEAN_FMT, CI_FMT)
    print_increase('Increase in CO2 emissions associated with fossil fuel exports:\n',
                   xCO2, bxCO2, MEAN_FMT, CI_FMT)

    # greenhouse gas probabilities
    fprintf('Probability that greenhouse gas emissions increase: %.3g%%.\n',
            100 * np.mean(bdCO2 + beCO2 + bCH4 > dCO2 + eCO2 + CH4))

    # greenhouse gas plot
    if figure_number > 0:
        comparison_bar_chart(
            figure_number,
            baseline=[dCO2, eCO2, CH4, xCO2],
            samples=[bdCO2, beCO2, bCH4, bxCO2],
            xticklabels=['Direct-use CO$_2$', 'Electricity CO$_2$', 'CH$_4$ (GWP100)', 'Export CO$_2$'],
            ylabel='Annual energy-related\ngreenhouse gas emissions (Gt CO$_{2e}$)',
            label_formats=['%.3g', '%.3g', '%.3g', '%.2g'],
            filename='emissions.png', to_save=to_save, outdir=outdir)
