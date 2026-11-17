"""Port of fitDirectUseParameters.m."""
import numpy as np

from common import BLUE, ORANGE, fprintf, grid_on, new_figure, save_figure


def fit_direct_use_parameters(to_report, figure_number, to_save, outdir='.'):
    """Fit year-over-year change in fossil fuel direct use vs. change in production.

    Uses fossil fuel production and consumption data from 2015 through 2025 to
    fit a linear model of the year-over-year percent change in domestic fossil
    fuel direct use vs. the year-over-year percent change in fossil fuel
    production.

    Inputs:
        to_report      whether to issue text reports
        figure_number  number of the figure to plot into (0 -> no plots)
        to_save        whether to save the plot
        outdir         folder for the saved plot

    Returns:
        b     parameter estimates from least-squares fit, [intercept, slope]
        eSig  standard error from least-squares fit
    """
    # production
    year = np.arange(2015, 2026)  # years spanned by data
    totalProduction = np.array([
        70.174, 65.460, 68.519, 75.824, 81.449, 76.209, 78.019, 82.296, 86.174, 86.544, 89.732,
    ]) * 1.055  # total production, EJ, https://www.eia.gov/totalenergy/data/monthly/pdf/sec12_7.pdf

    # production report
    if to_report:
        fprintf('Production increased from %.3g EJ in %i to %.3g EJ in %i (%.3g%%).\n',
                totalProduction[0], year[0], totalProduction[-1], year[-1],
                100 * (totalProduction[-1] / totalProduction[0] - 1))

    # overall consumption
    coalConsumption = np.array([
        15.549, 14.226, 13.837, 13.252, 11.316, 9.181, 10.549, 9.888, 8.171, 7.912, 8.671,
    ]) * 1.055  # coal consumption, EJ, https://www.eia.gov/totalenergy/data/monthly/pdf/sec12_8.pdf
    gasConsumption = np.array([
        28.191, 28.400, 28.049, 31.163, 32.264, 31.669, 31.711, 33.379, 33.676, 34.179, 34.624,
    ]) * 1.055  # gas consumption, EJ, https://www.eia.gov/totalenergy/data/monthly/pdf/sec12_8.pdf
    oilConsumption = np.array([
        35.368, 35.712, 36.043, 36.892, 36.866, 32.331, 35.243, 35.319, 35.448, 35.590, 36.115,
    ]) * 1.055  # oil consumption, EJ, https://www.eia.gov/totalenergy/data/monthly/pdf/sec12_8.pdf

    # consumption for electricity
    electricityCoalHeatContent = np.array([
        19.15, 19.15, 18.98, 18.92, 18.90, 18.88, 18.94, 18.79, 18.72, 18.79, 18.774,
    ])  # heat content of coal consumed for electricity, billion Btu per thousand short tons, https://www.eia.gov/totalenergy/data/monthly/pdf/mer_A_FULL.pdf
    electricityCoalConsumption = np.array([
        738444, 678554, 664993, 637217, 538606, 435827, 501435, 472834, 387205, 373258, 416995,
    ], dtype=float)  # electricity coal consumption, thousand short tons, https://www.eia.gov/totalenergy/data/monthly/pdf/sec6_4.pdf
    electricityCoalConsumption = electricityCoalConsumption * electricityCoalHeatContent / 947817  # 1 EJ = 947817 billion Btu
    electricityOilHeatContent = 5.9  # billion Btu per thousand barrels, https://www.eia.gov/totalenergy/data/monthly/pdf/mer_A_FULL.pdf
    electricityOilConsumption = np.array([
        128, 113, 101, 121, 88, 86, 95, 113, 81, 76, 93,
    ], dtype=float) * 365  # electricity oil consumption, thousand barrels, https://www.eia.gov/totalenergy/data/monthly/pdf/sec3_23.pdf
    electricityOilConsumption = electricityOilConsumption * electricityOilHeatContent / 947817  # 1 EJ = 947817 billion Btu
    electricityGasHeatContent = 1034  # billion Btu per billion cubic feet, https://www.eia.gov/totalenergy/data/monthly/pdf/mer_A_FULL.pdf
    electricityGasConsumption = np.array([
        9613, 9985, 9266, 10599, 11299, 11632, 11229, 12092, 12941, 13476, 13054,
    ], dtype=float)  # electricity gas consumption, billion cubic feet, https://www.eia.gov/totalenergy/data/monthly/pdf/sec4_6.pdf
    electricityGasConsumption = electricityGasConsumption * electricityGasHeatContent / 947817  # 1 EJ = 947817 billion Btu

    # direct consumption
    coalDirectConsumption = coalConsumption - electricityCoalConsumption  # direct coal consumption, EJ
    oilDirectConsumption = oilConsumption - electricityOilConsumption  # direct oil consumption, EJ
    gasDirectConsumption = gasConsumption - electricityGasConsumption  # direct gas consumption, EJ
    totalDirectConsumption = coalDirectConsumption + oilDirectConsumption + gasDirectConsumption  # total direct consumption, EJ

    # relative changes in direct consumption vs. production
    relativeProductionChange = np.diff(totalProduction) / totalProduction[:-1]
    relativeDirectConsumptionChange = np.diff(totalDirectConsumption) / totalDirectConsumption[:-1]

    # relative change fit
    y = relativeDirectConsumptionChange  # target
    n = len(y)  # number of data points
    x = relativeProductionChange  # feature
    X = np.column_stack([np.ones(n), x])  # feature matrix
    b = np.linalg.lstsq(X, y, rcond=None)[0]  # least-squares parameter estimate (MATLAB X\y)
    yh = X @ b  # prediction
    e = yh - y  # error
    eSig = np.sqrt(np.sum(e ** 2) / (n - X.shape[1]))  # standard error

    # report fit statistics
    if to_report:
        fprintf('Fit RMSE: %.4g. R^2: %.4g.\n',
                np.sqrt(np.mean(e ** 2)), 1 - np.var(e, ddof=1) / np.var(y, ddof=1))

    # relative change fit plot
    if figure_number > 0:
        fig, ax = new_figure(figure_number)
        xs = np.sort(x)
        xPoly = 100 * np.concatenate([xs, xs[::-1]])  # x polygon
        yPoly = 100 * np.concatenate([b[0] + b[1] * xs - 1.96 * eSig,
                                      b[0] + b[1] * xs[::-1] + 1.96 * eSig])  # y polygon
        ax.fill(xPoly, yPoly, facecolor=ORANGE, alpha=0.2, edgecolor='none')  # confidence interval
        grid_on(ax)
        ax.plot(100 * x, 100 * y, 'o', color=BLUE, markerfacecolor='none')  # data
        ax.plot(100 * xs, 100 * (b[0] + b[1] * xs), color=ORANGE)  # best-fit line
        ax.set_xlim(100 * np.min(x), 100 * np.max(x))
        yMax = np.ceil(np.max(np.abs(100 * y)))
        ax.set_ylim(-yMax, yMax)
        ax.set_xlabel('Percent change in fossil fuel production')
        ax.set_ylabel('Percent change in fossil fuel direct use')
        textStr = '$y = $' + '%.3g' % b[1]  # string for text annotation
        if b[0] > 0:
            textStr += '$x +$' + '%.3g' % (100 * b[0])
        else:
            textStr += '$x -$' + '%.3g' % (-100 * b[0])
        textStr += r'$+ e$, $\hat \sigma_e =$' + '%.3g' % (100 * eSig)
        small = 0.5  # margin for locating text string
        ax.text(ax.get_xlim()[0] + small, ax.get_ylim()[1] - small, textStr,
                va='top', color=ORANGE)
        if to_save:
            save_figure(fig, 'fit.png', outdir)

    return b, eSig
