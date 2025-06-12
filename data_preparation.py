import pandas as pd
import re
from groq import Groq

import time
import requests

train_csv = pd.read_csv('train.csv')



def clean_note(text):
    text = re.sub(r'\*\*.*?\*\*', '', text)  # Remove markdown bold
    text = re.sub(r'\s+', ' ', text)  # Remove extra whitespace
    return text.strip()

train_csv['clean_note'] = train_csv['note'].apply(clean_note)
train_csv['clean_note'][0]
print(train_csv['clean_note'][0])


GROQ_API_KEY = "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"  # Replace with your actual Groq API key
# client = Groq(api_key=API_KEY)  # FIXED: removed quotes around variable

system_prompt = (
    "You are a clinical summarizer tasked with generating concise, informative summaries for patient medical records. "
    "Summaries must be accurate, formal, and easy for a doctor to understand. Do not include doctors' names, prescription details, or information unrelated to the patient."
)

user_prompt_template = (
    'Given the following patient and his notes: "{prompt_notes}"\n\n'
    "Generate a complete but concise (max 100 words) and informative summary that focuses only on the unique patient, who is always the same throughout the note. "
    "The summary should emphasize the patient’s medical history, current condition, and any relevant diagnostic or procedural details, beginning with the present condition and moving backward chronologically.\n\n"

    "FOR EXAMPLE:\n"
    "The patient currently is a age-year-old gender who presented with chief complaint and has a medical history of relevant medical conditions.\n"
    "The patient was involved in incident/accident description, which led to specific injuries/traumas.\n"
    "The postoperative course involved relevant procedures performed on anatomical locations involved.\n"
    "The patient is currently prescribed medications for specific purposes.\n\n"

    "The summary must:\n"
    "- Begin with: 'The patient is a: '\n"
    "- Be formal and informative\n"
    "- Be no more than 100 words\n"
    "- Avoid unnecessary repetition\n"
    "- Avoid doctors’ names\n"
    "- Avoid dosage/prescription details\n"
    "- Focus only on the patient described\n"
    "- Include dates with full format (Year, Month, Day)"
)

def summarize_note1(note_text):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    user_prompt = user_prompt_template.replace("{prompt_notes}", note_text)

    payload = {
        "model": "llama3-8b-8192",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.3,
        "max_tokens": 1024
    }

    response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload)

    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return f"Error: {response.status_code}, {response.text}"


def find_patient_row(df, patient_name):
    for i, note in enumerate(df['clean_note']):
        if patient_name.lower() in note.lower():
            return i, note
    return None, None


def summarize_by_patient(df, patient_name):
    row_idx, note = find_patient_row(df, patient_name)

    if note is None:
        return f"No patient found with name: {patient_name}"

    # print(f"✅ Found patient note at row {row_idx}. Summarizing...")

    return summarize_note1(note)