import math
import streamlit as st
import matplotlib.pyplot as plt

st.set_page_config(page_title="Machine Design Toolkit — Single-File v0.2.7", layout="wide")
st.title("🛠️ Machine Design Toolkit — Single-File v0.2.7")

tool = st.sidebar.radio("Choose tool", [
    "Belt Drive Designer",
    "Bolted Joint",
    "Shaft Sizing",
    "Bearing Life",
    "Fillet Weld",
    "Thin Cylinder",
])

def belt_drive():
    st.header("🏁 Belt Drive Designer — Visual + Catalogue Assist")
    def belt_length_open(D, d, C): return 2*C + (math.pi/2)*(D + d) + ((D - d)**2)/(4*C)
    def belt_length_crossed(D, d, C): return 2*C + (math.pi/2)*(D + d) + ((D + d)**2)/(4*C)
    def wrap_angle_small_open(D, d, C):
        val = max(min((D - d) / (2*C), 1.0), -1.0); return math.pi - 2*math.asin(val)
    def wrap_angle_small_crossed(D, d, C):
        val = max(min((D + d) / (2*C), 1.0), -1.0); return math.pi + 2*math.asin(val)

    col1, col2 = st.columns(2)
    with col1:
        arrangement = st.selectbox("Arrangement", ["Open", "Crossed"])
        n1 = st.number_input("Driver RPM n₁", min_value=1, value=1450)
        n2 = st.number_input("Driven RPM n₂", min_value=1, value=725)
        d = st.number_input("Small pulley d (mm)", min_value=10.0, value=150.0, step=5.0)
        C = st.number_input("Centre distance C (mm)", min_value=50.0, value=800.0, step=10.0)
        D0 = d * (n1 / n2)
        D = st.number_input("Large pulley D (mm)", min_value=10.0, value=float(round(D0,1)), step=5.0)
    with col2:
        P = st.number_input("Required power (kW)", min_value=0.1, value=7.5, step=0.1)
        SF = st.number_input("Service factor", min_value=0.5, value=1.3, step=0.05)
        per = st.number_input("Per-belt rating (kW/belt)", min_value=0.01, value=2.0, step=0.05)

    Pdes = P*SF
    belts = max(1, int((Pdes + per - 1e-9)//per))
    st.success(f"Design power = {P:.2f} × {SF:.2f} = **{Pdes:.2f} kW**")
    st.info(f"Minimum number of belts: **{belts}**")

    if arrangement == "Open":
        L = belt_length_open(D, d, C)
        theta_s = wrap_angle_small_open(D, d, C)
    else:
        L = belt_length_crossed(D, d, C)
        theta_s = wrap_angle_small_crossed(D, d, C)

    ratio = n1 / n2
    v = math.pi * (d/1000.0) * n1 / 60.0
    theta_deg = theta_s * 180.0 / math.pi

    a,b,c,dv = st.columns(4)
    a.metric("Ratio n₁/n₂", f"{ratio:.3f}")
    b.metric("Belt length L", f"{L:.1f} mm")
    c.metric("Wrap angle (small)", f"{theta_deg:.1f}°")
    dv.metric("Belt speed v", f"{v:.2f} m/s")

    st.subheader("To-scale diagram")
    fig, ax = plt.subplots(figsize=(8,5))
    Rb, Rs = D/2.0, d/2.0; cx1, cx2 = 0.0, C; cy = 0.0
    ax.add_patch(plt.Circle((cx1, cy), Rs, fill=False))
    ax.add_patch(plt.Circle((cx2, cy), Rb, fill=False))
    if arrangement == "Open":
        val = max(min((Rb - Rs)/C, 1.0), -1.0); th = math.acos(val)
        t1s = (cx1 + Rs*math.sin(th),  cy + Rs*math.cos(th))
        t2s = (cx1 - Rs*math.sin(th),  cy - Rs*math.cos(th))
        t1b = (cx2 + Rb*math.sin(th),  cy + Rb*math.cos(th))
        t2b = (cx2 - Rb*math.sin(th),  cy - Rb*math.cos(th))
    else:
        val = max(min((Rb + Rs)/C, 1.0), -1.0); th = math.acos(val)
        t1s = (cx1 + Rs*math.sin(th),  cy - Rs*math.cos(th))
        t2s = (cx1 - Rs*math.sin(th),  cy + Rs*math.cos(th))
        t1b = (cx2 + Rb*math.sin(th),  cy + Rb*math.cos(th))
        t2b = (cx2 - Rb*math.sin(th),  cy - Rb*math.cos(th))
    ax.plot([t1s[0], t1b[0]], [t1s[1], t1b[1]])
    ax.plot([t2s[0], t2b[0]], [t2s[1], t2b[1]])
    pad = max(Rb, Rs) + 60
    ax.set_aspect('equal', adjustable='box')
    ax.set_xlim(-pad, C + pad); ax.set_ylim(-pad - max(Rb, Rs), pad + max(Rb, Rs)); ax.axis('off')
    st.pyplot(fig)

def bolted_joint():
    st.header("🔩 Bolted Joint — Placeholder")
    F = st.number_input("Service load F (kN)", min_value=0.0, value=10.0)
    phi = st.number_input("Joint stiffness φ", min_value=0.0, max_value=1.0, value=0.2, step=0.05)
    SF = st.number_input("Safety Factor", min_value=1.0, value=1.5, step=0.1)
    st.metric("Suggested Preload (rough)", f"{(F*phi*SF):.2f} kN")

def shaft_sizing():
    st.header("🪝 Shaft Sizing — Placeholder")
    T = st.number_input("Torque T (N·m)", min_value=1.0, value=500.0)
    tau = st.number_input("Allowable shear τ (MPa)", min_value=10.0, value=60.0)
    d = (16*T/(math.pi*(tau*1e6)))**(1/3); st.metric("Estimated d", f"{d*1000:.1f} mm")

def bearing_life():
    st.header("🧭 Bearing Life (L10) — Placeholder")
    C = st.number_input("Dynamic rating C (kN)", min_value=1.0, value=35.0)
    P = st.number_input("Equivalent load P (kN)", min_value=0.1, value=8.0)
    p = st.selectbox("Exponent p", [3, 10/3], index=0)
    L10 = (C/P)**p; st.metric("L10 (million revs)", f"{L10:.2f}")
    n = st.number_input("Speed (rpm)", min_value=1, value=1500)
    st.metric("Life (hours)", f"{(L10*1e6)/(60*n):.0f} h")

def fillet_weld():
    st.header("🧱 Fillet Weld — Placeholder")
    P = st.number_input("Applied shear (kN)", min_value=0.0, value=12.0)
    a = st.number_input("Throat size a (mm)", min_value=1.0, value=4.0)
    L = st.number_input("Effective length L (mm)", min_value=1.0, value=120.0)
    tau_allow = st.number_input("Allowable shear (MPa)", min_value=10.0, value=140.0)
    area = a*L; tau = (P*1e3)/area if area>0 else 0.0
    st.metric("Calc shear stress", f"{tau:.1f} MPa")

def thin_cyl():
    st.header("🥫 Thin Cylinder Basics — Placeholder")
    p = st.number_input("Internal pressure p (MPa)", min_value=0.0, value=1.2)
    D = st.number_input("Diameter D (mm)", min_value=1.0, value=600.0)
    t = st.number_input("Wall thickness t (mm)", min_value=0.1, value=6.0)
    st.metric("Hoop stress σh", f"{((p*1e6)*(D/1000.0)/(2*(t/1000.0)))/1e6:.2f} MPa")
    st.metric("Longitudinal stress σl", f"{((p*1e6)*(D/1000.0)/(4*(t/1000.0)))/1e6:.2f} MPa")

if tool == "Belt Drive Designer": belt_drive()
elif tool == "Bolted Joint": bolted_joint()
elif tool == "Shaft Sizing": shaft_sizing()
elif tool == "Bearing Life": bearing_life()
elif tool == "Fillet Weld": fillet_weld()
else: thin_cyl()
