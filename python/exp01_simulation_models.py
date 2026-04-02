"""
==============================================================================
Experiment 1: Survey of SimPowerSystems Models (Python Track)
==============================================================================
Course  : PCC-EE804L Advanced Power System Simulation and Scripting Lab
Semester: 8th, B.Tech EE, University of Kashmir

Six case studies, each matched 1:1 with the MATLAB track.
Each case introduces a power system model AND a simulation skill.

Case A: SMIB system           — basic pandapower + scipy swing equation
Case B: Transformer OC/SC     — parameter extraction and verification
Case C: Shunt compensation    — parametric sweep (voltage vs Q_shunt)
Case D: Fault analysis        — IEC 60909 + manual sequence networks
Case E: Motor DOL start       — d-q model ODE via scipy BDF solver
Case F: Cap switching          — why EMT matters (what power flow misses)

Requirements: pip install pandapower numpy scipy matplotlib
==============================================================================
"""
import pandapower as pp
import pandapower.networks as pn
import pandapower.shortcircuit as sc
import numpy as np
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt


def case_a_smib():
    """Case A: SMIB — 4-bus system with gen, transformer, line, infinite bus."""
    net = pp.create_empty_network(sn_mva=100, f_hz=50)
    b1 = pp.create_bus(net, 220, "HV Inf Bus")
    b2 = pp.create_bus(net, 220, "Line End")
    b3 = pp.create_bus(net, 22,  "Gen Terminal")

    pp.create_ext_grid(net, b1, vm_pu=1.0)
    pp.create_gen(net, b3, p_mw=100, vm_pu=1.05)
    pp.create_line_from_parameters(net, b1, b2, length_km=100,
        r_ohm_per_km=0.05, x_ohm_per_km=0.5,
        c_nf_per_km=10, max_i_ka=1)
    pp.create_transformer_from_parameters(net, b2, b3,
        sn_mva=150, vn_hv_kv=220, vn_lv_kv=22,
        vkr_percent=0.5, vk_percent=12,
        pfe_kw=50, i0_percent=0.05, shift_degree=30)

    pp.runpp(net, algorithm='nr')
    print("=== Case A: SMIB Power Flow ===")
    print(net.res_bus[['vm_pu', 'va_degree', 'p_mw', 'q_mvar']])

    # Swing equation: M d²δ/dt² = Pm - Pe_max sin(δ)
    H, Pm, Pe_max = 5.0, 0.8, 2.0  # p.u. on machine base
    ws = 2 * np.pi * 50
    def swing(t, y):
        return [y[1], (ws / (2 * H)) * (Pm - Pe_max * np.sin(y[0]))]

    d0 = np.arcsin(Pm / Pe_max)  # initial operating angle
    sol = solve_ivp(swing, [0, 2], [d0 + 0.1, 0], max_step=0.001)

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(sol.t, np.degrees(sol.y[0]), 'b-', linewidth=1.5)
    ax.set(xlabel='Time (s)', ylabel='δ (degrees)',
           title='Case A: Rotor Angle Oscillation (small perturbation from δ₀)')
    ax.axhline(np.degrees(d0), color='gray', ls=':', label=f'δ₀ = {np.degrees(d0):.1f}°')
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('case_a_swing.png', dpi=150)
    print(f"  Equilibrium angle δ₀ = {np.degrees(d0):.2f}°")
    return net


def case_b_transformer():
    """Case B: Transformer — verify equivalent circuit parameters."""
    net = pp.create_empty_network(sn_mva=100, f_hz=50)
    b_hv = pp.create_bus(net, 110, "HV")
    b_lv = pp.create_bus(net, 11, "LV")
    pp.create_ext_grid(net, b_hv, vm_pu=1.0)
    tid = pp.create_transformer_from_parameters(net, b_hv, b_lv,
        sn_mva=50, vn_hv_kv=110, vn_lv_kv=11,
        vkr_percent=1.0, vk_percent=10,
        pfe_kw=30, i0_percent=0.1)

    # OC test: no load on LV
    pp.runpp(net)
    print("\n=== Case B: Transformer ===")
    print(f"  No-load LV voltage: {net.res_bus.at[1, 'vm_pu']:.4f} p.u.")

    # Full load
    pp.create_load(net, b_lv, p_mw=50, q_mvar=0)
    pp.runpp(net)
    print(f"  Full-load LV voltage: {net.res_bus.at[1, 'vm_pu']:.4f} p.u.")
    print(f"  Voltage regulation = {(1 - net.res_bus.at[1, 'vm_pu']) * 100:.2f}%")
    print(f"  Parameters: Vk = {net.trafo.at[tid, 'vk_percent']}%, "
          f"Vkr = {net.trafo.at[tid, 'vkr_percent']}%, "
          f"Pfe = {net.trafo.at[tid, 'pfe_kw']} kW, "
          f"I0 = {net.trafo.at[tid, 'i0_percent']}%")


def case_c_compensation():
    """Case C: Shunt compensation — voltage vs reactive power sweep."""
    q_range = np.arange(-30, 30, 2)  # Mvar: negative = capacitive
    v_bus = []
    for q_sh in q_range:
        net = pp.create_empty_network(sn_mva=100, f_hz=50)
        b1 = pp.create_bus(net, 110)
        b2 = pp.create_bus(net, 110)
        pp.create_ext_grid(net, b1, vm_pu=1.0)
        pp.create_line_from_parameters(net, b1, b2, length_km=80,
            r_ohm_per_km=0.1, x_ohm_per_km=0.4,
            c_nf_per_km=10, max_i_ka=1)
        pp.create_load(net, b2, p_mw=80, q_mvar=40)
        if abs(q_sh) > 0.1:
            pp.create_shunt(net, b2, q_mvar=q_sh)
        pp.runpp(net)
        v_bus.append(net.res_bus.at[1, 'vm_pu'])

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(q_range, v_bus, 'o-', color='#3b82f6', markersize=3, linewidth=1.5)
    ax.axhline(0.95, color='red', ls='--', lw=0.8, label='V = 0.95 p.u.')
    ax.axhline(1.05, color='red', ls='--', lw=0.8, label='V = 1.05 p.u.')
    ax.set(xlabel='Q_shunt (Mvar, -ve = capacitive)', ylabel='V at load bus (p.u.)',
           title='Case C: Voltage vs Shunt Compensation')
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('case_c_compensation.png', dpi=150)
    print("\n=== Case C: Compensation ===")
    print(f"  V range: {min(v_bus):.4f} to {max(v_bus):.4f} p.u.")


def case_d_fault():
    """Case D: Fault analysis — IEC 60909 + manual sequence networks."""
    net = pn.case9()
    print("\n=== Case D: Fault Analysis (IEEE 9-bus) ===")
    sc.calc_sc(net, bus=4, fault='3ph')
    print(f"  3-phase fault at Bus 5: Ik'' = {net.res_bus_sc.at[4, 'ikss_ka']:.3f} kA")
    sc.calc_sc(net, bus=4, fault='2ph')
    print(f"  Line-line fault at Bus 5: Ik'' = {net.res_bus_sc.at[4, 'ikss_ka']:.3f} kA")

    # Manual SLG calculation via sequence networks
    Z1 = 0.05 + 0.25j  # Positive sequence Thevenin impedance (p.u.)
    Z2 = 0.05 + 0.25j  # Negative sequence (= Z1 for round rotor)
    Z0 = 0.10 + 0.40j  # Zero sequence
    Vf = 1.0            # Pre-fault voltage (p.u.)
    If_slg = 3 * Vf / (Z1 + Z2 + Z0)
    print(f"  SLG fault (manual):  |If| = {abs(If_slg):.3f} p.u.")
    print(f"    (I0 = I1 = I2 = {abs(If_slg)/3:.3f} p.u.)")


def case_e_motor():
    """Case E: Motor DOL start — d-q model ODE."""
    # Parameters in p.u. on motor base
    Rs, Rr, Xs, Xr, Xm = 0.01, 0.02, 0.1, 0.12, 3.0
    H = 0.5   # Inertia constant (seconds)
    TL = 0.5  # Load torque (p.u.)
    Vs = 1.0  # Supply voltage (p.u.)
    ws = 2 * np.pi * 50

    def motor_ode(t, y):
        psi_ds, psi_qs, psi_dr, psi_qr, wr = y
        s = 1 - wr  # slip

        D = Xs * Xr - Xm**2
        ids = (Xr * psi_ds - Xm * psi_dr) / D
        iqs = (Xr * psi_qs - Xm * psi_qr) / D
        idr = (-Xm * psi_ds + Xs * psi_dr) / D
        iqr = (-Xm * psi_qs + Xs * psi_qr) / D

        # Stator equations (synchronous reference frame)
        d_psi_ds = ws * (0  - Rs * ids + psi_qs)
        d_psi_qs = ws * (Vs - Rs * iqs - psi_ds)
        # Rotor equations
        d_psi_dr = ws * (0 - Rr * idr + s * psi_qr)
        d_psi_qr = ws * (0 - Rr * iqr - s * psi_dr)
        # Electromagnetic torque and mechanical equation
        Te = psi_ds * iqs - psi_qs * ids
        d_wr = (Te - TL) / (2 * H)

        return [d_psi_ds, d_psi_qs, d_psi_dr, d_psi_qr, d_wr]

    sol = solve_ivp(motor_ode, [0, 3], [0, 0, 0, 0, 0],
                    method='BDF', max_step=5e-4)

    D = Xs * Xr - Xm**2
    Is = np.sqrt(((Xr * sol.y[0] - Xm * sol.y[2]) / D)**2 +
                 ((Xr * sol.y[1] - Xm * sol.y[3]) / D)**2)
    Te = (sol.y[0] * (Xr * sol.y[1] - Xm * sol.y[3]) / D -
          sol.y[1] * (Xr * sol.y[0] - Xm * sol.y[2]) / D)

    fig, axes = plt.subplots(3, 1, figsize=(9, 7), sharex=True)
    axes[0].plot(sol.t, sol.y[4], 'b-', lw=1)
    axes[0].set_ylabel('ωr (p.u.)')
    axes[0].set_title('Case E: DOL Motor Starting — d-q Model')
    axes[1].plot(sol.t, Is, 'r-', lw=0.7)
    axes[1].set_ylabel('|Is| (p.u.)')
    axes[2].plot(sol.t, Te, 'g-', lw=0.7)
    axes[2].set(xlabel='Time (s)', ylabel='Te (p.u.)')
    for ax in axes:
        ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('case_e_motor.png', dpi=150)
    print(f"\n=== Case E: Motor Start ===")
    print(f"  Peak starting current: {np.max(Is):.2f} p.u.")
    print(f"  Final speed: {sol.y[4, -1]:.4f} p.u.")


def case_f_transient():
    """Case F: Capacitor switching — what power flow CANNOT see."""
    R, L, Cap = 0.5, 0.01, 100e-6  # Ohm, H, F
    Vm = 11e3 * np.sqrt(2 / 3)     # Peak phase voltage
    w = 2 * np.pi * 50
    f0 = 1 / (2 * np.pi * np.sqrt(L * Cap))

    print(f"\n=== Case F: Cap Switching ===")
    print(f"  Natural frequency f₀ = 1/(2π√LC) = {f0:.0f} Hz")
    print(f"  Worst case: switching at voltage zero → max overshoot ≈ 2×V_peak")

    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    for idx, phi_deg in enumerate([0, 90]):
        phi = np.radians(phi_deg)
        def cap_ode(t, y):
            i, vc = y
            di = (Vm * np.sin(w * t + phi) - R * i - vc) / L
            dvc = i / Cap
            return [di, dvc]
        sol = solve_ivp(cap_ode, [0, 0.06], [0, 0], max_step=1e-5)
        axes[idx].plot(sol.t * 1e3, sol.y[1] / 1e3, lw=1.2)
        axes[idx].axhline(Vm / 1e3, color='gray', ls=':', lw=0.8,
                          label=f'V_peak = {Vm/1e3:.1f} kV')
        axes[idx].set(xlabel='Time (ms)', ylabel='V_cap (kV)',
                      title=f'Switch at φ₀ = {phi_deg}°')
        axes[idx].legend(fontsize=8)
        axes[idx].grid(True, alpha=0.3)
    plt.suptitle('Case F: Cap Switching Transient — Steady-State Analysis Misses This')
    plt.tight_layout()
    plt.savefig('case_f_transient.png', dpi=150)


if __name__ == "__main__":
    case_a_smib()
    case_b_transformer()
    case_c_compensation()
    case_d_fault()
    case_e_motor()
    case_f_transient()
    plt.show()
    print("\n" + "=" * 60)
    print("  Experiment 1 complete. All plots saved.")
    print("  Next: Experiment 2 — Circuit Device Models")
    print("=" * 60)
