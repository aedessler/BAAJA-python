"""Port of tradeoffReport.m."""
import numpy as np

from common import fprintf


def tradeoff_report(Rc, bRc, MV, bMV, ML, bML, C, bC, DCO2, bDCO2, CH4, bCH4):
    """Report tradeoffs in the baseline and alternative scenarios.

    Inputs:
        Rc, bRc      clean electricity revenue, baseline and under BAAJA, billion $
        MV, bMV      mortality from fossil fuel air pollution (Vohra et al.), thousand lives
        ML, bML      mortality from fossil fuel air pollution (Lelieveld et al.), thousand lives
        C, bC        clean electricity generation, baseline and under BAAJA, EJ
        DCO2, bDCO2  domestic energy-related CO2 emissions, baseline and under BAAJA, Gt
                     (BAAJA.m passes the direct-use CO2 here)
        CH4, bCH4    domestic CH4 from fossil fuel production, baseline and under BAAJA, Gt CO2e
    """
    # clean electricity revenue vs. mortality from fossil fuel air pollution
    VSL = 11.85  # EPA value of a statistical life, million $/life
    fprintf('-------------------------------- TRADEOFFS --------------------------------\n')
    fprintf('Mean increase in clean electricity revenue per unit mean increase in mortality (Vohra et al.): %.3g million $/life.\n',
            np.mean(bRc - Rc) / np.mean(bMV - MV))
    fprintf('\tEquivalent to %.3g%% of the EPA value of a statistical life.\n',
            100 * np.mean(bRc - Rc) / np.mean(bMV - MV) / VSL)
    fprintf('Mean increase in clean electricity revenue per unit mean increase in mortality (Lelieveld et al.): %.3g million $/life.\n',
            np.mean(bRc - Rc) / np.mean(bML - ML))
    fprintf('\tEquivalent to %.3g%% of the EPA value of a statistical life.\n',
            100 * np.mean(bRc - Rc) / np.mean(bML - ML) / VSL)

    # clean electricity generation vs. greenhouse gases from fossil fuels
    NGCC = 0.45 / 3.6  # CO2e intensity of natural gas combined-cycle electricity, Gt/EJ
    coal = 1 / 3.6  # CO2e intensity of coal-fired electricity, Gt/EJ
    intensity = np.mean(bDCO2 + bCH4 - DCO2 - CH4) / np.mean(bC - C)  # Gt/EJ
    fprintf('Mean increase in domestic greenhouse gas emissions per unit mean increase in clean electricity generation: %.3g Gt/EJ (%.3g kg/kWh).\n',
            intensity, intensity * 3.6)  # 10^12 kg/Gt, 3.6*10^-12 EJ/kWh
    fprintf('\tEquivalent to %.3g%% of the greenhouse gas intensity of electricity from a typical natural gas power plant or %.3g%% from coal.\n',
            100 * intensity / NGCC, 100 * intensity / coal)
