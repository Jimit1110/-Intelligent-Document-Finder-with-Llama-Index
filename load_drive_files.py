"""This script uses the GoogleDriveReader from llama_index to load documents from a Google Drive folder."""

from llama_index.readers.google import GoogleDriveReader

def load_data_from_drive(folder_id: str):
    
    loader = GoogleDriveReader()
    docs = loader.load_data(folder_id=folder_id)
    for doc in docs:
        doc.id_ = doc.metadata["file_name"]
    return docs
