# Module: app.py
# Streamlit app for legal document Q&A assistant

import streamlit as st
import requests

st.set_page_config(page_title="Legal Q&A Assistant", layout="centered")
st.title("Legal Document Assistant")

# Initialize chat history with greeting on first load
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append((
        "Assistant", 
        "Hello! I am your Legal Document Assistant. Please upload one or more PDF files using the sidebar to begin."
    ))


# Sample PDF sources
SAMPLE_PDFS = {
    "Case 1 Sample": "Files/Case 1.pdf",
    "Case 2 Sample": "Files/Case 2.pdf",
    "Case 3 Sample": "Files/Case 3.pdf"
}


# Sidebar for file upload
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
            st.warning("Please upload at least one PDF file or select a sample.")
        else:
            files = []

            if uploaded_files:
                files.extend([("files", (f.name, f.getvalue(), f.type)) for f in uploaded_files])

            if sample_choice != "None":
                sample_path = SAMPLE_PDFS[sample_choice]
                try:
                    with open(sample_path, "rb") as f:
                        sample_bytes = f.read()
                        files.append(("files", (f"{sample_choice}.pdf", sample_bytes, "application/pdf")))
                except FileNotFoundError:
                    st.error(f"File not found: {sample_path}")


            response = requests.post("http://localhost:8000/upload/", files=files)
            if response.status_code == 200:
                st.success("Documents uploaded and processed successfully.")
                st.markdown("#### Uploaded Files:")
                if uploaded_files:
                    for f in uploaded_files:
                        st.markdown(f"- 📄 **{f.name}**")
                if sample_choice != "None":
                    st.markdown(f"- 📄 **{sample_choice}.pdf**")
                st.session_state.messages.append((
                    "Assistant",
                    "Your documents have been uploaded and processed. You may now ask your legal question below."
                ))
            else:
                st.error("Upload failed. Please try again.")



# Input for user question
query = st.chat_input("Enter your legal question")

if query:
    st.session_state.messages.append(("User", query))

    response = requests.post("http://localhost:8000/ask/", data={"query": query})

    if response.status_code == 200:
        answer = response.json()["answer"]
        st.session_state.messages.append(("Assistant", answer))
    else:
        st.error("An error occurred while retrieving the response.")
        

# Display chat history with dynamic-width transparent-style boxes
st.markdown("### Chat")

for role, msg in st.session_state.messages:
    bg_color = "rgba(240, 240, 240, 0.5)" if role == "User" else "rgba(220, 240, 255, 0.5)"
    border_color = "#ccc" if role == "User" else "#99ccee"
    align = "flex-end" if role == "User" else "flex-start"

    st.markdown(
        f"""
        <div style='
            display: flex;
            justify-content: {align};
        '>
            <div style='
                display: inline-block;
                max-width: 80%;
                padding: 12px 16px;
                margin-bottom: 12px;
                border-radius: 10px;
                background-color: {bg_color};
                border: 1px solid {border_color};
                word-wrap: break-word;
                font-size: 16px;
            '>
                <strong>{role}:</strong><br>{msg}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
