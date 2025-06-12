import streamlit as st
import pandas as pd
import re
import requests
from groq import Groq
import os

# Load the Groq API key from Streamlit secrets
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]

# --- Functions from data_preparation.py ---

def clean_note(text):
    text = re.sub(r'\*\*.*?\*\*', '', text)  # Remove markdown bold
    text = re.sub(r'\s+', ' ', text)  # Remove extra whitespace
    return text.strip()

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

def summarize_note1(note_text, model_name):
    client = Groq(api_key=GROQ_API_KEY)
    user_prompt = user_prompt_template.replace("{prompt_notes}", note_text)

    try:
        completion = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=1024,
            stream=False, # Set to False for direct response
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error communicating with Groq API using model {model_name}: {e}"


def extract_patient_info(df):
    patient_data = {}
    name_pattern = re.compile(r'Name:\s*([A-Za-z\s\.]+)')
    age_pattern = re.compile(r'Age:\s*(\d+)\s*years? old')

    for idx, note in df.iterrows():
        clean_note_text = note['clean_note']
        original_note_text = note['note']

        name_match = name_pattern.search(clean_note_text)
        age_match = age_pattern.search(clean_note_text)

        patient_name = name_match.group(1).strip() if name_match else f"Patient {idx+1}"
        patient_age = int(age_match.group(1)) if age_match else None

        # Generate a unique patient ID based on the row index
        unique_id = f"Patient ID {idx + 1}"
        
        patient_data[unique_id] = {
            "original_note": original_note_text,
            "clean_note": clean_note_text,
            "index": idx,
            "patient_name": patient_name, # Store name for potential future use
            "patient_age": patient_age    # Store age for potential future use
        }
    return patient_data

def summarize_by_unique_id(patient_data_map, unique_id):
    if unique_id not in patient_data_map:
        return f"Error: Unique ID '{unique_id}' not found."

    patient_info = patient_data_map[unique_id]
    note_text = patient_info["clean_note"]
    row_idx = patient_info["index"]

    # st.info(f"✅ Found patient note for '{unique_id}' at row {row_idx}. Summarizing...")
    return summarize_note1(note_text, st.session_state.selected_model), patient_info["original_note"]

# --- Streamlit App Layout ---

st.set_page_config(page_title="Medical Note Summarizer", layout="wide")

st.title("Medical Note Summarizer")
st.markdown("Select a patient from the dropdown to retrieve and summarize their medical notes.")

# Model selection using radio buttons
model_options = {
    "Llama 3 8B": "llama3-8b-8192",
    "Llama 4 Scout 17B": "meta-llama/llama-4-scout-17b-16e-instruct"
}

if "selected_model" not in st.session_state:
    st.session_state.selected_model = model_options["Llama 3 8B"]

selected_model_name = st.radio(
    "Choose a summarization model:",
    list(model_options.keys()),
    index=list(model_options.keys()).index(next(key for key, value in model_options.items() if value == st.session_state.selected_model)),
    key="model_selector"
)

st.session_state.selected_model = model_options[selected_model_name]

# Load data with caching
@st.cache_data
def load_data(path):
    try:
        df = pd.read_csv(path)
        df['clean_note'] = df['note'].apply(clean_note)
        return df
    except FileNotFoundError:
        st.error(f"Error: The file '{path}' was not found. Please ensure 'train.csv' is in the correct directory.")
        return None
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

# Use the provided path for train.csv
csv_path = "train.csv" # This assumes train.csv is in the same directory as app.py
df = load_data(csv_path)

if df is not None:
    patient_data_map = extract_patient_info(df)
    unique_patient_ids = sorted(list(patient_data_map.keys()))

    if not unique_patient_ids:
        st.warning("No patient information could be extracted from the notes.")
    else:
        selected_unique_id = st.selectbox(
            "Select Patient:",
            options=[""] + unique_patient_ids, # Add an empty option for initial state
            index=0
        )

        if selected_unique_id:
            with st.spinner(f"Generating summary for {selected_unique_id}..."):
                summary_result, original_note_content = summarize_by_unique_id(patient_data_map, selected_unique_id)
                
                if "Error" in summary_result:
                    st.warning(summary_result)
                else:
                    st.subheader("Original Note:")
                    st.text_area("Note Content", original_note_content, height=200)

                    st.subheader("Generated Summary:")
                    st.success(summary_result)
else:
    st.error("Application cannot run without the 'train.csv' file.")