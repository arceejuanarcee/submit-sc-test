import streamlit as st
import tempfile
from pathlib import Path
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Google Drive API scope
SCOPES = ['https://www.googleapis.com/auth/drive.file']

# Load service account credentials from Streamlit secrets
creds_dict = dict(st.secrets["google"])

# Authenticate using in-memory dictionary
credentials = service_account.Credentials.from_service_account_info(
    creds_dict, scopes=SCOPES)

# Initialize the Google Drive service
drive_service = build('drive', 'v3', credentials=credentials)

# Optional: Set a specific folder ID (must be shared with the service account)
FOLDER_ID = st.secrets["google"].get("folder_id")  # Set this in secrets if needed

# --- Streamlit UI ---
st.set_page_config(page_title="Upload to Google Drive")
st.title("📁 Upload a File to Google Drive")

user_name = st.text_input("Your Name")
user_email = st.text_input("Your Email")
uploaded_file = st.file_uploader("Choose a file")

if st.button("Upload"):
    if not uploaded_file:
        st.error("❗ Please choose a file to upload.")
    elif not user_name or not user_email:
        st.error("❗ Please enter both your name and email.")
    else:
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(uploaded_file.getvalue())
            tmp_path = tmp.name

        try:
            with st.spinner("Uploading to Google Drive..."):

                # Define metadata
                file_metadata = {
                    'name': uploaded_file.name,
                    'description': f"Uploaded by {user_name} ({user_email})"
                }
                if FOLDER_ID:
                    file_metadata['parents'] = [FOLDER_ID]

                media = MediaFileUpload(tmp_path, resumable=True)
                file = drive_service.files().create(
                    body=file_metadata,
                    media_body=media,
                    fields='id'
                ).execute()

                st.success(f"✅ Upload successful! File ID: {file.get('id')}")
        except Exception as e:
            st.error(f"❌ Upload failed: {e}")
        finally:
            Path(tmp_path).unlink(missing_ok=True)
