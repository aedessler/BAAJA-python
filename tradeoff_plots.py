"""Port of tradeoffPlots.m."""
import numpy as np
from matplotlib.patches import Rectangle
from matplotlib.ticker import MaxNLocator

from common import PURPLE, grid_on, new_figure, save_figure


def _first(mask):
    """MATLAB find(mask, 1, 'first'), returning None instead of [] if nothing matches."""
    idx = np.flatnonzero(mask)
    return int(idx[0]) if idx.size else None


def _auto_ylim(x, Y, xlim):
    """Automatic y-limits for the curves inside xlim, rounded out to tick values.

    MATLAB's automatic limits consider all of the data, including points left of
    the plotted x-range. With the repository's acLow = 0.97, the sweep passes
    through a_c = 1, where the change in clean generation is ~0 and the implied
    CO2e intensity is ~±500 kg/kWh, which would stretch the y-axis far beyond
    the curves that are actually shown. Fitting only the visible part avoids
    that. With acLow = 1 (the current version of the report) it gives the same
    limits MATLAB does, up to tick rounding.
    """
    visible = (x >= xlim[0]) & (x <= xlim[1])
    Yv = np.asarray(Y)[visible]
    Yv = Yv[np.isfinite(Yv)]
    ticks = MaxNLocator(nbins=8, steps=[1, 2, 2.5, 5, 10]).tick_values(Yv.min(), Yv.max())
    return ticks[0], ticks[-1]


def tradeoff_plots(ac, ap, Rc, bRc, ML, bML, C, bC, dCO2, bdCO2, eCO2, beCO2, CH4, bCH4,
                   figure_number, to_save, outdir='.'):
    """Plot tradeoff curves from the deterministic simulation (two figures).

    Inputs:
        ac            clean electricity relative change scalar, n x 1
        ap            fossil fuel production relative change scalar, 1 x 3
        Rc, bRc       clean electricity revenue, baseline and under BAAJA, billion $
        ML, bML       mortality from fossil fuel air pollution (Lelieveld et al.), thousand lives
        C, bC         clean electricity generation, baseline and under BAAJA, EJ
        dCO2, bdCO2   domestic CO2 from fossil fuel direct use, baseline and under BAAJA, Gt
        eCO2, beCO2   domestic CO2 from fossil fuel electricity, baseline and under BAAJA, Gt
        CH4, bCH4     domestic CH4 from fossil fuel production, baseline and under BAAJA, Gt CO2e
        figure_number number of the first figure to plot into
        to_save       whether to save the plots
        outdir        folder for the saved plots
    """
    acv = np.ravel(ac)
    apv = np.ravel(ap)
    xpct = 100 * (acv - 1)  # percent increase in clean electricity generation
    xlim = (1, 100 * (acv.max() - 1))

    # clean electricity revenue per life plot, Lelieveld et al. mortality intensity
    purple = PURPLE  # [0.4940, 0.1840, 0.5560]
    vEPA = 11.85  # EPA value of a statistical life, million $/life
    v = (bRc - Rc) / (bML - np.mean(ML))  # implied value of a statistical life, million $/life
    iStar = _first(np.max(v, axis=1) >= vEPA)  # index of first rise above EPA VSL
    fig, ax = new_figure(figure_number)
    lines = ax.plot(xpct, v)
    grid_on(ax)
    ax.axhline(vEPA, ls='--', lw=2, color=purple)
    ax.set_xlim(xlim)
    yLow, yHigh = _auto_ylim(xpct, v, xlim)
    ylim = (min(yLow, 0), yHigh)
    ax.set_ylim(ylim)
    ax.text(xlim[0], vEPA, r'EPA recommendation $\approx$ \$' + '%.3g million' % vEPA,
            color=purple, ha='left', va='bottom')
    if iStar is not None:
        ax.axvline(xpct[iStar], ls='--', lw=2, color=purple)
        ax.text(xpct[iStar], np.mean(ylim), '%.2g%%' % xpct[iStar], color=purple, va='center')
        ax.add_patch(Rectangle((xpct[iStar], vEPA), 100 * (acv.max() - acv[iStar]), ylim[1] - vEPA,
                               facecolor=purple, alpha=0.1, edgecolor='none'))
    ax.set_xlabel('Percent increase in clean electricity generation')
    ax.set_ylabel('Implied value of a statistical life\n' + r'(\$ millions)')
    ax.legend(lines, ['%.3g%% increase in fossil fuel production' % (100 * (apv[0] - 1)),
                      '%.3g%%' % (100 * (apv[1] - 1)),
                      '%.3g%%' % (100 * (apv[2] - 1))],
              loc='upper left')
    if to_save:
        save_figure(fig, 'valueOfLife.png', outdir)

    # CO2e emissions per clean electricity plot
    gas = 0.45 / 3.6  # CO2e intensity of natural gas combined-cycle electricity, Gt/EJ
    with np.errstate(divide='ignore', invalid='ignore'):  # bC - C is exactly 0 if ac hits 1
        c = (bdCO2 + beCO2 + bCH4 - dCO2 - eCO2 - CH4) / (bC - C) * 3.6  # implied CO2e intensity, kg/kWh
    iStar = _first((acv >= 1.01) & (np.min(c, axis=1) <= gas * 3.6))  # index of first drop below gas CO2e intensity
    fig, ax = new_figure(figure_number + 1)
    lines = ax.plot(xpct, c)  # kg/kWh
    grid_on(ax)
    ax.set_xlim(xlim)
    yLow, _ = _auto_ylim(xpct, c, xlim)
    ylim = (min(yLow, 0), 5)
    ax.set_ylim(ylim)
    ax.axhline(gas * 3.6, ls='--', lw=2, color=purple)
    ax.text(xlim[0], gas * 3.6, r'Natural gas $\approx$ ' + '%.3g kg/kWh' % (gas * 3.6),
            color=purple, ha='left', va='top')
    if iStar is not None:
        ax.axvline(xpct[iStar], ls='--', lw=2, color=purple)
        ax.text(xpct[iStar], np.mean(ylim), '%.2g%%' % xpct[iStar], color=purple, va='center')
        ax.add_patch(Rectangle((xpct[iStar], 0), 100 * (acv.max() - acv[iStar]), gas * 3.6,
                               facecolor=purple, alpha=0.1, edgecolor='none'))
    ax.set_xlabel('Percent increase in clean electricity generation')
    ax.set_ylabel('Implied CO$_{2e}$ intensity of new\nclean electricity generation (kg/kWh)')
    labels = ['%.3g%%' % (100 * (apv[0] - 1)),
              '%.3g%%' % (100 * (apv[1] - 1)),
              '%.3g%% increase in fossil fuel production' % (100 * (apv[2] - 1))]
    ax.legend(lines[::-1], labels[::-1], loc='upper right')  # MATLAB leg.Direction = 'reverse'
    if to_save:
        save_figure(fig, 'CO2eIntensity.png', outdir)
