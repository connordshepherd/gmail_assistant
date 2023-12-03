# ------------ Imports -------------
import streamlit as st
from openai import OpenAI
import openai
import requests
import json
import datetime
import pandas as pd
import base64
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from base64 import urlsafe_b64decode

GPT_MODEL = "gpt-4-1106-preview"

service = st.session_state.service

# ------------ Functions -------------

# This is a real function to search Gmail for a given query

def search_email(query):
    try:
        # Ensure "category:primary" is always included in the query
        full_query = f"{query} category:primary"

        # Fetch emails that match the query
        response = service.users().messages().list(userId='me', q=full_query, maxResults=10).execute()
        messages = response.get('messages', [])

        # Initialize a list to hold email details
        emails = []

        # Process each message
        for msg in messages:
            message = service.users().messages().get(userId='me', id=msg['id'], format='metadata').execute()
            headers = message['payload']['headers']
            
            # Extract sender, date, subject, and ID from headers and message
            email_info = {
                'id': msg['id'],  # Add the email ID
                'sender': next(header['value'] for header in headers if header['name'] == 'From'),
                'date': next(header['value'] for header in headers if header['name'] == 'Date'),
                'subject': next(header['value'] for header in headers if header['name'] == 'Subject'),
            }
            emails.append(email_info)

        # Return the list of emails
        return emails

    except HttpError as error:
        print(f'An error occurred: {error}')
        return []

# This is a real function to fetch the full text of an email

def get_email_details(email_id):
    try:
        # Fetch the email by ID
        email = service.users().messages().get(userId='me', id=email_id).execute()

        # Initialize the details dictionary
        email_details = {
            'sender': '',
            'recipients': '',
            'subject': '',
            'body': '',
            'attachments': []
        }

        # Extract headers for sender, recipients, and subject
        headers = email['payload']['headers']
        for header in headers:
            if header['name'].lower() == 'from':
                email_details['sender'] = header['value']
            elif header['name'].lower() == 'to':
                email_details['recipients'] = header['value']
            elif header['name'].lower() == 'subject':
                email_details['subject'] = header['value']

        # Function to recursively parse the email body and attachments
        def parse_parts(parts):
            body = ''
            attachments = []
            for part in parts:
                if part['mimeType'] == 'text/plain' and 'data' in part['body']:
                    body += urlsafe_b64decode(part['body']['data']).decode('utf-8')
                elif 'filename' in part and part['filename']:
                    attachments.append(part['filename'])
                if 'parts' in part:
                    sub_body, sub_attachments = parse_parts(part['parts'])
                    body += sub_body
                    attachments.extend(sub_attachments)
            return body, attachments

        # Parse email body and attachments
        if 'parts' in email['payload']:
            email_body, email_attachments = parse_parts(email['payload']['parts'])
            email_details['body'] = email_body
            email_details['attachments'] = email_attachments

        return email_details

    except Exception as error:
        print(f'An error occurred: {error}')
        return {}

# This defines the spec of the functions that OpenAI can call. They need to match the real functions above. These are LLM-readable descriptions of what the functions do.

tools = [
    {
        "type": "function",
        "function": {
            "name": "search_email",
            "description": "Searches Gmail to get a list of emails matching a user's query. Returns Email ID, sender, subject line, date. If you don't have an ID, use this.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The query to send Google, using GMail search syntax",
                    }
                },
                "required": ["query"],
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_email_details",
            "description": "Use a Gmail Email ID to read the body of an email. Returns sender, recipients, body text, date, names of attachments.",
            "parameters": {
                "type": "object",
                "properties": {
                    "id": {
                        "type": "string",
                        "description": "The ID of the email.",
                    }
                },
                "required": ["id"]
            },
        }
    },
]

# This code executes whichever function OpenAI decides to call within the conversation.

def execute_function_call(tool_call):
    # Assuming 'tool_call' is an instance of ChatCompletionMessageToolCall

    # Check the function name and proceed accordingly
    if tool_call.function.name == "search_email":
        # Parse the arguments as JSON
        query = json.loads(tool_call.function.arguments)["query"]
        # Assuming 'ask_database' is your custom function to query the database
        results = search_email(query)
    elif tool_call.function.name == "get_email_details":
        # Parse the arguments as JSON
        email_id = json.loads(tool_call.function.arguments)["id"]
        # Call the get_email_details function
        results = get_email_details(email_id)
    else:
        results = f"Error: function {tool_call.function.name} does not exist"

    return results

def handle_new_user_message(messages, new_user_message):
    # Append the new user message
    messages.append({"role": "user", "content": new_user_message})

    # Generate a response from the assistant
    new_response = openai.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=messages,
        tools=tools
    )

    # Extract the assistant message object
    assistant_message = new_response.choices[0].message
    assistant_message.content = str(assistant_message.tool_calls[0].function)
    messages.append(assistant_message)

    # Check and execute tool calls if present
    if assistant_message.tool_calls:
      for tool_call in assistant_message.tool_calls:
          # Assuming execute_function_call is a function you've defined to execute the tool call
          results = execute_function_call(tool_call)
          str_results = str(results)
          # Append the tool call message
          messages.append({
              "role": "tool", 
              "tool_call_id": tool_call.id, 
              "name": tool_call.function.name, 
              "content": str_results
          })

          # Generate a human-readable response for the tool call
          human_readable_response = openai.chat.completions.create(
              model="gpt-4-1106-preview",
              messages=messages,
              tools=tools
          )
          assistant_message = human_readable_response.choices[0].message
          messages.append({"role": "assistant", "content": assistant_message.content})

    return messages

# ------------- UI --------------

st.title("Gmail Assistant")

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

if "messages" not in st.session_state:
    st.session_state.messages = []

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Display existing messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
if prompt := st.chat_input("What is up?"):
    # Append user message to session state
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Call your handle_new_user_message function to process the input
    st.session_state.messages = handle_new_user_message(
        st.session_state.messages, prompt
    )

    # Display the latest message (assistant's response)
    latest_message = st.session_state.messages[-1]
    with st.chat_message(latest_message["role"]):
        st.markdown(latest_message["content"])
