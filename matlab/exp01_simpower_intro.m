%% ========================================================================
%  Experiment 1: Power Simulation and Scripting — SimPowerSystems Models
%  ========================================================================
%  Course  : PCC-EE804L Advanced Power System Simulation and Scripting Lab
%  Semester: 8th, B.Tech Electrical Engineering, University of Kashmir
%
%  Objective
%  ---------
%  Introduce Simscape Electrical (formerly SimPowerSystems) by building
%  a simple three-phase power system model PROGRAMMATICALLY — no manual
%  drag-and-drop. The script creates a Simulink model from scratch,
%  populates it with blocks, connects them, runs a time-domain simulation,
%  and extracts measurement data.
%
%  Requirements
%  ------------
%  MATLAB R2020b+, Simscape, Simscape Electrical
%
%  Author  : Prof. Mohd Aarish Shaheen, Dept. of EE, Univ. of Kashmir
%  Date    : April 2026
%% ========================================================================

clear; clc; close all;

%% ========================================================================
%  PART A: Programmatic Model Construction
%  ========================================================================
%  We build a system:
%     Three-Phase Source --> PI Section Line --> Three-Phase Load
%  with voltage and current measurements at the source and load ends.

mdl = 'exp01_three_phase_system';

% Close model if it's already open (avoids error on re-run)
if bdIsLoaded(mdl)
    close_system(mdl, 0);
end

% Create a new blank Simulink model
new_system(mdl);
open_system(mdl);

fprintf('Building model: %s\n', mdl);

%% --- Add Powergui (MANDATORY for all SimPowerSystems models) ---
%  Powergui sets the solver type. 'Continuous' uses Simulink's ODE solver;
%  'Discrete' uses a fixed-step solver at a specified sample time.
add_block('powerlib/powergui', [mdl '/powergui'], ...
    'SimulationMode', 'Continuous', ...
    'Position', [50 30 150 70]);

%% --- Three-Phase Source (represents the grid / slack bus) ---
%  11 kV line-to-line, 50 Hz, internal impedance included.
add_block('powerlib/Electrical Sources/Three-Phase Source', ...
    [mdl '/Source'], ...
    'Voltage',       '11000', ...          % Peak line-neutral voltage (V)
    'PhaseAngle',    '0', ...
    'Frequency',     '50', ...             % Indian grid frequency
    'InternalConnection', 'Yg', ...        % Star-grounded
    'SourceImpedance', 'on', ...
    'R',             '0.5', ...
    'L',             '0.01', ...
    'Position',      [100 150 160 210]);

%% --- Three-Phase V-I Measurement (Source Side) ---
%  Measures line-to-ground voltages and line currents.
add_block('powerlib/Measurements/Three-Phase V-I Measurement', ...
    [mdl '/VI_Source'], ...
    'VoltageMeasurement', 'phase-to-ground', ...
    'CurrentMeasurement', 'yes', ...
    'Position', [250 150 310 210]);

%% --- Three-Phase PI Section Line ---
%  Models a medium-length transmission line using the lumped π-circuit.
%  Parameters for a typical 11 kV overhead line:
%    R1 = 0.01273 Ω/km, L1 = 0.9337e-3 H/km, C1 = 12.74e-9 F/km
%    Length = 20 km
add_block('powerlib/Elements/Three-Phase PI Section Line', ...
    [mdl '/Line'], ...
    'Frequency',    '50', ...
    'Resistance',   '0.01273', ...         % Ω/km (positive sequence)
    'Inductance',   '0.9337e-3', ...       % H/km
    'Capacitance',  '12.74e-9', ...        % F/km
    'Length',        '20', ...             % km
    'Position',     [400 150 500 210]);

%% --- Three-Phase V-I Measurement (Load Side) ---
add_block('powerlib/Measurements/Three-Phase V-I Measurement', ...
    [mdl '/VI_Load'], ...
    'VoltageMeasurement', 'phase-to-ground', ...
    'CurrentMeasurement', 'yes', ...
    'Position', [580 150 640 210]);

%% --- Three-Phase Series RLC Load ---
%  60 MW + j20 Mvar load at 11 kV (star-connected, grounded neutral).
%  NominalVoltage is line-to-line RMS.
add_block('powerlib/Elements/Three-Phase Series RLC Load', ...
    [mdl '/Load'], ...
    'NominalVoltage',  '11000', ...
    'NominalFrequency','50', ...
    'ActivePower',     '60e6', ...
    'InductivePower',  '20e6', ...
    'CapacitivePower', '0', ...
    'Configuration',   'Y (grounded)', ...
    'Position',        [750 150 830 210]);

%% --- Scopes (to visualize waveforms) ---
%  Scope for source-side voltage
add_block('simulink/Sinks/Scope', [mdl '/Scope_V_Source'], ...
    'Position', [300 270 340 310]);

%  Scope for load-side voltage
add_block('simulink/Sinks/Scope', [mdl '/Scope_V_Load'], ...
    'Position', [630 270 670 310]);

%  Scope for source-side current
add_block('simulink/Sinks/Scope', [mdl '/Scope_I_Source'], ...
    'Position', [300 330 340 370]);

%% --- To Workspace blocks (export data for plotting) ---
add_block('simulink/Sinks/To Workspace', [mdl '/V_Source_WS'], ...
    'VariableName', 'V_source', ...
    'SaveFormat', 'Timeseries', ...
    'Position', [300 400 380 430]);

add_block('simulink/Sinks/To Workspace', [mdl '/V_Load_WS'], ...
    'VariableName', 'V_load', ...
    'SaveFormat', 'Timeseries', ...
    'Position', [630 400 710 430]);

%% --- Wire everything together ---
%  SimPowerSystems uses specialized "electrical" ports. The port labelling
%  convention: for Three-Phase Source, port 1 = ABC output, port 2 = neutral.
%  For PI Section Line, port 1 = sending end, port 2 = receiving end.

fprintf('Connecting blocks...\n');

% Source --> VI_Source (electrical connection, 3-phase bus)
add_line(mdl, 'Source/1',     'VI_Source/1', 'autoroute', 'on');

% VI_Source --> Line (sending end)
add_line(mdl, 'VI_Source/1',  'Line/1',      'autoroute', 'on');

% Line --> VI_Load (receiving end)
add_line(mdl, 'Line/2',       'VI_Load/1',   'autoroute', 'on');

% VI_Load --> Load
add_line(mdl, 'VI_Load/1',    'Load/1',      'autoroute', 'on');

% Measurement signal outputs to scopes and workspace
% (These are Simulink signal ports, not electrical ports)
add_line(mdl, 'VI_Source/3',  'Scope_V_Source/1', 'autoroute', 'on');  % Vabc
add_line(mdl, 'VI_Source/4',  'Scope_I_Source/1', 'autoroute', 'on');  % Iabc
add_line(mdl, 'VI_Load/3',   'Scope_V_Load/1',   'autoroute', 'on');

add_line(mdl, 'VI_Source/3',  'V_Source_WS/1',    'autoroute', 'on');
add_line(mdl, 'VI_Load/3',   'V_Load_WS/1',      'autoroute', 'on');

%% --- Set simulation parameters ---
set_param(mdl, ...
    'StopTime',    '0.1', ...       % 5 cycles at 50 Hz
    'Solver',      'ode23tb', ...   % Stiff solver (good for power systems)
    'MaxStep',     '1e-4', ...      % Adequate for 50 Hz waveforms
    'RelTol',      '1e-4');

fprintf('Model built successfully. Running simulation...\n');

%% ========================================================================
%  PART B: Run Simulation
%  ========================================================================

simOut = sim(mdl);

fprintf('Simulation complete.\n\n');

%% ========================================================================
%  PART C: Extract and Plot Results
%  ========================================================================

% Extract timeseries from workspace
t = V_source.Time;
v_src = V_source.Data;     % 3-phase source voltage (V)
v_ld  = V_load.Data;       % 3-phase load voltage (V)

figure('Name', 'Exp 1: Source and Load Voltages', 'Position', [100 100 900 600]);

subplot(2,1,1);
plot(t*1000, v_src/1000, 'LineWidth', 1.2);
xlabel('Time (ms)');
ylabel('Voltage (kV)');
title('Source-Side Three-Phase Voltage');
legend('V_a', 'V_b', 'V_c');
grid on;

subplot(2,1,2);
plot(t*1000, v_ld/1000, 'LineWidth', 1.2);
xlabel('Time (ms)');
ylabel('Voltage (kV)');
title('Load-Side Three-Phase Voltage');
legend('V_a', 'V_b', 'V_c');
grid on;

sgtitle('Experiment 1: Three-Phase Voltage Waveforms');
saveas(gcf, 'exp01_voltage_waveforms.png');
fprintf('Waveform plot saved: exp01_voltage_waveforms.png\n');

%% --- Compute RMS values ---
%  RMS over the last full cycle (last 20 ms for 50 Hz)
T_cycle = 1/50;                         % Period = 20 ms
idx_last_cycle = t >= (t(end) - T_cycle);
v_src_rms = sqrt(mean(v_src(idx_last_cycle, :).^2, 1));
v_ld_rms  = sqrt(mean(v_ld(idx_last_cycle, :).^2, 1));

fprintf('\n--- RMS Voltages (Phase-to-Ground) ---\n');
fprintf('  Source: Va = %.1f V, Vb = %.1f V, Vc = %.1f V\n', v_src_rms);
fprintf('  Load  : Va = %.1f V, Vb = %.1f V, Vc = %.1f V\n', v_ld_rms);
fprintf('  Source L-L RMS: %.1f V (%.3f kV)\n', v_src_rms(1)*sqrt(3), v_src_rms(1)*sqrt(3)/1000);
fprintf('  Load   L-L RMS: %.1f V (%.3f kV)\n', v_ld_rms(1)*sqrt(3), v_ld_rms(1)*sqrt(3)/1000);

% Voltage drop (percentage)
v_drop_pct = (1 - mean(v_ld_rms)/mean(v_src_rms)) * 100;
fprintf('\n  Voltage drop across line: %.2f%%\n', v_drop_pct);

%% ========================================================================
%  PART D: Demonstrate Parameter Sweep (Scripting Power)
%  ========================================================================
%  Sweep load from 20 MW to 120 MW in steps and record voltage at load bus.
%  This demonstrates the advantage of scripting over manual GUI interaction.

fprintf('\n--- Part D: Load Sweep (Scripting Demo) ---\n');

P_load_sweep = 20e6 : 10e6 : 120e6;   % 20 MW to 120 MW
V_load_rms_sweep = zeros(size(P_load_sweep));

for k = 1:length(P_load_sweep)
    % Change load active power
    set_param([mdl '/Load'], 'ActivePower', num2str(P_load_sweep(k)));
    
    % Re-run simulation
    simOut_k = sim(mdl);
    
    % Extract load voltage RMS (phase A, last cycle)
    t_k = V_load.Time;
    v_k = V_load.Data(:, 1);
    idx_k = t_k >= (t_k(end) - T_cycle);
    V_load_rms_sweep(k) = sqrt(mean(v_k(idx_k).^2));
end

% Restore original load
set_param([mdl '/Load'], 'ActivePower', '60e6');

% Plot voltage vs load
figure('Name', 'Exp 1: Load Sensitivity', 'Position', [200 200 700 450]);
plot(P_load_sweep/1e6, V_load_rms_sweep*sqrt(3)/1000, 'o-b', 'LineWidth', 1.5, 'MarkerSize', 6);
xlabel('Active Power Load (MW)');
ylabel('Load Bus L-L Voltage (kV)');
title('Voltage vs. Load — SimPowerSystems Parameter Sweep');
grid on;
yline(11*0.95, '--r', 'V_{min} = 0.95 p.u.');
yline(11, ':k', 'V_{nom} = 11 kV');
saveas(gcf, 'exp01_load_sensitivity.png');
fprintf('Load sensitivity plot saved: exp01_load_sensitivity.png\n');

%% ========================================================================
%  PART E: Equivalent with MATPOWER (if installed)
%  ========================================================================

if exist('runpf', 'file')
    fprintf('\n--- Part E: MATPOWER Cross-Validation ---\n');
    
    % Define the same 3-bus system in MATPOWER format
    mpc = struct();
    mpc.version = '2';
    mpc.baseMVA = 100;
    
    %  bus_i type Pd   Qd   Gs Bs area Vm    Va baseKV zone Vmax Vmin
    mpc.bus = [
        1    3    0    0    0  0  1   1.0   0  110    1   1.06  0.94;
        2    2    0    0    0  0  1   1.02  0  110    1   1.06  0.94;
        3    1    60   20   0  0  1   1.0   0  110    1   1.06  0.94;
    ];
    
    %  fbus tbus r       x       b     rateA rateB rateC ratio angle status angmin angmax
    mpc.branch = [
        1  2  0.00527  0.01578  0.01050  250  250  250  0  0  1  -360  360;
        2  3  0.00316  0.00947  0.00630  250  250  250  0  0  1  -360  360;
        1  3  0.00737  0.02205  0.01470  250  250  250  0  0  1  -360  360;
    ];
    %  Note: r, x in p.u. on 100 MVA base; b = total line charging (p.u.)
    %  For 149-AL1/24-ST1A @ 110 kV: Z_base = 110^2/100 = 121 Ω
    %  r = 0.194 * L / 121, x = 0.381 * L / 121, b = 2*pi*50 * 12.74e-9 * L * 121
    
    %  bus Pg   Qg   Qmax  Qmin  Vg    mBase status Pmax Pmin
    mpc.gen = [
        1  0    0    999  -999  1.0   100   1   999  0;
        2  40   0    100  -100  1.02  100   1   100  0;
    ];
    
    mpc.gencost = [
        2  0  0  3  0.01  10  100;
        2  0  0  3  0.02  15  200;
    ];
    
    results = runpf(mpc);
    
    fprintf('\nMATPOWER Bus Voltages:\n');
    fprintf('  Bus 1: |V| = %.4f p.u., angle = %.2f deg\n', results.bus(1,8), results.bus(1,9));
    fprintf('  Bus 2: |V| = %.4f p.u., angle = %.2f deg\n', results.bus(2,8), results.bus(2,9));
    fprintf('  Bus 3: |V| = %.4f p.u., angle = %.2f deg\n', results.bus(3,8), results.bus(3,9));
else
    fprintf('\n--- Part E: MATPOWER not installed. Skipping cross-validation. ---\n');
    fprintf('  Install from https://matpower.org/ for power flow comparison.\n');
end

%% ========================================================================
fprintf('\n========================================\n');
fprintf('  Experiment 1 Complete.\n');
fprintf('  Next: Experiment 2 — Circuit Device Models\n');
fprintf('========================================\n');
