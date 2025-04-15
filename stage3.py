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
    
    # Process each company
    for j in range(len(target_companies)):
        if connection_count > 99:
            print("Reached maximum connection limit (100). Stopping to prevent LinkedIn restrictions.")
            break
            
        company_name = target_companies[j]
        print(f"\nProcessing company {j+1}/{len(target_companies)}: {company_name}")
        
        # Save a screenshot of search results for debugging
        debug_screenshot = f"company_search_{company_name.replace(' ', '_')}.png"
        
        try:
            # Search for the company - use proper URL encoding
            search_url = f"https://www.linkedin.com/search/results/companies/?keywords={company_name.replace(' ', '%20')}&origin=GLOBAL_SEARCH_HEADER"
            print(f"Searching URL: {search_url}")
            driver.get(search_url)
            time.sleep(random.uniform(3, 5))  # Random wait to avoid detection
            
            # Save screenshot for debugging
            try:
                driver.save_screenshot(debug_screenshot)
                print(f"Saved search results screenshot to {debug_screenshot}")
            except Exception as e:
                print(f"Could not save screenshot: {e}")
            
            # Check if we're on the login page (session might have expired)
            if "login" in driver.current_url or "Sign in" in driver.title:
                print("LinkedIn session expired. Please run login.py again.")
                sys.exit(1)
                
            # Save the HTML for debugging
            html_path = f"company_search_{company_name.replace(' ', '_')}.html"
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(driver.page_source)
                
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
                            
                            # Try to find "Add note" button
                            add_note_button = None
                            try:
                                # Try a more comprehensive set of selectors for the "Add a note" button
                                add_note_selectors = [
                                    "button.artdeco-button--secondary:not(.artdeco-modal__confirm-dialog-btn)",
                                    "button.artdeco-button--muted",
                                    "button.artdeco-modal__dismiss",
                                    "button[aria-label='Add a note']",
                                    "button.artdeco-button[aria-label='Add a note']",
                                    "button[data-control-name='personalize_connection']"
                                ]
                                
                                # First try to find by text content
                                buttons = driver.find_elements(By.TAG_NAME, "button")
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
                                    for selector in add_note_selectors:
                                        try:
                                            buttons = driver.find_elements(By.CSS_SELECTOR, selector)
                                            for button in buttons:
                                                if button.is_displayed():
                                                    add_note_button = button
                                                    print(f"Found 'Add a note' button with selector: {selector}")
                                                    break
                                        except:
                                            continue
                                        
                                        if add_note_button:
                                            break
                                
                                if add_note_button:
                                    print("Adding a personalized note...")
                                    try:
                                        # Take screenshot before clicking to help with debugging
                                        driver.save_screenshot(f"before_add_note_{company_name}_{i}.png")
                                        
                                        # Try clicking the button
                                        try:
                                            add_note_button.click()
                                            print("Clicked 'Add a note' button")
                                        except:
                                            # Try JavaScript click if normal click fails
                                            driver.execute_script("arguments[0].click();", add_note_button)
                                            print("Clicked 'Add a note' button using JavaScript")
                                            
                                        time.sleep(random.uniform(2, 3))  # Give more time for modal to appear
                                        
                                        # Take screenshot after clicking
                                        driver.save_screenshot(f"after_add_note_{company_name}_{i}.png")
                                        
                                        # Find text area for personalized message
                                        message_selectors = [
                                            "textarea.ember-text-area",
                                            "textarea[name='message']",
                                            "textarea.send-invite__custom-message",
                                            "textarea#custom-message",
                                            "textarea.artdeco-text-input--input"
                                        ]
                                        
                                        message_box = None
                                        for msg_selector in message_selectors:
                                            try:
                                                message_elements = driver.find_elements(By.CSS_SELECTOR, msg_selector)
                                                for element in message_elements:
                                                    if element.is_displayed():
                                                        message_box = element
                                                        print(f"Found message textarea with selector: {msg_selector}")
                                                        break
                                            except:
                                                continue
                                            
                                            if message_box:
                                                break
                                        
                                        if not message_box:
                                            print("Could not find message textarea, continuing without note")
                                            # Take a screenshot to help diagnose the issue
                                            driver.save_screenshot(f"no_message_box_{company_name}_{i}.png")
                                            
                                            # Try to find and click the send button
                                            send_button = None
                                            send_selectors = [
                                                "button.artdeco-button--primary",
                                                "button[aria-label='Send now']"
                                            ]
                                            
                                            for selector in send_selectors:
                                                try:
                                                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                                                    for element in elements:
                                                        if element.is_displayed():
                                                            send_button = element
                                                            break
                                                except:
                                                    continue
                                                    
                                                if send_button:
                                                    break
                                            
                                            if send_button:
                                                send_button.click()
                                                print("Clicked send button without note")
                                            else:
                                                print("Could not find send button after add note")
                                        else:
                                            # Get person name if possible
                                            try:
                                                person_name_selectors = [
                                                    ".org-people-profile-card__profile-title",
                                                    ".artdeco-entity-lockup__title",
                                                    ".artdeco-entity-lockup__title span"
                                                ]
                                                
                                                person_name = None
                                                for name_selector in person_name_selectors:
                                                    try:
                                                        name_element = container.find_element(By.CSS_SELECTOR, name_selector)
                                                        if name_element:
                                                            person_name = name_element.text.split()[0]
                                                            print(f"Found person name: {person_name}")
                                                            break
                                                    except:
                                                        continue
                                                
                                                if person_name:
                                                    personalized_message = f"Hi {person_name},\n\n" + config.message
                                                else:
                                                    personalized_message = config.message
                                                    
                                            except Exception as e:
                                                print(f"Could not get person name: {e}")
                                                personalized_message = config.message
                                                
                                            # Type the message
                                            try:
                                                message_box.clear()
                                                message_box.send_keys(personalized_message)
                                                print("Added personalized message to textarea")
                                                time.sleep(random.uniform(1, 2))
                                            except Exception as e:
                                                print(f"Error typing message: {e}")
                                                    
                                                # Try again with JavaScript
                                                try:
                                                    driver.execute_script("arguments[0].value = arguments[1]", message_box, personalized_message)
                                                    print("Added message using JavaScript")
                                                except Exception as e:
                                                    print(f"Failed to add message with JavaScript: {e}")
                                            
                                            # Take screenshot with message added
                                            driver.save_screenshot(f"message_added_{company_name}_{i}.png")
                                            
                                            # Click send button
                                            send_selectors = [
                                                "button.artdeco-button--primary",
                                                "button[aria-label='Send now']",
                                                "button.ml1[type='submit']",
                                                "button.artdeco-button--3"
                                            ]
                                            
                                            send_button = None
                                            for send_selector in send_selectors:
                                                try:
                                                    send_buttons = driver.find_elements(By.CSS_SELECTOR, send_selector)
                                                    for button in send_buttons:
                                                        if button.is_displayed() and ("Send" in button.text or "send" in button.text.lower() or "Done" in button.text):
                                                            send_button = button
                                                            print(f"Found send button with selector: {send_selector}")
                                                            break
                                                except:
                                                    continue
                                                    
                                                if send_button:
                                                    break
                                            
                                            if not send_button:
                                                # Try finding any button that might be the send button
                                                buttons = driver.find_elements(By.TAG_NAME, "button")
                                                for button in buttons:
                                                    try:
                                                        if button.is_displayed() and ("Send" in button.text or "send" in button.text.lower() or "Done" in button.text):
                                                            send_button = button
                                                            print("Found send button by text content")
                                                            break
                                                    except:
                                                        continue
                                            
                                            if send_button:
                                                try:
                                                    send_button.click()
                                                    print("Clicked send button after adding note")
                                                except:
                                                    # Try JavaScript click if normal click fails
                                                    try:
                                                        driver.execute_script("arguments[0].click();", send_button)
                                                        print("Clicked send button with JavaScript")
                                                    except Exception as e:
                                                        print(f"Failed to click send button: {e}")
                                                
                                                connection_count += 1
                                                print(f"Connection request #{connection_count} sent successfully with note")
                                            else:
                                                print("Could not find send button")
                                            
                                    except Exception as e:
                                        print(f"Error adding note: {e}")
                                        traceback.print_exc()
                                        
                                        # Try to dismiss the modal if it's still open
                                        try:
                                            close_buttons = driver.find_elements(By.CSS_SELECTOR, "button.artdeco-modal__dismiss")
                                            for button in close_buttons:
                                                button.click()
                                                time.sleep(1)
                                        except:
                                            pass
                            else:
                                # If no "Add note" button, just send connection
                                print("No 'Add note' button found, sending connection without note")
                                
                                send_selectors = [
                                    "button.artdeco-button--primary",
                                    "button[aria-label='Send now']",
                                    "button.ml1[type='submit']"
                                ]
                                
                                send_button = None
                                for send_selector in send_selectors:
                                    try:
                                        send_buttons = driver.find_elements(By.CSS_SELECTOR, send_selector)
                                        for button in send_buttons:
                                            if button.is_displayed() and ("Send" in button.text or "send" in button.text.lower() or "Connect" in button.text):
                                                send_button = button
                                                break
                                    except:
                                        continue
                                    
                                    if send_button:
                                        break
                                
                                if not send_button:
                                    # Try finding any button that might be the send button
                                    buttons = driver.find_elements(By.TAG_NAME, "button")
                                    for button in buttons:
                                        try:
                                            if button.is_displayed() and ("Send" in button.text or "send" in button.text.lower() or "Connect" in button.text):
                                                send_button = button
                                                break
                                        except:
                                            continue
                                
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
                            print(f"Error with connection flow: {e}")
                            traceback.print_exc()
                            
                            # Try to dismiss any modal if it's open
                            try:
                                close_buttons = driver.find_elements(By.CSS_SELECTOR, "button.artdeco-modal__dismiss")
                                for button in close_buttons:
                                    button.click()
                                    time.sleep(1)
                            except:
                                pass
                    except Exception as e:
                        print(f"Error connecting with profile {i+1}: {e}")
                        traceback.print_exc()
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

