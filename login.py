from dependencies import *
import traceback
import sys

# Set up Chrome options
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--disable-popup-blocking")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option("useAutomationExtension", False)

# Initialize driver globally for other modules to access
driver = None

try:
    print("Initializing Chrome WebDriver...")
    
    # Try to use the ChromeDriverManager for automatic driver management
    try:
        from webdriver_manager.chrome import ChromeDriverManager
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        print("Using ChromeDriverManager for WebDriver")
    except Exception as e:
        print(f"ChromeDriverManager failed: {e}")
        print("Trying local ChromeDriver...")
        
        # Fall back to local driver if automatic management fails
        try:
            # First try the chromedriver in the main directory
            service = Service('./chromedriver')
            driver = webdriver.Chrome(service=service, options=chrome_options)
            print("Using local ChromeDriver from root directory")
        except Exception as e:
            print(f"Local ChromeDriver failed: {e}")
            print("Trying ChromeDriver in driver directory...")
            
            try:
                # Then try the one in the driver directory
                service = Service('./driver/chromedriver_linux64/chromedriver')
                driver = webdriver.Chrome(service=service, options=chrome_options)
                print("Using ChromeDriver from driver/chromedriver_linux64 directory")
            except Exception as e:
                print(f"Error initializing Chrome WebDriver: {e}")
                print("Please ensure chromedriver is available or install Chrome using the provided scripts.")
                sys.exit(1)
    
    # Make sure driver is initialized
    if driver is None:
        print("Failed to initialize WebDriver")
        sys.exit(1)
    
    # Set window size for better rendering
    driver.set_window_size(1920, 1080)
    
    # Add stealth features to appear more human-like
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    print("WebDriver initialized successfully.")
except Exception as e:
    print(f"Error setting up WebDriver: {e}")
    traceback.print_exc()
    sys.exit(1)

# Function to handle login
def login_to_linkedin():
    print("Starting LinkedIn login process...")
    
    try:
        # Navigate to LinkedIn login page
        print("Navigating to LinkedIn login page...")
        driver.get("https://www.linkedin.com/login")  # Direct to login page instead of homepage
        time.sleep(5)  # Wait longer to ensure page loads completely
        
        # Try to get and save a screenshot for debugging
        try:
            debug_screenshot = "linkedin_debug.png"
            driver.save_screenshot(debug_screenshot)
            print(f"Debug screenshot saved to {debug_screenshot}")
        except Exception as e:
            print(f"Warning: Could not save debug screenshot: {e}")
        
        # Get page source for debugging
        page_title = driver.title
        current_url = driver.current_url
        print(f"Current page: Title='{page_title}', URL='{current_url}'")
        
        # Try to find username field with multiple selectors
        username_field = None
        username_selectors = [
            (By.ID, "username"),  # Current LinkedIn login page
            (By.ID, "session_key"),  # Old LinkedIn login page
            (By.NAME, "session_key"),
            (By.NAME, "email-or-phone"),
            (By.CSS_SELECTOR, "input[name='session_key']"),
            (By.CSS_SELECTOR, "input[autocomplete='username']"),
            (By.CSS_SELECTOR, "input[type='text']")
        ]
        
        for selector_type, selector_value in username_selectors:
            try:
                elements = driver.find_elements(selector_type, selector_value)
                for element in elements:
                    if element.is_displayed():
                        username_field = element
                        print(f"Found username field using selector: {selector_type}={selector_value}")
                        break
                if username_field:
                    break
            except:
                continue
        
        # Try to find password field with multiple selectors
        password_field = None
        password_selectors = [
            (By.ID, "password"),  # Current LinkedIn login page
            (By.ID, "session_password"),  # Old LinkedIn login page
            (By.NAME, "session_password"),
            (By.CSS_SELECTOR, "input[name='session_password']"),
            (By.CSS_SELECTOR, "input[autocomplete='current-password']"),
            (By.CSS_SELECTOR, "input[type='password']")
        ]
        
        for selector_type, selector_value in password_selectors:
            try:
                elements = driver.find_elements(selector_type, selector_value)
                for element in elements:
                    if element.is_displayed():
                        password_field = element
                        print(f"Found password field using selector: {selector_type}={selector_value}")
                        break
                if password_field:
                    break
            except:
                continue
        
        # Try to find sign-in button with multiple selectors
        signin_button = None
        signin_selectors = [
            (By.CSS_SELECTOR, "button[type='submit']"),  # Most reliable
            (By.CLASS_NAME, "sign-in-form__submit-button"),
            (By.CSS_SELECTOR, "button[data-id='sign-in-form__submit-btn']"),
            (By.XPATH, "//button[contains(text(), 'Sign in')]"),
            (By.XPATH, "//button[contains(@class, 'sign-in')]")
        ]
        
        for selector_type, selector_value in signin_selectors:
            try:
                elements = driver.find_elements(selector_type, selector_value)
                for element in elements:
                    if element.is_displayed():
                        signin_button = element
                        print(f"Found sign-in button using selector: {selector_type}={selector_value}")
                        break
                if signin_button:
                    break
            except:
                continue
        
        # Check if we found all the required elements
        if not username_field or not password_field or not signin_button:
            missing = []
            if not username_field: missing.append("username field")
            if not password_field: missing.append("password field")
            if not signin_button: missing.append("sign-in button")
            print(f"Could not find these elements: {', '.join(missing)}")
            
            # Take a screenshot of all elements for debugging
            elements = driver.find_elements(By.TAG_NAME, "input")
            print("\nFound these input elements:")
            for element in elements:
                element_id = element.get_attribute("id")
                element_name = element.get_attribute("name")
                element_type = element.get_attribute("type")
                element_class = element.get_attribute("class")
                print(f"Element: ID='{element_id}', Name='{element_name}', Type='{element_type}', Class='{element_class}'")
            
            print("LinkedIn login page has changed. Please update the selectors.")
            return False
        
        # Fill in the login form
        print("Entering login credentials...")
        username_field.clear()
        username_field.send_keys(config.username)
        time.sleep(1)  # Small delay between actions to appear more human-like
        
        password_field.clear()
        password_field.send_keys(config.password)
        time.sleep(1)
        
        # Click the sign-in button
        print("Submitting login form...")
        signin_button.click()
        
        # Wait for login to complete
        print("Waiting for login to complete...")
        time.sleep(8)
        
        # Check if login was successful
        if "feed" in driver.current_url or "checkpoint" in driver.current_url or "mynetwork" in driver.current_url:
            print("Login successful!")
            return True
        else:
            print(f"Login might have failed. Current URL: {driver.current_url}")
            print("Please check your credentials in config.py")
            
            # Save a screenshot for debugging login failure
            try:
                failure_screenshot = "linkedin_login_failure.png"
                driver.save_screenshot(failure_screenshot)
                print(f"Login failure screenshot saved to {failure_screenshot}")
            except Exception as e:
                print(f"Warning: Could not save failure screenshot: {e}")
            
            return False
    except Exception as e:
        print(f"Error during login: {e}")
        traceback.print_exc()
        
        # Save a screenshot for debugging the exception
        try:
            error_screenshot = "linkedin_error.png"
            driver.save_screenshot(error_screenshot)
            print(f"Error screenshot saved to {error_screenshot}")
        except Exception as e:
            print(f"Warning: Could not save error screenshot: {e}")
        
        print("LinkedIn login page may have changed. Please check and update the selectors.")
        return False

# Actually perform the login
login_successful = login_to_linkedin()
if not login_successful:
    print("Login failed. Exiting.")
    sys.exit(1)
