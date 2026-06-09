import streamlit as st
import fitz                       # reads PDF  — from pymupdf
import docx                       # reads DOCX — from python-docx
from groq import Groq
import tempfile
import os

API_KEY = st.secrets["GROQ_API_KEY"]

# ── Read text from uploaded file ────────────────────────────

def read_file(uploaded_file):
    suffix = os.path.splitext(uploaded_file.name)[1]

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name

    text = ""

    if suffix == ".pdf":
        doc = fitz.open(tmp_path)
        for page in doc:
            text += page.get_text()
        doc.close()          # ← close the PDF before deleting

    elif suffix == ".docx":
        doc  = docx.Document(tmp_path)
        text = "\n".join([p.text for p in doc.paragraphs])

    try:
        os.unlink(tmp_path)  # ← wrapped in try in case it still fails
    except:
        pass

    return text.strip()

# ── Send full chat history and get reply ──────────

def chat(history):
    client   = Groq(api_key=API_KEY)
    response = client.chat.completions.create(
        model    = "llama-3.3-70b-versatile",  # free and very smart
        messages = [
            {"role": "system", "content": """You are a helpful assistant. You can:
1. Have normal friendly conversations
2. Summarize documents when the user uploads one and asks
3. Give an ATS score when the user uploads a resume and gives a job description

For ATS scoring always:
- Give a score out of 100
- List matched keywords
- List missing important keywords
- Give 3 specific tips to improve the resume

Be friendly, clear, and concise."""}
        ] + history
    )
    return response.choices[0].message.content

# ════════════════════════════════════════════════════════════
# STREAMLIT UI
# ════════════════════════════════════════════════════════════

st.set_page_config(page_title="Chatbot", page_icon="🤖", layout="centered")
st.title("🤖 Chatbot")
st.caption("Chat · Upload a doc to summarize · Upload resume for ATS score")

# ── Session state ────────────────────────────────────────────

if "messages" not in st.session_state:
    st.session_state.messages = []   # chat history

if "doc_text" not in st.session_state:
    st.session_state.doc_text = ""   # uploaded document text

if "doc_name" not in st.session_state:
    st.session_state.doc_name = ""   # uploaded file name

# ── Sidebar ──────────────────────────────────────────────────

with st.sidebar:
    st.header("📎 Upload a Document")
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
        st.session_state.messages = []
        st.session_state.doc_text = ""
        st.session_state.doc_name = ""
        st.rerun()

    st.divider()
    st.markdown("**How to use:**")
    st.markdown("- Type anything to chat")
    st.markdown("- Upload doc → *summarize this*")
    st.markdown("- Upload resume → *ATS score for: [paste JD]*")

# ── Display chat history ─────────────────────────────────────

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ── Chat input ───────────────────────────────────────────────

user_input = st.chat_input("Type a message...")

if user_input:

    # Show user message
    with st.chat_message("user"):
        st.markdown(user_input)

    # If document is uploaded, attach it to the message
    # Only attach document if the message seems to be about it
    doc_keywords = ["summarize", "summary", "ats", "score", "resume", 
                    "document", "pdf", "file", "key points", "what does", 
                    "tell me about", "review", "analyse", "analyze"]

    user_lower = user_input.lower()
    is_doc_related = any(keyword in user_lower for keyword in doc_keywords)

    if st.session_state.doc_text and is_doc_related:
        full_message = f"""{user_input}

[Document: {st.session_state.doc_name}]
{st.session_state.doc_text}"""
    else:
        full_message = user_input

    # Save to history
    st.session_state.messages.append({
        "role"   : "user",
        "content": full_message
    })

    # Get Gemini reply
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            reply = chat(st.session_state.messages)
        st.markdown(reply)

    # Save reply to history
    st.session_state.messages.append({
        "role"   : "assistant",
        "content": reply
    })