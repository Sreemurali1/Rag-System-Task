# Module: vectore_store.py
# Vector Store for Document Processing
# This module provides functionality to create and manage a vector store
# for document processing, including loading environment variables and parsing PDFs.

# Import necessary libraries
import os
import logging
from dotenv import load_dotenv
from langchain_cohere import CohereEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from langchain_core.documents import Document  # Import Document class for handling text chunks

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Validate required environment variables
required_keys = ["COHERE_API_KEY", "QDRANT_URL", "QDRANT_API_KEY"]
for key in required_keys:
    if not os.getenv(key):
        logger.error(f"Missing required environment variable: {key}")
        raise ValueError(f"{key} is not set.")

# Read API credentials
cohere_api_key = os.getenv("COHERE_API_KEY")
qdrant_url = os.getenv("QDRANT_URL")
qdrant_api_key = os.getenv("QDRANT_API_KEY")

# Initialize embedding model
cohere_embeddings = CohereEmbeddings(
    cohere_api_key=cohere_api_key,
    model="embed-english-light-v3.0"
)

# Initialize Qdrant client
client = QdrantClient(
    url=qdrant_url,
    api_key=qdrant_api_key
)

# Function to create a vector store in Qdrant
def vector_store(text_chunks, collection_name):
    """
    Stores text chunks in Qdrant vector store with Cohere embeddings.
    """
    try:
        # Try to create collection
        try:
            client.create_collection(
                collection_name=collection_name,
                vectors_config={"size": 384, "distance": "Cosine"}
            )
            logger.info(f"Created collection: {collection_name}")
        except Exception as e:
            if "already exists" in str(e):
                logger.warning(f"Collection already exists: {collection_name}. Deleting and recreating.")
                client.delete_collection(collection_name)
                client.create_collection(
                    collection_name=collection_name,
                    vectors_config={"size": 384, "distance": "Cosine"}
                )
                logger.info(f"Recreated collection: {collection_name}")
            else:
                raise

        # Wrap text chunks in LangChain Document objects
        documents = [Document(page_content=chunk, metadata={"source": collection_name}) for chunk in text_chunks]

        # Create vector store and add documents
        vector_store = QdrantVectorStore(
            client=client,
            collection_name=collection_name,
            embedding=cohere_embeddings
        )
        vector_store.add_documents(documents)

        logger.info(f"Successfully added {len(documents)} documents to collection: {collection_name}")
        return vector_store

    except Exception as e:
        logger.error(f"Error creating vector store: {e}")
        raise