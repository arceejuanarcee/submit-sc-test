<<<<<<< HEAD
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
=======
#!/usr/bin/env python3
"""
submit_commands.py

Upload a file to a Dropbox File Request via pure HTTP (no Selenium).
"""

import requests
import time
import json
import sys
from pathlib import Path

# ———— CONFIG ————
# The page you open to seed cookies:
REQUEST_LINK    = "https://www.dropbox.com/request/tydarVR6Ty4qZEwGGTPd"
# The same ID in that URL:
FILE_REQUEST_ID = "tydarVR6Ty4qZEwGGTPd"
OWNER_ID        = "28628469"
# The “ut=” value from your commit cURL (it may rotate per session):
UT_PARAM        = "QctBEbIm02vVqrYypQ3C"
# From your put_block URL query:
NS_ID_FOR_ROUTING = "2099574545"


def upload_via_http(request_link: str, file_path: str, user_name: str, user_email: str):
    session = requests.Session()

    # 1) GET the request page so Dropbox sets cookies (t, csrf, etc.)
    resp = session.get(request_link)
    resp.raise_for_status()

    # Grab the 't' cookie for both calls
    t_cookie = session.cookies.get("t")
    if not t_cookie:
        raise Exception("Missing cookie 't'; did initial GET succeed?")

    # 2) UPLOAD THE CHUNK (single‑block example)
    size = Path(file_path).stat().st_size
    put_url = "https://dl-web.dropbox.com/put_block_returning_token_unauth"
    put_params = {
        "owner_id":          OWNER_ID,
        "t":                 t_cookie,
        "reported_block_size": str(size),
        "num_blocks":        "1",
        "ns_id_for_routing": NS_ID_FOR_ROUTING,
    }
    put_headers = {
        "Accept":       "*/*",
        "Content-Type": "application/octet-stream",
        "Origin":       "https://www.dropbox.com",
        "Referer":      "https://www.dropbox.com/",
    }

    with open(file_path, "rb") as f:
        chunk = f.read()
    r1 = session.post(put_url,
                      params=put_params,
                      headers=put_headers,
                      data=chunk)
    r1.raise_for_status()

    # Extract the returned block_token
    block_token = r1.json().get("block_token")
    if not block_token:
        raise Exception(f"No block_token in response: {r1.text}")

    # 3) COMMIT THE UPLOAD
    commit_url = "https://www.dropbox.com/drops/commit_file_request_by_token"
    commit_params = {
        "ut":                UT_PARAM,
        "token":             FILE_REQUEST_ID,
        "submitted_email":   user_email,
        "submitted_user_name": user_name,
        "user_id":           OWNER_ID,
        "dest":              "",
        "client_ts":         str(int(time.time())),
        "reported_total_size": str(size),
        "name":              Path(file_path).name,
        "t":                 t_cookie,
    }
    commit_headers = {
        "Accept":       "*/*",
        "Content-Type": "application/octet-stream",
        "Origin":       "https://www.dropbox.com",
        "Referer":      request_link,
    }

    # Body is a raw JSON array of block tokens
    body = json.dumps([block_token])
    r2 = session.post(commit_url,
                      params=commit_params,
                      headers=commit_headers,
                      data=body)
    r2.raise_for_status()

    result = r2.json()
    if result.get("success") or result.get("status") == "ok":
        return True
    else:
        raise Exception(f"Commit failed: {result}")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: submit_commands.py <file_path> <Your Name> <your_email>")
        sys.exit(1)

    file_path, name, email = sys.argv[1], sys.argv[2], sys.argv[3]
    try:
        ok = upload_via_http(REQUEST_LINK, file_path, name, email)
        print("✅ Upload succeeded!" if ok else "❌ Upload failed.")
    except Exception as e:
        print("❌ Error during upload:", e)
        sys.exit(1)
>>>>>>> 6c1f89e337bccb726e104a955f7528f5478835ab
