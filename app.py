# Machine Design Toolkit (N5/N6) — v0.2.3
# Fix: Add unique Streamlit widget keys across all tabs to prevent DuplicateElementId.
# Feature retained: Formula + Inputs side-by-side.
# Quick start:
#   pip install streamlit fpdf numpy
#   streamlit run app.py

import math
from datetime import datetime

import numpy as np
import streamlit as st
from fpdf import FPDF

st.set_page_config(page_title="Machine Design Toolkit (N5/N6)", layout="wide")
st.title("🧮 Machine Design Toolkit (N5/N6) — v0.2.3  •  Formula-Guided Inputs")

# Sidebar meta (unique keys)
with st.sidebar:
    st.header("📁 Project")
    project = st.text_input("Project", "Workshop Calculations", key="meta_project")
    customer = st.text_input("Customer", "", key="meta_customer")
    calc_author = st.text_input("Author", "Wynand Oppermann", key="meta_author")
    today = st.text_input("Date", datetime.today().strftime("%Y-%m-%d"), key="meta_date")
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

def formula_card(latex: str, input_draw_fn=None, note: str = "", key_prefix: str = ""):
    col_l, col_r = st.columns([1.05, 1.15])
    with col_l:
        st.latex(latex)
        if note:
            st.caption(note)
    with col_r:
        if input_draw_fn:
            return input_draw_fn(key_prefix=key_prefix)
    return None

tabs = st.tabs([
    "Bolted Joint",
    "Shaft Sizing",
    "Bearing Life",
    "Belt Drive",
    "Fillet Weld",
    "Thin Cylinder",
])

# ────────────────────────────────────────────────────────────────
# 1) Bolted Joint — Formula-led UI
# ────────────────────────────────────────────────────────────────
with tabs[0]:
    st.subheader("Bolted Joint — Formula-Guided Inputs")
    st.markdown("Pick a preset size or enter **d** & **p** manually. Then follow the formulas.")

    use_preset = st.toggle("Use metric coarse preset", value=True, key="bolt_use_preset")
    pitch_map = {"M6":1.0,"M8":1.25,"M10":1.5,"M12":1.75,"M16":2.0,"M20":2.5}

    if use_preset:
        bolt = st.selectbox("Bolt size", list(pitch_map.keys()), index=3, key="bolt_size")  # M12 default
        d = float(bolt[1:])
        p = pitch_map[bolt]
        st.caption(f"Preset: d = {d} mm, p = {p} mm")
    else:
        c = st.columns(2)
        with c[0]:
            d = st.number_input("Nominal diameter d (mm)", min_value=1.0, value=12.0, step=0.5, key="bolt_d")
        with c[1]:
            p = st.number_input("Pitch p (mm)", min_value=0.5, value=1.75, step=0.05, key="bolt_p")

    # A) Stress area
    def draw_as(**kwargs):
        return {}
    formula_card(
        r"A_s=\frac{\pi}{4}\,\big(d-0.9382\,p\big)^2",
        draw_as,
        note="ISO metric coarse tensile stress area",
        key_prefix="bolt_as_"
    )
    As = (math.pi/4.0) * (d - 0.9382*p)**2  # mm²
    st.info(f"**Stress area A_s:** {As:.2f} mm²")

    # B) Preload
    def draw_preload(key_prefix: str, **kwargs):
        col1, col2, col3 = st.columns(3)
        with col1:
            prop_class = st.selectbox("Property class", ["8.8","10.9","12.9"], index=0, key=key_prefix+"class")
        with col2:
            Re_default = {"8.8": 640.0, "10.9": 940.0, "12.9": 1100.0}[prop_class]
            Re = st.number_input("Yield strength Re (MPa)", min_value=300.0, max_value=1400.0, value=Re_default, step=10.0, key=key_prefix+"Re")
        with col3:
            preload_frac = st.number_input("Preload fraction φ (0.6–0.8)", min_value=0.4, max_value=0.9, value=0.7, step=0.05, key=key_prefix+"phi")
        return {"prop_class":prop_class, "Re":Re, "phi":preload_frac}
    vals = formula_card(
        r"F_\mathrm{pre}=\phi\,R_e\,A_s",
        draw_preload,
        note="Target preload as a fraction of yield × stress area",
        key_prefix="bolt_pre_"
    )
    Re = vals["Re"]; preload_frac = vals["phi"]
    F_pre = preload_frac * Re * As  # N
    st.success(f"**Preload F_pre:** {F_pre/1000:.2f} kN")

    # C) Torque
    def draw_torque(key_prefix: str, **kwargs):
        col1, col2, col3 = st.columns(3)
        with col1:
            K = st.number_input("Torque factor K (0.15–0.25)", min_value=0.1, max_value=0.4, value=0.20, step=0.01, key=key_prefix+"K")
        with col2:
            SF = st.number_input("Safety factor on preload", min_value=1.0, max_value=2.0, value=1.0, step=0.1, key=key_prefix+"SF")
        with col3:
            req_clamp = st.number_input("Required clamp (kN)", min_value=0.0, value=0.0, step=0.5, key=key_prefix+"req")
        return {"K":K, "SF":SF, "req":req_clamp}
    v = formula_card(
        r"T=K\,\frac{F_\mathrm{pre}}{\mathrm{SF}}\frac{d}{1000}",
        draw_torque,
        note="T in N·m; d in mm",
        key_prefix="bolt_torque_"
    )
    T = v["K"] * (F_pre / v["SF"]) * d / 1000.0
    st.markdown(f"**Tightening torque:** {T:.1f} N·m")
    if v["req"]>0:
        ok = (F_pre/1000.0) >= v["req"]
        st.caption(f"Clamp check: {'✅ OK' if ok else '⚠️ Not OK'} — available {F_pre/1000:.2f} kN vs required {v['req']:.2f} kN")

    if st.button("📄 Export PDF — Bolted Joint", key="bolt_export"):
        pdf = export_pdf(
            "Bolted Joint — Formula-Guided",
            {"d (mm)": d, "p (mm)": p, "A_s (mm²)": round(As,2), "Re (MPa)": Re, "φ": preload_frac},
            {"F_pre (kN)": round(F_pre/1000.0,2), "Torque T (N·m)": round(T,1)}
        )
        st.download_button("Download PDF", data=pdf, file_name="bolted_joint_formulas.pdf", mime="application/pdf", key="bolt_export_dl")

# ────────────────────────────────────────────────────────────────
# 2) Shaft Sizing — Formula-led UI
# ────────────────────────────────────────────────────────────────
with tabs[1]:
    st.subheader("Shaft Sizing — Combined Bending & Torsion (ASME-style)")
    use_power = st.toggle("Compute T from P & n (else enter T directly)", value=True, key="shaft_use_power")

    if use_power:
        def draw_Tpower(key_prefix: str, **kwargs):
            c1, c2 = st.columns(2)
            with c1:
                P_kW = st.number_input("Power P (kW)", min_value=0.0, value=15.0, step=0.5, key=key_prefix+"P")
            with c2:
                n_rpm = st.number_input("Speed n (rpm)", min_value=1.0, value=1450.0, step=10.0, key=key_prefix+"n")
            return {"P":P_kW, "n":n_rpm}
        vals = formula_card(
            r"T=\frac{9550\,P}{n}",
            draw_Tpower,
            note="T in N·m (P in kW, n in rpm)",
            key_prefix="shaft_Tpower_"
        )
        T_Nm = 9550.0 * vals["P"] / vals["n"]
    else:
        def draw_T(key_prefix: str, **kwargs):
            return {"T": st.number_input("Torque T (N·m)", min_value=0.0, value=100.0, step=10.0, key=key_prefix+"T")}
        vals = formula_card(r"T=T", draw_T, key_prefix="shaft_Tdirect_")
        T_Nm = vals["T"]

    def draw_core(key_prefix: str, **kwargs):
        c1,c2,c3 = st.columns(3)
        with c1:
            M_Nm = st.number_input("Bending moment M (N·m)", min_value=0.0, value=500.0, step=10.0, key=key_prefix+"M")
        with c2:
            Km = st.number_input("Shock factor in bending K_m", min_value=1.0, value=1.5, step=0.1, key=key_prefix+"Km")
            Kt = st.number_input("Shock factor in torsion K_t", min_value=1.0, value=1.0, step=0.1, key=key_prefix+"Kt")
        with c3:
            tau_allow = st.number_input("Allowable shear τ_allow (MPa)", min_value=20.0, value=40.0, step=5.0, key=key_prefix+"tau")
            keyway_factor = st.number_input("Keyway factor (0.8–1.0)", min_value=0.7, max_value=1.0, value=0.85, step=0.01, key=key_prefix+"kw")
        return {"M":M_Nm, "Km":Km, "Kt":Kt, "tau":tau_allow, "kw":keyway_factor}
    p = formula_card(
        r"d=\left[\frac{16}{\pi\,\tau_\mathrm{allow}}\sqrt{(K_m M)^2+(K_t T)^2}\right]^{1/3}",
        draw_core,
        note="M and T in N·mm",
        key_prefix="shaft_core_"
    )
    Meq = p["Km"] * p["M"] * 1000.0
    Teq = p["Kt"] * T_Nm * 1000.0
    d_mm = ((16.0/(math.pi * p["tau"])) * math.sqrt(Meq**2 + Teq**2)) ** (1.0/3.0)
    d_mm /= p["kw"]
    st.success(f"**Recommended solid shaft diameter d:** {d_mm:.2f} mm")

    if st.button("📄 Export PDF — Shaft Sizing", key="shaft_export"):
        pdf = export_pdf(
            "Shaft Sizing — Formula-Guided",
            {"T (N·m)": round(T_Nm,2), "M (N·m)": round(p['M'],2), "K_m":p["Km"], "K_t":p["Kt"], "τ_allow (MPa)":p["tau"], "Keyway":p["kw"]},
            {"d (mm)": round(d_mm,2)},
        )
        st.download_button("Download PDF", data=pdf, file_name="shaft_sizing_formulas.pdf", mime="application/pdf", key="shaft_export_dl")

# ────────────────────────────────────────────────────────────────
# 3) Bearing Life — Formula-led UI
# ────────────────────────────────────────────────────────────────
with tabs[2]:
    st.subheader("Bearing Life (L10) — Formula-Guided")
    def draw_bearing(key_prefix: str, **kwargs):
        c1,c2,c3 = st.columns(3)
        with c1:
            btype = st.selectbox("Type", ["Ball (p=3)","Roller (p=10/3)"], index=0, key=key_prefix+"type")
        with c2:
            C_kN = st.number_input("Dynamic capacity C (kN)", min_value=0.1, value=25.0, step=0.5, key=key_prefix+"C")
            P_kN = st.number_input("Equivalent load P (kN)", min_value=0.01, value=5.0, step=0.1, key=key_prefix+"P")
        with c3:
            n = st.number_input("Speed n (rpm)", min_value=1.0, value=1450.0, step=10.0, key=key_prefix+"n")
        return {"btype":btype,"C":C_kN,"P":P_kN,"n":n}
    vals = formula_card(
        r"L_{10}=\left(\frac{C}{P}\right)^p\quad;\quad L_h=\frac{L_{10}\cdot 10^6}{60\,n}",
        draw_bearing,
        note="p = 3 (ball) or 10/3 (roller)",
        key_prefix="bear_"
    )
    p_exp = 3.0 if "Ball" in vals["btype"] else 10.0/3.0
    L10_mrev = (vals["C"]/vals["P"])**p_exp
    Lh = (L10_mrev*1e6) / (60.0*vals["n"])
    st.success(f"**L10:** {L10_mrev:.2f} million rev  |  **Life:** {Lh:.0f} h")

    if st.button("📄 Export PDF — Bearing Life", key="bear_export"):
        pdf = export_pdf(
            "Bearing Life — Formula-Guided",
            {"Type": vals["btype"], "C (kN)": vals["C"], "P (kN)": vals["P"], "n (rpm)": vals["n"]},
            {"L10 (million rev)": round(L10_mrev,2), "Life (h)": round(Lh,0)},
        )
        st.download_button("Download PDF", data=pdf, file_name="bearing_life_formulas.pdf", mime="application/pdf", key="bear_export_dl")

# ────────────────────────────────────────────────────────────────
# 4) Belt Drive — Formula-led UI
# ────────────────────────────────────────────────────────────────
with tabs[3]:
    st.subheader("Belt Drive Tensions — Formula-Guided")
    def draw_belt(key_prefix: str, **kwargs):
        c1,c2,c3 = st.columns(3)
        with c1:
            P_kW = st.number_input("Power P (kW)", min_value=0.0, value=7.5, step=0.5, key=key_prefix+"P")
            SF = st.number_input("Service factor", min_value=1.0, value=1.2, step=0.1, key=key_prefix+"SF")
            P_eff = P_kW*SF
        with c2:
            d_mm = st.number_input("Driver pulley diameter d (mm)", min_value=10.0, value=200.0, step=5.0, key=key_prefix+"d")
            n = st.number_input("Driver speed n (rpm)", min_value=1.0, value=1450.0, step=10.0, key=key_prefix+"n")
            v = math.pi * (d_mm/1000.0) * (n/60.0)
        with c3:
            theta_deg = st.number_input("Wrap θ (deg)", min_value=10.0, max_value=210.0, value=170.0, step=1.0, key=key_prefix+"theta")
            mu = st.number_input("Friction μ", min_value=0.05, max_value=1.0, value=0.30, step=0.01, key=key_prefix+"mu")
        return {"P_eff":P_eff,"v":v,"theta_deg":theta_deg,"mu":mu,"d":d_mm,"n":n,"P":P_kW,"SF":SF}
    vals = formula_card(
        r"\Delta T=\frac{P}{v}\quad;\quad \frac{T_1}{T_2}=e^{\mu \theta}\quad;\quad v=\pi d \frac{n}{60}",
        draw_belt,
        note="θ in radians in the ratio; UI takes degrees",
        key_prefix="belt_"
    )
    dT = (vals["P_eff"]*1000.0) / max(vals["v"], 1e-9)
    ratio = math.e ** (vals["mu"] * math.radians(vals["theta_deg"]))
    T1 = dT * ratio / (ratio-1.0)
    T2 = T1/ratio
    st.success(f"**v:** {vals['v']:.2f} m/s  |  **ΔT:** {dT:.0f} N  |  **T1:** {T1:.0f} N  |  **T2:** {T2:.0f} N")

    if st.button("📄 Export PDF — Belt Drive", key="belt_export"):
        pdf = export_pdf(
            "Belt Drive — Formula-Guided",
            {"P (kW)": vals["P"], "SF": vals["SF"], "d (mm)": vals["d"], "n (rpm)": vals["n"], "θ (deg)": vals["theta_deg"], "μ": vals["mu"]},
            {"v (m/s)": round(vals["v"],2), "ΔT (N)": round(dT,0), "T1 (N)": round(T1,0), "T2 (N)": round(T2,0)}
        )
        st.download_button("Download PDF", data=pdf, file_name="belt_drive_formulas.pdf", mime="application/pdf", key="belt_export_dl")

# ────────────────────────────────────────────────────────────────
# 5) Fillet Weld — Formula-led UI
# ────────────────────────────────────────────────────────────────
with tabs[4]:
    st.subheader("Fillet Weld Capacity — Formula-Guided")
    def draw_weld(key_prefix: str, **kwargs):
        c1,c2,c3 = st.columns(3)
        with c1:
            a = st.number_input("Leg size a (mm)", min_value=1.0, value=6.0, step=0.5, key=key_prefix+"a")
            length = st.number_input("Effective weld length (mm)", min_value=1.0, value=100.0, step=1.0, key=key_prefix+"L")
        with c2:
            lines = st.selectbox("Number of weld lines", [1,2], index=1, key=key_prefix+"lines")
            fv = st.number_input("Allowable shear τ_allow (MPa)", min_value=50.0, value=120.0, step=5.0, key=key_prefix+"fv")
        with c3:
            req_kN = st.number_input("Required capacity (kN)", min_value=0.0, value=0.0, step=1.0, key=key_prefix+"req")
        return {"a":a,"L":length,"lines":lines,"fv":fv,"req":req_kN}
    vals = formula_card(
        r"a_\mathrm{throat}=0.707\,a\quad;\quad A=a_\mathrm{throat}\,L\times \mathrm{lines}\quad;\quad F=A\,\tau_\mathrm{allow}",
        draw_weld,
        key_prefix="weld_"
    )
    throat = 0.707*vals["a"]
    area = throat * vals["L"] * vals["lines"]
    cap_N = area * vals["fv"]
    ok_text = ""
    if vals["req"]>0:
        ok = (cap_N/1000.0)>=vals["req"]
        ok_text = f" — check: {'✅ OK' if ok else '⚠️ Not OK'}"
    st.success(f"**Capacity:** {cap_N/1000:.2f} kN  (throat {throat:.2f} mm, area {area:.1f} mm²){ok_text}")

    if st.button("📄 Export PDF — Fillet Weld", key="weld_export"):
        pdf = export_pdf(
            "Fillet Weld — Formula-Guided",
            {"a (mm)": vals["a"], "L (mm)": vals["L"], "lines": vals["lines"], "τ_allow (MPa)": vals["fv"], "Req (kN)": vals["req"]},
            {"throat (mm)": round(throat,2), "Area (mm²)": round(area,1), "Capacity (kN)": round(cap_N/1000.0,2)}
        )
        st.download_button("Download PDF", data=pdf, file_name="fillet_weld_formulas.pdf", mime="application/pdf", key="weld_export_dl")

# ────────────────────────────────────────────────────────────────
# 6) Thin Cylinder — Formula-led UI
# ────────────────────────────────────────────────────────────────
with tabs[5]:
    st.subheader("Thin Cylinder — Stresses & Required Thickness (Formula-Guided)")
    def draw_cyl(key_prefix: str, **kwargs):
        c1,c2,c3 = st.columns(3)
        with c1:
            p_MPa = st.number_input("Internal pressure p (MPa)", min_value=0.0, value=0.5, step=0.05, key=key_prefix+"p")
            D_mm = st.number_input("Mean diameter D (mm)", min_value=1.0, value=600.0, step=5.0, key=key_prefix+"D")
        with c2:
            t_mm = st.number_input("Wall thickness t (mm)", min_value=0.1, value=6.0, step=0.5, key=key_prefix+"t")
            sigma_allow = st.number_input("Allowable hoop σ_allow (MPa)", min_value=50.0, value=150.0, step=5.0, key=key_prefix+"sigma")
        with c3:
            CA = st.number_input("Corrosion allowance CA (mm)", min_value=0.0, value=0.0, step=0.5, key=key_prefix+"CA")
            solve_t = st.toggle("Solve t for σ_allow", value=False, key=key_prefix+"solve")
        return {"p":p_MPa,"D":D_mm,"t":t_mm,"sigma":sigma_allow,"CA":CA,"solve":solve_t}
    vals = formula_card(
        r"\sigma_h=\frac{pD}{2t}\quad;\quad \sigma_l=\frac{pD}{4t}\quad;\quad t_\mathrm{req}=\frac{pD}{2\sigma_\mathrm{allow}}",
        draw_cyl,
        note="Thin-wall approximation (t ≤ D/10)",
        key_prefix="cyl_"
    )
    hoop = vals["p"]*vals["D"]/(2.0*vals["t"])
    longi = vals["p"]*vals["D"]/(4.0*vals["t"])
    st.success(f"**Hoop σ_h:** {hoop:.1f} MPa  |  **Longitudinal σ_l:** {longi:.1f} MPa")

    if vals["solve"]:
        t_req = vals["p"]*vals["D"]/(2.0*vals["sigma"])
        t_req_total = t_req + vals["CA"]
        st.info(f"**Required t (no CA):** {t_req:.2f} mm  |  **t with CA:** {t_req_total:.2f} mm")

    if st.button("📄 Export PDF — Thin Cylinder", key="cyl_export"):
        outs = {"σ_h (MPa)": round(hoop,1), "σ_l (MPa)": round(longi,1)}
        if vals["solve"]:
            outs.update({"t_req (mm)": round(t_req,2), "t_req+CA (mm)": round(t_req_total,2)})
        pdf = export_pdf(
            "Thin Cylinder — Formula-Guided",
            {"p (MPa)": vals["p"], "D (mm)": vals["D"], "t (mm)": vals["t"], "σ_allow (MPa)": vals["sigma"], "CA (mm)": vals["CA"], "Solve t": vals["solve"]},
            outs
        )
        st.download_button("Download PDF", data=pdf, file_name="thin_cylinder_formulas.pdf", mime="application/pdf", key="cyl_export_dl")

st.markdown("---")
st.caption("© 2025 — v0.2.3. Unique widget keys added to avoid DuplicateElementId across tabs.")

