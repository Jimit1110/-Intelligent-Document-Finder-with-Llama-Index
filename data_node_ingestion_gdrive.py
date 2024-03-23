from setup_ingestion_pipeline import create_or_load_pipeline
from load_gdrive_files import load_data_from_gdrive

def gdrive_data_ingestion(file_ids):
    
    documents = load_data_from_gdrive(file_ids)

    pipeline = create_or_load_pipeline()

    # Process the documents using the pipeline
    nodes = pipeline.run(documents=documents)
    print(f"Ingested {len(nodes)} Nodes")