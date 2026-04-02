# MATLAB Setup for Power System Lab

## Requirements

- MATLAB R2020b or later
- Simscape (base)
- Simscape Electrical (formerly SimPowerSystems)
- (Optional) Optimization Toolbox — for Exp 9 (OPF via fmincon)
- (Optional) MATPOWER — free add-on for power flow and OPF

## Verifying Simscape Electrical

```matlab
% Check if Simscape Electrical is installed
ver('simscape')
ver('sps')   % SimPowerSystems / Simscape Electrical

% If the above returns empty, the toolbox is not installed.
% Contact your university's MATLAB administrator for the academic license.
```

## Installing MATPOWER (free, no toolbox needed)

```matlab
% Download from: https://matpower.org/
% Unzip to a folder, then:
addpath(genpath('path/to/matpower'));
savepath;

% Verify:
test_matpower   % Should report all tests passed
```

## Notes on Programmatic Simulink Models

All MATLAB scripts in this lab build Simulink/Simscape models programmatically
using `new_system`, `add_block`, `set_param`, `add_line`, and `sim`. No .mdl or
.slx files are distributed — the .m script IS the model.

This approach:
- Is version-independent (no binary compatibility issues)
- Is diffable and git-friendly (plain text)
- Teaches students the Simulink API, not just the GUI drag-and-drop

After running a script, the model appears in a Simulink window. Students can
inspect it, modify parameters via the GUI, and re-run.
