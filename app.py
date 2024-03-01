"""this scripts is launching interface and generating output with it's metadata"""

import gradio as gr
from llama_index.llms.gemini import Gemini
from llama_index.core import Settings
from processing_and_indexing import index  

# Set the LLM model for the query engine
Settings.llm = Gemini(model="models/gemini-pro")
query_engine = index.as_query_engine()

# Define a function to process a query and return the response with metadata
def query_response(query):
    # Query the index for a response
    response = query_engine.query(query)
    if response.source_nodes:
        # Extract metadata from the response
        metadata = response.source_nodes[0].node.metadata
        filename = metadata.get("file_name", "Unknown")
        author = metadata.get("author", "Unknown")
        creation = metadata.get("created at", "Unknown")
        modified = metadata.get("modified at", "Unknown")
        # for metadat field:"page_label" checker is required, 
        # because if document has only one page than in it's metadata,
        # page_label field will not be there so it throughs Keyerror.
        try:
            page_label = metadata["page_label"]
        except KeyError:
            page_label = None
        metadata_str = f"File Name: {filename}\nAuthor: {author}\ncreation date: {creation}\nmodified date: {modified}"
        if page_label:
            metadata_str += f"\nPage Label: {page_label}"
    else:
        metadata_str = "No metadata available"

    return str(response), metadata_str

# Gradio interface for querying and displaying responses with metadata
iface = gr.Interface(
    fn=query_response,
    inputs="text",
    outputs=["text", "text"],
    title="Document Query System",
    description="Enter a query to retrieve information from documents.",
    examples=[["What is the project title?"]],
)
iface.launch()
