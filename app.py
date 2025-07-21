import streamlit as st
import tempfile
from pathlib import Path
from playwright.sync_api import sync_playwright

REQUEST_LINK    = "https://www.dropbox.com/request/tydarVR6Ty4qZEwGGTPd"

def upload_with_playwright(url: str, filepath: str, name: str, email: str):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page    = browser.new_page()
        page.goto(url)

        # attach file
        page.set_input_files('input[type="file"]', filepath)

        # fill metadata
        page.fill('input[name="name"]', name)
        page.fill('input[name="email"]', email)

        # submit
        page.click('button[type="submit"]')

        # wait for confirmation
        page.wait_for_selector("text=Thank you", timeout=20000)
        browser.close()

# ————— Streamlit UI —————
st.set_page_config(page_title="Upload via Playwright")
st.title("📂 Upload File to Dropbox File Request")

user_name    = st.text_input("Your Name")
user_email   = st.text_input("Your Email")
uploaded_file = st.file_uploader("Pick a file")

if st.button("Upload"):
    if not uploaded_file:
        st.error("Choose a file first.")
    elif not user_name or not user_email:
        st.error("Enter both name and email.")
    else:
        # persist to temp file
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(uploaded_file.getvalue())
            tmp_path = tmp.name

        try:
            with st.spinner("Launching browser and uploading..."):
                upload_with_playwright(REQUEST_LINK, tmp_path, user_name, user_email)
            st.success("✅ Uploaded via real browser!")
        except Exception as e:
            st.error(f"❌ Upload failed: {e}")
        finally:
            Path(tmp_path).unlink(missing_ok=True)
