"""API Incident Triage Expert System - Streamlit UI.

A simple rule-based (symbolic AI) expert system that acts like a virtual SRE.
The UI only handles input/output; all reasoning lives in engine.py and the
knowledge lives in knowledge_base.py.
"""
import streamlit as st

import engine
from knowledge_base import RULES, QUESTIONS, DIAGNOSES

# ---------- Page setup ----------
st.set_page_config(page_title="API Incident Triage", page_icon="🛠️", layout="centered")
st.title("🛠️ API Incident Triage Expert System")
st.caption("A rule-based (symbolic AI) expert system that acts as a virtual SRE "
           "and diagnoses why your web app / API is broken.")

# Sample incidents the user can load with one click
SAMPLES = {
    "-- choose a sample incident --": "",
    "Slow checkout": "Users get 504 timeout on checkout and the database seems slow",
    "Login broken": "After the deploy users get 401 unauthorized when they log in",
    "Server errors": "The API returns 500 internal server error and memory usage is very high",
    "Site unreachable": "The website is down, DNS lookup fails and the SSL certificate expired",
}


# ---------- Session state helpers ----------
def reset():
    """Put the app back to its starting state."""
    st.session_state.stage = "describe"
    st.session_state.answers = {}
    st.session_state.detected = []
    st.session_state.history = []
    st.session_state.description = ""


if "stage" not in st.session_state:
    reset()


def question_text(fact):
    """Readable text for a fact (falls back to the fact name)."""
    return QUESTIONS.get(fact, fact.replace("_", " "))


def diag_name(diag_id):
    return DIAGNOSES.get(diag_id, {}).get("name", diag_id)


def record(fact, value):
    """Store an answer, remember it in history and rerun the app."""
    st.session_state.answers[fact] = value
    st.session_state.history.append((fact, value))
    st.rerun()


def answers_table():
    """Answers as a list of dicts so st.table can show them (no pandas)."""
    return [{"Question": question_text(f), "Answer": "Yes" if v else "No"}
            for f, v in st.session_state.answers.items()]


# ---------- Sidebar ----------
with st.sidebar:
    st.header("How it works")
    st.markdown("1. **Describe** the incident in plain English\n"
                "2. **Answer** a few yes/no questions\n"
                "3. **Get** a diagnosis, a fix and an explanation")
    st.divider()
    st.subheader("Knowledge base")
    st.metric("Rules", len(RULES))
    st.metric("Total conditions", sum(len(r["if"]) for r in RULES))
    st.metric("Diagnoses", len(DIAGNOSES))
    st.divider()
    if st.button("🔄 Start over", use_container_width=True):
        reset()
        st.rerun()
    show_kb = st.checkbox("Show knowledge base")

stage = st.session_state.stage

# ---------- Stage 1: describe the problem ----------
if stage == "describe":
    st.subheader("1️⃣ Describe the incident")
    def load_sample():
        # Callback: copy the chosen sample into the text area (only when it changes)
        if SAMPLES[st.session_state.sample]:
            st.session_state.description = SAMPLES[st.session_state.sample]

    st.selectbox("Or load a sample incident:", list(SAMPLES.keys()),
                 key="sample", on_change=load_sample)

    text = st.text_area("What is going wrong?", key="description", height=120,
                        placeholder="Users get 504 timeout on checkout and the database seems slow")

    if st.button("🔍 Analyze", type="primary", use_container_width=True):
        # NLP step: turn free text into known facts
        detected = engine.extract_facts(text)
        st.session_state.detected = detected
        st.session_state.answers = {f: True for f in detected}
        st.session_state.history = []
        st.session_state.stage = "questions"
        st.rerun()

# ---------- Stage 2: ask questions (backward/forward chaining in engine) ----------
elif stage == "questions":
    detected = st.session_state.detected
    if detected:
        st.info("**From your description I understood:**\n\n"
                + "\n".join(f"- {question_text(f)}" for f in detected))
    else:
        st.info("I could not detect any known symptoms from your description, "
                "so I will ask you some questions.")

    answers = st.session_state.answers
    # Stop as soon as a rule fires, or when there is nothing useful left to ask
    if engine.find_diagnosis(answers) is not None:
        st.session_state.stage = "result"
        st.rerun()
    q = engine.next_question(answers)
    if q is None:
        st.session_state.stage = "result"
        st.rerun()

    st.subheader(f"2️⃣ Question {len(st.session_state.history) + 1}")
    with st.container(border=True):
        st.markdown(f"### {question_text(q)}")

    c1, c2, c3 = st.columns(3)
    if c1.button("✅ Yes", use_container_width=True):
        record(q, True)
    if c2.button("❌ No", use_container_width=True):
        record(q, False)
    if c3.button("🤷 Don't know", use_container_width=True):
        record(q, False)  # unknown is treated as "not observed"

    if st.session_state.history:
        if st.button("⬅ Undo last answer"):
            fact, _ = st.session_state.history.pop()
            st.session_state.answers.pop(fact, None)
            st.rerun()

# ---------- Stage 3: show the result ----------
elif stage == "result":
    st.subheader("3️⃣ Diagnosis")
    answers = st.session_state.answers
    rule = engine.find_diagnosis(answers)

    if rule:
        diag = DIAGNOSES.get(rule["then"], {})
        st.success(f"### {diag.get('name', rule['then'])}")

        col1, col2 = st.columns(2)
        col1.metric("Layer", diag.get("layer", "-"))
        col2.metric("Confidence", f"{rule['cf'] * 100:.0f}%")
        st.progress(float(rule["cf"]))

        st.write(diag.get("description", ""))

        st.markdown("#### 🔧 Recommended fix")
        st.markdown("\n".join(f"{i}. {step}" for i, step in enumerate(diag.get("fix", []), 1)))

        with st.expander("🧠 How did I reach this? (reasoning)"):
            for line in engine.explain(rule, answers):
                st.write("• " + line)
            st.markdown(f"**Rule {rule['id']}:** IF "
                        + " AND ".join(f"`{c}`" for c in rule["if"])
                        + f" THEN **{diag_name(rule['then'])}** (CF = {rule['cf']})")
    else:
        st.warning("No rule matched your answers. Try describing the incident "
                   "in more detail (status codes, which component is slow, recent changes).")

    with st.expander("📋 All your answers", expanded=not rule):
        if answers:
            st.table(answers_table())
        else:
            st.write("No answers recorded.")

    if st.button("Diagnose another incident", type="primary", use_container_width=True):
        reset()
        st.rerun()

# ---------- Optional: show the whole knowledge base ----------
if show_kb:
    st.divider()
    st.subheader("📚 Knowledge base (rules)")
    st.dataframe([{"ID": r["id"],
                   "IF": " AND ".join(r["if"]),
                   "THEN": diag_name(r["then"]),
                   "CF": r["cf"]} for r in RULES],
                 use_container_width=True, hide_index=True)
