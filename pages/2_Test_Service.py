import streamlit as st

service = st.session_state.service

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

query = st.text_input(label="Query")

if st.button("Query"):
  emails = search_email(query)
  st.write(emails)
