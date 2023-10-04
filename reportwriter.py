import streamlit as st
import openai

# Use Streamlit's secrets management
API_KEY = st.secrets["openai"]["api_key"]
openai.api_key = API_KEY

def parse_toc_input(toc_input):
    sections = toc_input.split(' ')
    toc_dict = {}
    for section in sections:
        parts = section.split(':')
        if len(parts) != 2:
            st.error(f"Invalid section format: {section}. Please follow the format 'Title:WordLimit'")
            return None  # or you might want to raise an exception
        title, word_limit = parts
        try:
            toc_dict[title.strip()] = int(word_limit.strip())
        except ValueError:
            st.error(f"Invalid word limit: {word_limit}. Word limit should be an integer.")
            return None  # or you might want to raise an exception
    return toc_dict

def generate_report(text_data, toc, model):
    openai.api_key = 'your-api-key'  # Handle this securely
    
    model_name = "gpt-3.5-turbo" if model == "GPT-3.5 Turbo" else "gpt-4" 
    
    # Constructing the prompt
    prompt = f"Create a report from the following data:\n{text_data}\n"
    for title, limit in toc.items():
        prompt += f"\nTitle: {title}\nWord Limit: {limit}\n"
    
    try:
        response = openai.Completion.create(
            engine=model_name,
            prompt=prompt,
            max_tokens=2000  # Set an arbitrary limit
        )
        report = response['choices'][0]['text'].strip()
        return report
    except Exception as e:
        return str(e)

st.title("Report Writer")

uploaded_file = st.file_uploader("Choose a text file", type="txt")

st.subheader("Table of Contents")
toc_input = st.text_area("Enter your table of contents with word limits (e.g., Introduction:300, Methods:500)")

model_choice = st.selectbox("Select Model", ["GPT-3.5 Turbo", "GPT-4"])

if st.button("Generate Report"):
    if uploaded_file is not None and toc_input:
        text_data = uploaded_file.read().decode("utf-8")
        toc = parse_toc_input(toc_input)
        report = generate_report(text_data, toc, model_choice)
        st.text(report)
    else:
        st.warning("Please provide all necessary inputs.")
