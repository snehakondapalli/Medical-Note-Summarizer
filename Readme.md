# 🩺 Medical Note Summarizer using Groq API

This project is an AI-powered clinical note summarizer that leverages large language models (LLMs) via the **Groq API** to generate concise, physician-friendly summaries from unstructured patient notes and structured encounter data.



---

https://github.com/user-attachments/assets/d31e3489-1d2e-47bf-8ff9-ebcc74dfc31e

## 🚀 Features

- ✅ Parses and cleans raw medical notes
- ✅ Combines unstructured notes with structured `encounter_data`
- ✅ Extracts patient metadata (name, birth year) for accurate identification
- ✅ Summarizes medical histories with LLMs via Groq
- ✅ Query-based summarization by patient name and birth year
- ✅ Streamlit app for interactive usage

---

## 🛠️ Tech Stack

- **Python** (Pandas, Regex)
- **Streamlit** (interactive UI)
- **Groq API** (LLM-based summarization)
- **LLMs**: `llama3-8b-8192` or `meta-llama/llama-4-scout-17b-16e-instruct`

---

## 🧪 How It Works

1. User loads a CSV containing:
   - `note` (clinical text)
   - `encounter_data` (structured dictionary-like info)
2. System combines both fields and cleans the text
3. Model generates a structured clinical summary

---

## 🖥️ Streamlit App

### To run locally:

```bash
pip install -r requirements.txt
streamlit run app.py
