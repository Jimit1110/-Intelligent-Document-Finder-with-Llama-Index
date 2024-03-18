from load_drive_files import load_data_from_drive
from load_onedrive_files import load_data_from_onedrive
from setup_ingestion_pipeline import create_or_load_pipeline

def ingestion(one_drive_folder_id, google_drive_folder_id):
    #load data based on the provided folder ID(Google drive OR Onedrive)
    if google_drive_folder_id==None:
        docs = load_data_from_onedrive(one_drive_folder_id)
    elif one_drive_folder_id==None:
        docs = load_data_from_drive(google_drive_folder_id)

    # Create or load the ingestion pipeline
    pipeline = create_or_load_pipeline()

    # Process the documents using the pipeline
    nodes = pipeline.run(documents=docs)
    print(f"Ingested {len(nodes)} Nodes")