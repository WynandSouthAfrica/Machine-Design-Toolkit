
import streamlit as st

st.set_page_config(page_title="Machine Design Toolkit v0.2.4", layout="wide")
st.title("🛠️ Machine Design Toolkit — v0.2.4")

st.markdown("""
Welcome, Wynand! This **all‑in‑one** app hosts your growing set of design calculators.

**Included pages (left sidebar → Pages):**
- **Belt Drive Designer** — to‑scale geometry + catalogue assist
- **Bolted Joint** — quick preload & proof check (placeholder)
- **Shaft Sizing** — rough torsion sizing (placeholder)
- **Bearing Life** — L10 life skeleton (placeholder)
- **Fillet Weld** — shear capacity skeleton (placeholder)
- **Thin Cylinder** — hoop/longitudinal stress (placeholder)

> Version **v0.2.4**: first integrated toolkit with the new Belt Drive visualiser.
""")

st.info("Tip: Keep this folder in a Git repo. Tag versions like v0.2.4 as you iterate.")
