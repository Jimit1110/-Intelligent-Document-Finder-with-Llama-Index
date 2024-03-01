"""this scripts is to set perticular opensource model for embedding perpose"""

from llama_index.embeddings.huggingface import HuggingFaceEmbedding

def embed_model():
    embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5", cache_folder="cache_model")
    return embed_model