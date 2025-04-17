from dependencies import *
from login import driver
import config
import time
import random
import sys
import traceback

try:
    # Use companies directly from config instead of CSV
    target_companies = config.companies_list
    print(f"Target companies from config: {', '.join(target_companies)}")
    
    connection_count = 0
    connection_limit = 100  # LinkedIn limit to avoid restrictions
    
    # Process each company
    for j, company_name in enumerate(target_companies):
        if connection_count >= connection_limit:
            print(f"Reached maximum connection limit ({connection_limit}). Stopping to prevent LinkedIn restrictions.")
            break
            
        print(f"\nProcessing company {j+1}/{len(target_companies)}: {company_name}")
        
        try:
            # First try direct people search for the company - more effective
            search_url = f"https://www.linkedin.com/search/results/people/?keywords={company_name.replace(' ', '%20')}&origin=GLOBAL_SEARCH_HEADER"
            print(f"Searching for people at company: {search_url}")
            driver.get(search_url)
            time.sleep(random.uniform(3, 5))  # Random wait to avoid detection
            
            # Save screenshot for debugging
            try:
                debug_screenshot = f"people_search_{company_name.replace(' ', '_')}.png"
                driver.save_screenshot(debug_screenshot)
                print(f"Saved people search screenshot to {debug_screenshot}")
            except Exception as e:
                print(f"Could not save screenshot: {e}")
            
            # Check if we're on the login page (session might have expired)
            if "login" in driver.current_url or "Sign in" in driver.title:
                print("LinkedIn session expired. Please run login.py again.")
                sys.exit(1)
            
            # Scroll down to load more profiles
            print("Scrolling to load more profiles...")
            for scroll in range(3):
                driver.execute_script("window.scrollBy(0, 800);")
                time.sleep(random.uniform(1, 2))
            
            # Find people in search results
            people_containers = []
            
            # Try multiple selectors for people containers
            people_selectors = [
                "li.reusable-search__result-container", 
                "li.search-result",
                ".entity-result__item",
                ".search-results__result-item",
                "li.artdeco-list__item"
            ]
            
            for selector in people_selectors:
                try:
                    people_containers = driver.find_elements(By.CSS_SELECTOR, selector)
                    if people_containers:
                        print(f"Found {len(people_containers)} people using selector: {selector}")
                        break
                except Exception as e:
                    print(f"Error finding people with selector {selector}: {e}")
            
            if not people_containers or len(people_containers) < 2:
                print(f"Few or no people found in direct search. Trying company page approach...")
                
                # Try the company search approach as a fallback
                company_search_url = f"https://www.linkedin.com/search/results/companies/?keywords={company_name.replace(' ', '%20')}&origin=GLOBAL_SEARCH_HEADER"
                print(f"Searching for company: {company_search_url}")
                driver.get(company_search_url)
                time.sleep(random.uniform(3, 5))
                
                # Save screenshot for debugging
                try:
                    debug_screenshot = f"company_search_{company_name.replace(' ', '_')}.png"
                    driver.save_screenshot(debug_screenshot)
                    print(f"Saved company search screenshot to {debug_screenshot}")
                except Exception as e:
                    print(f"Could not save screenshot: {e}")
                
                # Save the HTML for debugging
                try:
                    html_path = f"company_search_{company_name.replace(' ', '_')}.html"
                    with open(html_path, "w", encoding="utf-8") as f:
                        f.write(driver.page_source)
                except Exception as e:
                    print(f"Could not save HTML: {e}")
                    
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
                    
                    # Save screenshot of people page
                    try:
                        people_screenshot = f"company_people_{company_name.replace(' ', '_')}.png"
                        driver.save_screenshot(people_screenshot)
                        print(f"Saved people page screenshot to {people_screenshot}")
                    except Exception as e:
                        print(f"Could not save people screenshot: {e}")
                    
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
                        
                    # Use employee containers from company page
                    people_containers = employee_containers
                else:
                    print(f"No company results found for: {company_name}")
                    continue
            
            # Process profiles (up to 10 to increase chances of successful connections)
            print(f"Processing up to 10 profiles for {company_name}...")
            processed_profiles = 0
            for i, container in enumerate(people_containers[:10]):
                if connection_count >= connection_limit:
                    print(f"Reached maximum connection limit ({connection_limit}). Stopping.")
                    break
                    
                try:
                    # Scroll to the profile
                    driver.execute_script("arguments[0].scrollIntoView();", container)
                    time.sleep(random.uniform(1, 2))
                    
                    # Try to find the connect button with different selectors
                    connect_button = None
                    
                    # First try to find by text content
                    buttons = container.find_elements(By.TAG_NAME, "button")
                    for button in buttons:
                        try:
                            if "Connect" in button.text:
                                connect_button = button
                                print("Found connect button by text content")
                                break
                        except:
                            continue
                    
                    # If not found by text, try selectors
                    if not connect_button:
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
                                        print(f"Found connect button with selector: {selector}")
                                        break
                            except:
                                continue
                                
                            if connect_button:
                                break
                    
                    # Check for LinkedIn Premium profile - try to find the Message button
                    if not connect_button:
                        message_selectors = [
                            "button.message-anywhere-button",
                            "button.artdeco-button[aria-label='Message']",
                            "button.artdeco-button--primary"
                        ]
                        
                        for selector in message_selectors:
                            try:
                                buttons = container.find_elements(By.CSS_SELECTOR, selector)
                                for button in buttons:
                                    if "Message" in button.text or "message" in button.text.lower():
                                        print("Found Premium profile with Message button - sending a message instead of connection")
                                        # Click message button
                                        try:
                                            button.click()
                                            print("Clicked Message button")
                                            time.sleep(random.uniform(2, 3))
                                            
                                            # Get person name if possible
                                            person_name = None
                                            try:
                                                name_selectors = [
                                                    ".org-people-profile-card__profile-title",
                                                    ".artdeco-entity-lockup__title",
                                                    ".entity-result__title-text a",
                                                    ".app-aware-link"
                                                ]
                                                
                                                for name_selector in name_selectors:
                                                    try:
                                                        name_elements = container.find_elements(By.CSS_SELECTOR, name_selector)
                                                        for element in name_elements:
                                                            if element.text.strip():
                                                                person_name = element.text.split()[0]
                                                                print(f"Found person name: {person_name}")
                                                                break
                                                    except:
                                                        continue
                                                    
                                                    if person_name:
                                                        break
                                            except Exception as e:
                                                print(f"Could not get person name: {e}")
                                            
                                            # Prepare personalized message
                                            if person_name:
                                                personalized_message = f"Hi {person_name},\n\n" + config.message
                                            else:
                                                personalized_message = config.message
                                            
                                            # Find message field
                                            message_field = None
                                            message_field_selectors = [
                                                "div.msg-form__contenteditable",
                                                "div[role='textbox']",
                                                ".msg-form__message-texteditor"
                                            ]
                                            
                                            for field_selector in message_field_selectors:
                                                try:
                                                    fields = driver.find_elements(By.CSS_SELECTOR, field_selector)
                                                    for field in fields:
                                                        if field.is_displayed():
                                                            message_field = field
                                                            print(f"Found message field with selector: {field_selector}")
                                                            break
                                                except:
                                                    continue
                                                
                                                if message_field:
                                                    break
                                            
                                            if message_field:
                                                # Type the message
                                                try:
                                                    message_field.clear()
                                                    message_field.send_keys(personalized_message)
                                                    print("Added personalized message")
                                                    time.sleep(random.uniform(1, 2))
                                                    
                                                    # Find and click send button
                                                    send_button = None
                                                    msg_send_selectors = [
                                                        "button.msg-form__send-button",
                                                        "button[type='submit']"
                                                    ]
                                                    
                                                    for send_selector in msg_send_selectors:
                                                        try:
                                                            send_buttons = driver.find_elements(By.CSS_SELECTOR, send_selector)
                                                            for send_btn in send_buttons:
                                                                if send_btn.is_displayed():
                                                                    send_button = send_btn
                                                                    print(f"Found message send button with selector: {send_selector}")
                                                                    break
                                                        except:
                                                            continue
                                                        
                                                        if send_button:
                                                            break
                                                    
                                                    if send_button:
                                                        try:
                                                            send_button.click()
                                                            print("Clicked send message button")
                                                            connection_count += 1
                                                            print(f"Message #{connection_count} sent to premium profile")
                                                            
                                                            # Close message dialog
                                                            time.sleep(random.uniform(1, 2))
                                                            close_buttons = driver.find_elements(By.CSS_SELECTOR, "button.msg-overlay-bubble-header__control--close-btn")
                                                            if close_buttons:
                                                                close_buttons[0].click()
                                                            
                                                            processed_profiles += 1
                                                            # Add random delay between profiles
                                                            delay = random.uniform(5, 8)
                                                            print(f"Waiting {delay:.1f} seconds before next profile...")
                                                            time.sleep(delay)
                                                            continue
                                                        except Exception as e:
                                                            print(f"Error clicking send message button: {e}")
                                                except Exception as e:
                                                    print(f"Error typing or sending message: {e}")
                                            else:
                                                print("Could not find message text field")
                                            
                                            # Close message dialog if we couldn't send the message
                                            close_buttons = driver.find_elements(By.CSS_SELECTOR, "button.msg-overlay-bubble-header__control--close-btn")
                                            if close_buttons:
                                                close_buttons[0].click()
                                                
                                        except Exception as e:
                                            print(f"Error handling premium profile: {e}")
                                        
                                        # Skip to next profile since we already tried to message this one
                                        connect_button = None  # Set to None to skip regular connect flow
                                        break
                            except:
                                continue
                            
                            if connect_button is None:  # Set to None if we handled a premium profile
                                break
                    
                    if not connect_button:
                        print("No connect button found for this profile, skipping")
                        continue
                        
                    # Click connect button
                    print("Clicking connect button...")
                    try:
                        connect_button.click()
                        print("Connect button clicked successfully")
                    except:
                        try:
                            # Try JavaScript click if normal click fails
                            driver.execute_script("arguments[0].click();", connect_button)
                            print("Connect button clicked with JavaScript")
                        except Exception as e:
                            print(f"Failed to click Connect button: {e}")
                            continue  # Skip this profile if we can't click the button
                        
                    time.sleep(random.uniform(2, 3))
                    
                    # Take screenshot after clicking connect
                    try:
                        driver.save_screenshot(f"connect_clicked_{company_name}_{i}.png")
                    except:
                        pass
                    
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
                        
                        # Take screenshot before clicking add note
                        try:
                            driver.save_screenshot(f"before_add_note_{company_name}_{i}.png")
                        except:
                            pass
                            
                        # Click the "Add a note" button
                        try:
                            add_note_button.click()
                            print("Add note button clicked successfully")
                        except:
                            try:
                                # Try JavaScript click if normal click fails
                                driver.execute_script("arguments[0].click();", add_note_button)
                                print("Add note button clicked with JavaScript")
                            except Exception as e:
                                print(f"Failed to click Add note button: {e}")
                                # Try continuing with connection without note
                            
                        time.sleep(random.uniform(2, 3))
                        
                        # Take screenshot after clicking add note
                        try:
                            driver.save_screenshot(f"after_add_note_{company_name}_{i}.png")
                        except:
                            pass
                        
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
                                    ".artdeco-entity-lockup__title",
                                    ".entity-result__title-text a",
                                    ".app-aware-link"
                                ]
                                
                                for selector in name_selectors:
                                    try:
                                        name_elements = container.find_elements(By.CSS_SELECTOR, selector)
                                        for element in name_elements:
                                            if element.text.strip():
                                                person_name = element.text.split()[0]
                                                print(f"Found person name: {person_name}")
                                                break
                                    except:
                                        continue
                                    
                                    if person_name:
                                        break
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
                            
                            # Take screenshot with message added
                            try:
                                driver.save_screenshot(f"message_added_{company_name}_{i}.png")
                            except:
                                pass
                        else:
                            print("Could not find message textarea")
                        
                        # Find and click the send button
                        send_button = None
                        send_selectors = [
                            "button.artdeco-button--primary",
                            "button[aria-label='Send now']",
                            "button.ml1[type='submit']",
                            "button.artdeco-button--3"
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
                                # Take screenshot before clicking
                                try:
                                    driver.save_screenshot(f"before_send_{company_name}_{i}.png")
                                except:
                                    pass
                                    
                                send_button.click()
                                print("Clicked send button successfully")
                            except:
                                try:
                                    # Try JavaScript click if normal click fails
                                    driver.execute_script("arguments[0].click();", send_button)
                                    print("Clicked send button with JavaScript")
                                except Exception as e:
                                    print(f"Failed to click Send button: {e}")
                                    continue
                            
                            # Take screenshot after clicking
                            try:
                                driver.save_screenshot(f"after_send_{company_name}_{i}.png")
                            except:
                                pass
                                
                            connection_count += 1
                            processed_profiles += 1
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
                            "button[aria-label='Send now']",
                            "button.ml1[type='submit']"
                        ]
                        
                        for selector in send_selectors:
                            try:
                                buttons = driver.find_elements(By.CSS_SELECTOR, selector)
                                for button in buttons:
                                    if button.is_displayed() and ("Send" in button.text or "Connect" in button.text):
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
                                    if button.is_displayed() and ("Send" in button.text or "Connect" in button.text):
                                        send_button = button
                                        print("Found send button by text content")
                                        break
                                except:
                                    continue
                        
                        if send_button:
                            try:
                                send_button.click()
                                print("Clicked send button (without note) successfully")
                            except:
                                try:
                                    # Try JavaScript click if normal click fails
                                    driver.execute_script("arguments[0].click();", send_button)
                                    print("Clicked send button with JavaScript")
                                except Exception as e:
                                    print(f"Failed to click Send button: {e}")
                                    continue
                            
                            connection_count += 1
                            processed_profiles += 1
                            print(f"Connection request #{connection_count} sent (without note)")
                        else:
                            print("Could not find send button")
                    
                    # Add random delay between connection requests
                    delay = random.uniform(5, 8)
                    print(f"Waiting {delay:.1f} seconds before next profile...")
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
            
            print(f"Processed {processed_profiles} profiles for company: {company_name}")
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
