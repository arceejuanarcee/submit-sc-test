import streamlit as st
import tempfile
import json
from pydrive2.auth import ServiceAccountCredentials
from pydrive2.drive import GoogleDrive

# --- Google Drive Setup ---
def authorize_drive():
    gauth = ServiceAccountCredentials()
    gauth.LoadServiceConfigFile("submit-sc-d36fa519abf2.json")
    gauth.Authorize()
    return GoogleDrive(gauth)

# 📁 Replace this with your target Google Drive folder ID
FOLDER_ID = "D2 Commands"

def upload_to_drive(drive, filename, content, metadata):
    # Upload the file
    file_drive = drive.CreateFile({'title': filename, 'parents': [{'id': FOLDER_ID}]})
    file_drive.SetContentString(content.decode())
    file_drive.Upload()

    # Upload the metadata
    meta_name = f"{filename}.meta.json"
    meta_drive = drive.CreateFile({'title': meta_name, 'parents': [{'id': FOLDER_ID}]})
    meta_drive.SetContentString(json.dumps(metadata))
    meta_drive.Upload()

# --- Streamlit UI ---
st.set_page_config(page_title="Upload File to Google Drive")
st.title("📁 Upload File for Processing")

user_name = st.text_input("Your Name")
user_email = st.text_input("Your Email")
uploaded_file = st.file_uploader("Upload your .txt command file")

if st.button("Upload"):
    if not uploaded_file:
        st.error("❗ Please choose a file.")
    elif not user_name or not user_email:
        st.error("❗ Please enter both your name and email.")
    else:
        try:
            drive = authorize_drive()
            metadata = {
                "filename": uploaded_file.name,
                "name": user_name,
                "email": user_email
            }

            file_content = uploaded_file.getvalue()
            upload_to_drive(drive, uploaded_file.name, file_content, metadata)

            st.success("✅ File and metadata uploaded to Google Drive!")
        except Exception as e:
            st.error(f"❌ Upload failed: {e}")
