import streamlit as st
import tempfile
import json
from pathlib import Path
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

st.set_page_config(page_title="Upload File to Google Drive")
st.title("📂 Upload File to Google Drive")

# --- Authenticate and return Drive instance ---
def get_drive():
    creds_dict = dict(st.secrets["google"])  # ✅ FIXED here

    # Save secrets to a temp file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(creds_dict, f)
        credentials_path = f.name

    gauth = GoogleAuth()
    gauth.LoadServiceConfigFile(credentials_path)  # Load as config file
    gauth.ServiceAuth()

    return GoogleDrive(gauth)

# --- Upload logic ---
def upload_to_drive(file_path, filename, name, email):
    drive = get_drive()
    gfile = drive.CreateFile({
        'title': filename,
        'description': f"Uploaded by {name} ({email})"
    })
    gfile.SetContentFile(file_path)
    gfile.Upload()

# --- Streamlit UI ---
user_name = st.text_input("Your Name")
user_email = st.text_input("Your Email")
uploaded_file = st.file_uploader("Choose a file to upload")

if st.button("Upload"):
    if not uploaded_file:
        st.error("❗ Please choose a file to upload.")
    elif not user_name or not user_email:
        st.error("❗ Please enter both name and email.")
    else:
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(uploaded_file.getvalue())
            tmp_path = tmp.name

        try:
            with st.spinner("Uploading to Google Drive..."):
                upload_to_drive(tmp_path, uploaded_file.name, user_name, user_email)
            st.success("✅ Upload successful!")
        except Exception as e:
            st.error(f"❌ Upload failed: {e}")
        finally:
            Path(tmp_path).unlink(missing_ok=True)
