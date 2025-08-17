
import streamlit as st
from fpdf import FPDF
from datetime import date
import json
from io import BytesIO

APP_TITLE = "OMEC Habit Tracker - v0.3 (PDF only)"
DEFAULT_TASKS = ["Stretching", "German Lessons", "OMEC Designs", "Paint Bathroom"]

# ---------------- UI THEME (OMEC style, ASCII-safe) ----------------
st.set_page_config(page_title=APP_TITLE, layout="centered")

OMEC_PRIMARY = "#0EA5A1"  # teal-ish
OMEC_BG = "#0B1620"       # deep navy
OMEC_CARD = "#111827"     # dark card
OMEC_TEXT = "#E5E7EB"     # light text

css = f"""
<style>
  .stApp {{
    background-color: {OMEC_BG};
    color: {OMEC_TEXT};
  }}
  .omec-card {{
    background: {OMEC_CARD};
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 16px;
    padding: 1.2rem 1.2rem;
    box-shadow: 0 6px 30px rgba(0,0,0,0.35);
  }}
  .omec-pill {{
    display: inline-block;
    padding: 4px 10px;
    border-radius: 999px;
    background: {OMEC_PRIMARY}22;
    border: 1px solid {OMEC_PRIMARY}66;
    color: {OMEC_TEXT};
    font-size: 0.85rem;
    margin-right: 8px;
  }}
  .small {{
    opacity: 0.8;
    font-size: 0.9rem;
  }}
</style>
"""
st.markdown(css, unsafe_allow_html=True)

# ---------------- Session state ----------------
if "tasks" not in st.session_state:
    st.session_state.tasks = DEFAULT_TASKS.copy()

# ---------------- Header ----------------
st.markdown("<div class='omec-card'><h1 style='margin:0'>OMEC Habit Tracker</h1><div class='small'>v0.3 - PDF export - No data stored</div></div>", unsafe_allow_html=True)
st.write("")

# ---------------- Task Manager ----------------
with st.container():
    st.markdown("<div class='omec-card'>", unsafe_allow_html=True)
    st.subheader("Task Manager")
    st.caption("Add/edit your own tasks. Import/export presets to reuse later. (We don't store anything.)")

    colA, colB = st.columns([2,1])
    with colA:
        raw_tasks = st.text_area("Tasks (one per line)", value="\n".join(st.session_state.tasks), height=140)
    with colB:
        new_task = st.text_input("Quick add")
        if st.button("Add"):
            t = new_task.strip()
            if t:
                lines = [x.strip() for x in raw_tasks.splitlines() if x.strip()]
                lines.append(t)
                raw_tasks = "\n".join(sorted(set(lines), key=lambda x: lines.index(x)))
                st.session_state.tasks = [x for x in raw_tasks.splitlines() if x.strip()]
                st.success(f"Added: {t}")
                st.rerun()

        if st.button("Apply edits"):
            st.session_state.tasks = [x.strip() for x in raw_tasks.splitlines() if x.strip()]
            st.success("Tasks updated.")

    # Import / Export presets
    c1, c2 = st.columns(2)
    with c1:
        up = st.file_uploader("Import preset (.json)", type=["json"])
        if up is not None:
            try:
                data = json.load(up)
                if isinstance(data, dict) and "tasks" in data and isinstance(data["tasks"], list):
                    st.session_state.tasks = [str(x) for x in data["tasks"] if str(x).strip()]
                    st.success("Preset loaded.")
                    st.rerun()
                else:
                    st.error("Invalid preset format. Expecting { 'tasks': [ ... ] }")
            except Exception as e:
                st.error(f"Could not read preset: {e}")
    with c2:
        preset = json.dumps({"tasks": st.session_state.tasks}, indent=2)
        st.download_button("Export preset (.json)", data=preset, file_name="OMEC_tasks_preset.json", mime="application/json")

    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- Daily Check-in ----------------
with st.container():
    st.markdown("<div class='omec-card'>", unsafe_allow_html=True)
    st.subheader("Daily Check-in")
    col1, col2 = st.columns([1,2])
    with col1:
        selected_date = st.date_input("Date", value=date.today())
    with col2:
        st.markdown("<span class='omec-pill'>No autosave</span><span class='omec-pill'>Export to PDF</span>", unsafe_allow_html=True)

    checks = {}
    if len(st.session_state.tasks) == 0:
        st.info("No tasks. Add tasks above to start tracking.")
    else:
        grid_cols = st.columns(2)
        for i, task in enumerate(st.session_state.tasks):
            with grid_cols[i % 2]:
                checks[task] = st.checkbox(task, value=False, key=f"chk_{i}")

    notes = st.text_area("Notes (optional)", placeholder="Wins / obstacles / quick notes...")
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- PDF Generation ----------------
class HabitPDF(FPDF):
    def header(self):
        self.set_fill_color(14,165,161)
        self.rect(0, 0, 210, 18, 'F')
        self.set_text_color(255,255,255)
        self.set_font("Helvetica", "B", 14)
        self.set_xy(10, 5)
        self.cell(0, 8, "OMEC Habit Tracker - v0.3", 0, 1, "L")

    def footer(self):
        self.set_y(-15)
        self.set_text_color(150,150,150)
        self.set_font("Helvetica", "", 9)
        self.cell(0, 10, "Generated by OMEC Habit Tracker - file is your record (no data stored)", 0, 0, "C")

def sanitize_ascii(text: str) -> str:
    replacements = {
        "—": "-",
        "–": "-",
        "✅": "",
        "☑": "[x]",
        "☐": "[ ]",
        "•": "-",
        "...": "...",
        "’": "'",
        "“": '"',
        "”": '"'
    }
    for k,v in replacements.items():
        text = text.replace(k,v)
    return text.encode("latin-1", "ignore").decode("latin-1")

def generate_pdf(d: date, checks: dict, notes: str) -> bytes:
    pdf = HabitPDF()
    pdf.set_auto_page_break(auto=True, margin=16)
    pdf.add_page()

    # Title
    pdf.set_text_color(31,41,55)
    pdf.set_xy(10, 24)
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, sanitize_ascii(f"Daily Log - {d.isoformat()}"), ln=1)

    # Checklist
    pdf.set_font("Helvetica", "", 12)
    pdf.ln(2)
    for task, done in checks.items():
        box = "[x]" if done else "[ ]"
        pdf.cell(0, 8, sanitize_ascii(f"{box}  {task}"), ln=1)

    # Notes
    pdf.ln(4)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Notes:", ln=1)
    pdf.set_font("Helvetica", "", 12)
    safe_notes = sanitize_ascii(notes or "")
    if safe_notes.strip():
        for line in safe_notes.splitlines():
            pdf.multi_cell(0, 6, line)
    else:
        pdf.set_text_color(120,120,120)
        pdf.cell(0, 6, "-", ln=1)
        pdf.set_text_color(31,41,55)

    # Summary footer
    pdf.ln(6)
    done_count = sum(1 for v in checks.values() if v)
    total = max(1, len(checks))
    pct = int(done_count * 100 / total) if total > 0 else 0
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, sanitize_ascii(f"Completion: {done_count}/{total} tasks - {pct}%"), ln=1)

    return pdf.output(dest="S").encode("latin-1")

st.markdown("<div class='omec-card'>", unsafe_allow_html=True)
st.subheader("Export")
if st.button("Generate PDF"):
    if not st.session_state.tasks:
        st.warning("Add at least one task in the Task Manager.")
    else:
        pdf_bytes = generate_pdf(selected_date, checks, notes)
        st.download_button("Download Daily Log (PDF)", data=pdf_bytes, file_name=f"OMEC_Daily_Log_{selected_date.isoformat()}.pdf", mime="application/pdf")
        st.success("PDF ready. Save it wherever you want. No data was stored.")
st.markdown("</div>", unsafe_allow_html=True)

st.caption("Tip: Keep your PDFs and task presets in organized folders, e.g., OMEC/Habits/2025-08.")
