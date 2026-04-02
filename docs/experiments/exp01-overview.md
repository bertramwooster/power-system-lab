# Experiment 1: Power Simulation and Scripting — SimPowerSystems Models

## Objective

Introduce students to the two simulation environments used throughout this lab:
1. **MATLAB/Simscape Electrical** (formerly SimPowerSystems) — industry-standard, GUI + scripting
2. **Python/pandapower** — open-source, script-only, built on PYPOWER (a MATPOWER port)

By the end of this experiment, students should be able to:
- Create a simple power network (buses, lines, generators, loads) in both environments
- Run a basic power flow and interpret results (bus voltages, line loadings, losses)
- Understand the difference between time-domain simulation (Simscape) and steady-state power flow (pandapower)

## Theory (Key Equations)

### Bus Classification

Every bus in a power system is classified by which two of four quantities are specified:

| Bus type | Known | Unknown |
|----------|-------|---------|
| Slack (swing) | |V|, δ | P, Q |
| PV (generator) | P, |V| | Q, δ |
| PQ (load) | P, Q | |V|, δ |

### Power Flow Equations

For bus i connected to N buses, the injected complex power is:

    Sᵢ = Pᵢ + jQᵢ = Vᵢ Σⱼ (Yᵢⱼ Vⱼ)*

Expanding into real and reactive components:

    Pᵢ = Σⱼ |Vᵢ||Vⱼ|(Gᵢⱼ cos δᵢⱼ + Bᵢⱼ sin δᵢⱼ)
    Qᵢ = Σⱼ |Vᵢ||Vⱼ|(Gᵢⱼ sin δᵢⱼ − Bᵢⱼ cos δᵢⱼ)

where Yᵢⱼ = Gᵢⱼ + jBᵢⱼ is the (i,j) element of the bus admittance matrix, and δᵢⱼ = δᵢ − δⱼ.

These nonlinear algebraic equations are solved iteratively (Newton-Raphson in Exp 8).
In Exp 1, we use the built-in solvers to establish familiarity with the workflow.

### Transmission Line π-Model

A medium-length transmission line is represented as:

    ┌───[Z = R + jωL]───┐
    │                     │
   [Y/2 = jωC/2]       [Y/2 = jωC/2]
    │                     │
    ┴                     ┴

where Z is series impedance per unit length × length, Y is shunt admittance per unit length × length.

## Procedure

### Python Track

1. Install pandapower: `pip install pandapower`
2. Run `exp01_intro_pandapower.py`
3. Observe: bus voltages (p.u.), line loading (%), power losses
4. Modify: change load at Bus 3 from 60 MW to 90 MW, re-run, observe voltage drop
5. Load IEEE 9-bus test case and compare structure

### MATLAB Track

1. Open MATLAB with Simscape Electrical toolbox
2. Run `exp01_simpower_intro.m`
3. A Simulink model opens automatically — inspect the blocks
4. Observe: voltage and current waveforms in Scope blocks
5. Modify: change source voltage, re-run, observe changes

## Expected Outputs

- Python: Printed DataFrames (bus results, line results), saved voltage profile plot
- MATLAB: Simulink model with Scope showing 3-phase voltage/current waveforms; printed RMS values

## Discussion Questions

1. What is the fundamental difference between time-domain simulation (Simscape) and steady-state power flow (pandapower)?
2. Why does the slack bus absorb whatever power mismatch exists in the system?
3. If all bus voltages are 1.0 p.u. and all angles are 0°, what does this "flat start" imply physically?
4. How does the π-model approximate a distributed-parameter transmission line?
