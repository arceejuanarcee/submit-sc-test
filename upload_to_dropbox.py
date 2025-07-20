import os
from submit_commands import upload_via_selenium

files = sorted(
    [f for f in os.listdir("files_to_upload")],
    key=lambda x: os.path.getmtime(os.path.join("files_to_upload", x)),
    reverse=True
)

if files:
    latest = files[0]
    upload_via_selenium(
        "https://www.dropbox.com/request/YOUR_REQUEST_ID",
        os.path.join("files_to_upload", latest),
        name="GitHub Action",
        email="upload@bot.com"
    )
else:
    print("No file to upload.")
