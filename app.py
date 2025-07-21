# app.py
import streamlit as st
import requests
import time
import json
import tempfile
from pathlib import Path

# ————— CONFIG —————
REQUEST_LINK       = "https://www.dropbox.com/request/tydarVR6Ty4qZEwGGTPd"
FILE_REQUEST_ID    = "tydarVR6Ty4qZEwGGTPd"
OWNER_ID           = "28628469"
UT_PARAM           = "QctBEbIm02vVqrYypQ3C"        # update if it rotates
NS_ID_FOR_ROUTING  = "2099574545"

# ———— UPLOAD FUNCTION ————
def upload_via_http(request_link: str, filepath: str, user_name: str, user_email: str) -> bool:
    session = requests.Session()
    # 1) GET the request page so cookies (t, csrf, etc.) are set
    session.get(request_link).raise_for_status()
    t_cookie = session.cookies.get("t")
    if not t_cookie:
        raise Exception("Missing cookie ‘t’; initial GET failed?")

    # 2) Single‐block upload
    size = Path(filepath).stat().st_size
    put_url = "https://dl-web.dropbox.com/put_block_returning_token_unauth"
    put_params = {
        "owner_id": OWNER_ID,
        "t":        t_cookie,
        "reported_block_size": str(size),
        "num_blocks":          "1",
        "ns_id_for_routing":   NS_ID_FOR_ROUTING,
    }
    put_headers = {
        "Accept":       "*/*",
        "Content-Type": "application/octet-stream",
        "Origin":       "https://www.dropbox.com",
        "Referer":      "https://www.dropbox.com/",
    }
    with open(filepath, "rb") as f:
        chunk = f.read()
    r1 = session.post(put_url, params=put_params, headers=put_headers, data=chunk)
    r1.raise_for_status()
    block_token = r1.json().get("block_token")
    if not block_token:
        raise Exception(f"No block_token in response: {r1.text}")

    # 3) Commit the upload
    commit_url = "https://www.dropbox.com/drops/commit_file_request_by_token"
    commit_params = {
        "ut":                 UT_PARAM,
        "token":              FILE_REQUEST_ID,
        "submitted_email":    user_email,
        "submitted_user_name": user_name,
        "user_id":            OWNER_ID,
        "dest":               "",
        "client_ts":          str(int(time.time())),
        "reported_total_size": str(size),
        "name":               Path(filepath).name,
        "t":                  t_cookie,
    }
    commit_headers = {
        "Accept":       "*/*",
        "Content-Type": "application/octet-stream",
        "Origin":       "https://www.dropbox.com",
        "Referer":      request_link,
    }
    body = json.dumps([block_token])
    r2 = session.post(commit_url, params=commit_params, headers=commit_headers, data=body)
    r2.raise_for_status()
    result = r2.json()
    if result.get("success") or result.get("status") == "ok":
        return True
    else:
        raise Exception(f"Commit failed: {result}")

# ————— Streamlit UI —————
st.set_page_config(page_title="Upload to Dropbox Request")
st.title("📂 Upload File to Dropbox File Request")

user_name  = st.text_input("Your Name")
user_email = st.text_input("Your Email")
uploaded_file = st.file_uploader("Choose a file to upload")

if st.button("Upload"):
    if not uploaded_file:
        st.error("Please choose a file first.")
    elif not user_name or not user_email:
        st.error("Please provide both your name and email.")
    else:
        # Save to a temp file
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(uploaded_file.getvalue())
            tmp_path = tmp.name

        try:
            with st.spinner("Uploading..."):
                success = upload_via_http(REQUEST_LINK, tmp_path, user_name, user_email)
            if success:
                st.success("✅ File uploaded successfully!")
            else:
                st.error("❌ Upload did not succeed.")
        except Exception as e:
            st.error(f"❌ Upload failed: {e}")
        finally:
            # Clean up
            Path(tmp_path).unlink(missing_ok=True)
