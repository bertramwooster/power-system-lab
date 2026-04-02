# ⚡ Advanced Power System Simulation & Scripting Lab

**PCC-EE804L** · 8th Semester · B.Tech Electrical Engineering  
**University of Kashmir**, Zakura Campus, Srinagar

---

## Overview

This repository contains complete, runnable code for all 11 experiments in the **Advanced Power System Simulation and Scripting Lab**. Every experiment is provided in two parallel tracks:

| Track | Stack | License | Folder |
|-------|-------|---------|--------|
| **Python** | pandapower, NumPy, SciPy, Matplotlib | Free / Open Source | `python/` |
| **MATLAB** | Simscape Electrical, MATPOWER | Academic License | `matlab/` |

> **Interactive Lab Manual**: An interactive web-based lab manual with live simulations is available at:  
> 🔗 *https://claude.ai/public/artifacts/9911515a-09a8-48a0-bdb9-995971b65b25*

---

## Experiments

| # | Title | Python | MATLAB | Status |
|---|-------|--------|--------|--------|
| 1 | Power Simulation & Scripting; SimPowerSystems Models | ✅ | ✅ | Ready |
| 2 | Models of Power Circuit Devices; Measuring & Control Blocks | 🔜 | 🔜 | — |
| 3 | Power Electronics Devices Simulation | 🔜 | 🔜 | — |
| 4 | Electric Machine & Electric Drive Simulation | 🔜 | 🔜 | — |
| 5 | Electric Power Production & Transmission | 🔜 | 🔜 | — |
| 6 | Renewable Sources & Wind Generators | 🔜 | 🔜 | — |
| 7 | Power System Scripting in Python/MATLAB | 🔜 | 🔜 | — |
| 8 | Power Flow Analysis (Newton-Raphson from scratch) | 🔜 | 🔜 | — |
| 9 | Optimal Power Flow Analysis | 🔜 | 🔜 | — |
| 10 | Time Domain Analysis: Numerical Integration & Transients | 🔜 | 🔜 | — |
| 11 | Challenges of Scripting for Power System Education | 🔜 | — | — |

---

## Quick Start (Python Track)

```bash
# Clone the repository
git clone https://github.com/<your-username>/power-system-lab.git
cd power-system-lab

# Install dependencies
pip install -r python/requirements.txt

# Run Experiment 1
cd python
python exp01_intro_pandapower.py
```

**Requirements**: Python 3.9+, pip

### What you'll see (Experiment 1)

```
=== Part A: 3-Bus System Power Flow ===
--- Bus Results ---
                   vm_pu  va_degree    p_mw   q_mvar
Bus 1 (Slack)     1.0000     0.0000  21.536    9.413
Bus 2 (PV)        1.0200    -0.2641  40.000    2.087
Bus 3 (PQ)        0.9836    -1.8724 -60.000  -20.000
...
```

Output plots are saved as `.png` files in the working directory.

---

## Quick Start (MATLAB Track)

```matlab
% Open MATLAB, navigate to the matlab/ folder
cd matlab

% Run Experiment 1
exp01_simpower_intro
% → A Simulink model opens with the 3-phase circuit
% → Waveforms appear in Scope blocks
% → Results print to the Command Window
```

**Requirements**: MATLAB R2020b+, Simscape Electrical toolbox  
**Optional**: MATPOWER (free, from https://matpower.org)

> **Note**: No `.mdl` or `.slx` files are distributed. Every MATLAB script builds its Simulink model programmatically using `new_system`, `add_block`, `set_param`, `add_line`. The `.m` file IS the model. This approach is version-independent, git-friendly, and teaches the Simulink API.

---

## Repository Structure

```
power-system-lab/
├── README.md                  ← You are here
├── LICENSE                    ← MIT License
├── .gitignore
│
├── python/                    ← Python track (free, open-source)
│   ├── requirements.txt       ← pip install -r requirements.txt
│   ├── exp01_intro_pandapower.py
│   ├── exp02_circuit_device_models.py
│   └── ...
│
├── matlab/                    ← MATLAB track (requires Simscape Electrical)
│   ├── exp01_simpower_intro.m
│   ├── exp02_circuit_device_models.m
│   └── ...
│
└── docs/                      ← Theory, setup guides, experiment overviews
    ├── setup-python.md
    ├── setup-matlab.md
    └── experiments/
        ├── exp01-overview.md
        └── ...
```

---

## Theory & References

Each experiment's theory is documented in `docs/experiments/`. The following textbooks are referenced throughout:

| Topic | Reference |
|-------|-----------|
| Power flow, economic dispatch, transient stability | Grainger & Stevenson, *Power Systems Analysis and Design* |
| Circuit transients, state-space modelling | Hayt & Kimmerly, *Engineering Circuit Analysis* |
| Power electronics topologies | P. S. Bimbhra, *Power Electronics* |
| Electrical machines, d-q model | P. S. Bimbhra, *Electrical Machinery* |
| Control systems, state-space | Ogata, *Modern Control Engineering* |
| Numerical methods (Euler, RK4) | Kreyszig, *Advanced Engineering Mathematics* |
| Signals & systems | Oppenheim, Willsky & Nawab, *Signals and Systems* |
| Power system protection | Paithankar & Bhide, *Power System Protection* |

---

## Interactive Lab Manual

The web-based interactive lab manual includes:

- **Live simulations** — drag sliders to change load, generation, voltage setpoints and watch the power flow update in real time
- **One-line diagrams** with color-coded voltage magnitudes
- **Code tabs** — copy Python or MATLAB code directly from the browser
- **Theory sections** — key equations and procedural steps for each experiment

Access it at: 🔗 *https://claude.ai/public/artifacts/9911515a-09a8-48a0-bdb9-995971b65b25*  
No installation, no login, no account needed — just a web browser.

---

## Contributing

This is a teaching repository. If you find bugs or want to suggest improvements:

1. Open an issue describing the problem
2. If you have a fix, submit a pull request
3. For new experiments or extensions, discuss in an issue first

---

## License

MIT License — see [LICENSE](LICENSE).

Course material © 2026 Mohd Aarish Shaheen, Department of Electrical Engineering, University of Kashmir.

---

## Acknowledgements

- [MATLAB](https://www.mathworks.com/) — MathWorks is the leading developer of mathematical computing software for engineers and scientists.
- [pandapower](https://www.pandapower.org/) — Fraunhofer IEE & University of Kassel
- [MATPOWER](https://matpower.org/) — Cornell University
- [PyPSA](https://pypsa.org/) — Karlsruhe Institute of Technology & TU Berlin
