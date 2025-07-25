import streamlit as st
import json
import tempfile
from pathlib import Path
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

def get_google_drive():
    creds = st.secrets["google"]
    with tempfile.NamedTemporaryFile(delete=False, mode="w") as f:
        json.dump(dict(creds), f)
        credentials_path = f.name

    gauth = GoogleAuth()
    gauth.LoadServiceConfigFile()
    gauth.LoadCredentialsFile(credentials_path)
    gauth.Authorize()

    return GoogleDrive(gauth)

def upload_to_gdrive(file_path: str, filename: str):
    drive = get_google_drive()
    gfile = drive.CreateFile({'title': filename})
    gfile.SetContentFile(file_path)
    gfile.Upload()
    return gfile['alternateLink']

st.set_page_config(page_title="Upload File to Google Drive")
st.title("📁 Upload File to Google Drive")

user_name = st.text_input("Your Name")
user_email = st.text_input("Your Email")
uploaded_file = st.file_uploader("Choose a file to upload")

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
                uploaded_url = upload_to_gdrive(tmp_path, uploaded_file.name)
            st.success(f"✅ File uploaded successfully! [View File]({uploaded_url})")
        except Exception as e:
            st.error(f"❌ Upload failed: {e}")
        finally:
            Path(tmp_path).unlink(missing_ok=True)
