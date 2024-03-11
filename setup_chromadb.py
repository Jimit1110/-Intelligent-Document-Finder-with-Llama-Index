"""This script uses chromadb to create or get a vector database (vectordb) for storing vectors."""

import chromadb
from llama_index.vector_stores.chroma import ChromaVectorStore
import atexit

def create_or_get_vectordb(caller=None):
    # It creates a persistent client with the specified path to store the database.
    chroma_client = chromadb.PersistentClient(path="chroma_db")
    # If the collection "quickstart" does not exist, it creates it

    if caller == "call_from_pipeline":
        try:
            chroma_client.delete_collection(name="quickstart")
        except:
            pass 
    
    chroma_collection = chroma_client.get_or_create_collection("quickstart")
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)

    atexit.register(lambda: chroma_client.reset())
    return vector_store