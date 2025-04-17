from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

# Set up Chrome options for compatibility
chrome_options = Options()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Initialize the driver with local ChromeDriver
service = Service('./chromedriver')
driver = webdriver.Chrome(service=service, options=chrome_options)

# Navigate to LinkedIn login page
driver.get("https://www.linkedin.com")
print("Navigating to LinkedIn...")
time.sleep(5)  # Wait longer for the page to fully load

# Find all form elements to inspect what's available
print("\nLooking for login form elements...")
form_elements = driver.find_elements(By.TAG_NAME, "input")
for element in form_elements:
    element_id = element.get_attribute("id")
    element_name = element.get_attribute("name")
    element_type = element.get_attribute("type")
    element_class = element.get_attribute("class")
    print(f"Element: ID='{element_id}', Name='{element_name}', Type='{element_type}', Class='{element_class}'")
    
print("\nLooking for button elements...")
button_elements = driver.find_elements(By.TAG_NAME, "button")
for element in button_elements:
    element_text = element.text
    element_class = element.get_attribute("class")
    element_id = element.get_attribute("id")
    print(f"Button: Text='{element_text}', Class='{element_class}', ID='{element_id}'")

# Take a screenshot to visually inspect the page
screenshot_path = "linkedin_login.png"
driver.save_screenshot(screenshot_path)
print(f"\nScreenshot saved to {screenshot_path}")

# Look for any input fields that might be for username/password
print("\nLooking for potential username/password fields...")
potential_username = driver.find_elements(By.CSS_SELECTOR, "input[type='text'], input[type='email']")
for element in potential_username:
    print(f"Potential username field: ID='{element.get_attribute('id')}', Name='{element.get_attribute('name')}', Class='{element.get_attribute('class')}'")

potential_password = driver.find_elements(By.CSS_SELECTOR, "input[type='password']")
for element in potential_password:
    print(f"Potential password field: ID='{element.get_attribute('id')}', Name='{element.get_attribute('name')}', Class='{element.get_attribute('class')}'")

# Output page title to confirm we're on the expected page
print(f"\nPage title: {driver.title}")
print(f"Current URL: {driver.current_url}")

# Close the driver
driver.quit() 