# Module: pdf_parser
# This script is designed to parse PDF files and extract text from them.
# It uses the PyMuPDF library (also known as fitz) to handle PDF files.

# Import necessary libraries
import fitz  # PyMuPDF
from langchain.text_splitter import RecursiveCharacterTextSplitter


# Function to extract text from PDF bytes using PyMuPDF
def get_pdf_text(pdf: bytes) -> str:
    text = ""
    try:
        with fitz.open(stream=pdf, filetype="pdf") as doc:
            for page in doc:
                text += page.get_text()
    except Exception as e:
        print(f"Error while reading PDF: {e}")
    return text


# Function to split text into chunks
def get_text_chunks(text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=2500, chunk_overlap=350)
    chunks = text_splitter.split_text(text)
    return chunks
