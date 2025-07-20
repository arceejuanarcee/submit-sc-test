import streamlit as st
import requests
import base64

def push_to_github(uploaded_file, filename):
    token = st.secrets["GITHUB_PAT"]
    username = st.secrets["GITHUB_USERNAME"]
    repo = st.secrets["GITHUB_REPO"]
    path = f"files_to_upload/{filename}"
    url = f"https://api.github.com/repos/{username}/{repo}/contents/{path}"
    content = base64.b64encode(uploaded_file.read()).decode("utf-8")
    response = requests.put(
        url,
        headers={
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        },
        json={
            "message": f"Add {filename} from Streamlit",
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
            res = push_to_github(uploaded_file, uploaded_file.name)
            if res.status_code == 201:
                st.success("✅ File pushed to GitHub. GitHub Action will handle Dropbox upload.")
            else:
                st.error(f"❌ GitHub push failed: {res.status_code}\n{res.text}")

if __name__ == "__main__":
    show()
