import streamlit as st
import tempfile
import json
from pathlib import Path
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

# --- Set up page ---
st.set_page_config(page_title="Upload File to Google Drive")
st.title("📂 Upload File to Google Drive")

# --- Google Drive Setup ---
def get_google_drive():
    creds = dict(st.secrets["google"])

    # Write credentials to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".json", mode="w") as tmp:
        json.dump(creds, tmp)
        credentials_path = tmp.name

    gauth = GoogleAuth()
    gauth.LoadServiceConfigSettings()
    gauth.ServiceAuth(credentials_path)

    return GoogleDrive(gauth)

# --- Upload Logic ---
def upload_to_drive(file_path, filename, name, email):
    drive = get_google_drive()

    # Create metadata with name and email (if needed)
    file = drive.CreateFile({
        'title': filename,
        'description': f"Uploaded by: {name} ({email})"
    })
    file.SetContentFile(file_path)
    file.Upload()

# --- Streamlit Form ---
user_name = st.text_input("Your Name")
user_email = st.text_input("Your Email")
uploaded_file = st.file_uploader("Choose a file to upload", type=["txt", "pdf", "png", "jpg", "csv", "zip"])

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
                upload_to_drive(tmp_path, uploaded_file.name, user_name, user_email)
            st.success("✅ File uploaded successfully to Google Drive!")
        except Exception as e:
            st.error(f"❌ Upload failed: {e}")
        finally:
            Path(tmp_path).unlink(missing_ok=True)
