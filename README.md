# BAAJA (Python)

This is a Python version of the model behind Kevin J. Kircher's report "Potential impacts of the Bipartisan American Affordability and Jobs Act on United States energy systems" (https://kevinjkircher.com/baaja/). The model uses Monte Carlo simulation and deterministic sensitivity analysis to estimate how the Act could affect US energy flows, revenues, jobs, greenhouse gas emissions, and mortality from fossil fuel air pollution.

It is a line-by-line port of Kircher's MATLAB code at https://github.com/kevinjkircher/BAAJA, as of commit [`349cb80`](https://github.com/kevinjkircher/BAAJA/tree/349cb80ff0892d93e9202487fbd292e2f070c5bb). The model, data, and analysis are his. This repository only translates them into Python.

## Running it

Requires Python 3.9+ with NumPy ≥ 1.22 and Matplotlib (`pip install -r requirements.txt`).

```bash
python baaja.py                       # text report + 8 figures on screen, like running BAAJA.m
python baaja.py --save --no-show      # write the figures as 600-dpi PNGs instead
python baaja.py --ac-low 1            # clean-electricity range used in the current report (see below)
python baaja.py -N 1e6 --no-plots     # quicker run, text only
python baaja.py -h                    # all options
```

A full run (10 million Monte Carlo samples) takes about 10 seconds and about 2 GB of memory.

From Python or Jupyter, `run()` returns every variable that BAAJA.m leaves in the MATLAB workspace:

```python
from baaja import run
r = run(to_report=False, fig_num=0)
r['sC']    # Monte Carlo samples of clean electricity generation under BAAJA, EJ
r['b']     # direct-use regression coefficients
```

## File map

| MATLAB (original repository) | Python (this repository) |
|---|---|
| `BAAJA.m` | `baaja.py` (`run()` plus a command-line interface) |
| `initializeBaselineParameters.m` | `initialize_baseline_parameters.py` |
| `setDerivedParameters.m` | `set_derived_parameters.py` |
| `fitDirectUseParameters.m` | `fit_direct_use_parameters.py` |
| `stochasticSimulation.m` | `stochastic_simulation.py` |
| `deterministicSimulation.m` | `deterministic_simulation.py` |
| `trirnd.m` | `trirnd.py` |
| `energyReport.m`, `revenueReport.m`, `jobReport.m`, `greenhouseGasReport.m`, `mortalityReport.m`, `tradeoffReport.m` | `energy_report.py`, `revenue_report.py`, `job_report.py`, `greenhouse_gas_report.py`, `mortality_report.py`, `tradeoff_report.py` |
| `tradeoffPlots.m` | `tradeoff_plots.py` |
| — | `common.py`: `fprintf`, MATLAB-style `quantile`, and the bar chart shared by the five report figures |

Variable names (`E`, `C`, `eta`, `lamd`, `sRc`, …) and the order of every function's inputs and outputs follow the MATLAB code, so the two can be read side by side. Each function's MATLAB `arguments` block became its docstring.

## Differences from the MATLAB version

- **Random numbers.** NumPy's generator replaces MATLAB's, so Monte Carlo results differ from a MATLAB run in the last reported digit. Runs use seed 0 by default, so they are reproducible; pass `--seed` to change it.
- **Quantiles** use NumPy's `hazen` method, which is the method MATLAB's `quantile` uses by default.
- **Tradeoff plot y-axes.** MATLAB picks automatic axis limits from all of the data, including points left of the plotted range. With the original code's `acLow = 0.97`, the sweep passes through zero change in clean generation, where the implied CO₂e intensity is about ±500 kg/kWh, so those limits would make the y-axis useless. The Python version sets the automatic limits from the visible part of the curves. With `--ac-low 1` this gives the same axes as MATLAB.
- **Figures** use Matplotlib with MATLAB's default colors and a LaTeX-like font. They follow the same layout but are not pixel-identical.

## Which clean-electricity range?

`BAAJA.m` in the original repository (commit `349cb80`) sets `acLow = 0.97`, which allows BAAJA to *decrease* clean generation by up to 3%. Footnote 32 of the current report says that earlier versions used 0.97 and that the current version treats a decrease as impossible, i.e. `acLow = 1`. The Python default stays at 0.97 to match the MATLAB code. Use `--ac-low 1` to reproduce the current report.

## Check against the report

MATLAB was not available for a side-by-side run, so the port was checked against the numbers in the current report instead. With `--ac-low 1`, every number checked from the report's text was reproduced to within Monte Carlo noise in the last digit. The non-random parts (baseline values and the direct-use regression) match exactly. For example:

| Quantity | Report | Python |
|---|---|---|
| Direct-use regression β₀, β₁, σ | −0.0060, 0.4729, 0.0355 | −0.0060, 0.4729, 0.0355 |
| Fit RMSE, R² | 0.0317, 0.383 | 0.0317, 0.383 |
| Clean electricity increase | 0.33 (0.08 to 0.59) EJ | 0.334 (0.0746 to 0.593) EJ |
| Fossil fuel revenue increase | $29.3 ($15.9 to $42.6) billion | $29.3 ($15.9 to $42.6) billion |
| Clean / fossil job increase | 31,600 / 44,700 | 31,600 / 44,700 |
| Domestic CO₂e increase | 120 (−129 to 369) Mt, P = 82.7% | 120 (−129 to 369) Mt, P = 82.7% |
| Mortality increase (Lelieveld) | 1,200 (−3,100 to 5,500) | 1,230 (−3,060 to 5,520) |
| Clean revenue per life | $3.6 million | $3.55 million |
| CO₂e per new clean kWh | 1.2 kg | 1.18 kg |
| Tradeoff-plot thresholds | ≥ 5% clean increase | 5% |

## License

MIT, the same as the original. `LICENSE` keeps Kevin J. Kircher's copyright notice for the original code, as the MIT license requires, and adds a notice for the Python port.
