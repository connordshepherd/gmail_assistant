import streamlit as st
import base64
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

# Session state
if 'service' not in st.session_state:
    st.session_state.service = None

info_message = """Go to https://developers.google.com/oauthplayground/ 
Click on the gear icon (Settings) in the top right corner
Check the box for "Use your own OAuth credentials"
Plug in the client_id and client_secret values
Select Gmail API v1 and https://www.googleapis.com/auth/gmail.readonly, click Authorize, Log in"""

# This is a real function to authenticate into Gmail

def authenticate_gmail(access_token, refresh_token, client_id, client_secret):
    """
    Authenticate and create a Gmail service using provided OAuth credentials.

    Args:
    access_token (str): OAuth2 access token.
    refresh_token (str): OAuth2 refresh token.
    client_id (str): OAuth2 client ID.
    client_secret (str): OAuth2 client secret.

    Returns:
    googleapiclient.discovery.Resource: Authenticated Gmail service.
    """
    # Manual credentials setup
    info = {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "client_id": client_id,
        "client_secret": client_secret,
        "token_uri": "https://oauth2.googleapis.com/token",  # Google's token refresh endpoint
        "scopes": ["https://www.googleapis.com/auth/gmail.readonly"]
    }
    creds = Credentials.from_authorized_user_info(info)

    # Build the Gmail service
    service = build('gmail', 'v1', credentials=creds)
    return service

st.title("Build Gmail Service")
st.info(info_message)

client_id = '122758298025-1vcijqke0mov1seirsef5rll4v7no0s3.apps.googleusercontent.com'
client_secret = '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'
access_token = 'ya29.a0AfB_byDBnbF08281Wi58_yHM5QcvrCSueGF8zF27TS-H9GllFTZhjDna6nhdWT4_v02P5N6g9DymK4y-whwyzt-EOa7QdokNSZWYaThEwvWnIUvwVg1oUMLKWxiMl7nFf0Fdt2oUi8cAKsNuggpv_JBSnNz0eu4w1AJzaCgYKAZYSARESFQHGX2MigUB4VhwQ6mPDwzjnO3Ngjw0171'
refresh_token = '1//04c9xtGz7JgL4CgYIARAAGAQSNgF-L9IrEe5oWoEPezKm5W72Z3fYoXMUs7t4ccIaJIRrJEXj6IwCgPTWdpPzkjx1su5o8FoT4Q'

input_client_id = st.text_input(label="Client ID", value=client_id)
input_client_secret = st.text_input(label="Client Secret", value=client_secret)
input_access_token = st.text_input(label="Access Token", value=access_token)
input_refresh_token = st.text_input(label="Access Token", value=refresh_token)

if st.button("Build Service"):
  service = authenticate_gmail(input_access_token, input_refresh_token, input_client_id, input_client_secret)
  st.session_state.service = service
  st.success("It Built")
