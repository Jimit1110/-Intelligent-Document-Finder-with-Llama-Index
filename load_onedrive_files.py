from llama_index.readers.microsoft_onedrive import OneDriveReader
from dotenv import load_dotenv
import os

load_dotenv()
CLIENT_ID = os.getenv('CLIENT_ID')

def load_data_from_onedrive(folder_id: str):
    loader = OneDriveReader(client_id=CLIENT_ID)
    #load documents from the specified OneDrive folder (recursive=False meaning don't interate through subfolders within folder)
    documents = loader.load_data(folder_id=folder_id, recursive=True)
    for doc in documents:
        doc.id_ = doc.metadata["file_name"]
    return documents