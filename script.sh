#!/usr/bin/env bash

# LinkedIn Direct Connect Script
# This script automates the process of sending connection requests to people at specified companies in config.py

echo "====================================="
echo "LinkedIn Direct Connect Tool"
echo "====================================="
echo "This tool will help you connect with people working at companies listed in config.py"
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install Python 3 and try again."
    exit 1
fi

# Check if pip is installed
if ! command -v pip &> /dev/null; then
    echo "pip is not installed. Please install pip and try again."
    exit 1
fi

# Ensure config.py exists
if [ ! -f "config.py" ]; then
    echo "config.py is missing. Creating a template config file..."
    cat > config.py << 'EOL'
# LinkedIn credentials
username = "your-email@example.com"
password = "your-password"

# List of companies to connect with people
companies_list = ["amazon", "microsoft", "apple", "google", "facebook"]

# Personalized message for connection requests
message = """
Hi there,

I hope you're doing well! I'm reaching out because I'm interested in opportunities at your company.
I'd love to connect and learn more about your experience there.

Thank you for your time!

Best regards,
Your Name
"""
EOL
    echo "✅ Created config.py template. Please edit it with your LinkedIn credentials and preferences."
    echo "   Then run this script again."
    exit 1
fi


# Install required packages
echo "Installing required packages..."
pip install -r requirements.txt || {
    echo "Creating requirements.txt and installing dependencies..."
    cat > requirements.txt << 'EOL'
selenium
beautifulsoup4
webdriver-manager
pandas
lxml
EOL
    pip install -r requirements.txt
}           

# Check for chromedriver
echo "Checking for Chrome and chromedriver..."
if [ ! -f "chromedriver" ] && [ ! -f "./driver/chromedriver" ]; then
    echo "ChromeDriver not found. Attempting to download the appropriate version..."
    
    # Check if Chrome is installed
    if ! command -v google-chrome &> /dev/null; then
        echo "Chrome is not installed. Installing Chrome..."
        ./install_chrome.sh || {
            echo "⚠️ Chrome installation failed. Please install Chrome manually and try again."
            exit 1
        }
    fi
    
    # Get Chrome version
    chrome_version=$(google-chrome --version | awk '{print $3}' | cut -d. -f1)
    
    # Download compatible chromedriver
    ./get_chrome_driver.sh || {
        echo "⚠️ Failed to download ChromeDriver. Please download it manually and place it in the project directory."
        echo "   Visit: https://chromedriver.chromium.org/downloads"
        exit 1
    }
fi

# Fix permissions issues
echo "Setting executable permissions on scripts..."
chmod +x run_direct_connect.sh
chmod +x get_chrome_driver.sh
chmod +x install_chrome.sh

# Create the direct connect script if it doesn't exist
if [ ! -f "direct_connect.py" ]; then
    echo "Creating direct_connect.py script..."
    cat > direct_connect.py << 'EOL'
from dependencies import *
from login import driver
import config
import time
import random
import sys
import traceback

try:
    # Use companies directly from config
    target_companies = config.companies_list
    print(f"Target companies from config: {', '.join(target_companies)}")
    
    connection_count = 0
    
    # Process each company
    for j in range(len(target_companies)):
        if connection_count > 99:
            print("Reached maximum connection limit (100). Stopping to prevent LinkedIn restrictions.")
            break
            
        company_name = target_companies[j]
        print(f"\nProcessing company {j+1}/{len(target_companies)}: {company_name}")
        
        try:
            # Search for the company - use proper URL encoding
            search_url = f"https://www.linkedin.com/search/results/companies/?keywords={company_name.replace(' ', '%20')}&origin=GLOBAL_SEARCH_HEADER"
            print(f"Searching URL: {search_url}")
            driver.get(search_url)
            time.sleep(random.uniform(3, 5))  # Random wait to avoid detection
            
            # Check if we're on the login page (session might have expired)
            if "login" in driver.current_url or "Sign in" in driver.title:
                print("LinkedIn session expired. Please run login.py again.")
                sys.exit(1)
                
            src = driver.page_source
            parser = soup(src, "html.parser")
            
            # Find company results with updated selectors
            company_selectors = [
                "li.reusable-search__result-container", 
                "li.search-result",
                ".entity-result__item",
                ".search-results__result-item",
                "li.artdeco-list__item"
            ]
            
            company_results = []
            for selector in company_selectors:
                company_results = parser.select(selector)
                if company_results:
                    print(f"Found {len(company_results)} company results using selector: {selector}")
                    break
            
            if company_results:
                # Find company link - try various selectors
                company_link = None
                
                # Try to find the company link directly from search results
                for result in company_results[:1]:  # Only try with the first result
                    # Try all links in the search result
                    link_elements = result.find_all("a", href=True)
                    for link in link_elements:
                        href = link.get('href', '')
                        if '/company/' in href:
                            company_link = href
                            print(f"Found company link: {company_link}")
                            break
                    
                    # If found, break out
                    if company_link:
                        break
                        
                # If link not found from selectors, try direct search in the HTML
                if not company_link:
                    all_links = parser.find_all("a", href=True)
                    for link in all_links:
                        href = link.get('href', '')
                        if '/company/' in href:
                            company_link = href
                            print(f"Found company link from general search: {company_link}")
                            break
                
                if not company_link:
                    print(f"Could not find company link for: {company_name}")
                    continue
                    
                # Make sure link is a full URL
                if not company_link.startswith('http'):
                    if company_link.startswith('/'):
                        company_link = f"https://www.linkedin.com{company_link}"
                    else:
                        company_link = f"https://www.linkedin.com/{company_link}"
                
                # Navigate to company people page
                people_url = company_link
                if not people_url.endswith('/people/'):
                    people_url = people_url.rstrip('/') + '/people/'
                
                print(f"Visiting company people page: {people_url}")
                driver.get(people_url)
                time.sleep(random.uniform(5, 8))  # Allow page to load
                
                # Scroll down to load more profiles
                for scroll in range(3):
                    driver.execute_script("window.scrollBy(0, 700);")
                    time.sleep(random.uniform(1, 2))
                
                # Find employee profiles with updated selectors
                employee_containers = []
                
                # Try multiple selectors for employee containers
                selectors = [
                    "li.org-people-profile-card",
                    "div.org-people-profile-card",
                    "li.artdeco-list__item",
                    ".org-people-profile-card"
                ]
                
                for selector in selectors:
                    try:
                        employee_containers = driver.find_elements(By.CSS_SELECTOR, selector)
                        if employee_containers:
                            print(f"Found {len(employee_containers)} employee profiles using selector: {selector}")
                            break
                    except Exception as e:
                        print(f"Error finding employees with selector {selector}: {e}")
                
                if not employee_containers:
                    print(f"No employee profiles found for: {company_name}")
                    continue
                    
                # Process up to 5 employee profiles to avoid excessive connections
                for i, container in enumerate(employee_containers[:5]):
                    if connection_count >= 99:
                        print("Reached maximum connection limit. Stopping.")
                        break
                        
                    try:
                        # Scroll to the profile
                        driver.execute_script("arguments[0].scrollIntoView();", container)
                        time.sleep(random.uniform(1, 2))
                        
                        # Try to find the connect button with different selectors
                        connect_button = None
                        connect_selectors = [
                            "button.artdeco-button--secondary",
                            "button.artdeco-button--2",
                            "button.org-people-profile-card__profile-action",
                            "button[data-control-name='connect']"
                        ]
                        
                        for selector in connect_selectors:
                            try:
                                buttons = container.find_elements(By.CSS_SELECTOR, selector)
                                for button in buttons:
                                    if "Connect" in button.text:
                                        connect_button = button
                                        break
                            except:
                                continue
                                
                            if connect_button:
                                break
                        
                        if not connect_button:
                            print("No connect button found for this profile, skipping")
                            continue
                            
                        # Click connect button
                        print("Clicking connect button...")
                        try:
                            connect_button.click()
                        except:
                            # Try JavaScript click if normal click fails
                            driver.execute_script("arguments[0].click();", connect_button)
                            
                        time.sleep(random.uniform(2, 3))
                        
                        # Try to find and click "Add a note" button
                        add_note_button = None
                        buttons = driver.find_elements(By.TAG_NAME, "button")
                        
                        # First try to find by text content
                        for button in buttons:
                            try:
                                if "Add a note" in button.text or "add a note" in button.text.lower():
                                    add_note_button = button
                                    print("Found 'Add a note' button by text content")
                                    break
                            except:
                                continue
                        
                        # If not found by text, try selectors
                        if not add_note_button:
                            add_note_selectors = [
                                "button.artdeco-button--secondary:not(.artdeco-modal__confirm-dialog-btn)",
                                "button.artdeco-button--muted",
                                "button.artdeco-modal__dismiss",
                                "button[aria-label='Add a note']",
                                "button[data-control-name='personalize_connection']"
                            ]
                            
                            for selector in add_note_selectors:
                                try:
                                    note_buttons = driver.find_elements(By.CSS_SELECTOR, selector)
                                    for button in note_buttons:
                                        if button.is_displayed():
                                            add_note_button = button
                                            print(f"Found 'Add a note' button with selector: {selector}")
                                            break
                                except:
                                    continue
                                
                                if add_note_button:
                                    break
                        
                        # Process the connection - with or without note
                        if add_note_button:
                            print("Adding a personalized note...")
                            
                            # Click the "Add a note" button
                            try:
                                add_note_button.click()
                            except:
                                # Try JavaScript click if normal click fails
                                driver.execute_script("arguments[0].click();", add_note_button)
                                
                            time.sleep(random.uniform(2, 3))
                            
                            # Find text area for personalized message
                            message_box = None
                            message_selectors = [
                                "textarea.ember-text-area",
                                "textarea[name='message']",
                                "textarea.send-invite__custom-message",
                                "textarea#custom-message",
                                "textarea.artdeco-text-input--input"
                            ]
                            
                            for selector in message_selectors:
                                try:
                                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                                    for element in elements:
                                        if element.is_displayed():
                                            message_box = element
                                            print(f"Found message textarea with selector: {selector}")
                                            break
                                except:
                                    continue
                                
                                if message_box:
                                    break
                            
                            if message_box:
                                # Get person name if possible
                                person_name = None
                                try:
                                    name_selectors = [
                                        ".org-people-profile-card__profile-title",
                                        ".artdeco-entity-lockup__title"
                                    ]
                                    
                                    for selector in name_selectors:
                                        try:
                                            name_element = container.find_element(By.CSS_SELECTOR, selector)
                                            if name_element:
                                                person_name = name_element.text.split()[0]
                                                print(f"Found person name: {person_name}")
                                                break
                                        except:
                                            continue
                                except Exception as e:
                                    print(f"Could not get person name: {e}")
                                
                                # Prepare personalized message
                                if person_name:
                                    personalized_message = f"Hi {person_name},\n\n" + config.message
                                else:
                                    personalized_message = config.message
                                
                                # Type the message
                                try:
                                    message_box.clear()
                                    message_box.send_keys(personalized_message)
                                    print("Added personalized message")
                                except:
                                    # Try JavaScript if normal typing fails
                                    try:
                                        driver.execute_script("arguments[0].value = arguments[1]", message_box, personalized_message)
                                        print("Added message using JavaScript")
                                    except Exception as e:
                                        print(f"Failed to add message: {e}")
                            
                            # Find and click the send button
                            send_button = None
                            send_selectors = [
                                "button.artdeco-button--primary",
                                "button[aria-label='Send now']",
                                "button.ml1[type='submit']"
                            ]
                            
                            for selector in send_selectors:
                                try:
                                    buttons = driver.find_elements(By.CSS_SELECTOR, selector)
                                    for button in buttons:
                                        if button.is_displayed() and ("Send" in button.text or "Done" in button.text):
                                            send_button = button
                                            print(f"Found send button with selector: {selector}")
                                            break
                                except:
                                    continue
                                
                                if send_button:
                                    break
                            
                            # If not found by selectors, try to find by text
                            if not send_button:
                                buttons = driver.find_elements(By.TAG_NAME, "button")
                                for button in buttons:
                                    try:
                                        if button.is_displayed() and ("Send" in button.text or "send" in button.text.lower()):
                                            send_button = button
                                            print("Found send button by text content")
                                            break
                                    except:
                                        continue
                            
                            if send_button:
                                try:
                                    send_button.click()
                                    print("Clicked send button")
                                except:
                                    # Try JavaScript click if normal click fails
                                    driver.execute_script("arguments[0].click();", send_button)
                                
                                connection_count += 1
                                print(f"Connection request #{connection_count} sent with personalized note")
                            else:
                                print("Could not find send button")
                        else:
                            # If no "Add a note" button, just send the connection
                            print("No 'Add a note' button found, sending connection without note")
                            
                            # Find and click send button
                            send_button = None
                            send_selectors = [
                                "button.artdeco-button--primary",
                                "button[aria-label='Send now']"
                            ]
                            
                            for selector in send_selectors:
                                try:
                                    buttons = driver.find_elements(By.CSS_SELECTOR, selector)
                                    for button in buttons:
                                        if button.is_displayed():
                                            send_button = button
                                            break
                                except:
                                    continue
                                
                                if send_button:
                                    break
                            
                            if send_button:
                                try:
                                    send_button.click()
                                except:
                                    # Try JavaScript click if normal click fails
                                    driver.execute_script("arguments[0].click();", send_button)
                                
                                connection_count += 1
                                print(f"Connection request #{connection_count} sent (without note)")
                            else:
                                print("Could not find send button")
                        
                        # Add random delay between connection requests
                        delay = random.uniform(5, 8)
                        print(f"Waiting {delay:.1f} seconds before next connection...")
                        time.sleep(delay)
                        
                    except Exception as e:
                        print(f"Error connecting with profile {i+1}: {e}")
                        traceback.print_exc()
                        
                        # Try to dismiss any modal if it's open
                        try:
                            close_buttons = driver.find_elements(By.CSS_SELECTOR, "button.artdeco-modal__dismiss")
                            for button in close_buttons:
                                try:
                                    button.click()
                                except:
                                    pass
                        except:
                            pass
            else:
                print(f"No company results found for: {company_name}")
                
            # Wait between companies to avoid being flagged
            if j < len(target_companies) - 1:
                delay = random.uniform(3, 5)
                print(f"Waiting {delay:.1f} seconds before next company...")
                time.sleep(delay)
                
        except Exception as e:
            print(f"Error processing company {company_name}: {e}")
            traceback.print_exc()

    print(f"\nDirect Connect completed. Sent {connection_count} connection requests.")
    
except Exception as e:
    print(f"Critical error: {e}")
    traceback.print_exc()
    sys.exit(1)
EOL
    echo "✅ Created direct_connect.py script."
fi

echo "====================================="
echo "Starting LinkedIn Direct Connect Process"
echo "====================================="
echo "First, we'll log you into LinkedIn."
echo "Then we'll connect with people at your target companies."
echo

# Run the script
python3 direct_connect.py

echo
echo "====================================="
echo "LinkedIn Direct Connect Process Completed"
echo "====================================="
echo "To run this process again later, just execute: ./script.sh"
