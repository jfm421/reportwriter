import streamlit as st
import openai
import requests
import os
from docx import Document


# Use Streamlit's secrets management
API_KEY = st.secrets["openai"]["api_key"]
openai.api_key = API_KEY

def check_api_status():
    url = "https://api.openai.com/v1/engines"
    headers = {"Authorization": f"Bearer {API_KEY}"}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Will raise an HTTPError for bad responses (4xx and 5xx)
        return True, "The API is online and accessible."
    except requests.RequestException as e:
        return False, f"Failed to access the API: {str(e)}"
        
def parse_toc_input(toc_input):
    sections = toc_input.strip().split('\n')
    toc_dict = {}
    for section in sections:
        parts = section.split(':')
        if len(parts) != 2:
            st.error(f"Invalid section format: {section}. Please follow the format 'Title:WordLimit'")
            return None
        title, word_limit = parts
        try:
            toc_dict[title.strip()] = int(word_limit.strip())
        except ValueError:
            st.error(f"Invalid word limit in section '{title}': {word_limit}. Word limit should be an integer.")
            return None
    return toc_dict

def generate_report(text_data, toc, model, custom_instructions):
    model_name = "gpt-3.5-turbo" if model == "GPT-3.5 Turbo" else "gpt-4"  
    
    # Constructing the prompt
    prompt = f"{custom_instructions}\n\nCreate a report from the following data:\n{text_data}\n"
    for title, limit in toc.items():
        prompt += f"\nTitle: {title}\nWord Limit: {limit}\n"
    
    st.text(f"Prompt: {prompt}")  # Debugging line to display the prompt
    
    try:
        response = openai.ChatCompletion.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000  # Set an arbitrary limit
        )
        report = response['choices'][0]['message']['content']  
        return report
    except Exception as e:
        st.error(f"Failed to generate report: {str(e)}")
        return None

def export_report(report, file_format):
    if file_format == 'Word':
        doc = Document()
        doc.add_paragraph(report)
        file_path = 'report.docx'
        doc.save(file_path)
    else:
        file_path = 'report.txt'
        with open(file_path, 'w') as file:
            file.write(report)
    
    return file_path

def get_file_content(file_path):
    with open(file_path, "rb") as file:
        return file.read()


st.title("Report Writer")

# Call the function to check API status
status, message = check_api_status()
if not status:
    st.markdown(
        f"""
        <style>
        .red-circle {{
            width: 20px;
            height: 20px;
            border-radius: 50%;
            background-color: red;
            display: inline-block;
        }}
        </style>
        <div>
            <span class="red-circle"></span>
            {message}
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        f"""
        <style>
        .green-circle {{
            width: 20px;
            height: 20px;
            border-radius: 50%;
            background-color: green;
            display: inline-block;
        }}
        </style>
        <div>
            <span class="green-circle"></span>
            {message}
        </div>
        """,
        unsafe_allow_html=True,
    )

uploaded_file = st.file_uploader("Choose a text file", type="txt")

st.subheader("Table of Contents")
toc_input = st.text_area("Enter your table of contents with word limits (e.g., Introduction:300, Methods:500)")

st.subheader("Custom Instructions")
custom_instructions = st.text_area("Enter any custom instructions for the report generation:")

model_choice = st.selectbox("Select Model", ["GPT-3.5 Turbo", "GPT-4"])


report = None  # Define report variable at the top of your script

# Initialize session_state variables if they don't exist
if 'report' not in st.session_state:
    st.session_state['report'] = ''

if st.button("Generate Report"):
    if uploaded_file is not None and toc_input:
        text_data = uploaded_file.read().decode("utf-8")
        toc = parse_toc_input(toc_input)
        st.session_state['report'] = generate_report(text_data, toc, model_choice, custom_instructions)
        st.text(st.session_state['report'])
    else:
        st.warning("Please provide all necessary inputs.")

export_format = st.selectbox("Export Format", ["Word", "Text"])
if st.button("Export Report") and st.session_state['report']:
    file_path = export_report(st.session_state['report'], export_format)
    
    with open(file_path, "rb") as file:
        file_bytes = file.read()
    
    st.download_button(
        label=f"Download {file_path}",
        data=file_bytes,
        file_name=file_path,
        mime="application/octet-stream"
    )
