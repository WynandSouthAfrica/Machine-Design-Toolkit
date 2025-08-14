
import streamlit as st, math
st.title("🥫 Thin Cylinder Basics — Placeholder (v0.2.4)")
p = st.number_input("Internal pressure p (MPa)", min_value=0.0, value=1.2)
D = st.number_input("Diameter D (mm)", min_value=1.0, value=600.0)
t = st.number_input("Wall thickness t (mm)", min_value=0.1, value=6.0)
sigma_h = (p*1e6)*(D/1000.0)/(2*(t/1000.0))
sigma_l = (p*1e6)*(D/1000.0)/(4*(t/1000.0))
st.metric("Hoop Stress σh", f"{sigma_h/1e6:.2f} MPa")
st.metric("Longitudinal Stress σl", f"{sigma_l/1e6:.2f} MPa")
st.caption("⚠️ Placeholder. Add joint efficiency, corrosion allowance, code refs later.")
