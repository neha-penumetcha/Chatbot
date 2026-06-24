import streamlit as st
import fitz
import docx
from groq import Groq
import tempfile
import os
import re

API_KEY = st.secrets["GROQ_API_KEY"]

# ── Prompts ──────────────────────────────────────────────────

CHAT_SYSTEM = """You are a helpful assistant. Be friendly, clear, and concise."""

ATS_SYSTEM = """You are an expert ATS (Applicant Tracking System) analyst and resume coach.

When given a resume and job description, produce an ATS analysis in EXACTLY this format — no extra text:

ATS SCORE: [X/100]

SCORE BREAKDOWN:
- Keyword Match: [X/40]
- Skills Alignment: [X/25]
- Experience Relevance: [X/20]
- Education & Certifications: [X/10]
- Formatting/Parseability: [X/5]

MATCHED KEYWORDS: [comma-separated list]

MISSING KEYWORDS: [comma-separated list of important missing terms]

STRENGTHS:
- [strength 1]
- [strength 2]

TOP 3 IMPROVEMENTS:
1. [specific, actionable fix]
2. [specific, actionable fix]
3. [specific, actionable fix]

Keep the entire response under 400 words."""

SUMMARY_SYSTEM = """You are a document analyst. Summarize the given document clearly and concisely.
Structure: Overview (2-3 sentences), Key Points (bullet list), Conclusion (1 sentence).
Keep it under 300 words."""

# ── File reading ─────────────────────────────────────────────

def read_file(uploaded_file):
    suffix = os.path.splitext(uploaded_file.name)[1].lower()
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name

    text = ""
    if suffix == ".pdf":
        doc = fitz.open(tmp_path)
        for page in doc:
            text += page.get_text()
        doc.close()
    elif suffix == ".docx":
        doc = docx.Document(tmp_path)
        text = "\n".join([p.text for p in doc.paragraphs])

    try:
        os.unlink(tmp_path)
    except:
        pass

    return text.strip()

# ── Token-efficient text trimmer ─────────────────────────────

def trim(text, max_chars=3000):
    """Keep text under max_chars to save tokens."""
    return text[:max_chars] + "\n[truncated]" if len(text) > max_chars else text

# ── Intent detection ─────────────────────────────────────────

def detect_intent(user_input: str) -> str:
    """Returns 'ats', 'summary', or 'chat'."""
    lower = user_input.lower()
    ats_words    = ["ats", "score", "job description", "jd", "match", "keywords", "tailor"]
    summary_words= ["summarize", "summary", "key points", "what does", "explain", "overview", "what is this"]
    if any(w in lower for w in ats_words):
        return "ats"
    if any(w in lower for w in summary_words):
        return "summary"
    return "chat"

# ── API calls ─────────────────────────────────────────────────

def call_groq(system_prompt: str, user_message: str, history: list = None):
    client = Groq(api_key=API_KEY)
    messages = [{"role": "system", "content": system_prompt}]
    if history:
        messages += history[-6:]  # only last 3 exchanges for context
    messages.append({"role": "user", "content": user_message})

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        max_tokens=600,       # tight limit for ATS/summary
        temperature=0.3,      # lower = more consistent ATS output
    )
    return response.choices[0].message.content

def run_ats(resume_text: str, user_input: str) -> str:
    """Extract JD from user message, run focused ATS analysis."""
    # Try to isolate the job description part from the message
    jd_text = user_input
    for prefix in ["ats score for:", "ats score:", "score for:", "score this for:"]:
        if prefix in user_input.lower():
            jd_text = user_input[user_input.lower().index(prefix) + len(prefix):].strip()
            break

    prompt = f"""RESUME:
{trim(resume_text, 2500)}

JOB DESCRIPTION:
{trim(jd_text, 1500)}"""

    return call_groq(ATS_SYSTEM, prompt)

def run_summary(doc_text: str, doc_name: str) -> str:
    prompt = f"Document: {doc_name}\n\n{trim(doc_text, 3000)}"
    return call_groq(SUMMARY_SYSTEM, prompt)

def run_chat(user_input: str, history: list) -> str:
    return call_groq(CHAT_SYSTEM, user_input, history)

# ════════════════════════════════════════════════════════════
# STREAMLIT UI
# ════════════════════════════════════════════════════════════

st.set_page_config(page_title="Resume ATS Checker", page_icon="📄", layout="centered")
st.title("📄 Resume ATS Checker & Doc Summarizer")
st.caption("Chat · Summarize documents · Get ATS score for your resume")

# ── Session state ─────────────────────────────────────────────

for key, default in {
    "messages": [],
    "doc_text": "",
    "doc_name": "",
    "chat_history": [],  # lean history for chat context (no doc blobs)
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ── Sidebar ───────────────────────────────────────────────────

with st.sidebar:
    st.header("📎 Upload a File")
    uploaded = st.file_uploader("PDF or Word file", type=["pdf", "docx"])

    if uploaded:
        if uploaded.name != st.session_state.doc_name:
            with st.spinner("Reading file..."):
                st.session_state.doc_text = read_file(uploaded)
                st.session_state.doc_name = uploaded.name
        st.success(f"✅ {st.session_state.doc_name}")
        st.caption(f"{len(st.session_state.doc_text):,} characters extracted")

    st.divider()
    if st.button("🗑️ Clear chat"):
        st.session_state.messages      = []
        st.session_state.chat_history  = []
        st.session_state.doc_text      = ""
        st.session_state.doc_name      = ""
        st.rerun()

    st.divider()
    st.markdown("**How to use:**")
    st.markdown("- 💬 Type anything to chat")
    st.markdown("- 📄 Upload doc → *summarize this*")
    st.markdown("- 📋 Upload resume → *ATS score for: [paste job description]*")

# ── Display chat history ──────────────────────────────────────

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ── Chat input ────────────────────────────────────────────────

user_input = st.chat_input("Type a message...")

if user_input:
    with st.chat_message("user"):
        st.markdown(user_input)

    intent = detect_intent(user_input)
    reply  = ""

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):

            if intent == "ats" and st.session_state.doc_text:
                reply = run_ats(st.session_state.doc_text, user_input)

            elif intent == "summary" and st.session_state.doc_text:
                reply = run_summary(st.session_state.doc_text, st.session_state.doc_name)

            elif intent in ("ats", "summary") and not st.session_state.doc_text:
                reply = "Please upload a file first using the sidebar, then ask again!"

            else:
                # Pure chat — pass lean history, no doc blobs
                reply = run_chat(user_input, st.session_state.chat_history)

        st.markdown(reply)

    # Save display history (full content for UI)
    st.session_state.messages.append({"role": "user",      "content": user_input})
    st.session_state.messages.append({"role": "assistant", "content": reply})

    # Save lean chat history (no doc blobs — keeps tokens low)
    st.session_state.chat_history.append({"role": "user",      "content": user_input})
    st.session_state.chat_history.append({"role": "assistant", "content": reply})
