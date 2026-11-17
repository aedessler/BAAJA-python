"""Helpers shared by the Python port of the BAAJA MATLAB code.

These reproduce the few MATLAB behaviors the original code relies on:
fprintf-style printing, MATLAB's default quantile method, MATLAB's default
plot colors, and the grouped bar charts drawn by the report functions.
"""
import os
import sys

import numpy as np

Q1 = 0.025  # low quantile to report
Q2 = 0.975  # high quantile to report

# MATLAB's default line colors, so the figures look like the originals
MATLAB_COLORS = ['#0072BD', '#D95319', '#EDB120', '#7E2F8E',
                 '#77AC30', '#4DBEEE', '#A2142F']
BLUE, ORANGE, YELLOW, PURPLE = MATLAB_COLORS[:4]


def fprintf(fmt, *args):
    """MATLAB fprintf to the screen: C-style format string, no automatic newline."""
    sys.stdout.write(fmt % args)


def quantile(x, p):
    """MATLAB quantile(x, p): works down columns and uses MATLAB's default method.

    MATLAB treats sorted data as the (0.5/n), (1.5/n), ..., ((n-0.5)/n)
    quantiles and interpolates linearly between them. NumPy calls this the
    'hazen' method.
    """
    return np.quantile(x, p, axis=0, method='hazen')


def print_increase(title, base, samples, mean_fmt, ci_fmt):
    """Print the mean and 95% interval of (samples - base), absolute and relative.

    This is the block of three fprintf calls that the MATLAB report functions
    repeat for every quantity. mean_fmt takes (absolute, percent); ci_fmt takes
    (absolute low, absolute high, percent low, percent high).
    """
    fprintf(title)
    m = np.mean(samples)
    fprintf(mean_fmt, m - base, 100 * (m / base - 1))
    dLow, dHigh = quantile(samples - base, [Q1, Q2])
    sLow, sHigh = quantile(samples, [Q1, Q2])
    fprintf(ci_fmt, dLow, dHigh, 100 * (sLow / base - 1), 100 * (sHigh / base - 1))


# ---------------------------------------------------------------- plotting

_STYLE = {
    'axes.prop_cycle': None,  # set on first use (needs cycler from matplotlib)
    'font.family': 'serif',
    'font.serif': ['STIXGeneral', 'DejaVu Serif'],
    'mathtext.fontset': 'stix',  # LaTeX-like math, like MATLAB's latex interpreter
    'legend.fancybox': False,
    'legend.edgecolor': '0.15',
}


def new_figure(number):
    """MATLAB `figure(number), clf`. Returns (figure, axes)."""
    import matplotlib.pyplot as plt
    from cycler import cycler

    style = dict(_STYLE, **{'axes.prop_cycle': cycler(color=MATLAB_COLORS)})
    plt.rcParams.update(style)
    fig = plt.figure(number)
    fig.clf()
    ax = fig.add_subplot()
    return fig, ax


def grid_on(ax):
    """MATLAB `grid on`."""
    ax.grid(True, color='0.15', alpha=0.15)
    ax.set_axisbelow(True)


def save_figure(fig, filename, outdir='.'):
    """MATLAB exportgraphics(gcf, filename, 'resolution', 600)."""
    os.makedirs(outdir, exist_ok=True)
    fig.savefig(os.path.join(outdir, filename), dpi=600, bbox_inches='tight')


def comparison_bar_chart(figure_number, baseline, samples, xticklabels, ylabel,
                         label_formats=None, filename=None, to_save=False, outdir='.'):
    """Grouped bar chart drawn by every report function.

    For each category there is a blue bar at the baseline value and an orange bar
    at the Monte Carlo mean, each labeled in white with its value, plus a black
    error bar on the orange bar spanning the 2.5th to 97.5th percentiles.
    """
    fig, ax = new_figure(figure_number)
    k = len(baseline)
    if label_formats is None:
        label_formats = ['%.3g'] * k

    # MATLAB's grouped-bar geometry for two series
    x = np.arange(1, k + 1)
    group_width = min(0.8, 2 / 3.5)
    x1 = x - group_width / 4  # bar midpoints for first data series
    x2 = x + group_width / 4  # bar midpoints for second data series
    bar_width = 0.8 * group_width / 2

    baseline = np.array([np.mean(v) for v in baseline], dtype=float)
    means = np.array([np.mean(s) for s in samples])
    lows, highs = np.array([quantile(s, [Q1, Q2]) for s in samples]).T

    ax.bar(x1, baseline, bar_width, label='2025 as it was', zorder=2)
    ax.bar(x2, means, bar_width, label='2025 under BAAJA', zorder=2)
    grid_on(ax)
    for xi, yi, fmt in zip(x1, baseline, label_formats):
        ax.text(xi, yi / 2, fmt % yi, color='white', ha='center', va='center', zorder=4)
    for xi, yi, fmt in zip(x2, means, label_formats):
        ax.text(xi, yi / 2, fmt % yi, color='white', ha='center', va='center', zorder=4)
    ax.errorbar(x2, means, yerr=[means - lows, highs - means], fmt='none',
                ecolor='k', elinewidth=2, capsize=6, capthick=2, zorder=3)
    ax.set_xticks(x, xticklabels)
    ax.set_ylabel(ylabel)
    ax.legend(loc='upper right')
    if to_save and filename:
        save_figure(fig, filename, outdir)
    return fig
