# Machine Design Toolkit (N5/N6) — v0.2.1
# Fixes:
#  - Conveyor tab: Flow area label now in cm² (correct factor 1e4)
#  - Idler spacing now reported in mm (converted from metres)
# Quick start:
#   pip install streamlit fpdf numpy
#   streamlit run app.py

import math
from datetime import datetime

import numpy as np
import streamlit as st
from fpdf import FPDF

st.set_page_config(page_title="Machine Design Toolkit (N5/N6)", layout="wide")
st.title("🧮 Machine Design Toolkit (N5/N6) — v0.2.1")

# ────────────────────────────────────────────────────────────────
# Sidebar meta
# ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("📁 Project")
    project = st.text_input("Project", "Workshop Calculations")
    customer = st.text_input("Customer", "")
    calc_author = st.text_input("Author", "Wynand Oppermann")
    today = st.text_input("Date", datetime.today().strftime("%Y-%m-%d"))
    st.markdown("---")
    st.header("⚠️ Disclaimer")
    st.caption("Educational helper. Verify with relevant standards and your engineering judgement.")
    st.markdown("---")
    st.caption("Units: MPa, kW, kN, mm, rpm, N·m (metric).")

def export_pdf(title: str, inputs: dict, outputs: dict) -> bytes:
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, f"{title}", ln=True)
    pdf.set_font("Arial", size=11)
    pdf.cell(0, 8, f"Project: {project}", ln=True)
    if customer:
        pdf.cell(0, 8, f"Customer: {customer}", ln=True)
    pdf.cell(0, 8, f"Author: {calc_author}", ln=True)
    pdf.cell(0, 8, f"Date: {today}", ln=True)
    pdf.ln(4)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "Inputs", ln=True)
    pdf.set_font("Arial", size=11)
    for k, v in inputs.items():
        pdf.cell(0, 7, f"• {k}: {v}", ln=True)
    pdf.ln(2)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "Outputs", ln=True)
    pdf.set_font("Arial", size=11)
    for k, v in outputs.items():
        pdf.cell(0, 7, f"• {k}: {v}", ln=True)
    pdf.ln(4)
    pdf.set_font("Arial", size=10)
    pdf.multi_cell(0, 6, "Note: Educational tool. Verify against standards (SANS/ISO/VDI/ASME).")
    return pdf.output(dest="S").encode("latin1")

# ────────────────────────────────────────────────────────────────
# Tabs
# ────────────────────────────────────────────────────────────────
tabs = st.tabs([
    "Bolted Joint",
    "Shaft Sizing",
    "Bearing Life",
    "Belt Drive",
    "Fillet Weld",
    "Thin Cylinder",
    "Conveyor Basics",
    "Mechatronics (Starter)",
])

# (Tabs 0–5 identical to v0.2; omitted here for brevity in this patch snippet)
# To keep this patch self-contained for you, we include Conveyor + Mechatronics fully.

# ────────────────────────────────────────────────────────────────
# 7) Conveyor Basics (patched)
# ────────────────────────────────────────────────────────────────
with tabs[6]:
    st.subheader("Conveyor Basics — Spacing, Flow & Power (heuristics + sag method)")

    st.markdown("**A) Line Loads & Capacity**")
    c1, c2, c3 = st.columns(3)
    with c1:
        belt_mass_per_m = st.number_input("Belt mass per metre (kg/m)", min_value=1.0, value=15.0, step=0.5, help="From belt datasheet")
        bulk_density = st.number_input("Bulk density ρ (t/m³)", min_value=0.2, value=0.75, step=0.05)
        belt_speed = st.number_input("Belt speed v (m/s)", min_value=0.1, value=2.5, step=0.1)
    with c2:
        capacity_tph = st.number_input("Capacity (t/h)", min_value=1.0, value=200.0, step=5.0)
        return_mass_per_m = st.number_input("Return side additional mass (kg/m)", min_value=0.0, value=0.0, step=0.5, help="Scrapers, buildup etc.")
        length_L = st.number_input("Conveyor length L (m)", min_value=1.0, value=60.0, step=1.0)
    with c3:
        incline_deg = st.number_input("Incline angle (deg)", min_value=0.0, max_value=35.0, value=24.0, step=0.5)
        friction_factor = st.number_input("Friction factor f (0.015–0.03)", min_value=0.005, max_value=0.08, value=0.02, step=0.001)
        service_factor = st.number_input("Service factor on power", min_value=1.0, value=1.15, step=0.05)

    # Mass flow and cross-sectional area (approx)
    m_dot = capacity_tph * 1000.0 / 3600.0  # kg/s
    A_m2 = m_dot / (bulk_density*1000.0 * belt_speed) if bulk_density > 0 else 0.0

    g = 9.81
    w_belt = belt_mass_per_m * g  # N/m
    w_mat = (m_dot / belt_speed) * g  # N/m
    w_carry = w_belt + w_mat
    w_return = (belt_mass_per_m + return_mass_per_m) * g

    # Correct label: cm² (1 m² = 10,000 cm²)
    st.markdown(f"**Flow area A:** {A_m2*1e4:.0f} cm² (approx)  |  **Carry line load:** {w_carry:.0f} N/m  |  **Return line load:** {w_return:.0f} N/m")

    st.markdown("---")
    st.markdown("**B) Idler Spacing from Sag Ratio**  \nUses parabolic sag approximation:  *S = 8·f·T / w*  (f = sag/span). Provide tension estimates at the section.")
    s1, s2 = st.columns(2)
    with s1:
        f_carry = st.number_input("Carry sag ratio f_carry (typ. 0.01–0.02)", min_value=0.005, max_value=0.05, value=0.015, step=0.001)
        T_carry = st.number_input("Carry strand tension estimate T_carry (N)", min_value=1000.0, value=8000.0, step=500.0)
        S_carry_m = 8.0 * f_carry * T_carry / max(w_carry, 1e-9)  # metres
        st.markdown(f"**Recommended carry spacing S_carry:** {S_carry_m*1000.0:.0f} mm")
    with s2:
        f_return = st.number_input("Return sag ratio f_return (typ. 0.02–0.03)", min_value=0.005, max_value=0.08, value=0.025, step=0.001)
        T_return = st.number_input("Return strand tension estimate T_return (N)", min_value=500.0, value=4000.0, step=250.0)
        S_return_m = 8.0 * f_return * T_return / max(w_return, 1e-9)  # metres
        st.markdown(f"**Recommended return spacing S_return:** {S_return_m*1000.0:.0f} mm")

    st.caption("Rule-of-thumb sanity checks: carry 800–1200 mm, return 1500–3000 mm for many mid-size belts. Adjust for width, trough angle (35°/40°/45°), and duty.")

    st.markdown("---")
    st.markdown("**C) Power on Incline (lift + friction)**")
    incline_rad = math.radians(incline_deg)
    P_lift_W = m_dot * 9.81 * belt_speed * math.sin(incline_rad)
    W_total = (w_carry + w_return) * length_L
    F_fric = friction_factor * W_total
    P_fric_W = F_fric * belt_speed
    P_total_kW = (P_lift_W + P_fric_W) / 1000.0 * service_factor

    c4, c5, c6 = st.columns(3)
    with c4: st.markdown(f"**Lift power:** {P_lift_W/1000:.2f} kW")
    with c5: st.markdown(f"**Friction power:** {P_fric_W/1000:.2f} kW")
    with c6: st.markdown(f"**Motor power (with SF):** {P_total_kW:.2f} kW")

    if st.button("📄 Export PDF — Conveyor Basics"):
        pdf = export_pdf(
            "Conveyor Basics — Spacing, Flow & Power",
            {
                "Belt mass (kg/m)": belt_mass_per_m, "ρ (t/m³)": bulk_density, "v (m/s)": belt_speed,
                "Capacity (t/h)": capacity_tph, "Return add mass (kg/m)": return_mass_per_m, "L (m)": length_L,
                "Incline (deg)": incline_deg, "f friction": friction_factor, "Service factor": service_factor,
                "f_carry": f_carry, "T_carry (N)": T_carry, "f_return": f_return, "T_return (N)": T_return
            },
            {
                "A (m²)": round(A_m2,4), "w_carry (N/m)": round(w_carry,0), "w_return (N/m)": round(w_return,0),
                "S_carry (mm)": round(S_carry_m*1000.0,0), "S_return (mm)": round(S_return_m*1000.0,0),
                "P_lift (kW)": round(P_lift_W/1000,2), "P_fric (kW)": round(P_fric_W/1000,2), "P_motor (kW)": round(P_total_kW,2)
            }
        )
        st.download_button("Download PDF", data=pdf, file_name="conveyor_basics_report.pdf", mime="application/pdf")

# ────────────────────────────────────────────────────────────────
# 8) Mechatronics (Starter) — unchanged from v0.2
# ────────────────────────────────────────────────────────────────
with tabs[7]:
    st.subheader("Mechatronics Starter — N4/N5/N6 Helpers")

    m_tabs = st.tabs(["DC Motor & Gearbox Sizing", "Pneumatic Cylinder Sizing", "Signal Scaling (4–20 mA)"])

    # A) DC Motor & Gearbox sizing (simplified)
    with m_tabs[0]:
        c1, c2, c3 = st.columns(3)
        with c1:
            load_torque = st.number_input("Load torque at shaft (N·m)", min_value=0.0, value=50.0, step=1.0)
            speed_req = st.number_input("Required output speed (rpm)", min_value=1.0, value=60.0, step=1.0)
            accel_time = st.number_input("Accel time to speed (s)", min_value=0.1, value=2.0, step=0.1)
        with c2:
            inertia_load = st.number_input("Equivalent inertia at load J (kg·m²)", min_value=0.0, value=0.05, step=0.005)
            gear_eff = st.number_input("Gearbox efficiency η_g", min_value=0.5, max_value=1.0, value=0.9, step=0.01)
            sf = st.number_input("Service factor", min_value=1.0, value=1.5, step=0.1)
        with c3:
            gear_ratio = st.number_input("Gear ratio i = ω_motor/ω_out", min_value=1.0, value=20.0, step=1.0)
            motor_eff = st.number_input("Motor efficiency η_m", min_value=0.5, max_value=1.0, value=0.85, step=0.01)

        omega_out = speed_req * 2*math.pi / 60.0
        T_accel = inertia_load * omega_out / max(accel_time, 1e-6)
        T_out = (load_torque + T_accel) * sf
        T_motor = T_out / (gear_ratio * gear_eff)
        omega_motor = omega_out * gear_ratio
        P_mech = (T_motor * omega_motor) / max(motor_eff, 1e-6)  # W

        st.markdown(f"**Motor shaft torque:** {T_motor:.2f} N·m   |   **Motor speed:** {omega_motor*60/(2*math.pi):.0f} rpm")
        st.markdown(f"**Estimated electrical power:** {P_mech/1000:.2f} kW")

    # B) Pneumatic cylinder sizing
    with m_tabs[1]:
        c1, c2, c3 = st.columns(3)
        with c1:
            force_req = st.number_input("Required force (kN)", min_value=0.1, value=5.0, step=0.1)
            pressure_bar = st.number_input("Supply pressure (bar)", min_value=2.0, value=6.0, step=0.5)
            safety = st.number_input("Safety factor", min_value=1.0, value=1.3, step=0.1)
        with c2:
            rod_d_mm = st.number_input("Rod diameter (mm)", min_value=6.0, value=16.0, step=1.0)
            double_acting = st.toggle("Double-acting (retract area reduced)", value=True)
            stroke_mm = st.number_input("Stroke (mm)", min_value=10.0, value=200.0, step=5.0)
        with c3:
            cycles_per_min = st.number_input("Cycles per minute", min_value=1.0, value=10.0, step=1.0)

        p_Pa = pressure_bar * 1e5
        F_N = force_req * 1000.0 * safety
        A_m2 = F_N / p_Pa
        bore_mm = math.sqrt(4*A_m2/math.pi) * 1000.0

        stroke_m = stroke_mm / 1000.0
        A_piston = (math.pi*(bore_mm/1000.0)**2)/4.0
        A_rod = (math.pi*(rod_d_mm/1000.0)**2)/4.0
        vol_extend = A_piston * stroke_m
        vol_retract = (A_piston - (A_rod if double_acting else 0.0)) * stroke_m
        free_air_per_cycle = (vol_extend + vol_retract) * pressure_bar  # m³ at 1 bar abs
        free_air_per_min = free_air_per_cycle * cycles_per_min

        st.markdown(f"**Bore diameter:** {bore_mm:.1f} mm")
        st.markdown(f"**Free air consumption:** {free_air_per_min*1000:.1f} NL/min (approx)")

    # C) Signal scaling 4–20 mA
    with m_tabs[2]:
        c1, c2, c3 = st.columns(3)
        with c1:
            eng_min = st.number_input("Engineering min", value=0.0, step=0.1)
            eng_max = st.number_input("Engineering max", value=100.0, step=1.0)
        with c2:
            mA_in = st.number_input("Measured current (mA)", min_value=0.0, value=12.0, step=0.1)
        with c3:
            st.text_input("Input range (mA)", "4–20", disabled=True)

        span_eng = eng_max - eng_min
        value = eng_min + (max(min(mA_in,20.0),0.0) - 4.0) * (span_eng/16.0)
        st.markdown(f"**Scaled value:** {value:.3f}")

st.markdown("---")
st.caption("© 2025 — v0.2.1 patch. Next up: keys/keyseats, chains, gears, beams, PV heads, conveyor libraries, PID helpers, VFD sizing.")
