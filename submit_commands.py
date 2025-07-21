import streamlit as st
import requests
import base64
import json
from io import BytesIO

def push_to_github(file_content, filename, commit_message):
    token = st.secrets["GITHUB_PAT"]
    username = st.secrets["GITHUB_USERNAME"]
    repo = st.secrets["GITHUB_REPO"]
    path = f"files_to_upload/{filename}"
    url = f"https://api.github.com/repos/{username}/{repo}/contents/{path}"

    content = base64.b64encode(file_content).decode("utf-8")
    response = requests.put(
        url,
        headers={
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        },
        json={
            "message": commit_message,
            "content": content,
            "branch": "main"
        }
    )
    return response

def show():
    st.title("📤 Upload to Dropbox via GitHub Actions")
    uploaded_file = st.file_uploader("Choose a file")
    name = st.text_input("Your Name")
    email = st.text_input("Your Email")

    if st.button("Upload"):
        if not uploaded_file or not name or not email:
            st.warning("Please complete all fields.")
        else:
            # Read uploaded file content
            file_bytes = uploaded_file.read()

            # Push uploaded file to GitHub
            file_res = push_to_github(
                file_bytes,
                uploaded_file.name,
                f"Add {uploaded_file.name} from Streamlit"
            )

            # Create metadata JSON
            metadata = {
                "name": name,
                "email": email,
                "filename": f"files_to_upload/{uploaded_file.name}"
            }
            metadata_bytes = BytesIO(json.dumps(metadata).encode("utf-8"))

            # Push metadata.json to GitHub
            meta_res = push_to_github(
                metadata_bytes.read(),
                "metadata.json",
                "Add metadata for Dropbox upload"
            )

            if file_res.status_code == 201 and meta_res.status_code == 201:
                st.success("✅ File and metadata pushed to GitHub. GitHub Action will handle Dropbox upload.")
            else:
                st.error(f"❌ GitHub push failed.\nFile: {file_res.status_code}\nMeta: {meta_res.status_code}")

if __name__ == "__main__":
    show()
