# Module: app.py
# Streamlit app for legal document Q&A assistant

import streamlit as st
import requests
import time
import os

# Set up
st.set_page_config(page_title="Legal Q&A Assistant", layout="centered")
st.title("Legal Document Assistant")

# Environment variable for API
API_URL = os.getenv("API_URL", "http://localhost:8000")

# Helper for retries
def post_with_retry(url, **kwargs):
    for i in range(10):
        try:
            response = requests.post(url, **kwargs)
            return response
        except requests.exceptions.ConnectionError:
            time.sleep(2)
    return None

# Initialize chat
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append((
        "Assistant",
        "Hello! I am your Legal Document Assistant. Please upload one or more PDF files using the sidebar to begin."
    ))

# Sample files
SAMPLE_PDFS = {
    "Case 1 Sample": "Files/Case 1.pdf",
    "Case 2 Sample": "Files/Case 2.pdf",
    "Case 3 Sample": "Files/Case 3.pdf"
}

# Sidebar
with st.sidebar:
    st.subheader("Upload Legal Documents")

    uploaded_files = st.file_uploader(
        "Select one or more PDF files",
        type=["pdf"],
        accept_multiple_files=True,
        label_visibility="collapsed"
    )

    sample_choice = st.selectbox("Or select a sample PDF", ["None"] + list(SAMPLE_PDFS.keys()))

    if st.button("Submit Documents"):
        if not uploaded_files and sample_choice == "None":
            st.warning("Please upload at least one PDF or choose a sample.")
        else:
            files = []

            # Add uploaded files
            if uploaded_files:
                for f in uploaded_files:
                    files.append(("files", (f.name, f.getvalue(), f.type)))

            # Add sample file
            if sample_choice != "None":
                sample_path = SAMPLE_PDFS[sample_choice]
                try:
                    with open(sample_path, "rb") as f:
                        sample_bytes = f.read()
                        files.append(("files", (f"{sample_choice}.pdf", sample_bytes, "application/pdf")))
                except FileNotFoundError:
                    st.error(f"Sample file not found: {sample_path}")

            # Send to FastAPI
            response = post_with_retry(f"{API_URL}/upload/", files=files)

            if response and response.status_code == 200:
                st.success("Documents uploaded and processed successfully.")
                st.markdown("#### Uploaded Files:")
                if uploaded_files:
                    for f in uploaded_files:
                        st.markdown(f"- 📄 **{f.name}**")
                if sample_choice != "None":
                    st.markdown(f"- 📄 **{sample_choice}.pdf**")
                st.session_state.messages.append((
                    "Assistant",
                    "Your documents are processed. You may now ask your legal question below."
                ))
            else:
                st.error("Upload failed. Please try again.")

# Chat input
query = st.chat_input("Enter your legal question")

if query:
    st.session_state.messages.append(("User", query))
    response = post_with_retry(f"{API_URL}/ask/", data={"query": query})
    if response and response.status_code == 200:
        answer = response.json().get("answer", "No answer returned.")
        st.session_state.messages.append(("Assistant", answer))
    else:
        st.error("An error occurred while retrieving the response.")

# Display chat history
st.markdown("### Chat")

for role, msg in st.session_state.messages:
    bg_color = "rgba(240, 240, 240, 0.5)" if role == "User" else "rgba(220, 240, 255, 0.5)"
    border_color = "#ccc" if role == "User" else "#66afe9"
    st.markdown(f"""
        <div style='background-color: {bg_color}; border: 1px solid {border_color}; 
                    border-radius: 10px; padding: 10px; margin-bottom: 10px'>
            <strong>{role}:</strong><br>{msg}
        </div>
    """, unsafe_allow_html=True)

