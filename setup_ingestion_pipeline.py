"""this script is to define method for creation of ingestion pipeline which helps to process documents further """

from setup_chromadb import create_or_get_vectordb
from setup_embedding_model import embed_model
from llama_index.core.storage.docstore import SimpleDocumentStore
from llama_index.core.ingestion import (
    IngestionPipeline
)
from llama_index.core.node_parser import SentenceSplitter

def create_or_load_pipeline():
    pipeline = IngestionPipeline(
        transformations=[
            SentenceSplitter(),
            embed_model(),
        ],
        vector_store=create_or_get_vectordb(caller="call_from_pipeline"),
        docstore=SimpleDocumentStore()
    )
    pipeline.persist("pipeline_store")
    pipeline.load("pipeline_store")

    return pipeline