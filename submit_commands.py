import os
import traceback
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager

# ─── CONFIG ────────────────────────────────────────────────────────────────
REQUEST_LINK = "https://www.dropbox.com/request/tydarVR6Ty4qZEwGGTPd"
TIMEOUT_SEC  = 30
# ────────────────────────────────────────────────────────────────────────────

def upload_via_selenium(request_url: str, filepath: str, name: str, email: str):
    opts = FirefoxOptions()
    opts.add_argument("--headless")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Firefox(
        service=FirefoxService(GeckoDriverManager().install()),
        options=opts
    )

    try:
        driver.get(request_url)
        wait = WebDriverWait(driver, TIMEOUT_SEC)

        file_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']")))
        file_input.send_keys(os.path.abspath(filepath))

        name_field = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='Add your name']")))
        email_field = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='you@example.com']")))
        name_field.clear()
        name_field.send_keys(name)
        email_field.clear()
        email_field.send_keys(email)

        upload_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(normalize-space(.), 'Upload')]")))
        upload_btn.click()
        wait.until(EC.staleness_of(upload_btn))

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
            try:
                upload_via_selenium(REQUEST_LINK, str(temp_path), name, email)
                st.success("File uploaded successfully!")
            except Exception as err:
                st.error(f"Upload failed: {err}")
                st.exception(traceback.format_exc())
            finally:
                temp_path.unlink(missing_ok=True)

    st.caption("Note: This uses a headless Firefox browser to submit to Dropbox request link.")
