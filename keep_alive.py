from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import sys

app_url = "https://kerem-digital-twin.streamlit.app/"

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # Initialize the driver
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def visit_app():
    driver = setup_driver()
    print(f"Visiting {app_url}...")
    try:
        driver.get(app_url)
        # Wait for the app to load (Streamlit loading animation)
        time.sleep(15) 
        
        # Optional: Check if page title contains "Streamlit" or your app title
        print(f"Page title: {driver.title}")
        
        # If the 'Wake Up' button exists, this would be where we click it
        # specific logic depends on the specific "Yes, get this app back up!" button structure
        
        print("Visit complete.")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        driver.quit()

if __name__ == "__main__":
    visit_app()