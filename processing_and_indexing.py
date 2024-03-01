"""this scripts is for loading a documents, creating pipeline and for indexing the documents"""

from load_drive_files import load_data 
from setup_ingestion_pipeline import create_or_load_pipeline
from setup_chromadb import create_or_get_vectordb
from setup_embedding_model import embed_model

from llama_index.core import VectorStoreIndex

# Initialize a set to keep track of indexed files
indexed_files = set()

def new_index(vector_store, embed_model):
    index = VectorStoreIndex.from_vector_store(
        vector_store=vector_store,
        embed_model=embed_model,
    )
    return index

# Load documents from Google Drive
docs = load_data(folder_id="1KNKbip-FRVO4KL815gulGk0nQL4WMkFl")

# Create or load the ingestion pipeline
pipeline = create_or_load_pipeline()

# Process the documents using the pipeline
nodes = pipeline.run(documents=docs)
print(f"Ingested {len(nodes)} Nodes")

# Index the documents, skipping already indexed ones
index = new_index(create_or_get_vectordb(), embed_model())
for doc in docs:
    if doc.metadata["file_name"] not in indexed_files:
        indexed_files.add(doc.metadata["file_name"])
    else:
        print(f"Documents is already indexed. Skipping...")

print("Indexing completed.")

# Save the updated set of indexed file names
with open("indexed_files.txt", "w") as f:
    f.write("\n".join(indexed_files))