import os
import traceback
import streamlit as st
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ─── CONFIG ────────────────────────────────────────────────────────────────
REQUEST_LINK = "https://www.dropbox.com/request/tydarVR6Ty4qZEwGGTPd"
TIMEOUT_SEC = 30
# ────────────────────────────────────────────────────────────────────────────


def get_driver():
    opts = Options()
    opts.add_argument("--headless=new")  # Use Chromium's new headless mode
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")

    # This uses the system-installed chromedriver via packages.txt
    return webdriver.Chrome(options=opts)


def upload_via_selenium(request_url: str, filepath: str, name: str, email: str):
    driver = get_driver()
    try:
        driver.get(request_url)
        wait = WebDriverWait(driver, TIMEOUT_SEC)

        # Optional: Close cookie iframe
        try:
            wait.until(EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, "iframe[id*='ccpa-iframe']")))
            close_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label='Close']")))
            close_btn.click()
            driver.switch_to.default_content()
        except:
            driver.switch_to.default_content()

        # Upload file
        file_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']")))
        file_input.send_keys(os.path.abspath(filepath))

        # Fill name and email
        name_field = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='Add your name']")))
        email_field = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='you@example.com']")))
        name_field.clear()
        name_field.send_keys(name)
        email_field.clear()
        email_field.send_keys(email)

        # Click upload button
        upload_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(normalize-space(.), 'Upload')]")))
        driver.execute_script("arguments[0].click();", upload_btn)
        wait.until(EC.staleness_of(upload_btn))

    finally:
        driver.quit()


def show():
    st.title("📤 Submit File to Dropbox")

    uploaded_file = st.file_uploader("Select file to upload", type=["txt", "log", "pdf"])
    name = st.text_input("Your Name")
    email = st.text_input("Your Email")

    if st.button("Upload"):
        if not uploaded_file or not name or not email:
            st.warning("Please complete all fields.")
        else:
            # Save temporary file
            temp_path = Path(uploaded_file.name)
            temp_path.write_bytes(uploaded_file.read())
            try:
                upload_via_selenium(REQUEST_LINK, str(temp_path), name, email)
                st.success("✅ File uploaded successfully!")
            except Exception:
                st.error("❌ Upload failed:")
                st.exception(traceback.format_exc())
            finally:
                temp_path.unlink(missing_ok=True)

    st.caption("This app uses a headless Chromium browser to upload your file to Dropbox.")


if __name__ == "__main__":
    show()
