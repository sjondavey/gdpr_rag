import logging
import os
from openai import OpenAI
import platform
import bcrypt
from dotenv import load_dotenv

import streamlit as st

from azure.storage.blob import BlobServiceClient, ContentSettings

from regulations_rag.rerank import RerankAlgos
from regulations_rag.corpus_chat import ChatParameters
from regulations_rag.embeddings import  EmbeddingParameters

from gdpr_rag.corpus_index import GDPRCorpusIndex
from regulations_rag.corpus_chat import CorpusChat

DEV_LEVEL = 15
ANALYSIS_LEVEL = 25
logging.addLevelName(DEV_LEVEL, 'DEV')       
logging.addLevelName(ANALYSIS_LEVEL, 'ANALYSIS')       

logger = logging.getLogger(__name__)
logger.setLevel(ANALYSIS_LEVEL)


# The container will be the same for all files in the session so only connect to it once.
@st.cache_resource
def _get_blog_container():
    if st.session_state['use_environmental_variables']:
        connection_string = f"DefaultEndpointsProtocol=https;AccountName=gdprragstorageaccount;AccountKey={st.session_state['blob_store_key']};EndpointSuffix=core.windows.net"
        # Create the BlobServiceClient object using the connection string
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    else:
        tmp_credential = DefaultAzureCredential()
        blob_service_client = BlobServiceClient(st.session_state['blob_account_url'], credential=tmp_credential)

    # Get the container client
    container_client = blob_service_client.get_container_client(st.session_state['blob_container_name'])

    # Check if the container exists, and create it if it doesn't
    if not container_client.exists():
        container_client.create_container()

    return container_client

@st.cache_resource
def _get_blob_for_global_logging(filename):
    container_client = _get_blog_container()
    blob_client = container_client.get_blob_client(filename)
    
    blob_exists = blob_client.exists()
    if not blob_exists:
        with open(st.session_state['global_logging_file_name'], "rb") as temp_file:
            container_client.upload_blob(name=filename, data=temp_file, content_settings=ContentSettings(content_type='text/plain'))
    return blob_client


# summary data for analysis is sent to individual files per session
# https://stackoverflow.com/questions/77600048/azure-function-logging-to-azure-blob-with-python
def _get_blob_for_session_data_logging(filename):
    container_client = _get_blog_container()

    blob_client = container_client.get_blob_client(filename)
    # Check if blob exists, if not create an append blob
    try:
        blob_client.get_blob_properties()  # Check if blob exists
    except:
        # Create an empty append blob if it doesn't exist
        blob_client.create_append_blob()
    return blob_client



def setup_for_azure():
    if 'service_provider' not in st.session_state:
        st.session_state['service_provider'] = 'azure'

    if "use_environmental_variables" not in st.session_state:
        st.session_state['use_environmental_variables'] = True 
        if st.session_state['use_environmental_variables']:
            load_dotenv()

            if 'openai_key' not in st.session_state:
                openai_api_key = os.getenv("OPENAI_API_KEY_GDPR")
                st.session_state['openai_key'] = openai_api_key
            if 'corpus_decryption_key' not in st.session_state:
                st.session_state['corpus_decryption_key'] = os.getenv("DECRYPTION_KEY_GDPR")
            # blob storage for global and session logging

    else: # use key_vault
        raise NotImplementedError()

    # No passwords yet in Azure but passwords required for other pages
    if not "password_correct" in st.session_state: 
        st.session_state["password_correct"] = True



def setup_for_streamlit(insist_on_password = False):
    if 'service_provider' not in st.session_state:
        st.session_state['service_provider'] = 'streamlit'

    if 'corpus_decryption_key' not in st.session_state:
        st.session_state['corpus_decryption_key'] = st.secrets["index"]["decryption_key"]

    if 'openai_api' not in st.session_state:
        st.session_state['openai_key'] = st.secrets['openai']['OPENAI_API_KEY']

        if not insist_on_password:
            if "password_correct" not in st.session_state.keys():
                st.session_state["password_correct"] = True
        else:
            ## Password
            def check_password():
                """Returns `True` if the user had a correct password."""

                def login_form():
                    """Form with widgets to collect user information"""
                    with st.form("Credentials"):
                        st.text_input("Username", key="username")
                        st.text_input("Password", type="password", key="password")
                        st.form_submit_button("Log in", on_click=password_entered)

                def password_entered():
                    """Checks whether a password entered by the user is correct."""
                    pwd_raw = st.session_state['password']
                    if st.session_state["username"] in st.secrets[
                        "passwords"
                    ] and bcrypt.checkpw(
                        pwd_raw.encode(),
                        st.secrets.passwords[st.session_state["username"]].encode(),
                    ):
                        st.session_state["password_correct"] = True
                        logger.log(ANALYSIS_LEVEL, f"New questions From: {st.session_state['username']}")
                        del st.session_state["password"]  # Don't store the username or password.
                        del pwd_raw
                        st.session_state["user_id"] = st.session_state["username"] 
                        del st.session_state["username"]
                        
                    else:
                        st.session_state["password_correct"] = False

                # Return True if the username + password is validated.
                if st.session_state.get("password_correct", False):
                    return True

                # Show inputs for username + password.
                login_form()
                if "password_correct" in st.session_state:
                    st.error("😕 User not known or password incorrect")
                return False

            if not check_password():
                st.stop()

# Currently only set up for azure using environmental variables. Other options need to be built
def setup_log_storage(filename):
    if 'service_provider' in st.session_state and st.session_state['service_provider'] == 'azure':
        if st.session_state['use_environmental_variables'] == True:
            if 'blob_account_url' not in st.session_state:
                st.session_state['blob_account_url'] = os.getenv('BLOB_ACCOUNT_URL', 'https://gdprragstorageaccount.blob.core.windows.net/')
                st.session_state['blob_container_name'] = os.getenv('BLOB_CONTAINER', 'gdprtest01') # set a default in case 'BLOB_CONTAINER' is not set
                st.session_state['blob_store_key'] = os.getenv("CHAT_BLOB_STORE")
                st.session_state['blob_client_for_session_data'] = _get_blob_for_session_data_logging(filename)
                st.session_state['blob_name_for_global_logs'] = "app_log_data.txt"
                st.session_state['blob_client_for_global_data'] = _get_blob_for_global_logging(st.session_state['blob_name_for_global_logs'])


@st.cache_resource
def load_gdpr_corpus_index(key):
    logger.log(ANALYSIS_LEVEL, f"*** Loading gdpr corpis index. This should only happen once")
    return GDPRCorpusIndex(key)

def load_data():
    with st.spinner(text="Loading the excon documents and index - hang tight! This should take 5 seconds."):
        embedding_parameters = EmbeddingParameters("text-embedding-3-large", 1024)
        corpus_index = load_gdpr_corpus_index(st.session_state['corpus_decryption_key'])
        model_to_use =  "gpt-4o"
        chat_parameters = ChatParameters(chat_model = model_to_use, api_key=st.session_state['openai_key'], temperature = 0, max_tokens = 500, token_limit_when_truncating_message_queue = 3500)

        rerank_algo = RerankAlgos.LLM
        rerank_algo.params["openai_client"] = chat_parameters.openai_client
        rerank_algo.params["model_to_use"] = model_to_use
        rerank_algo.params["user_type"] = corpus_index.user_type
        rerank_algo.params["corpus_description"] = corpus_index.corpus_description
        rerank_algo.params["final_token_cap"] = 5000 # can go large with the new models

        
        chat = CorpusChat(
                          embedding_parameters = embedding_parameters, 
                          chat_parameters = chat_parameters, 
                          corpus_index = corpus_index,
                          rerank_algo = rerank_algo,   
                          user_name_for_logging=st.session_state["user_id"])

        return chat


def write_session_data_to_blob(text):
    if 'service_provider' in st.session_state and st.session_state['service_provider'] == 'azure':
        # Session log for user
        st.session_state['blob_client_for_session_data'].append_block(text + "\n")

def write_global_data_to_blob():
    if 'service_provider' in st.session_state and st.session_state['service_provider'] == 'azure':
        with open(st.session_state['global_logging_file_name'], "r") as temp_file:
            content = temp_file.read()
    st.session_state['blob_client_for_global_data'].upload_blob(data=content, overwrite=True)
