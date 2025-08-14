
import streamlit as st, math
st.title("🧭 Bearing Life (L10) — Placeholder (v0.2.4)")
C = st.number_input("Dynamic rating C (kN)", min_value=1.0, value=35.0)
P = st.number_input("Equivalent load P (kN)", min_value=0.1, value=8.0)
p_exp = st.selectbox("Exponent p", [3, 10/3], index=0, help="Ball bearings: 3; Roller: 10/3")
L10 = (C/P)**p_exp
st.metric("L10 (million revs)", f"{L10:.2f}")
n = st.number_input("Speed (rpm)", min_value=1, value=1500)
hours = (L10*1e6)/(60*n)
st.metric("Life (hours)", f"{hours:.0f} h")
st.caption("⚠️ Placeholder. Add reliability factors, temp, lubrication factors later.")
