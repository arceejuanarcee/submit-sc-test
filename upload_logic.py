from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

def upload_via_selenium(filename, name, email, dropbox_request_id):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(f"https://www.dropbox.com/request/{dropbox_request_id}")

    time.sleep(2)
    upload = driver.find_element("xpath", "//input[@type='file']")
    upload.send_keys(filename)

    time.sleep(2)
    driver.find_element("xpath", "//input[@name='uploader_name']").send_keys(name)
    driver.find_element("xpath", "//input[@name='uploader_email']").send_keys(email)
    driver.find_element("xpath", "//button[.//span[text()='Upload']]").click()

    time.sleep(5)
    driver.quit()
