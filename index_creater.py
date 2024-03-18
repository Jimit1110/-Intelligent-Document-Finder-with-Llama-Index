from llama_index.core import VectorStoreIndex

def new_index(vector_store, embed_model):
    #create a new VectorStoreIndex using the provided vector store and embedding model
    index = VectorStoreIndex.from_vector_store(
        vector_store=vector_store,
        embed_model=embed_model,
    )
    return index