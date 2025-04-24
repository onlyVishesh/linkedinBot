from dependencies import *
from login import driver
import config
import time
import random
import sys
import traceback
import pandas as pd
import csv
import re

# Function to load role data from CSV files
def load_role_data():
    try:
        # Load roles data
        roles_df = pd.read_csv("roles_of_person_in_pervious_list.csv")
        people_df = pd.read_csv("names_and_positions.csv")
        
        # Clean up data (remove duplicate entries, etc.)
        roles_df = roles_df.dropna(subset=['Name', 'Company_Name'])
        
        print(f"Loaded {len(roles_df)} role entries and {len(people_df)} people entries")
        return roles_df, people_df
    except Exception as e:
        print(f"Error loading role data: {e}")
        return None, None

# Function to check if a person is in HR
def is_hr_role(job_title):
    if not job_title or job_title == "Not found":
        return False
    
    hr_keywords = [
        "hr", "human resources", "talent", "recruiting", "recruiter", 
        "personnel", "people operations", "hiring", "recruitment",
        "talent acquisition", "staffing", "people", "workforce", 
        "employee experience", "human capital", "talent management",
        "talent specialist", "hiring manager", "recruiting manager",
        "hr business partner", "hrbp", "hr generalist", "hr specialist",
        "talent partner", "people partner", "recruiting coordinator"
    ]
    
    job_title_lower = job_title.lower()
    return any(keyword in job_title_lower for keyword in hr_keywords)

# Function to extract keywords from job description
def extract_keywords_from_job_description(job_description):
    if not job_description or job_description == "Not found":
        return []
        
    # Common tech keywords to look for
    tech_keywords = [
        "javascript", "react", "node", "python", "java", "aws", "cloud", 
        "fullstack", "frontend", "backend", "web", "mobile", "app", 
        "software", "developer", "engineer", "tech", "code", "programming",
        "devops", "ai", "machine learning", "data", "api", "database"
    ]
    
    # Extract keywords that appear in the job description
    job_desc_lower = job_description.lower()
    found_keywords = [keyword for keyword in tech_keywords if keyword in job_desc_lower]
    
    return found_keywords

# Enhanced function to create personalized message based on role, company and job description
def create_personalized_message(person_name, job_title, company_name, job_description=None):
    # Default to first name only
    first_name = person_name.split()[0] if person_name and len(person_name.split()) > 0 else "there"
    
    # Base message template
    base_message = config.message
    
    # Check if the person is in HR - prioritize HR contacts
    if is_hr_role(job_title):
        # Create specialized HR-specific message
        message = f"Hi {first_name}, "
        
        # Core HR message - ensure it's under 200 characters including the personalization
        if company_name and company_name != "Not found":
            company_name_clean = re.sub(r'·.*$', '', company_name).strip()
            if len(company_name_clean) > 20:
                company_name_clean = company_name_clean[:20] + "..."
                
            hr_message = f"As {company_name_clean}'s {job_title}, you might be looking for tech talent. I'm a full-stack developer with 5+ projects and 30% performance gains. Can we connect about matching my skills with your tech openings? Portfolio: onlyvishesh.vercel.app"
        else:
            hr_message = f"As a {job_title}, you might be looking for tech talent. I'm a full-stack developer with 5+ projects and 30% performance improvements. Can we connect about open tech roles at your company? Portfolio: onlyvishesh.vercel.app"
        
        message += hr_message
    else:
        # Non-HR message
        message = f"Hi {first_name}! "
        
        # Extract relevant tech keywords from job description if available
        tech_keywords = extract_keywords_from_job_description(job_description)
        
        # If we have tech keywords, customize message to mention them (limit to 2 keywords max)
        if tech_keywords and len(tech_keywords) > 0:
            tech_str = ", ".join(tech_keywords[:2])
            if "MERN" in base_message and tech_str:
                # Replace generic "MERN expertise" with specific tech keywords
                base_message = base_message.replace("MERN expertise", f"{tech_str} expertise")
        
        # Add the base message
        message += base_message
        
        # Personalize based on company name if available
        if company_name and company_name != "Not found":
            # Extract just the company name without extras
            company_name_clean = re.sub(r'·.*$', '', company_name).strip()
            
            # If company name is too long, use shortened version
            if len(company_name_clean) > 30:
                company_name_clean = company_name_clean[:30] + "..."
                
            # Replace "your company" with actual company name
            message = message.replace("your company", company_name_clean)
    
    # Make sure the message is under 200 characters
    if len(message) > 200:
        message = message[:197] + "..."
        
    return message

# Function to prioritize HR profiles when processing a list of employee profiles
def prioritize_hr_profiles(employee_containers, driver):
    """
    Sorts the employee profiles to prioritize HR professionals.
    Returns a sorted list with HR profiles first.
    """
    prioritized_profiles = []
    non_hr_profiles = []
    
    print("Analyzing profiles to identify and prioritize HR professionals...")
    
    for container in employee_containers:
        # Get the job title from the container
        try:
            job_title_selectors = [
                ".org-people-profile-card__profile-position",
                ".artdeco-entity-lockup__subtitle",
                ".artdeco-entity-lockup__caption"
            ]
            
            job_title = None
            for selector in job_title_selectors:
                try:
                    title_element = container.find_element(By.CSS_SELECTOR, selector)
                    if title_element and title_element.text.strip():
                        job_title = title_element.text.strip()
                        break
                except:
                    continue
            
            # If we found a job title, check if it's an HR role
            if job_title and is_hr_role(job_title):
                print(f"Found HR profile with title: {job_title}")
                prioritized_profiles.append((container, True))  # True indicates HR role
            else:
                non_hr_profiles.append((container, False))  # False indicates non-HR role
                
        except Exception as e:
            print(f"Error analyzing profile for HR role: {e}")
            non_hr_profiles.append((container, False))
    
    # Combine lists with HR profiles first
    sorted_profiles = prioritized_profiles + non_hr_profiles
    
    print(f"Prioritized {len(prioritized_profiles)} HR profiles out of {len(sorted_profiles)} total profiles")
    return sorted_profiles

try:
    # Load role data
    roles_df, people_df = load_role_data()
    
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
                                                            profile_name = driver.find_element(By.CSS_SELECTOR, "h1.text-heading-xlarge").text
                                                        except:
                                                            profile_name = None
                                                            
                                                        # Get profile URL to identify the person
                                                        try:
                                                            profile_url = driver.current_url.split('?')[0]
                                                        except:
                                                            profile_url = None
                                                            
                                                        # Try to get current position
                                                        try:
                                                            profile_position = driver.find_element(By.CSS_SELECTOR, ".text-body-medium.break-words").text
                                                        except:
                                                            profile_position = None
                                                            
                                                        # Try to get company information from the page
                                                        try:
                                                            company_info = driver.find_element(By.CSS_SELECTOR, ".inline-show-more-text.inline-show-more-text--is-collapsed").text
                                                        except:
                                                            company_info = company_name
                                                            
                                                        # Look up additional data from our CSV files
                                                        additional_info = None
                                                        job_desc = None
                                                        
                                                        if roles_df is not None and profile_name:
                                                            # Find matching entries in our roles database
                                                            matching_roles = roles_df[roles_df['Name'].str.contains(profile_name.split()[0], case=False, na=False)]
                                                            
                                                            if not matching_roles.empty:
                                                                # Get first match
                                                                first_match = matching_roles.iloc[0]
                                                                additional_info = first_match.get('Company_Name')
                                                                job_desc = first_match.get('Information')
                                                                
                                                                # Print what we found
                                                                print(f"Found additional info for {profile_name}: {additional_info}")
                                                        
                                                        # Create personalized message based on all collected info
                                                        personalized_message = create_personalized_message(
                                                            profile_name, 
                                                            profile_position, 
                                                            company_info if company_info else additional_info,
                                                            job_desc
                                                        )
                                                        
                                                        # Log priority for HR professionals
                                                        if profile_position and is_hr_role(profile_position):
                                                            print(f"Prioritizing message to HR professional: {profile_position}")
                                                        
                                                        # Add personalized message to textarea
                                                        try:
                                                            textarea = message_box
                                                            textarea.clear()
                                                            textarea.send_keys(personalized_message)
                                                            print(f"Added personalized message: {personalized_message}")
                                                        except:
                                                            # Try with JavaScript if normal method fails
                                                            try:
                                                                driver.execute_script("arguments[0].value = arguments[1]", textarea, personalized_message)
                                                                print("Added message using JavaScript")
                                                            except Exception as e:
                                                                print(f"Failed to add message: {e}")
                                                            
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
                                                        print("Sent connection request with personalized note")
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
            print(f"Processing employee profiles from {company_name}...")

            # Prioritize HR profiles in the list
            prioritized_profiles = prioritize_hr_profiles(employee_containers, driver)

            # Process prioritized profiles - process more profiles (up to 10) instead of just 5
            for i, (container, is_hr) in enumerate(prioritized_profiles[:10]):
                if connection_count >= 99:
                    print("Reached maximum connection limit. Stopping.")
                    break
                    
                try:
                    # Print whether this is an HR profile
                    if is_hr:
                        print(f"Processing HR profile {i+1}/{len(prioritized_profiles[:10])}")
                    else:
                        print(f"Processing non-HR profile {i+1}/{len(prioritized_profiles[:10])}")
                    
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
                                    person_name = name_element.text
                                    print(f"Found person name: {person_name}")
                                    break
                            except:
                                continue
                    except Exception as e:
                        print(f"Could not get person name: {e}")
                        
                    # Get job title
                    job_title = None
                    try:
                        title_selectors = [
                            ".org-people-profile-card__profile-position",
                            ".artdeco-entity-lockup__subtitle",
                            ".artdeco-entity-lockup__caption"
                        ]
                        
                        for selector in title_selectors:
                            try:
                                title_element = container.find_element(By.CSS_SELECTOR, selector)
                                if title_element:
                                    job_title = title_element.text
                                    print(f"Found job title: {job_title}")
                                    break
                            except:
                                continue
                    except Exception as e:
                        print(f"Could not get job title: {e}")
                        
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
                        # Scroll button into view and click
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", connect_button)
                        time.sleep(random.uniform(1, 1.5))
                        
                        try:
                            # Use JavaScript click which is more reliable
                            driver.execute_script("arguments[0].click();", connect_button)
                            print(f"Clicked connect button for profile {i+1}")
                            time.sleep(random.uniform(2, 3))
                            
                            # Look for the "Add a note" option
                            add_note_button = None
                            note_selectors = [
                                "button.artdeco-button--secondary",
                                "button.artdeco-modal__confirm-dialog-btn",
                                "button[aria-label='Add a note']"
                            ]
                            
                            for selector in note_selectors:
                                try:
                                    buttons = driver.find_elements(By.CSS_SELECTOR, selector)
                                    for btn in buttons:
                                        if btn.is_displayed() and any(text in btn.text.lower() for text in ["add a note", "note", "personalize"]):
                                            add_note_button = btn
                                            print(f"Found 'Add a note' button: {btn.text}")
                                            break
                                except:
                                    continue
                                    
                                if add_note_button:
                                    break
                                    
                            if add_note_button:
                                # Click the "Add a note" button
                                driver.execute_script("arguments[0].click();", add_note_button)
                                print("Clicked 'Add a note' button")
                                time.sleep(random.uniform(1, 2))
                                
                                # Find the textarea for the note
                                textarea = None
                                textarea_selectors = [
                                    "textarea.ember-text-area",
                                    "textarea.artdeco-text-input--input",
                                    "textarea[name='message']"
                                ]
                                
                                for selector in textarea_selectors:
                                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                                    for elem in elements:
                                        if elem.is_displayed():
                                            textarea = elem
                                            print(f"Found textarea with selector: {selector}")
                                            break
                                            
                                    if textarea:
                                        break
                                        
                                if textarea:
                                    # Lookup additional information from our CSV data if possible
                                    additional_info = None
                                    job_desc = None
                                    
                                    if roles_df is not None and person_name:
                                        # Find matching entries in our roles database
                                        matching_roles = roles_df[roles_df['Name'].str.contains(person_name.split()[0], case=False, na=False)]
                                        
                                        if not matching_roles.empty:
                                            # Get first match
                                            first_match = matching_roles.iloc[0]
                                            additional_info = first_match.get('Company_Name')
                                            job_desc = first_match.get('Information')
                                            
                                            # Print what we found
                                            print(f"Found additional info from CSV for {person_name}")
                                    
                                    # Check if this is an HR professional and prioritize accordingly
                                    is_hr_professional = job_title and is_hr_role(job_title)
                                    if is_hr_professional:
                                        print(f"Creating specialized message for HR professional with title: {job_title}")
                                    
                                    # Create personalized message using all available information
                                    personalized_message = create_personalized_message(
                                        person_name,  # Full name 
                                        job_title,    # Job title from profile
                                        company_name, # Company name 
                                        job_desc      # Additional job description if available
                                    )
                                    
                                    # Add the personalized message to the textarea
                                    try:
                                        textarea.clear()
                                        textarea.send_keys(personalized_message)
                                        print(f"Added personalized message: {personalized_message}")
                                    except Exception as e:
                                        # Try with JavaScript if normal method fails
                                        try:
                                            driver.execute_script("arguments[0].value = arguments[1]", textarea, personalized_message)
                                            print("Added message using JavaScript")
                                        except Exception as e:
                                            print(f"Failed to add message: {e}")
                                            
                                    time.sleep(random.uniform(1, 2))
                                    
                                    # Find and click the Send button
                                    send_button = None
                                    for selector in ["button.artdeco-button--primary", "button[aria-label='Send now']"]:
                                        elements = driver.find_elements(By.CSS_SELECTOR, selector)
                                        for element in elements:
                                            if element.is_displayed() and any(text in element.text.lower() for text in ["send", "done"]):
                                                send_button = element
                                                break
                                                
                                        if send_button:
                                            break
                                            
                                    if send_button:
                                        # Click the Send button and count this as a connection
                                        driver.execute_script("arguments[0].click();", send_button)
                                        print(f"Sent connection request to {person_name}" + 
                                              (f" (HR Professional)" if is_hr_professional else ""))
                                        connection_count += 1
                                        
                                        # Add short delay to avoid server errors
                                        time.sleep(random.uniform(2, 3))
                                    else:
                                        print("Could not find Send button")
                        except Exception as e:
                            print(f"Error with 'Add a note' flow: {e}")
                    except Exception as e:
                        print(f"Error clicking connect button: {e}")
                        
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