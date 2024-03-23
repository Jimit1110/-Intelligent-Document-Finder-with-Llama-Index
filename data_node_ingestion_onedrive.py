from load_onedrive_files import load_data_from_onedrive
from setup_ingestion_pipeline import create_or_load_pipeline

def onedrive_data_ingestion(one_drive_folder_id):    
    docs = load_data_from_onedrive(one_drive_folder_id)

    # Create or load the ingestion pipeline
    pipeline = create_or_load_pipeline()

    # Process the documents using the pipeline
    nodes = pipeline.run(documents=docs)
    print(f"Ingested {len(nodes)} Nodes")