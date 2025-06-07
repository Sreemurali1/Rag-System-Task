# Module: main.py
# Description: FastAPI application to upload PDFs, extract text, store in vector DB, and answer questions using Groq.

# Import necessary libraries
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import os
from groq import Groq
from vectore_store import vector_store 
from pdf_parser import get_pdf_text, get_text_chunks
from langchain_qdrant import QdrantVectorStore
from langchain_cohere import CohereEmbeddings
from qdrant_client import QdrantClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastAPI
app = FastAPI()

# Constants
collection_name = "legal_documents"
cohere_api_key = os.getenv("COHERE_API_KEY")
qdrant_url = os.getenv("QDRANT_URL")
qdrant_api_key = os.getenv("QDRANT_API_KEY")
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Initialize embeddings and Qdrant client for use in both upload and ask endpoints
cohere_embeddings = CohereEmbeddings(
    cohere_api_key=cohere_api_key,
    model="embed-english-light-v3.0"
)

qdrant_client = QdrantClient(
    url=qdrant_url,
    api_key=qdrant_api_key
)

# Endpoint to upload PDFs and store in vector DB
@app.post("/upload/")
async def upload_pdfs(files: List[UploadFile] = File(...)):
    all_chunks = []

    for file in files:
        pdf_bytes = await file.read()
        text = get_pdf_text(pdf_bytes)
        chunks = get_text_chunks(text)
        all_chunks.extend(chunks)

    # Store in vector DB
    vector_store(all_chunks, collection_name)
    return {"status": "PDFs processed and stored in vector DB", "chunks": len(all_chunks)}

# Endpoint for asking questions
@app.post("/ask/")
async def ask_question(query: str = Form(...)):
    # Load existing vector store
    vs = QdrantVectorStore(
        client=qdrant_client,
        collection_name=collection_name,
        embedding=cohere_embeddings
    )

    # Retrieve top 5 matching chunks
    docs_and_scores = vs.similarity_search_with_score(query, k=5)
    docs = [doc for doc, _ in docs_and_scores]
    context = "\n".join([doc.page_content for doc in docs])

    messages = [
    {
        "role": "system",
        "content": (
            "Start with greeting the user.\n"
            "You are an expert legal assistant specialized in extracting precise information from court judgments and legal documents.\n"
            "You must only use the content provided in the context below to answer the question.\n"
            "If the context contains the phrases 'Based on the provided context' or 'According to the provided context', IGNORE those lines completely when generating your answer.\n"
            "Additionally, DO NOT repeat or include the phrases 'Based on the context', 'According to the context', or any similar wording in your response.\n"
            "Your goal is to extract person names, roles (e.g., Petitioner, Respondent), and factual information with precision.\n"
            "If the answer is not clearly mentioned in the text, respond with: 'The requested information is not available in the provided documents.'\n"
            "Do not infer, speculate, or rely on prior knowledge. Stick strictly to the provided text.\n"
            "Ensure your answer is factual, concise, and free from unnecessary introductory phrases."
        )
    },
    {
        "role": "user",
        "content": f"Context:\n{context}\n\nQuestion: {query}\n\nAnswer:"
    }
]

    # Generate Response using Groq
    completion = groq_client.chat.completions.create(
        model="llama3-70b-8192",
        messages=messages
    )

    return {"answer": completion.choices[0].message.content}


# Run the FastAPI app with Uvicorn
if __name__ == "__main__":   
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

