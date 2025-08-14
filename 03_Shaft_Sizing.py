
import streamlit as st, math
st.title("🪝 Shaft Sizing — Placeholder (v0.2.4)")
T = st.number_input("Torque T (N·m)", min_value=1.0, value=500.0)
tau_allow = st.number_input("Allowable Shear (MPa)", min_value=10.0, value=60.0)
d = (16*T/(math.pi*(tau_allow*1e6)))**(1.0/3.0)
st.metric("Estimated Shaft Diameter", f"{d*1000:.1f} mm")
st.caption("⚠️ Placeholder. Add combined bending, keyway factors, fatigue later.")
