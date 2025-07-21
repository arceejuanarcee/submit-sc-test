import os
import traceback
import platform
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# ─── CONFIG ────────────────────────────────────────────────────────────────
REQUEST_LINK = "https://www.dropbox.com/request/tydarVR6Ty4qZEwGGTPd"
TIMEOUT_SEC  = 30
# ────────────────────────────────────────────────────────────────────────────

def get_chrome_options():
    """Configure Chrome options for different environments"""
    opts = webdriver.ChromeOptions()
    
    # Basic headless options
    opts.add_argument("--headless")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--disable-extensions")
    opts.add_argument("--disable-plugins")
    opts.add_argument("--disable-images")
    opts.add_argument("--disable-javascript")
    opts.add_argument("--window-size=1920,1080")
    
    # Additional options for cloud environments
    opts.add_argument("--remote-debugging-port=9222")
    opts.add_argument("--disable-background-timer-throttling")
    opts.add_argument("--disable-renderer-backgrounding")
    opts.add_argument("--disable-backgrounding-occluded-windows")
    
    # Try to use system Chrome if available
    system = platform.system().lower()
    if system == "linux":
        # Common Chrome paths on Linux
        chrome_paths = [
            "/usr/bin/chromium",
            "/usr/bin/chromium-browser", 
            "/usr/bin/google-chrome",
            "/usr/bin/google-chrome-stable"
        ]
        for path in chrome_paths:
            if os.path.exists(path):
                opts.binary_location = path
                break
    
    return opts

def upload_via_selenium(request_url: str, filepath: str, name: str, email: str):
    opts = get_chrome_options()
    
    try:
        # Try to use ChromeDriverManager first
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=opts)
    except Exception as e:
        print(f"ChromeDriverManager failed: {e}")
        try:
            # Fallback to system chromedriver
            service = Service("/usr/bin/chromedriver")
            driver = webdriver.Chrome(service=service, options=opts)
        except Exception as e2:
            raise Exception(f"Both ChromeDriverManager and system chromedriver failed. ChromeDriverManager error: {e}. System chromedriver error: {e2}")
    
    try:
        print("Loading page...")
        driver.get(request_url)
        wait = WebDriverWait(driver, TIMEOUT_SEC)

        print("Looking for file input...")
        file_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']")))
        file_input.send_keys(os.path.abspath(filepath))

        print("Filling form fields...")
        name_field = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='Add your name']")))
        email_field = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='you@example.com']")))
        name_field.clear()
        name_field.send_keys(name)
        email_field.clear()
        email_field.send_keys(email)

        print("Clicking upload button...")
        upload_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(normalize-space(.), 'Upload')]")))
        upload_btn.click()
        wait.until(EC.staleness_of(upload_btn))
        print("Upload completed successfully!")

    finally:
        driver.quit()


def show():
    import streamlit as st
    from pathlib import Path

    st.title("📤 Submit Commands to TU")
    uploaded_file = st.file_uploader("Select file to upload", type=["txt", "log"])
    name = st.text_input("Your Name")
    email = st.text_input("Your Email")

    if st.button("Upload"):  
        if not uploaded_file or not name or not email:
            st.warning("Please provide file, name, and email.")
        else:
            # Save temp file
            temp_path = Path(uploaded_file.name)
            temp_path.write_bytes(uploaded_file.read())
            
            # Show progress
            with st.spinner("Uploading file..."):
                try:
                    upload_via_selenium(REQUEST_LINK, str(temp_path), name, email)
                    st.success("File uploaded successfully!")
                except Exception as err:
                    st.error(f"Upload failed: {err}")
                    st.error("Full error details:")
                    st.code(traceback.format_exc())
                finally:
                    temp_path.unlink(missing_ok=True)

    st.caption("Note: This uses a headless browser to submit to Dropbox request link.")