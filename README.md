# Machine Design Toolkit (N5/N6) — v0.2.3

**Fix:** Duplicate widget IDs in Streamlit tabs caused an error. v0.2.3 adds unique `key=` values to every widget.

Quick start:
```bash
python -m venv .venv && source .venv/bin/activate  # (Windows: .venv\Scripts\activate)
pip install -r requirements.txt
streamlit run app.py
```
