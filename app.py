import streamlit as st
from llama_index.llms.gemini import Gemini
from llama_index.core import Settings
from load_drive_files import load_data_from_drive
from setup_ingestion_pipeline import create_or_load_pipeline
from setup_chromadb import create_or_get_vectordb
from setup_embedding_model import embed_model
from llama_index.core import VectorStoreIndex
import requests
from dotenv import load_dotenv
import os
import re

load_dotenv()
GOOGLEAI_API_KEY=os.getenv('GOOGLEAI_API_KEY')

API_URL_SIGNUP = "http://localhost:8000/auth/"
API_URL_LOGIN = "http://localhost:8000/auth/token"
API_URL_LOAD_DATA = "http://localhost:8000/auth/google-drive"

st.title("Welcom To Intelligent Document Finder App")

#folder_id = st.text_input("Enter Google Drive folder link:")


def new_index(vector_store, embed_model):
    index = VectorStoreIndex.from_vector_store(
        vector_store=vector_store,
        embed_model=embed_model,
    )
    return index

#set up the Geming LLM model    
Settings.llm = Gemini(model="models/gemini-pro")


#function to get JWT token which is returned by backend API enpoint for login
@st.cache_data()
def get_token(username, password):
    login_data = {"username": username, "password": password}
    login_response = requests.post(API_URL_LOGIN, data=login_data)

    if login_response.status_code == 200:
        st.success("Login successful")
        return login_response.json().get('access_token')
    else:
        st.error("Failed to login. Please check your credentials.")
        return None

#function to handle query response
def query_response(query):
    
    response = query_engine.query(query)
    if response.source_nodes:
        metadata = response.source_nodes[0].node.metadata
        filename = metadata.get("file name", "Unknown")
        author = metadata.get("author", "Unknown")
        creation = metadata.get("created at", "Unknown")
        modified = metadata.get("modified at", "Unknown")
        try:
            page_label = metadata["page_label"]
        except KeyError:
            page_label = None
        return str(response), f"File Name: {filename}", f"Author: {author}", f"Creation Date: {creation}", f"Modified Date: {modified}", f"Page Number: {page_label}"
    else:
        return str(response), "No metadata available", "", "", "", ""

#define the user interface for signup, login, and search
choice=st.selectbox('Login/Signup/Search',['Login','Sign up','Search'])

if choice == 'Sign up' :

    st.header("Sign up if you are not registered already!!")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Signup"):
        data = {"username": username, "password": password}
        #sending a request to API endpoint with required data
        response = requests.post(API_URL_SIGNUP, json=data)

        if response.status_code == 201:
            st.success("User created successfully")
        else:
            st.error("Failed to create user. Please try again.")

if choice == 'Login' :

    st.header("Login to use the app")
    login_username = st.text_input("Username")
    login_password = st.text_input("Password", type="password")

    if st.button("Login"):
        token = get_token(login_username, login_password)
        if token:
            # Store the token in session state
            st.session_state.token = token
            #st.write("Token:", st.session_state.token)


if choice == 'Search' :
    #interface for providing google drive folder link and querying
    st.header("Provide your Google drive folder Id!!")
    google_drive_folder_link = st.text_input("Google Drive Folder link")
    #check if the input field is not empty
    if google_drive_folder_link:
        try:
            #extract the folder ID from the Google Drive folder link using regular expression
            google_drive_folder_id = re.search(r"/folders/([^\s/]+)", google_drive_folder_link).group(1)
        except:
            st.error("please provide valid google drive folder link")
    if st.button("Load Data"):
        datauser={"token": st.session_state.token, "google_drive_folder_id": google_drive_folder_id}
        #sending request to API endpoints for users verification
        response = requests.post(API_URL_LOAD_DATA, json=datauser)
        #if user is verified sucessfully than process the documents from folder 
        if response.status_code == 200:
            message=response.json().get('message')
            st.write(message)
                        
            docs = load_data_from_drive(google_drive_folder_id)
    
            # Create or load the ingestion pipeline
            pipeline = create_or_load_pipeline()

            # Process the documents using the pipeline
            nodes = pipeline.run(documents=docs)
            print(f"Ingested {len(nodes)} Nodes")
            st.write(f"Data loaded from Google Drive folder: {google_drive_folder_id} and processed.")
        else:
            st.error("Failed to Authenticate please provide link of your google drive folder only!!")
    #index the documents
    index = new_index(create_or_get_vectordb(), embed_model())
    query_engine = index.as_query_engine()

    query = st.text_input("Enter your query:")
    if st.button("Query"):
        response, File_name, owner, date_creation, date_modified, page_no = query_response(query)
        st.subheader("Response:")
        st.write(response)
        st.subheader("Metadata:")
        st.write(File_name)
        st.write(owner)
        st.write(date_creation)
        st.write(date_modified)
        st.write(page_no)