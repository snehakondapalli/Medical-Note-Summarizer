# Streamlit App Creation Plan

### **Goal**
To develop a Streamlit web application that allows users to input a patient's name, find their medical note from a CSV file, and display a concise summary generated using the Groq API.

### **Architectural Overview**

The application will consist of a Streamlit frontend that interacts with the existing data preparation and summarization logic. The `train.csv` file will be loaded once and cached for efficiency. The Groq API key will be securely managed using Streamlit secrets.

```mermaid
graph TD
    A[User Input Patient Name] --> B{Streamlit App};
    B --> C[Load train.csv (cached)];
    C --> D{Find Patient Note};
    D --> E[Clean Note];
    E --> F[Call Groq API for Summary];
    F --> G[Display Original Note & Summary];
    G --> B;
```

### **Detailed Plan Steps**

1.  **Create `requirements.txt`**:
    *   This file will list all the Python packages required for the application to run.
    *   **Action**: Create a file named `requirements.txt` in the root directory of your project with the following content:
        ```
        streamlit
        pandas
        requests
        groq
        ```

2.  **Create `app.py` (Streamlit Application File)**:
    *   This will be the main Streamlit application script. It will incorporate the logic from `data_preparation.py` and set up the user interface.
    *   **Action**: Create a file named `app.py` in the root directory of your project. The content will include:
        *   Imports for `streamlit`, `pandas`, `re`, `requests`, and `Groq`.
        *   The `clean_note`, `system_prompt`, `user_prompt_template`, `summarize_note1`, `find_patient_row`, and `summarize_by_patient` functions/variables from `data_preparation.py`.
        *   Modification of the `GROQ_API_KEY` to securely retrieve it from Streamlit secrets.
        *   Implementation of a cached function to load `train.csv` efficiently.
        *   The Streamlit UI elements for input and output.

3.  **Configure Streamlit Secrets**:
    *   To securely manage your Groq API key, Streamlit provides a secrets management system.
    *   **Action**:
        *   Create a new directory named `.streamlit` in the root of your project (if it doesn't already exist).
        *   Inside the `.streamlit` directory, create a file named `secrets.toml`.
        *   Add your Groq API key to this file as follows:
            ```toml
            GROQ_API_KEY="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" # Replace with your actual Groq API key
            ```
            **Note**: Remember to replace the placeholder value with your actual Groq API key.

4.  **Instructions for Running the App**:
    *   Once the files are set up, you will need to install the dependencies and run the Streamlit application.
    *   **Action**: I will provide the necessary terminal commands to install the dependencies and launch the Streamlit app.