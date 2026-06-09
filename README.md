# 🤖 Resume & Document Chatbot

A free, AI-powered chatbot built with Python and Streamlit that can hold normal conversations, summarize any document, and give detailed ATS (Applicant Tracking System) scores for resumes.

🔗 **Live Demo**: [https://chatbot-ua8i2g7cenmd3jrnwvmotz.streamlit.app/](https://chatbot-ua8i2g7cenmd3jrnwvmotz.streamlit.app/)

---

## ✨ Features

- 💬 **Normal Chat** — Have casual conversations with an AI assistant
- 📄 **Document Summarization** — Upload any PDF or DOCX and ask it to summarize
- 📊 **ATS Score** — Upload your resume and paste a job description to get a detailed ATS match score, missing keywords, and improvement tips
- 🆓 **Completely Free** — Uses Groq's free API (no credit card needed)
- 🌐 **Deployed Online** — Accessible from any device, anywhere

---

## 🖼️ How It Looks

| Feature | What to do |
|---|---|
| Chat | Just type in the message box |
| Summarize | Upload a PDF/DOCX → type "summarize this" |
| ATS Score | Upload resume → type "ATS score for: [paste job description]" |
| Key points | Upload a doc → type "what are the key points?" |

---

## 🛠️ Tech Stack

| Tool | Purpose |
|---|---|
| Python | Core programming language |
| Streamlit | Web UI framework |
| Groq API (llama-3.3-70b) | Free AI model for chat and analysis |
| PyMuPDF (fitz) | Reading and extracting text from PDF files |
| python-docx | Reading and extracting text from Word files |

---

## 🚀 Run It Locally

### Step 1 — Clone the repository

```bash
git clone https://github.com/YOUR-USERNAME/resume-chatbot.git
cd resume-chatbot
```

### Step 2 — Install dependencies

```bash
pip install -r requirements.txt
```

### Step 3 — Get a free Groq API key

1. Go to 👉 [console.groq.com](https://console.groq.com)
2. Sign up with Google
3. Go to **API Keys** → **Create API key**
4. Copy the key (starts with `gsk_...`)

### Step 4 — Add your API key

Create a folder called `.streamlit` in the project directory and inside it create a file called `secrets.toml`:

```
resume-chatbot/
└── .streamlit/
        └── secrets.toml
```

Inside `secrets.toml` paste:

```toml
GROQ_API_KEY = "gsk_your-actual-key-here"
```

### Step 5 — Run the app

```bash
streamlit run chatbot.py
```

Open your browser at `http://localhost:8501` and you're good to go!

---

## 📁 Project Structure

```
resume-chatbot/
│
├── chatbot.py              # Main application code
├── requirements.txt        # Python libraries needed
├── .gitignore              # Tells Git to ignore secrets
├── README.md               # This file
└── .streamlit/
        └── secrets.toml    # Your API key (NOT uploaded to GitHub)
```

---

## 🔒 Environment Variables

This project uses Streamlit Secrets to keep the API key safe. Never hardcode your API key in the code.

| Variable | Description |
|---|---|
| `GROQ_API_KEY` | Your free Groq API key from console.groq.com |

When deploying to Streamlit Cloud, add this in **App Settings → Secrets**:

```toml
GROQ_API_KEY = "gsk_your-actual-key-here"
```

---

## ☁️ Deploy Your Own

1. Fork this repository
2. Go to 👉 [share.streamlit.io](https://share.streamlit.io)
3. Click **"New app"** → select your forked repo
4. Set main file as `chatbot.py`
5. Go to **Advanced settings → Secrets** and add your `GROQ_API_KEY`
6. Click **Deploy** — your app is live in minutes!

---

## 📦 Dependencies

```
streamlit
pymupdf
python-docx
groq
```

Install all at once:
```bash
pip install -r requirements.txt
```

---

## 🙋 How to Use

### Normal conversation
Just type anything in the chat box — the bot will respond naturally.

### Summarize a document
1. Click **"Browse files"** in the left sidebar
2. Upload a PDF or DOCX file
3. Type **"summarize this"** in the chat
4. Get a clean, structured summary instantly

### Get ATS score for your resume
1. Upload your resume PDF or DOCX in the sidebar
2. Find a job description you want to apply for
3. Type in the chat: **"ATS score for: [paste the full job description here]"**
4. Get a score out of 100, matched keywords, missing keywords, and improvement tips

### Clear the chat
Click **"🗑️ Clear chat"** in the sidebar to start fresh.

---

## ⚠️ Limitations

- Groq free tier has a daily request limit (plenty for personal use)
- Scanned PDF files (images of text) cannot be read — only text-based PDFs work
- Very large documents may be slow to process


