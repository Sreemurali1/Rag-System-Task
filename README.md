#  RAG System with LLaMA-3, Qdrant, and FastAPI
RAG System using LLaMA-3, Qdrant, Groq API, and FastAPI
This project implements a scalable Retrieval-Augmented Generation (RAG) pipeline that combines Groq's LLaMA-3 large language model, Qdrant vector database, and FastAPI. It supports multi-PDF uploads, text chunking, vector storage with Cohere embeddings, and intelligent query answering using retrieved context. Ideal for document-based Q&A and knowledge retrieval systems.

This project is a full-stack Retrieval-Augmented Generation (RAG) system using:
- **LLaMA-3** via Groq API for high-speed inference
- **Qdrant** for vector similarity search
- **Cohere** embeddings for encoding document chunks
- **FastAPI** backend to handle file uploads and queries

##  Features
- Upload one or multiple PDFs
- Extract and chunk text
- Store chunks as vector embeddings in Qdrant
- Query the documents using semantic search + LLaMA-3 reasoning
- Simple and scalable architecture

## 🔧 Tech Stack
-  LLM: LLaMA-3 70B (Groq API)
-  Vector Store: Qdrant
-  Embeddings: Cohere
-  Backend: FastAPI
-  PDF Parsing: PyMuPDF

## ⚙️ How to Run

```bash
git clone https://github.com/Sreemurali1/Rag-System-task.git
cd your-repo-name
pip install -r requirements.txt
uvicorn main:app --reload

