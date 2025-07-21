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
