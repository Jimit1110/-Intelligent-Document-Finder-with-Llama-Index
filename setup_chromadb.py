"""This script uses chromadb to create or get a vector database (vectordb) for storing vectors."""

import chromadb
from llama_index.vector_stores.chroma import ChromaVectorStore

def create_or_get_vectordb():
    # It creates a persistent client with the specified path to store the database.
    chroma_client = chromadb.PersistentClient(path="chroma_db")
    # If the collection "quickstart" does not exist, it creates it
    chroma_collection = chroma_client.get_or_create_collection("quickstart")
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)

    return vector_store