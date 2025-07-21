import os
import requests
from pathlib import Path
from bs4 import BeautifulSoup
import re

# ─── CONFIG ────────────────────────────────────────────────────────────────
REQUEST_LINK = "https://www.dropbox.com/request/tydarVR6Ty4qZEwGGTPd"
# ────────────────────────────────────────────────────────────────────────────

def extract_form_data(html_content):
    """Extract form action URL and hidden fields from Dropbox request page"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find the upload form
    form = soup.find('form')
    if not form:
        raise Exception("Could not find upload form on page")
    
    # Get form action URL
    action = form.get('action')
    if not action:
        raise Exception("Could not find form action URL")
    
    # Extract hidden fields
    hidden_fields = {}
    for input_tag in form.find_all('input', type='hidden'):
        name = input_tag.get('name')
        value = input_tag.get('value', '')
        if name:
            hidden_fields[name] = value
    
    return action, hidden_fields

def upload_via_http(request_url: str, filepath: str, name: str, email: str):
    """Upload file using pure HTTP requests"""
    
    # Create a session to maintain cookies
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    })
    
    # Step 1: Get the upload page to extract form data
    print("Getting upload form...")
    response = session.get(request_url)
    response.raise_for_status()
    
    # Step 2: Parse the form to get action URL and hidden fields
    try:
        action_url, hidden_fields = extract_form_data(response.text)
        if not action_url.startswith('http'):
            # Relative URL, make it absolute
            from urllib.parse import urljoin
            action_url = urljoin(request_url, action_url)
    except Exception as e:
        raise Exception(f"Failed to parse upload form: {e}")
    
    # Step 3: Prepare the upload data
    print(f"Uploading to: {action_url}")
    
    # Prepare files
    with open(filepath, 'rb') as f:
        files = {
            'file': (os.path.basename(filepath), f, 'text/plain')
        }
        
        # Prepare form data
        data = hidden_fields.copy()
        data.update({
            'name': name,
            'email': email
        })
        
        # Step 4: Upload the file
        upload_response = session.post(action_url, files=files, data=data)
    
    # Step 5: Check if upload was successful
    if upload_response.status_code in [200, 302]:
        # Check response content for success indicators
        if 'success' in upload_response.text.lower() or upload_response.status_code == 302:
            return True
        else:
            # Look for error messages in the response
            soup = BeautifulSoup(upload_response.text, 'html.parser')
            error_elements = soup.find_all(text=re.compile('error|failed|invalid', re.I))
            if error_elements:
                raise Exception(f"Upload may have failed: {error_elements[0]}")
    else:
        raise Exception(f"Upload failed with status {upload_response.status_code}: {upload_response.text[:500]}")
    
    return True

def show():
    import streamlit as st
    from pathlib import Path
    import traceback

    st.title("📤 Submit Commands to TU")
    
    # Check if required packages are available
    try:
        import requests
        from bs4 import BeautifulSoup
        packages_available = True
    except ImportError as e:
        packages_available = False
        st.error(f"Required packages not installed: {e}")
        st.info("Add to requirements.txt: requests, beautifulsoup4")
    
    uploaded_file = st.file_uploader("Select file to upload", type=["txt", "log"])
    name = st.text_input("Your Name")
    email = st.text_input("Your Email")

    if st.button("Upload"):  
        if not uploaded_file or not name or not email:
            st.warning("Please provide file, name, and email.")
        elif not packages_available:
            st.error("Required packages are not installed.")
        else:
            # Save temp file
            temp_path = Path(uploaded_file.name)
            temp_path.write_bytes(uploaded_file.read())
            
            with st.spinner("Uploading file..."):
                try:
                    upload_via_http(REQUEST_LINK, str(temp_path), name, email)
                    st.success("File uploaded successfully!")
                except Exception as err:
                    st.error(f"Upload failed: {err}")
                    
                    # Show detailed error for debugging
                    with st.expander("Show detailed error"):
                        st.code(traceback.format_exc())
                finally:
                    temp_path.unlink(missing_ok=True)

    st.caption("Note: This uses HTTP requests to submit directly to Dropbox.")