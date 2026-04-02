"""
==============================================================================
Experiment 1: Power Simulation and Scripting — Introduction to pandapower
==============================================================================
Course  : PCC-EE804L Advanced Power System Simulation and Scripting Lab
Semester: 8th, B.Tech Electrical Engineering, University of Kashmir

Objective
---------
    Introduce the pandapower framework by building a 3-bus power system from
    scratch, running Newton-Raphson power flow, and interpreting results.
    Then load the IEEE 9-bus (WSCC) test case to demonstrate the library's
    built-in benchmark networks.

Theory
------
    pandapower solves the steady-state AC power flow equations:

        P_i = sum_j |V_i||V_j| (G_ij cos(d_ij) + B_ij sin(d_ij))
        Q_i = sum_j |V_i||V_j| (G_ij sin(d_ij) - B_ij cos(d_ij))

    using the Newton-Raphson method (details in Experiment 8). Here we treat
    the solver as a black box and focus on network construction and result
    interpretation.

Requirements
------------
    pip install pandapower numpy matplotlib pandas

Author  : Prof. Mohd Aarish Shaheen, Dept. of Electrical Engineering, Univ. of Kashmir
Date    : April 2026
==============================================================================
"""

import pandapower as pp
import pandapower.networks as pn
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


# ============================================================================
# PART A: Build a 3-bus system from scratch
# ============================================================================

def create_three_bus_system():
    """
    Create a simple 3-bus power system:

        Bus 1 (Slack, 110 kV) ---- Line 1-2 (50 km) ---- Bus 2 (PV, 110 kV)
              |                                                  |
              |                                                  |
         Line 1-3 (70 km)                                 Line 2-3 (30 km)
              |                                                  |
              |                                                  |
        Bus 3 (PQ, 110 kV) ----- Load: 60 MW + j20 Mvar -------+

    Bus 1: External grid (slack), V = 1.0 p.u.
    Bus 2: Generator, P = 40 MW, V = 1.02 p.u.
    Bus 3: Load bus, P_load = 60 MW, Q_load = 20 Mvar
    """
    # Step 1: Create an empty network (50 Hz, Indian standard)
    net = pp.create_empty_network(name="3-Bus Tutorial System", f_hz=50.0)

    # Step 2: Create buses
    #   vn_kv: rated voltage in kV (base voltage for per-unit conversion)
    bus1 = pp.create_bus(net, vn_kv=110.0, name="Bus 1 (Slack)")
    bus2 = pp.create_bus(net, vn_kv=110.0, name="Bus 2 (PV)")
    bus3 = pp.create_bus(net, vn_kv=110.0, name="Bus 3 (PQ)")

    # Step 3: Create external grid (slack bus)
    #   vm_pu: voltage magnitude setpoint in per-unit
    #   The slack bus balances P and Q to satisfy KCL for the whole system.
    pp.create_ext_grid(net, bus=bus1, vm_pu=1.0, name="Grid Connection")

    # Step 4: Create generator at Bus 2 (PV bus)
    #   p_mw:  scheduled real power injection
    #   vm_pu: voltage magnitude setpoint
    pp.create_gen(net, bus=bus2, p_mw=40.0, vm_pu=1.02, name="Generator G1")

    # Step 5: Create load at Bus 3 (PQ bus)
    pp.create_load(net, bus=bus3, p_mw=60.0, q_mvar=20.0, name="Load L1")

    # Step 6: Create transmission lines
    #   std_type: standard conductor from pandapower's built-in library
    #   "149-AL1/24-ST1A 110.0" is an ACSR conductor rated for 110 kV
    #   Parameters per km: r = 0.194 Ω, x = 0.381 Ω, c = 9.38 nF, max_i = 0.535 kA
    pp.create_line(net, from_bus=bus1, to_bus=bus2, length_km=50.0,
                   std_type="149-AL1/24-ST1A 110.0", name="Line 1-2")
    pp.create_line(net, from_bus=bus2, to_bus=bus3, length_km=30.0,
                   std_type="149-AL1/24-ST1A 110.0", name="Line 2-3")
    pp.create_line(net, from_bus=bus1, to_bus=bus3, length_km=70.0,
                   std_type="149-AL1/24-ST1A 110.0", name="Line 1-3")

    return net


def run_and_display(net, title="Power Flow Results"):
    """Run Newton-Raphson power flow and display results."""
    # Run power flow (NR method, flat start)
    pp.runpp(net, algorithm='nr', init='flat', enforce_q_lims=False)

    print(f"\n{'='*72}")
    print(f"  {title}")
    print(f"{'='*72}")

    # Bus results: voltage magnitude (p.u.), angle (deg), P & Q injections (MW/Mvar)
    print("\n--- Bus Results ---")
    bus_res = net.res_bus.copy()
    bus_res.index = net.bus['name']
    print(bus_res[['vm_pu', 'va_degree', 'p_mw', 'q_mvar']].to_string(float_format='%.4f'))

    # Line results: loading (%), P & Q flow, losses
    print("\n--- Line Results ---")
    line_res = net.res_line.copy()
    line_res.index = net.line['name']
    cols = ['p_from_mw', 'q_from_mvar', 'p_to_mw', 'q_to_mvar',
            'pl_mw', 'ql_mvar', 'loading_percent']
    print(line_res[cols].to_string(float_format='%.4f'))

    # Summary
    total_loss_mw = net.res_line['pl_mw'].sum()
    total_loss_mvar = net.res_line['ql_mvar'].sum()
    print(f"\nTotal system losses: {total_loss_mw:.4f} MW + j{total_loss_mvar:.4f} Mvar")

    return net


def plot_voltage_profile(net, filename="exp01_voltage_profile.png"):
    """Bar chart of bus voltage magnitudes."""
    fig, ax = plt.subplots(figsize=(8, 5))

    bus_names = net.bus['name'].values
    vm_pu = net.res_bus['vm_pu'].values

    colors = ['#2ecc71' if 0.95 <= v <= 1.05 else '#e74c3c' for v in vm_pu]
    bars = ax.bar(bus_names, vm_pu, color=colors, edgecolor='black', linewidth=0.8)

    # Acceptable voltage band (±5%)
    ax.axhline(y=1.05, color='gray', linestyle='--', linewidth=0.8, label='±5% limits')
    ax.axhline(y=0.95, color='gray', linestyle='--', linewidth=0.8)
    ax.axhline(y=1.00, color='black', linestyle='-', linewidth=0.5, alpha=0.3)

    ax.set_ylabel('Voltage Magnitude (p.u.)')
    ax.set_title('Bus Voltage Profile — 3-Bus System')
    ax.set_ylim(0.90, 1.10)
    ax.legend()

    # Annotate bars
    for bar, v in zip(bars, vm_pu):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.003,
                f'{v:.4f}', ha='center', va='bottom', fontsize=10)

    plt.tight_layout()
    plt.savefig(filename, dpi=150)
    print(f"\nVoltage profile saved to: {filename}")
    plt.show()


# ============================================================================
# PART B: Load IEEE 9-Bus (WSCC) Test Case
# ============================================================================

def demo_ieee_9bus():
    """
    The IEEE 9-bus system (Western System Coordinating Council benchmark):
        - 3 generators, 3 loads, 9 buses, 9 branches
        - Widely used for transient stability studies
        - Data originally from Anderson & Fouad, "Power System Control and Stability"

    pandapower includes this (and many others) as built-in networks.
    """
    net = pn.case9()

    print(f"\n{'='*72}")
    print("  IEEE 9-Bus (WSCC) System — Loaded from pandapower.networks")
    print(f"{'='*72}")
    print(f"\n  Buses: {len(net.bus)}")
    print(f"  Lines: {len(net.line)}")
    print(f"  Transformers: {len(net.trafo)}")
    print(f"  Generators: {len(net.gen) + len(net.ext_grid)}")
    print(f"  Loads: {len(net.load)}")

    # Run power flow
    pp.runpp(net, algorithm='nr')

    print("\n--- Bus Results (IEEE 9-Bus) ---")
    print(net.res_bus[['vm_pu', 'va_degree']].to_string(float_format='%.4f'))

    print("\n--- Generator Dispatch ---")
    if len(net.ext_grid) > 0:
        print("  Ext. Grid (Slack):")
        print(net.res_ext_grid[['p_mw', 'q_mvar']].to_string(float_format='%.4f'))
    if len(net.gen) > 0:
        print("  Generators:")
        print(net.res_gen[['p_mw', 'q_mvar']].to_string(float_format='%.4f'))

    return net


# ============================================================================
# PART C: Sensitivity Analysis — What happens when load increases?
# ============================================================================

def load_sensitivity_study(net_func, bus_idx=2, load_range_mw=None):
    """
    Vary the load at a specific bus and track voltage magnitude.
    This is a precursor to the full PV (nose) curve analysis in Experiment 7.

    Parameters
    ----------
    net_func : callable
        Function that returns a fresh network (to avoid stale state).
    bus_idx : int
        Index of the bus whose load to vary.
    load_range_mw : array-like
        Range of real power loads to sweep.
    """
    if load_range_mw is None:
        load_range_mw = np.arange(10, 151, 5)

    voltages = []
    converged = []

    for p in load_range_mw:
        net = net_func()
        net.load.at[0, 'p_mw'] = p  # modify load
        try:
            pp.runpp(net, algorithm='nr', init='flat')
            voltages.append(net.res_bus.at[bus_idx, 'vm_pu'])
            converged.append(True)
        except pp.LoadflowNotConverged:
            voltages.append(np.nan)
            converged.append(False)

    # Plot
    fig, ax = plt.subplots(figsize=(9, 5))
    mask = np.array(converged)
    ax.plot(load_range_mw[mask], np.array(voltages)[mask],
            'o-', color='#3498db', markersize=4, linewidth=1.5, label='V at Bus 3')

    if not all(mask):
        collapse_mw = load_range_mw[~mask][0] if any(~mask) else None
        if collapse_mw:
            ax.axvline(x=collapse_mw, color='red', linestyle='--',
                       label=f'Non-convergence at {collapse_mw} MW')

    ax.axhline(y=0.95, color='gray', linestyle=':', label='V = 0.95 p.u.')
    ax.set_xlabel('Load at Bus 3 (MW)')
    ax.set_ylabel('Voltage Magnitude at Bus 3 (p.u.)')
    ax.set_title('Load Sensitivity Study — Voltage vs. Load at Bus 3')
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    filename = "exp01_load_sensitivity.png"
    plt.savefig(filename, dpi=150)
    print(f"\nLoad sensitivity plot saved to: {filename}")
    plt.show()


# ============================================================================
# PART D: Inspect Network Data Structures
# ============================================================================

def inspect_network_internals(net):
    """
    pandapower stores everything in pandas DataFrames. This function
    exposes the internal data structures so students understand what
    the solver actually sees.
    """
    print(f"\n{'='*72}")
    print("  Internal Data Structures")
    print(f"{'='*72}")

    print("\n--- net.bus (Bus Data) ---")
    print(net.bus.to_string())

    print("\n--- net.line (Line Data) ---")
    print(net.line.to_string())

    print("\n--- net.gen (Generator Data) ---")
    print(net.gen.to_string())

    print("\n--- net.load (Load Data) ---")
    print(net.load.to_string())

    # The internal admittance matrix (Y-bus) can be extracted after runpp
    if net.res_bus.shape[0] > 0:
        from pandapower.pd2ppc import _pd2ppc
        from pandapower.pypower.makeYbus import makeYbus

        # Convert pandapower to PYPOWER internal format
        ppc, _ = _pd2ppc(net)
        Ybus, _, _ = makeYbus(ppc['baseMVA'], ppc['bus'], ppc['branch'])

        print("\n--- Y-bus Matrix (Complex Admittance) ---")
        Ybus_dense = Ybus.toarray()
        n = Ybus_dense.shape[0]
        for i in range(n):
            row = "  ".join([f"{Ybus_dense[i, j]:12.4f}" for j in range(n)])
            print(f"  Row {i}: {row}")


# ============================================================================
# MAIN — Run all parts
# ============================================================================

if __name__ == "__main__":

    print("=" * 72)
    print("  EXPERIMENT 1: Introduction to Power System Simulation (pandapower)")
    print("  PCC-EE804L, University of Kashmir")
    print("=" * 72)

    # Part A: Build and solve 3-bus system
    net = create_three_bus_system()
    run_and_display(net, title="Part A: 3-Bus System Power Flow")
    plot_voltage_profile(net)

    # Part B: IEEE 9-bus test case
    net9 = demo_ieee_9bus()

    # Part C: Load sensitivity
    print(f"\n{'='*72}")
    print("  Part C: Load Sensitivity Study")
    print(f"{'='*72}")
    load_sensitivity_study(create_three_bus_system, bus_idx=2)

    # Part D: Internal data structures
    net_inspect = create_three_bus_system()
    pp.runpp(net_inspect)
    inspect_network_internals(net_inspect)

    print(f"\n{'='*72}")
    print("  Experiment 1 Complete.")
    print("  Next: Experiment 2 — Models of Power Circuit Devices")
    print(f"{'='*72}")
