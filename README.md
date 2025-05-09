README.md

# 📥 TeraBox File Downloader (Python + Selenium)

A robust Python tool that automates file downloads from [TeraBox](https://www.terabox.com/) using **Selenium browser automation**. Ideal for files shared via public links that may involve JavaScript-rendered pages or dynamic download flows.

---

## 📚 Table of Contents

- [Features](#-features)
- [Requirements](#️-requirements)
- [Installation](#-installation)
- [Usage](#-usage)
- [Tested With](#-tested-with)
- [Known Limitations](#-known-limitations)
- [License](#-license)
- [Disclaimer](#-disclaimer)
- [Contributors](#-contributors)

---

## 🚀 Features

- 🖱️ Full Selenium automation for reliability
- ⏳ Smart wait for buttons and interactions
- 🔗 Extracts actual downloadable link
- 📥 Downloads with progress bar (`tqdm`)
- 🔄 Graceful error handling (invalid/expired links)

---

## 🛠️ Requirements

- Python 3.7 or higher
- Google Chrome browser
- pip packages:

bash:
pip install -r requirements.txt

Requirements.txt

selenium
webdriver-manager
requests
tqdm

main.py

import os
import time
import re
import requests
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def setup_browser(headless=False):
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    return driver

def extract_download_link(driver, link):
    driver.get(link)

    try:
        # Wait for download button to be clickable
        download_button = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, '//a[contains(@class,"download-button")]'))
        )
        download_button.click()

        # Wait for the download link or redirection
        time.sleep(5)

        # Check for direct download link (may appear after clicking download)
        current_url = driver.current_url
        if "terabox" not in current_url:
            return current_url

        # Look for <a href> in page source
        matches = re.findall(r'href=[\'"]?([^\'" >]+)', driver.page_source)
        for match in matches:
            if match.startswith("https://") and ("download" in match or "file" in match):
                return match

    except Exception as e:
        print(f"[!] Error extracting link: {e}")
        return None

def download_file(url, output_path):
    try:
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            total = int(r.headers.get('content-length', 0))
            with open(output_path, 'wb') as f, tqdm(
                desc=output_path,
                total=total,
                unit='iB',
                unit_scale=True,
                unit_divisor=1024,
            ) as bar:
                for data in r.iter_content(chunk_size=1024):
                    size = f.write(data)
                    bar.update(size)
        print(f"\n✅ Download complete: {output_path}")
    except Exception as e:
        print(f"[!] Download failed: {e}")

def main():
    print("🔗 TeraBox Downloader\n")
    link = input("Paste your TeraBox link here: ").strip()

    if "terabox" not in link:
        print("❌ Invalid TeraBox URL.")
        return

    driver = setup_browser()
    print("🌐 Opening browser...")

    try:
        download_url = extract_download_link(driver, link)
        driver.quit()

        if download_url:
            print(f"✅ Download link found:\n{download_url}")
            filename = download_url.split("/")[-1].split("?")[0]
            download_file(download_url, filename)
        else:
            print("❌ Could not extract a download URL. Try manually or check if the file is private.")

    finally:
        driver.quit()

if __name__ == "__main__":
    main()

installation

git clone https://github.com/yourusername/terabox-downloader.git
cd terabox-downloader
pip install -r requirements.txt

usage

python main.py



The script will:

1.Launch a Chrome browser.

2.Click the download button.

3.Extract the real download URL.

4.Download the file to your system.

🧪 Tested With
Public file links from https://www.terabox.com/

Chrome Stable (v122+) with webdriver-manager

File sizes up to 2GB in testing

⚠️ Known Limitations
❌ Files requiring login/captcha will not work

❌ Expired or private links will fail gracefully

📦 Some large downloads may timeout; auto-resume not yet supported

📃 License
MIT License © 2025

🔐 Disclaimer
⚠️ This tool is for educational and personal use only. Automating access to TeraBox may violate their Terms of Service. Use responsibly.

🤝 Contributors
Sonu Shaw – Core Developer
