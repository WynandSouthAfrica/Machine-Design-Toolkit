
import math
import streamlit as st
import matplotlib.pyplot as plt

st.title("🏁 Belt Drive Designer — Visual + Catalogue Assist (v0.2.4)")

st.markdown(
    "Calculate belt geometry (length, wrap angle, belt speed) and render a **to‑scale** diagram. "
    "Use your catalogue to pick the belt section & per‑belt power; the app completes the rest."
)

def belt_length_open(D, d, C):
    return 2*C + (math.pi/2)*(D + d) + ((D - d)**2)/(4*C)

def belt_length_crossed(D, d, C):
    return 2*C + (math.pi/2)*(D + d) + ((D + d)**2)/(4*C)

def wrap_angle_small_open(D, d, C):
    val = (D - d) / (2*C)
    val = max(min(val, 1.0), -1.0)
    alpha = math.asin(val)
    return math.pi - 2*alpha

def wrap_angle_small_crossed(D, d, C):
    val = (D + d) / (2*C)
    val = max(min(val, 1.0), -1.0)
    alpha = math.asin(val)
    return math.pi + 2*alpha

def mm_to_m(x): return x/1000.0

def belt_speed(d_small_mm, n_small_rpm):
    return math.pi * mm_to_m(d_small_mm) * n_small_rpm / 60.0

def draw_system(ax, mode, arrangement, D, d, C):
    R_big, R_small = D/2.0, d/2.0
    cx1, cy1 = 0.0, 0.0
    cx2, cy2 = C, 0.0

    circle1 = plt.Circle((cx1, cy1), R_small, fill=False)
    circle2 = plt.Circle((cx2, cy2), R_big, fill=False)
    ax.add_patch(circle1); ax.add_patch(circle2)

    if arrangement == "Open":
        val = (R_big - R_small)/C
        val = max(min(val, 1.0), -1.0)
        theta = math.acos(val)
        t1_small = (cx1 + R_small*math.sin(theta), cy1 + R_small*math.cos(theta))
        t2_small = (cx1 - R_small*math.sin(theta), cy1 - R_small*math.cos(theta))
        t1_big   = (cx2 + R_big*math.sin(theta),  cy2 + R_big*math.cos(theta))
        t2_big   = (cx2 - R_big*math.sin(theta),  cy2 - R_big*math.cos(theta))
    else:
        val = (R_big + R_small)/C
        val = max(min(val, 1.0), -1.0)
        theta = math.acos(val)
        t1_small = (cx1 + R_small*math.sin(theta), cy1 - R_small*math.cos(theta))
        t2_small = (cx1 - R_small*math.sin(theta), cy1 + R_small*math.cos(theta))
        t1_big   = (cx2 + R_big*math.sin(theta),  cy2 + R_big*math.cos(theta))
        t2_big   = (cx2 - R_big*math.sin(theta),  cy2 - R_big*math.cos(theta))

    ax.plot([t1_small[0], t1_big[0]], [t1_small[1], t1_big[1]])
    ax.plot([t2_small[0], t2_big[0]], [t2_small[1], t2_big[1]])

    ax.annotate(f"d (small) = {d:.1f} mm", (cx1, cy1 - R_small - 20), ha="center")
    ax.annotate(f"D (large) = {D:.1f} mm", (cx2, cy2 - R_big - 20), ha="center")
    ax.annotate(f"C = {C:.1f} mm", ((cx1+cx2)/2, cy1 + max(R_big, R_small) + 40), ha="center")

    pad = max(R_big, R_small) + 60
    ax.set_aspect('equal', adjustable='box')
    ax.set_xlim(-pad, C + pad)
    ax.set_ylim(-pad - max(R_big, R_small), pad + max(R_big, R_small))
    ax.axis('off')

with st.sidebar:
    st.header("Inputs")
    mode = st.selectbox("Belt Type", ["Flat", "V"])
    arrangement = st.selectbox("Arrangement", ["Open", "Crossed"])

    col1, col2 = st.columns(2)
    with col1:
        n_driver = st.number_input("Driver RPM (n₁)", min_value=1, value=1450)
        d_small = st.number_input("Small Pulley d (mm)", min_value=10.0, value=150.0, step=5.0)
        C = st.number_input("Center Distance C (mm)", min_value=50.0, value=800.0, step=10.0)
    with col2:
        n_driven = st.number_input("Driven RPM (n₂)", min_value=1, value=725)
        D_auto = d_small * (n_driver / n_driven)
        D = st.number_input("Large Pulley D (mm)", min_value=10.0, value=float(round(D_auto,1)), step=5.0)

    st.divider()
    st.subheader("Power & Catalogue")
    P_required = st.number_input("Required Power (kW)", min_value=0.1, value=7.5, step=0.1)
    service_factor = st.number_input("Service Factor (from catalogue)", min_value=0.5, value=1.3, step=0.05)
    per_belt_rating = st.number_input("Per-belt power rating (kW/belt)", min_value=0.01, value=2.0, step=0.05)

P_design = P_required * service_factor
belt_count_min = max(1, int((P_design + per_belt_rating - 1e-9) // per_belt_rating))

st.success(f"Design Power = {P_required:.2f} × {service_factor:.2f} = **{P_design:.2f} kW**")
if mode == "V":
    st.info(f"Minimum number of belts (using catalogue per-belt rating): **{belt_count_min}**")

ratio = n_driver / n_driven
if arrangement == "Open":
    L = belt_length_open(D, d_small, C)
    theta_small = wrap_angle_small_open(D, d_small, C)
else:
    L = belt_length_crossed(D, d_small, C)
    theta_small = wrap_angle_small_crossed(D, d_small, C)

v = math.pi * (d_small/1000.0) * n_driver / 60.0
theta_small_deg = theta_small * 180.0 / math.pi

st.subheader("Geometry & Performance")
colA, colB, colC, colD = st.columns(4)
with colA: st.metric("Speed Ratio (n₁/n₂)", f"{ratio:.3f}")
with colB: st.metric("Belt Length L", f"{L:.1f} mm")
with colC: st.metric("Wrap Angle (small)", f"{theta_small_deg:.1f}°")
with colD: st.metric("Belt Speed v", f"{v:.2f} m/s")

st.subheader("To‑Scale Diagram")
fig, ax = plt.subplots(figsize=(8, 5))
draw_system(ax, mode, arrangement, D, d_small, C)
st.pyplot(fig)

with st.expander("Catalogue Workflow Notes"):
    st.markdown("""
1. Pick **Service Factor** from the catalogue.
2. Compute **Design Power**.
3. Choose **belt section / min pulley diameters** per catalogue.
4. Read **per‑belt rating** at your RPM & wrap from the catalogue.
5. Enter that rating above to get **belts needed** (V‑belts).
6. Use **belt length** to pick a **standard length**; tweak **C** if required.
7. Target **wrap ≥ 120°** on the small pulley (typical for V‑belts).
""")
