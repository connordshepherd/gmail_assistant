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
access_token = 'ya29.a0AfB_byDrNOKPf_Ny30S_9QUTtCRwhiO78pFbkUqsqzF_pHTnn8nvF-eA3davyN8TX1Wdw1CD7Fd2xP9XqJ3aYO1NTrFT4nMNsN22BOd666C9GX_g68rZSwUH7B0xdYY2Dw66CQD7ocELT3ywxVLLhY8fhg_U69lN2-8NaCgYKAR0SARESFQHGX2MiW4SdUBT9O-0IUp7S-tujgg0171'
refresh_token = '1//04JP5BC-5g3NzCgYIARAAGAQSNgF-L9IrhNfEx4GQM1REeqa2DU7PKfWO7sRiAmC8buSrpvNMm_lG9SNKDUhIVvpg2JIAPb5Nnw'

input_client_id = st.text_input(label="Client ID", value=client_id)
input_client_secret = st.text_input(label="Client Secret", value=client_secret)
input_access_token = st.text_input(label="Access Token", value=access_token)
input_refresh_token = st.text_input(label="Access Token", value=refresh_token)

if st.button("Build Service"):
  service = authenticate_gmail(access_token, refresh_token, client_id, client_secret)
  st.session_state.service = service
  st.success("It Built")
