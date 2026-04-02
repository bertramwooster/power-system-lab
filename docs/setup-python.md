# Python Setup for Power System Lab

## Requirements

- Python 3.9 or later
- pip (package manager)

## Installation

```bash
pip install -r requirements.txt
```

## Package Versions (tested)

| Package | Version | Purpose |
|---------|---------|---------|
| pandapower | ≥ 2.13 | Power flow, OPF, network modelling |
| numpy | ≥ 1.24 | Numerical arrays |
| scipy | ≥ 1.11 | ODE solvers, optimization, FFT |
| matplotlib | ≥ 3.7 | Plotting |
| pandas | ≥ 2.0 | Tabular data |

## Optional (for advanced experiments)

| Package | Version | Purpose |
|---------|---------|---------|
| pypsa | ≥ 0.26 | Network-constrained OPF (Exp 9) |
| jupyter | ≥ 1.0 | Interactive notebooks |

## Verifying Installation

```python
import pandapower as pp
import pandapower.networks as pn

net = pn.case9()
pp.runpp(net)
print(net.res_bus)
# Should print a 9-row DataFrame with vm_pu, va_degree, p_mw, q_mvar
```

## Troubleshooting

- If `pandapower` install fails on Windows, try: `pip install pandapower --no-deps` then install dependencies manually.
- If `numba` causes issues (pandapower optional dependency), install with: `pip install pandapower[all]` or skip numba.
- All scripts save figures to the current working directory. Run from within the `scripts/python/` folder.
