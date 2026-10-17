from __future__ import annotations

import base64
import json
import re
from datetime import datetime
from pathlib import Path

import streamlit as st

APP_DIR = Path(__file__).resolve().parent
DATA_FILE = APP_DIR / "student_data.json"
UPLOAD_DIR = APP_DIR / "uploads"
BRANCHES = {"CE": "Civil Engineering", "ME": "Mechanical Engineering"}
SEMESTERS = list(range(1, 9))
SUBJECT_SLOTS = 6

st.set_page_config(page_title="Pathway | Engineering Study Hub", page_icon="📘", layout="wide")
st.markdown("""
<style>
:root { --ink:#172b3a; --muted:#71808c; --teal:#137c72; --wash:#e6f4f1; }
.stApp { background:#f6f8f7; color:var(--ink); }
[data-testid="stSidebar"] { background:#ffffff; border-right:1px solid #e6ebed; }
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h2 { color:#172b3a; }
.block-container { max-width:1320px; padding-top:1.6rem; padding-bottom:3rem; }
[data-testid="stMetric"] { background:white; border:1px solid #e6ebed; border-radius:15px; padding:16px 18px; box-shadow:0 8px 24px #14283308; }
[data-testid="stMetricLabel"] { color:#71808c; }
[data-testid="stMetricValue"] { color:#172b3a; }
div[data-testid="stVerticalBlockBorderWrapper"] { background:#fff; border-color:#e6ebed; border-radius:15px; }
.stButton > button, .stDownloadButton > button { border-radius:9px; font-weight:650; }
.stButton > button[kind="primary"] { background:#137c72; border-color:#137c72; }
.small-muted { color:#71808c; font-size:.86rem; }
.pill { display:inline-block; background:#e6f4f1; color:#137c72; padding:4px 10px; border-radius:30px; font-size:.78rem; font-weight:700; }
</style>
""", unsafe_allow_html=True)


def empty_data():
    return {
        "profile": {"name": "", "branch": "CE", "semester": 1, "goal": "Still exploring"},
        "subjects": {b: {str(s): [f"Subject {i}" for i in range(1, SUBJECT_SLOTS + 1)] for s in SEMESTERS} for b in BRANCHES},
        "study": {},
    }


def load_data():
    if DATA_FILE.exists():
        try:
            saved = json.loads(DATA_FILE.read_text(encoding="utf-8"))
            base = empty_data()
            base["profile"].update(saved.get("profile", {}))
            for branch in BRANCHES:
                for sem in SEMESTERS:
                    incoming = saved.get("subjects", {}).get(branch, {}).get(str(sem), [])
                    if incoming:
                        base["subjects"][branch][str(sem)] = (incoming + [f"Subject {i}" for i in range(1, 7)])[:6]
                    key = study_key(branch, sem)
                    if key in saved.get("study", {}):
                        base["study"][key] = saved["study"][key]
            return base
        except (json.JSONDecodeError, OSError, TypeError):
            pass
    return empty_data()


def study_key(branch, sem):
    return f"{branch}:{sem}"


def save_data():
    APP_DIR.mkdir(parents=True, exist_ok=True)
    DATA_FILE.write_text(json.dumps(st.session_state.data, ensure_ascii=False, indent=2), encoding="utf-8")


def study_record(branch, sem):
    key = study_key(branch, sem)
    return st.session_state.data["study"].setdefault(key, {"notes": {}, "microbits": {}, "pdfs": {}})


def subject_names(branch, sem):
    return st.session_state.data["subjects"][branch][str(sem)]


def clean_filename(value):
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip("_.") or "resource"


def export_notes_pdf(title, body):
    from io import BytesIO
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.units import inch
    from xml.sax.saxutils import escape

    output = BytesIO()
    doc = SimpleDocTemplate(output, pagesize=letter, rightMargin=0.7*inch, leftMargin=0.7*inch, topMargin=0.7*inch, bottomMargin=0.7*inch)
    styles = getSampleStyleSheet()
    paragraphs = [Paragraph(escape(title), styles["Title"]), Spacer(1, 0.18*inch)]
    for line in (body or "No notes added yet.").splitlines():
        paragraphs.append(Paragraph(escape(line) if line.strip() else "&nbsp;", styles["BodyText"]))
        paragraphs.append(Spacer(1, 5))
    doc.build(paragraphs)
    return output.getvalue()


if "data" not in st.session_state:
    st.session_state.data = load_data()
if "flash_index" not in st.session_state:
    st.session_state.flash_index = 0

profile = st.session_state.data["profile"]
with st.sidebar:
    st.markdown("## 📘 Pathway")
    st.caption("Engineering Study Hub")
    st.divider()
    page = st.radio("WORKSPACE", ["Dashboard", "Courses & Notes", "Micro Bits", "Exam Practice", "Setup & Profile"], label_visibility="visible", key="page")
    st.divider()
    branch = st.selectbox("Branch", list(BRANCHES.keys()), format_func=lambda x: f"{x} · {BRANCHES[x]}", index=list(BRANCHES).index(profile.get("branch", "CE")))
    semester = st.selectbox("Semester", SEMESTERS, index=max(0, min(7, int(profile.get("semester", 1))-1)), format_func=lambda x: f"Semester {x}  ·  Year {(x+1)//2}")
    profile["branch"] = branch
    profile["semester"] = semester
    save_data()
    st.divider()
    st.markdown("**Your study space**")
    st.caption("Notes and uploads are saved on this computer in the app folder.")

record = study_record(branch, semester)
subjects = subject_names(branch, semester)
subject_name = st.session_state.get("selected_subject", subjects[0])
if subject_name not in subjects:
    subject_name = subjects[0]
    st.session_state.selected_subject = subject_name

# Page header
c1, c2 = st.columns([6, 1])
with c1:
    st.markdown(f"<span class='pill'>{BRANCHES[branch].upper()} · SEMESTER {semester}</span>", unsafe_allow_html=True)
    st.title({"Dashboard":"Your study space", "Courses & Notes":"Courses and notes", "Micro Bits":"Micro bits for quick revision", "Exam Practice":"Exam practice", "Setup & Profile":"Set up your subjects"}[page])
    st.markdown(f"Welcome{', ' + profile['name'] if profile.get('name') else ''}. Keep your notes, revision points, and exam practice together.")
with c2:
    st.write("")
    st.write("")
    st.markdown("### 🎓")

if page == "Dashboard":
    filled = sum(1 for x in subjects if not x.lower().startswith("subject "))
    note_count = sum(1 for x in record.get("notes", {}).values() if x.strip())
    bit_count = sum(len(x) for x in record.get("microbits", {}).values())
    pdf_count = sum(len(x) for x in record.get("pdfs", {}).values())
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Subjects this semester", f"{filled}/6")
    m2.metric("Notes saved", note_count)
    m3.metric("Micro bits", bit_count)
    m4.metric("PDF resources", pdf_count)
    st.write("")
    left, right = st.columns([1.5, 1])
    with left:
        with st.container(border=True):
            st.subheader("Your semester at a glance")
            st.caption("Choose a subject to open its notes, revision bits, and resources.")
            for i, name in enumerate(subjects, 1):
                row = st.columns([0.5, 5, 1.2])
                row[0].markdown(f"**{i:02d}**")
                row[1].write(name)
                if row[2].button("Open", key=f"open_{i}"):
                    st.session_state.selected_subject = name
                    st.session_state.page = "Courses & Notes"
                    st.rerun()
    with right:
        with st.container(border=True):
            st.subheader("Quick revision")
            st.caption("A few minutes of active recall can help you spot gaps.")
            if bit_count:
                all_bits = [(sub, bit) for sub, bits in record.get("microbits", {}).items() for bit in bits]
                st.info(f"{len(all_bits)} micro bit(s) ready across your subjects.")
                if st.button("Start a quick review", type="primary"):
                    st.session_state.page = "Micro Bits"
                    st.rerun()
            else:
                st.write("Add short definitions, formulas, or key facts in **Micro Bits** to start a revision set.")
        with st.container(border=True):
            st.subheader("Your study material")
            st.write("Use the subject setup to replace the six editable subject slots for each semester.")
            if st.button("Set up my subjects"):
                st.session_state.page = "Setup & Profile"
                st.rerun()

elif page == "Courses & Notes":
    with st.container(border=True):
        st.subheader("Select a subject")
        subject_name = st.selectbox("Subject", subjects, key="course_subject_select", index=subjects.index(subject_name))
        st.session_state.selected_subject = subject_name
    note_key = subject_name
    current_note = record["notes"].get(note_key, "")
    left, right = st.columns([1.25, 1])
    with left:
        with st.container(border=True):
            st.subheader("Class notes")
            st.caption("Type or paste your own notes. They are saved in the local app data file.")
            notes = st.text_area("Notes", current_note, height=310, placeholder="Add definitions, concepts, derivations, examples, or reminders...", label_visibility="collapsed", key=f"note_{branch}_{semester}_{clean_filename(subject_name)}")
            b1, b2 = st.columns([1, 1])
            if b1.button("Save notes", type="primary", key="save_note"):
                record["notes"][note_key] = notes
                save_data()
                st.success("Notes saved on this computer.")
            pdf_bytes = export_notes_pdf(f"{subject_name} - Semester {semester}", notes)
            b2.download_button("Download notes as PDF", data=pdf_bytes, file_name=f"{branch}_Sem{semester}_{clean_filename(subject_name)}_notes.pdf", mime="application/pdf")
    with right:
        with st.container(border=True):
            st.subheader("Subject PDFs")
            st.caption("Upload lecture handouts or your own PDF study sheets for this subject.")
            uploaded = st.file_uploader("Choose a PDF", type=["pdf"], key=f"pdf_upload_{branch}_{semester}_{clean_filename(subject_name)}")
            if uploaded and st.button("Save PDF to this subject", key="save_pdf"):
                UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
                safe = clean_filename(uploaded.name)
                filename = f"{branch}_S{semester}_{clean_filename(subject_name)}_{safe}"
                target = UPLOAD_DIR / filename
                target.write_bytes(uploaded.getvalue())
                record["pdfs"].setdefault(note_key, [])
                if not any(p.get("file") == filename for p in record["pdfs"][note_key]):
                    record["pdfs"][note_key].append({"file": filename, "name": uploaded.name})
                save_data()
                st.success("PDF saved.")
                st.rerun()
            files = record.get("pdfs", {}).get(note_key, [])
            if files:
                choice = st.selectbox("Saved PDFs", range(len(files)), format_func=lambda i: files[i]["name"], key="saved_pdf_choice")
                chosen = files[choice]
                path = UPLOAD_DIR / chosen["file"]
                if path.exists():
                    data = path.read_bytes()
                    st.download_button("Download selected PDF", data=data, file_name=chosen["name"], mime="application/pdf")
                    with st.expander("Preview PDF"):
                        encoded = base64.b64encode(data).decode("ascii")
                        st.markdown(f'<iframe src="data:application/pdf;base64,{encoded}" width="100%" height="480" style="border:1px solid #e6ebed;border-radius:10px"></iframe>', unsafe_allow_html=True)
                else:
                    st.warning("The saved PDF file is missing from the uploads folder.")
            else:
                st.caption("No PDFs saved for this subject yet.")

elif page == "Micro Bits":
    with st.container(border=True):
        st.subheader("Choose a subject")
        subject_name = st.selectbox("Subject", subjects, key="micro_subject_select", index=subjects.index(subject_name))
        st.session_state.selected_subject = subject_name
    bits = record["microbits"].setdefault(subject_name, [])
    left, right = st.columns([1.15, 1])
    with left:
        with st.container(border=True):
            st.subheader("Add a micro bit")
            st.caption("Keep each item short: one formula, definition, fact, or memory cue.")
            with st.form("microbit_form", clear_on_submit=True):
                prompt = st.text_input("Prompt or topic", placeholder="e.g. Define a key term")
                answer = st.text_area("Answer / reminder", placeholder="Write a short, clear answer...")
                add = st.form_submit_button("Save micro bit", type="primary")
            if add:
                if prompt.strip() and answer.strip():
                    bits.append({"prompt": prompt.strip(), "answer": answer.strip()})
                    record["microbits"][subject_name] = bits
                    save_data()
                    st.success("Micro bit saved.")
                    st.rerun()
                else:
                    st.error("Add both a prompt and its answer.")
            if bits:
                st.markdown("#### Saved micro bits")
                for i, bit in enumerate(bits):
                    with st.expander(bit["prompt"]):
                        st.write(bit["answer"])
                        if st.button("Delete this micro bit", key=f"del_bit_{i}"):
                            bits.pop(i)
                            record["microbits"][subject_name] = bits
                            save_data()
                            st.rerun()
    with right:
        with st.container(border=True):
            st.subheader("Quick flip review")
            if bits:
                idx = st.session_state.flash_index % len(bits)
                bit = bits[idx]
                st.markdown(f"**Recall:** {bit['prompt']}")
                if st.button("Reveal answer", key="reveal_bit"):
                    st.info(bit["answer"])
                x, y = st.columns(2)
                if x.button("← Previous"):
                    st.session_state.flash_index = (idx - 1) % len(bits)
                    st.rerun()
                if y.button("Next →"):
                    st.session_state.flash_index = (idx + 1) % len(bits)
                    st.rerun()
                st.caption(f"Card {idx + 1} of {len(bits)}")
            else:
                st.info("No revision cards yet. Add a few prompts and short answers to begin.")
            st.caption("Micro bits are your own material; check facts and formulas against your course references.")

elif page == "Exam Practice":
    with st.container(border=True):
        st.subheader("Choose a subject")
        subject_name = st.selectbox("Subject", subjects, key="exam_subject_select", index=subjects.index(subject_name))
        st.session_state.selected_subject = subject_name
    bits = record["microbits"].get(subject_name, [])
    if not bits:
        st.info("Add micro bits for this subject first. They become your self-test question bank.")
        if st.button("Go to Micro Bits", type="primary"):
            st.session_state.page = "Micro Bits"
            st.rerun()
    else:
        st.markdown("#### Self-test")
        st.caption("Try to answer before revealing the reminder. Track what you need to revise again.")
        if "exam_order" not in st.session_state or st.session_state.get("exam_subject") != subject_name:
            st.session_state.exam_order = list(range(len(bits)))
            st.session_state.exam_position = 0
            st.session_state.exam_subject = subject_name
        pos = st.session_state.exam_position % len(bits)
        bit = bits[st.session_state.exam_order[pos]]
        with st.container(border=True):
            st.markdown(f"### {bit['prompt']}")
            answer = st.text_area("Your answer", key=f"exam_answer_{pos}", placeholder="Try recalling the answer before revealing it...")
            if st.button("Show reminder", type="primary"):
                st.success(bit["answer"])
            col_a, col_b, col_c = st.columns([1, 1, 3])
            if col_a.button("Need to revise"):
                st.session_state.exam_position = (pos + 1) % len(bits)
                st.rerun()
            if col_b.button("Got it"):
                st.session_state.exam_position = (pos + 1) % len(bits)
                st.rerun()
            col_c.caption(f"Question {pos + 1} of {len(bits)} · Built from your own micro bits")
        st.caption("This is a personal revision aid, not an official exam paper or a guarantee of syllabus coverage.")

elif page == "Setup & Profile":
    left, right = st.columns([1, 1.2])
    with left:
        with st.container(border=True):
            st.subheader("Student profile")
            name = st.text_input("Name (optional)", profile.get("name", ""))
            goal_options = ["Still exploring", "Design and analysis", "Construction and infrastructure", "Manufacturing and production", "Government exams", "Higher studies and research"]
            goal = st.selectbox("Current goal", goal_options, index=goal_options.index(profile.get("goal", goal_options[0])) if profile.get("goal") in goal_options else 0)
            if st.button("Save profile", type="primary"):
                profile["name"] = name.strip()
                profile["goal"] = goal
                save_data()
                st.success("Profile saved.")
    with right:
        with st.container(border=True):
            st.subheader(f"Edit the six subject slots · {branch} semester {semester}")
            st.caption("Subject titles vary by university. Replace these editable placeholders with your own syllabus names.")
            with st.form(f"subjects_{branch}_{semester}"):
                new_subjects = []
                for i, old in enumerate(subjects, 1):
                    new_subjects.append(st.text_input(f"Subject {i}", old, key=f"subj_{branch}_{semester}_{i}"))
                save_subjects = st.form_submit_button("Save semester subjects", type="primary")
            if save_subjects:
                st.session_state.data["subjects"][branch][str(semester)] = [x.strip() or f"Subject {i}" for i, x in enumerate(new_subjects, 1)]
                save_data()
                st.success("The six subject slots have been saved.")
                st.rerun()
    with st.container(border=True):
        st.subheader("All eight semesters")
        st.caption("Set up each semester by choosing it in the sidebar and editing its six subject slots. This keeps the app suitable for different university syllabi.")
        cols = st.columns(4)
        for sem in SEMESTERS:
            with cols[(sem-1) % 4]:
                filled_sem = sum(1 for x in subject_names(branch, sem) if not x.lower().startswith("subject "))
                st.metric(f"Semester {sem}", f"{filled_sem}/6 named")


