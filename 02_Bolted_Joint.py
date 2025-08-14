
import streamlit as st, math
st.title("🔩 Bolted Joint — Placeholder (v0.2.4)")
st.markdown("Quick skeleton for preload/proof checks. Enter your numbers; formulas to be completed with your course tables.")
F = st.number_input("Service Load F (kN)", min_value=0.0, value=10.0)
phi = st.number_input("Joint stiffness factor φ", min_value=0.0, max_value=1.0, value=0.2, step=0.05)
SF = st.number_input("Desired Safety Factor", min_value=1.0, value=1.5, step=0.1)
Fpre = (F * phi) * SF
st.metric("Suggested Preload (rough)", f"{Fpre:.2f} kN")
st.caption("⚠️ Placeholder only. We'll wire in proper formulas and catalogue values next.")
