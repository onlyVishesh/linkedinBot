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
        
        try:
            # Instead of searching, go directly to the company page
            # Format: https://www.linkedin.com/company/amazon/
            company_url = f"https://www.linkedin.com/company/{company_name.lower().replace(' ', '-')}/"
            print(f"Directly visiting company page: {company_url}")
            driver.get(company_url)
            time.sleep(random.uniform(3, 5))  # Random wait to avoid detection
            
            # Save screenshot for debugging
            debug_screenshot = f"company_search_{company_name.replace(' ', '_')}.png"
            try:
                driver.save_screenshot(debug_screenshot)
                print(f"Saved company page screenshot to {debug_screenshot}")
            except Exception as e:
                print(f"Could not save screenshot: {e}")
            
            # Check if we're on the login page (session might have expired)
            if "login" in driver.current_url or "Sign in" in driver.title:
                print("LinkedIn session expired. Please run login.py again.")
                sys.exit(1)
            
            # Check if we landed on the company page
            if "/company/" not in driver.current_url:
                print(f"Could not find company page for {company_name}. Trying search approach...")
                
                # Fall back to search if direct approach fails
                search_url = f"https://www.linkedin.com/search/results/companies/?keywords={company_name.replace(' ', '%20')}&origin=GLOBAL_SEARCH_HEADER"
                print(f"Searching URL: {search_url}")
                driver.get(search_url)
                time.sleep(random.uniform(3, 5))
                
                # Save screenshot for debugging
                try:
                    driver.save_screenshot(f"search_{company_name}.png")
                    print(f"Saved search results screenshot")
                except Exception as e:
                    print(f"Could not save screenshot: {e}")
                
                # Save the HTML for debugging
                html_path = f"company_search_{company_name.replace(' ', '_')}.html"
                with open(html_path, "w", encoding="utf-8") as f:
                    f.write(driver.page_source)
                print(f"Saved HTML to {html_path}")
                
                # Print the current URL (for debugging)
                print(f"Current URL: {driver.current_url}")
                
                # Try to directly click on the first company result
                try:
                    # Find company search results - try multiple selectors
                    company_link_found = False
                    
                    # Try multiple selectors for the company links
                    company_selectors = [
                        "a.app-aware-link[href*='/company/']",  # App-aware links containing "/company/"
                        "a[href*='/company/']",                  # Any link containing "/company/"
                        ".entity-result__title a",              # Entity result titles
                        ".search-result__info a",               # Search result info links
                        ".search-result__title a"               # Search result title links
                    ]
                    
                    for selector in company_selectors:
                        try:
                            company_links = driver.find_elements(By.CSS_SELECTOR, selector)
                            if company_links:
                                print(f"Found {len(company_links)} company links with selector: {selector}")
                                # Click the first result
                                company_links[0].click()
                                print("Clicked on first company result")
                                company_link_found = True
                                time.sleep(random.uniform(3, 5))
                                break
                        except Exception as e:
                            print(f"Error finding company links with selector {selector}: {e}")
                    
                    if not company_link_found:
                        print("Could not find clickable company links. Trying to extract URLs from page...")
                        
                        # Parse the page source and try to extract company URLs
                        src = driver.page_source
                        parser = soup(src, "html.parser")
                        all_links = parser.find_all("a", href=True)
                        
                        company_links = []
                        for link in all_links:
                            href = link.get('href', '')
                            if '/company/' in href:
                                company_links.append(href)
                        
                        if company_links:
                            print(f"Found {len(company_links)} company links from HTML")
                            # Navigate to the first company link
                            company_url = company_links[0]
                            if not company_url.startswith('http'):
                                if company_url.startswith('/'):
                                    company_url = f"https://www.linkedin.com{company_url}"
                                else:
                                    company_url = f"https://www.linkedin.com/{company_url}"
                            
                            print(f"Navigating to company URL: {company_url}")
                            driver.get(company_url)
                            time.sleep(random.uniform(3, 5))
                        else:
                            print(f"No company links found for {company_name}. Skipping.")
                            continue
                            
                except Exception as e:
                    print(f"Error processing search results: {e}")
                    traceback.print_exc()
                    continue
            
            # At this point, we should be on the company page
            # Navigate to the people/employees page from here
            current_url = driver.current_url
            people_url = current_url.rstrip("/") + "/people/"
            
            print(f"Navigating to company people page: {people_url}")
            driver.get(people_url)
            time.sleep(random.uniform(5, 8))  # Allow page to load
            
            # Save screenshot of people page
            try:
                people_screenshot = f"people_search_{company_name.replace(' ', '_')}.png"
                driver.save_screenshot(people_screenshot)
                print(f"Saved people page screenshot to {people_screenshot}")
            except Exception as e:
                print(f"Could not save people screenshot: {e}")
            
            # Scroll down to load more profiles
            for scroll in range(3):
                driver.execute_script("window.scrollBy(0, 700);")
                time.sleep(random.uniform(1, 2))
            
            # Find employee profiles
            # Try multiple selectors for employee containers - updated for current LinkedIn UI
            employee_containers = []
            selectors = [
                "li.org-people-profile-card",
                "div.org-people-profile-card",
                "li.artdeco-list__item",
                ".org-people-profile-card",
                # Additional selectors that might work on newer LinkedIn UI
                "li.ember-view",
                "div.org-people-profile-card__profile-info"
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
                # Try a more general approach
                print("Trying alternative method to find employee profiles...")
                try:
                    # Find any links that might contain profile URLs
                    profile_links = driver.find_elements(By.XPATH, "//a[contains(@href, '/in/')]")
                    if profile_links:
                        print(f"Found {len(profile_links)} potential profile links")
                        
                        # Process these links directly
                        for i, profile_link in enumerate(profile_links[:5]):  # Process up to 5 profiles
                            if connection_count >= 99:
                                print("Reached maximum connection limit. Stopping.")
                                break
                            
                            try:
                                href = profile_link.get_attribute('href')
                                if href and '/in/' in href:
                                    print(f"Visiting profile: {href}")
                                    driver.get(href)
                                    time.sleep(random.uniform(5, 7))
                                    
                                    # Look for the connect button on the profile page
                                    connect_button = None
                                    connect_selectors = [
                                        "button.artdeco-button--2.artdeco-button--primary",  # Primary connect button
                                        "button.artdeco-button--lite",  # "More" actions button
                                        "button.pvs-profile-actions__action",  # Another possible button
                                        "button.artdeco-button--secondary"  # Secondary actions
                                    ]
                                    
                                    for selector in connect_selectors:
                                        try:
                                            buttons = driver.find_elements(By.CSS_SELECTOR, selector)
                                            for btn in buttons:
                                                if btn.is_displayed() and any(text in btn.text for text in ["Connect", "connect", "CONNECTION", "Connection"]):
                                                    connect_button = btn
                                                    print(f"Found connect button: {btn.text}")
                                                    break
                                        except:
                                            continue
                                            
                                        if connect_button:
                                            break
                                            
                                    # If we found connect button, try to click it and send connection
                                    if connect_button:
                                        # Process connection - click connect button
                                        try:
                                            connect_button.click()
                                            print("Clicked connect button")
                                            time.sleep(random.uniform(2, 3))
                                            
                                            # Look for Add a note option
                                            add_note_button = None
                                            try:
                                                # Check all buttons for "Add a note" text
                                                buttons = driver.find_elements(By.TAG_NAME, "button")
                                                for btn in buttons:
                                                    if btn.is_displayed() and any(text in btn.text for text in ["Add a note", "add a note", "note"]):
                                                        add_note_button = btn
                                                        print(f"Found 'Add a note' button: {btn.text}")
                                                        break
                                                        
                                                # If not found by text, try by attribute
                                                if not add_note_button:
                                                    note_selectors = [
                                                        "button[aria-label='Add a note']",
                                                        "button.artdeco-button--secondary",
                                                        "button.artdeco-button--muted"
                                                    ]
                                                    for selector in note_selectors:
                                                        elements = driver.find_elements(By.CSS_SELECTOR, selector)
                                                        for elem in elements:
                                                            if elem.is_displayed():
                                                                add_note_button = elem
                                                                print(f"Found 'Add a note' button with selector: {selector}")
                                                                break
                                                                
                                                        if add_note_button:
                                                            break
                                                            
                                                if add_note_button:
                                                    # Click add note button
                                                    driver.execute_script("arguments[0].click();", add_note_button)
                                                    print("Clicked 'Add a note' button")
                                                    time.sleep(random.uniform(1, 2))
                                                    
                                                    # Find the message textarea
                                                    message_box = None
                                                    message_selectors = [
                                                        "textarea.ember-text-area",
                                                        "textarea[name='message']",
                                                        "textarea.send-invite__custom-message",
                                                        "textarea.artdeco-text-input--input"
                                                    ]
                                                    
                                                    for selector in message_selectors:
                                                        elements = driver.find_elements(By.CSS_SELECTOR, selector)
                                                        for elem in elements:
                                                            if elem.is_displayed():
                                                                message_box = elem
                                                                print(f"Found message textarea with selector: {selector}")
                                                                break
                                                                
                                                        if message_box:
                                                            break
                                                            
                                                    if message_box:
                                                        # Try to get person's name
                                                        try:
                                                            profile_name = driver.find_element(By.CSS_SELECTOR, "h1.text-heading-xlarge").text.split()[0]
                                                            personalized_message = f"Hi {profile_name},\n\n" + config.message
                                                        except:
                                                            personalized_message = config.message
                                                            
                                                        # Add message
                                                        try:
                                                            message_box.clear()
                                                            message_box.send_keys(personalized_message)
                                                            print("Added personalized message")
                                                        except:
                                                            driver.execute_script("arguments[0].value = arguments[1]", message_box, personalized_message)
                                                            print("Added message using JavaScript")
                                                            
                                                        time.sleep(random.uniform(1, 2))
                                                    else:
                                                        print("Could not find message textarea")
                                                        
                                                    # Find and click the send button
                                                    send_button = None
                                                    send_selectors = [
                                                        "button.artdeco-button--primary",
                                                        "button[aria-label='Send now']",
                                                        "button[type='submit']"
                                                    ]
                                                    
                                                    for selector in send_selectors:
                                                        elements = driver.find_elements(By.CSS_SELECTOR, selector)
                                                        for elem in elements:
                                                            if elem.is_displayed() and any(text in elem.text for text in ["Send", "send", "Done", "done"]):
                                                                send_button = elem
                                                                print(f"Found send button: {elem.text}")
                                                                break
                                                                
                                                        if send_button:
                                                            break
                                                            
                                                    if send_button:
                                                        driver.execute_script("arguments[0].click();", send_button)
                                                        print("Sent connection request with note")
                                                        connection_count += 1
                                                    else:
                                                        print("Could not find send button")
                                                else:
                                                    # If no add note button found, try to find and click the send button directly
                                                    send_button = None
                                                    send_selectors = [
                                                        "button.artdeco-button--primary",
                                                        "button[aria-label='Send now']",
                                                        "button[type='submit']"
                                                    ]
                                                    
                                                    for selector in send_selectors:
                                                        elements = driver.find_elements(By.CSS_SELECTOR, selector)
                                                        for elem in elements:
                                                            if elem.is_displayed() and any(text in elem.text for text in ["Send", "send", "Connect", "connect"]):
                                                                send_button = elem
                                                                print(f"Found send button: {elem.text}")
                                                                break
                                                                
                                                        if send_button:
                                                            break
                                                            
                                                    if send_button:
                                                        driver.execute_script("arguments[0].click();", send_button)
                                                        print("Sent connection request without note")
                                                        connection_count += 1
                                                    else:
                                                        print("Could not find send button")
                                            except Exception as e:
                                                print(f"Error with 'Add a note' flow: {e}")
                                        except Exception as e:
                                            print(f"Error clicking connect button: {e}")
                                            
                                    # Go back to the people page
                                    driver.get(people_url)
                                    time.sleep(random.uniform(3, 5))
                            except Exception as e:
                                print(f"Error processing profile link: {e}")
                                driver.get(people_url)  # Go back to people page on error
                                time.sleep(random.uniform(3, 5))
                        
                        # We processed profiles with the alternative approach
                        continue
                except Exception as e:
                    print(f"Alternative method failed: {e}")
                    
                print(f"No employee profiles found for: {company_name}")
                continue
            
            # Process employee profiles
            print(f"Processing up to 5 employee profiles from {company_name}...")
            for i, container in enumerate(employee_containers[:5]):
                if connection_count >= 99:
                    print("Reached maximum connection limit. Stopping.")
                    break
                    
                try:
                    # Get person's name for personalization
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
                        
                    # Scroll to make the profile visible
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", container)
                    time.sleep(random.uniform(1, 2))
                    
                    # Find connect button - try different selectors
                    connect_button = None
                    connect_selectors = [
                        "button.artdeco-button--secondary",
                        "button.artdeco-button--2",
                        "button.org-people-profile-card__profile-action",
                        "button[data-control-name='connect']",
                        # Additional selectors for newer LinkedIn UI
                        "button.artdeco-button--muted"
                    ]
                    
                    for selector in connect_selectors:
                        try:
                            buttons = container.find_elements(By.CSS_SELECTOR, selector)
                            for button in buttons:
                                if button.is_displayed() and "Connect" in button.text:
                                    connect_button = button
                                    print(f"Found connect button with text: '{button.text}'")
                                    break
                        except:
                            continue
                            
                        if connect_button:
                            break
                            
                    if not connect_button:
                        # If no connect button found in the container, look at all buttons in the page
                        buttons = driver.find_elements(By.TAG_NAME, "button")
                        visible_connect_buttons = []
                        
                        for btn in buttons:
                            try:
                                if btn.is_displayed() and "Connect" in btn.text:
                                    # Check if this button is near the current container
                                    container_rect = container.rect
                                    button_rect = btn.rect
                                    
                                    # Check if button is close to the container vertically
                                    vertical_distance = abs(button_rect['y'] - container_rect['y'])
                                    if vertical_distance < 200:  # Adjust this threshold as needed
                                        visible_connect_buttons.append(btn)
                            except:
                                continue
                        
                        # If we found visible connect buttons near the container, use the first one
                        if visible_connect_buttons:
                            connect_button = visible_connect_buttons[0]
                            print(f"Found connect button near profile: '{connect_button.text}'")
                            
                    if not connect_button:
                        print("No connect button found for this profile, skipping")
                        continue
                        
                    # Click connect button
                    try:
                        driver.execute_script("arguments[0].click();", connect_button)
                        print("Clicked connect button")
                        time.sleep(random.uniform(2, 3))
                    except Exception as e:
                        print(f"Error clicking connect button: {e}")
                        continue
                        
                    # Look for "Add a note" option - updated selectors for newer LinkedIn UI
                    add_note_button = None
                    note_selectors = [
                        "button[aria-label='Add a note']",
                        "button.artdeco-button--secondary",
                        "button.artdeco-button--muted",
                        "button.artdeco-modal__confirm-dialog-btn"
                    ]
                    
                    # First look for buttons containing "Add a note" text
                    buttons = driver.find_elements(By.TAG_NAME, "button")
                    for btn in buttons:
                        try:
                            if btn.is_displayed() and ("Add a note" in btn.text or "add a note" in btn.text.lower()):
                                add_note_button = btn
                                print(f"Found 'Add a note' button by text: '{btn.text}'")
                                break
                        except:
                            continue
                            
                    # If not found by text, try selectors
                    if not add_note_button:
                        for selector in note_selectors:
                            try:
                                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                                for elem in elements:
                                    if elem.is_displayed():
                                        add_note_button = elem
                                        print(f"Found potential 'Add a note' button with selector: {selector}")
                                        break
                            except:
                                continue
                                
                            if add_note_button:
                                break
                                
                    if add_note_button:
                        # Click "Add a note" button
                        try:
                            driver.execute_script("arguments[0].click();", add_note_button)
                            print("Clicked 'Add a note' button")
                            time.sleep(random.uniform(1, 2))
                        except Exception as e:
                            print(f"Error clicking 'Add a note' button: {e}")
                            
                            # Try to find and click send button directly
                            try:
                                send_buttons = driver.find_elements(By.CSS_SELECTOR, "button.artdeco-button--primary")
                                for btn in send_buttons:
                                    if btn.is_displayed() and any(text in btn.text for text in ["Send", "Connect"]):
                                        driver.execute_script("arguments[0].click();", btn)
                                        print("Sent connection request without note")
                                        connection_count += 1
                                        break
                            except:
                                print("Could not send connection request")
                            
                            continue
                            
                        # Find textarea for note
                        textarea = None
                        textarea_selectors = [
                            "textarea.ember-text-area",
                            "textarea[name='message']",
                            "textarea.send-invite__custom-message",
                            "textarea.artdeco-text-input--input"
                        ]
                        
                        for selector in textarea_selectors:
                            try:
                                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                                for elem in elements:
                                    if elem.is_displayed():
                                        textarea = elem
                                        print(f"Found textarea with selector: {selector}")
                                        break
                            except:
                                continue
                                
                            if textarea:
                                break
                                
                        if textarea:
                            # Create personalized message
                            if person_name:
                                personalized_message = f"Hi {person_name},\n\n" + config.message
                            else:
                                personalized_message = config.message
                                
                            # Add personalized message to textarea
                            try:
                                textarea.clear()
                                textarea.send_keys(personalized_message)
                                print("Added personalized message")
                            except:
                                # Try with JavaScript if normal method fails
                                try:
                                    driver.execute_script("arguments[0].value = arguments[1]", textarea, personalized_message)
                                    print("Added message using JavaScript")
                                except Exception as e:
                                    print(f"Failed to add message: {e}")
                                    
                            time.sleep(random.uniform(1, 2))
                            
                            # Find and click send button
                            send_button = None
                            send_selectors = [
                                "button.artdeco-button--primary",
                                "button[aria-label='Send now']",
                                "button[type='submit']"
                            ]
                            
                            for selector in send_selectors:
                                try:
                                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                                    for elem in elements:
                                        if elem.is_displayed() and any(text in elem.text for text in ["Send", "send", "Done", "done"]):
                                            send_button = elem
                                            print(f"Found send button: {elem.text}")
                                            break
                                except:
                                    continue
                                    
                                if send_button:
                                    break
                                    
                            if send_button:
                                try:
                                    driver.execute_script("arguments[0].click();", send_button)
                                    print("Sent connection request with personalized note")
                                    connection_count += 1
                                except Exception as e:
                                    print(f"Error clicking send button: {e}")
                            else:
                                print("Could not find send button")
                        else:
                            print("Could not find textarea for note")
                            
                            # Try to find and click send button directly
                            try:
                                send_buttons = driver.find_elements(By.CSS_SELECTOR, "button.artdeco-button--primary")
                                for btn in send_buttons:
                                    if btn.is_displayed() and any(text in btn.text for text in ["Send", "Connect"]):
                                        driver.execute_script("arguments[0].click();", btn)
                                        print("Sent connection request without note")
                                        connection_count += 1
                                        break
                            except:
                                print("Could not send connection request")
                    else:
                        # If no "Add a note" button, just send connection
                        send_button = None
                        send_selectors = [
                            "button.artdeco-button--primary",
                            "button[aria-label='Send now']",
                            "button[type='submit']"
                        ]
                        
                        for selector in send_selectors:
                            try:
                                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                                for elem in elements:
                                    if elem.is_displayed() and any(text in elem.text for text in ["Send", "send", "Connect", "connect"]):
                                        send_button = elem
                                        print(f"Found send button: {elem.text}")
                                        break
                            except:
                                continue
                                
                            if send_button:
                                break
                                
                        if send_button:
                            try:
                                driver.execute_script("arguments[0].click();", send_button)
                                print("Sent connection request without note")
                                connection_count += 1
                            except Exception as e:
                                print(f"Error clicking send button: {e}")
                        else:
                            print("Could not find send button")
                            
                    # Wait between connection attempts
                    delay = random.uniform(5, 8)
                    print(f"Waiting {delay:.1f} seconds before next connection...")
                    time.sleep(delay)
                    
                    # Try to dismiss any open modal dialogs that might be left over
                    try:
                        dismiss_buttons = driver.find_elements(By.CSS_SELECTOR, "button.artdeco-modal__dismiss")
                        for btn in dismiss_buttons:
                            if btn.is_displayed():
                                driver.execute_script("arguments[0].click();", btn)
                                print("Dismissed modal dialog")
                                time.sleep(1)
                    except:
                        pass
                        
                except Exception as e:
                    print(f"Error with profile {i+1}: {e}")
                    traceback.print_exc()
                    
                    # Try to dismiss any open modal dialogs
                    try:
                        dismiss_buttons = driver.find_elements(By.CSS_SELECTOR, "button.artdeco-modal__dismiss")
                        for btn in dismiss_buttons:
                            if btn.is_displayed():
                                driver.execute_script("arguments[0].click();", btn)
                                print("Dismissed modal dialog after error")
                                time.sleep(1)
                    except:
                        pass
                        
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