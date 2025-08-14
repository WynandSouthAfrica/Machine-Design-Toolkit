
import streamlit as st, math
st.title("🧱 Fillet Weld — Placeholder (v0.2.4)")
P = st.number_input("Applied shear (kN)", min_value=0.0, value=12.0)
a = st.number_input("Throat size a (mm)", min_value=1.0, value=4.0)
L = st.number_input("Effective length L (mm)", min_value=1.0, value=120.0)
tau_allow = st.number_input("Allowable shear (MPa)", min_value=10.0, value=140.0)
area = a * L
tau = (P*1e3) / area
st.metric("Calc Shear Stress", f"{tau:.1f} MPa")
st.caption("⚠️ Placeholder. Add eccentricity, combined loads, code factors later.")
