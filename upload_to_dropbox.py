import json
from upload_logic import upload_via_selenium

with open("files_to_upload/metadata.json", "r") as f:
    metadata = json.load(f)

filename = metadata["filename"]
name = metadata["name"]
email = metadata["email"]
dropbox_request_id = "YOUR_REQUEST_ID"

upload_via_selenium(filename, name, email, dropbox_request_id)
