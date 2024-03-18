import streamlit as st
from llama_index.llms.gemini import Gemini
from llama_index.core import Settings
from setup_chromadb import create_or_get_vectordb
from setup_embedding_model import embed_model
import requests
from dotenv import load_dotenv
import os
from extract_id_from_onedrive import extract_onedrive_folder_id
from extract_id_from_googledrive import extract_googledrive_folder_id
from data_node_ingestion import ingestion
from index_creater import new_index

google_drive_folder_id=None
one_drive_folder_id=None

load_dotenv()
GOOGLEAI_API_KEY=os.getenv('GOOGLEAI_API_KEY')

API_URL_SIGNUP = "http://localhost:8000/auth/"
API_URL_LOGIN = "http://localhost:8000/auth/token"
API_URL_GDRIVE_VERIFY = "http://localhost:8000/auth/google-drive"
API_URL_LOAD_ONEDRIVE ="http://localhost:8000/auth/one-drive"

st.title("Welcom To Intelligent Document Finder App")

#set up the Gemini LLM model    
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
        #checking whether google drive folder id is available or one drive and extracting metadata accordingly.
        if google_drive_folder_id:
            filename = metadata.get("file name", "Unknown")
            author = metadata.get("author", "Unknown")
            creation = metadata.get("created at", "Unknown")
            modified = metadata.get("modified at", "Unknown")
        elif one_drive_folder_id:
            filename = metadata.get("file_name", "Unknown")
            author = metadata.get("created_by_user", "Unknown")
            creation = metadata.get("created_dateTime", "Unknown")
            modified = metadata.get("last_modified_datetime", "Unknown")
        try:
            page_label = metadata["page_label"]
        except KeyError:
            page_label = None
        #returning response with metadata
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

if choice == 'Search' :
    #interface for providing google folder link and querying
    st.header("Provide your Google Drive or One Drive folder URL")
    folder_link = st.text_input("Folder URL")
    #checking if folder link is provided in input field or not.
    if folder_link:
        #checking if provided link is of google drive or one drive and extracting folder id accordingly.
        if folder_link.startswith("https://drive.google.com") or folder_link.startswith("http://drive.google.com"):
            #calling a function to extract folder id from URL.
            google_drive_folder_id = extract_googledrive_folder_id(folder_link)
        elif folder_link.startswith("https://onedrive.live.com") or folder_link.startswith("http://onedrive.live.com"):
            #calling a function to extract folder id from URL.
            one_drive_folder_id = extract_onedrive_folder_id(folder_link)
    if st.button("Load Data"):
        if google_drive_folder_id:
            datauser={"token": st.session_state.token, "google_drive_folder_id": google_drive_folder_id}
            #sending request to API endpoints for users verification
            response = requests.post(API_URL_GDRIVE_VERIFY, json=datauser)
            #if user is verified sucessfully than process the documents from folder 
            if response.status_code == 200:
                message=response.json().get('message')
                st.write(message)
                #calling a function which ingest nodes in pipeline.
                ingestion(one_drive_folder_id, google_drive_folder_id)
                st.write(f"Data loaded from Google Drive folder: {google_drive_folder_id} and processed.")
            else:
                st.error("Failed to Authenticate please provide link of your google drive folder only!!")
        elif one_drive_folder_id:
            #calling a function which ingest nodes in pipeline.
            ingestion(one_drive_folder_id, google_drive_folder_id)
            st.write(f"Data loaded from One Drive folder: {one_drive_folder_id} and processed.")

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