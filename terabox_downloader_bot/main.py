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
