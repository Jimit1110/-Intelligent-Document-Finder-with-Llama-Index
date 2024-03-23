import streamlit as st
from llama_index.llms.gemini import Gemini
from llama_index.core import Settings
from setup_chromadb import create_or_get_vectordb
from setup_embedding_model import embed_model
import requests
from dotenv import load_dotenv
import os
from extract_id_from_onedrive import extract_onedrive_folder_id
from data_node_ingestion_onedrive import onedrive_data_ingestion
from index_creater import new_index
from data_node_ingestion_onedrive import onedrive_data_ingestion
from get_gdrive_file_ids import list_files
from data_node_ingestion_gdrive import gdrive_data_ingestion

one_drive_folder_id=None
#checking if token is not in session_state then adding it with empty string. 
if "token" not in st.session_state:
    st.session_state["token"] = ""

load_dotenv()
GOOGLEAI_API_KEY=os.getenv('GOOGLEAI_API_KEY')

API_URL_SIGNUP = "http://localhost:8000/auth/"
API_URL_LOGIN = "http://localhost:8000/auth/token"

st.title("Welcom To Intelligent Document Finder App")

#set up the Gemini LLM model    
Settings.llm = Gemini(model="models/gemini-pro")

#function to get JWT token which is returned by backend API enpoint for login
@st.cache_data()
def get_token(username, password):
    login_data = {"username": username, "password": password}
    #sending request to API endpoin for login and generating JWT token.
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
        if one_drive_folder_id is None:
            metadata = response.source_nodes[0].node.metadata    
            filename = metadata.get("file name", "Unknown")
            author = metadata.get("author", "Unknown")
            creation = metadata.get("created at", "Unknown")
            modified = metadata.get("modified at", "Unknown")
        else:
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
    folder_link = "https://onedrive.live.com/?id=root"
    #extracting id from above URL.
    one_drive_folder_id = extract_onedrive_folder_id(folder_link)
    if st.button("Connect One Drive"):
        #checking whether user is logged in or not.
        if st.session_state.token:
            if one_drive_folder_id:
                #calling a function which ingest nodes in pipeline.
                onedrive_data_ingestion(one_drive_folder_id)
                st.success("Google Drive is connect successfully and data loaded !!!")
            else:
                st.error("Please login first")
    if st.button('Connect Google Drive'):
        #checking whether user is logged in or not.
        if st.session_state.token:
            file_ids, folder_ids = list_files()
            gdrive_data_ingestion(file_ids)
            st.success("Google Drive is connect successfully and data loaded !!!")
        else:
            st.error("Please login first")
    
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