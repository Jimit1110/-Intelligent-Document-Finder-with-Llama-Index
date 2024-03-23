"""This script uses the GoogleDriveReader from llama_index to load documents from a Google Drive folder."""

from llama_index.readers.google import GoogleDriveReader

def load_data_from_gdrive(file_ids):
    
    loader = GoogleDriveReader()
    docs = loader.load_data(file_ids=file_ids)
    for doc in docs:
        doc.id_ = doc.metadata["file_name"]
    return docs
