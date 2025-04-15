from dependencies import *
import config
import time
import os
import traceback
import sys

try:
    # Import login module and check if driver is available
    import login
    if login.driver is None:
        print("Error: WebDriver not initialized in login module")
        sys.exit(1)
        
    driver = login.driver
    
    # Check if file exists and is not empty to avoid duplicate headers
    filename = "names_and_positions.csv"
    headers = ["Name", "ProfileLinks", "current_designation", "current_location"]
    
    # Create a new file or append to existing
    file_exists = os.path.isfile(filename) and os.path.getsize(filename) > 0
    File = open(filename, 'a')
    writer_object = writer(File)
    
    # Only write headers if file didn't exist or was empty
    if not file_exists:
        writer_object.writerow(headers)
        print(f"Created new CSV file: {filename}")
    else:
        print(f"Appending to existing CSV file: {filename}")
    
    companies_list = config.companies_list
    total_profiles_found = 0
    
    for j in range(len(companies_list)):
        company = companies_list[j]
        print(f"\nSearching for people at {company} ({j+1}/{len(companies_list)})...")
        
        try:
            # Navigate to the search results page
            search_url = f"https://www.linkedin.com/search/results/people/?keywords={company}&origin=SWITCH_SEARCH_VERTICAL"
            driver.get(search_url)
            print(f"Loaded search URL: {search_url}")
            time.sleep(5)  # Allow page to load completely
            
            # Take a screenshot to debug
            try:
                debug_screenshot = f"search_results_{company}.png"
                driver.save_screenshot(debug_screenshot)
                print(f"Saved search results screenshot to {debug_screenshot}")
            except Exception as e:
                print(f"Warning: Could not save search results screenshot: {e}")
            
            # Scroll down to load more results
            print("Scrolling to load more results...")
            for scroll in range(4):
                try:
                    driver.execute_script("window.scrollBy(0, 1000);")
                    time.sleep(2)
                except Exception as e:
                    print(f"Warning: Error during scrolling: {e}")
                    break
            
            # Save the HTML to a file for debugging
            try:
                with open(f"debug_html_{company}.html", "w", encoding="utf-8") as f:
                    f.write(driver.page_source)
                print(f"Saved HTML source to debug_html_{company}.html")
            except Exception as e:
                print(f"Warning: Could not save HTML source: {e}")
            
            # Get the page source after scrolling
            src = driver.page_source
            htmlParser = soup(src, "html.parser")
            
            # Try multiple selectors for search results
            print("Extracting search results...")
            content = []
            
            # Try different container selectors
            container_selectors = [
                "li.reusable-search__result-container",
                "li.entity-result",
                "li.search-result",
                "div.entity-result__item",
                ".entity-result",
                ".search-results__result-item",
                "li.artdeco-list__item"
            ]
            
            for selector in container_selectors:
                content = htmlParser.select(selector)
                if content:
                    print(f"Found {len(content)} profiles using selector: {selector}")
                    break
            
            if not content:
                print("DEBUG: No profiles found with normal selectors. Trying raw tag search...")
                
                # Try to find all li elements that might contain profiles
                li_elements = htmlParser.find_all("li")
                print(f"Found {len(li_elements)} li elements")
                
                # Filter out li elements that might be search results
                potential_results = []
                for li in li_elements:
                    # Look for classes that might indicate a search result
                    classes = li.get("class", [])
                    class_str = " ".join(classes) if classes else ""
                    
                    # Check for telltale attributes or content that suggests this is a profile
                    has_profile_img = li.find("img") is not None
                    has_profile_link = li.find("a", href=lambda href: href and "/in/" in href) is not None
                    has_keyword = any(keyword in class_str.lower() for keyword in ["result", "entity", "profile", "search"])
                    
                    if has_profile_link or (has_profile_img and has_keyword):
                        potential_results.append(li)
                
                print(f"Found {len(potential_results)} potential profile elements")
                
                if potential_results:
                    content = potential_results
                else:
                    print(f"No profiles found for {company}. Moving to next company.")
                    continue
            
            profiles_found = 0
            for i, item in enumerate(content):
                try:
                    # Debug each item
                    print(f"\nProcessing search result #{i+1}:")
                    
                    # Debug the structure of this item
                    item_html = str(item)
                    print(f"Item HTML length: {len(item_html)} characters")
                    if len(item_html) < 300:
                        print(f"Item HTML snippet: {item_html[:300]}")
                    else:
                        print(f"Item HTML snippet (truncated): {item_html[:300]}...")
                    
                    # Extract name using multiple methods
                    name = "Not found"
                    
                    # Method 1: Try img alt attribute
                    img_selectors = ["img.entity-result__image", "img.presence-entity__image", "img.ivm-view-attr__img--centered", "img"]
                    for selector in img_selectors:
                        img_elements = item.select(selector)
                        print(f"Found {len(img_elements)} images with selector '{selector}'")
                        for img_element in img_elements:
                            if img_element.has_attr('alt') and img_element['alt'].strip():
                                name = img_element['alt'].strip()
                                print(f"Found name from image: {name}")
                                break
                        if name != "Not found":
                            break
                    
                    # Method 2: Try spans with name text
                    if name == "Not found":
                        name_selectors = [
                            "span.entity-result__title-text a", 
                            "span.entity-result__title-text span", 
                            "h3.actor-name",
                            "span.app-aware-link",
                            "a.app-aware-link",
                            "span.artdeco-entity-lockup__title",
                            "span.entity-result__title-line span"
                        ]
                        for selector in name_selectors:
                            name_elements = item.select(selector)
                            print(f"Found {len(name_elements)} elements with selector '{selector}'")
                            for name_element in name_elements:
                                text = name_element.get_text().strip()
                                if text:
                                    name = text
                                    print(f"Found name from text: {name}")
                                    break
                            if name != "Not found":
                                break
                    
                    # Method 3: Try any h3 or span tags that might contain names
                    if name == "Not found":
                        name_elements = item.select("h3, span.linked-area, a[href*='/in/']")
                        print(f"Found {len(name_elements)} alternative name elements")
                        for element in name_elements:
                            text = element.get_text().strip()
                            if text and len(text) > 3:
                                if "View profile" not in text and "Connect" not in text:
                                    name = text
                                    print(f"Found name from alternative element: {name}")
                                    break
                    
                    # Method 4: Last resort - check for any text elements
                    if name == "Not found":
                        all_text_elements = item.find_all(text=True)
                        filtered_texts = [text.strip() for text in all_text_elements if text.strip() and len(text.strip()) > 3]
                        print(f"Found {len(filtered_texts)} text elements")
                        if filtered_texts:
                            # Try to find a name-like text (first text that's not clearly not a name)
                            for text in filtered_texts:
                                if not any(keyword in text.lower() for keyword in ["view", "connect", "message", "follow", "linkedin"]):
                                    name = text
                                    print(f"Found possible name from raw text: {name}")
                                    break
                    
                    # Skip if name not found
                    if name == "Not found":
                        print("Could not extract name, skipping this profile")
                        continue
                        
                    # Clean up name
                    name = name.replace("\n", "").replace(",", "|").strip()
                    
                    # Extract profile link
                    profile_links = "Not found"
                    link_selectors = [
                        "a.app-aware-link", 
                        "a[href*='/in/']",
                        "a.search-result__result-link",
                        "a.entity-result__link"
                    ]
                    
                    for selector in link_selectors:
                        link_elements = item.select(selector)
                        print(f"Found {len(link_elements)} link elements with selector '{selector}'")
                        for link_element in link_elements:
                            if link_element.has_attr('href') and '/in/' in link_element['href']:
                                profile_links = link_element['href'].split("?")[0]  # Remove query parameters
                                print(f"Found profile link: {profile_links}")
                                break
                        if profile_links != "Not found":
                            break
                    
                    # If no links found with selectors, try to find any link with "/in/"
                    if profile_links == "Not found":
                        all_links = item.find_all("a", href=True)
                        print(f"Found {len(all_links)} total links")
                        for link in all_links:
                            if '/in/' in link['href']:
                                profile_links = link['href'].split("?")[0]
                                print(f"Found profile link from general search: {profile_links}")
                                break
                    
                    # Extract designation/title
                    current_designation = "Not found"
                    designation_selectors = [
                        "div.entity-result__primary-subtitle",
                        "span.entity-result__primary-subtitle",
                        "div.search-result__info-container p.subline-level-1",
                        "p.entity-result__summary",
                        "div.artdeco-entity-lockup__subtitle",
                        "span.artdeco-entity-lockup__subtitle"
                    ]
                    
                    for selector in designation_selectors:
                        designation_elements = item.select(selector)
                        print(f"Found {len(designation_elements)} designation elements with selector '{selector}'")
                        for designation_element in designation_elements:
                            text = designation_element.get_text().strip()
                            if text:
                                current_designation = text
                                print(f"Found designation: {current_designation}")
                                break
                        if current_designation != "Not found":
                            break
                    
                    # Extract location
                    current_location = "Not found"
                    location_selectors = [
                        "div.entity-result__secondary-subtitle",
                        "span.entity-result__secondary-subtitle",
                        "div.search-result__info-container p.subline-level-2",
                        "p.entity-result__insights",
                        "div.artdeco-entity-lockup__caption",
                        "span.artdeco-entity-lockup__caption"
                    ]
                    
                    for selector in location_selectors:
                        location_elements = item.select(selector)
                        print(f"Found {len(location_elements)} location elements with selector '{selector}'")
                        for location_element in location_elements:
                            text = location_element.get_text().strip()
                            if text:
                                current_location = text
                                print(f"Found location: {current_location}")
                                break
                        if current_location != "Not found":
                            break
                    
                    # Clean up data
                    current_designation = current_designation.replace("\n", "").replace(",", "|").strip()
                    current_location = current_location.replace("\n", "").replace(",", "|").strip()
                    
                    # Write to CSV
                    data = [name, profile_links, current_designation, current_location]
                    writer_object.writerow(data)
                    print(f"Added to CSV: {name} - {current_designation}")
                    
                    profiles_found += 1
                    total_profiles_found += 1
                    
                    # Limit the number of profiles per company to avoid rate limiting
                    if profiles_found >= 10:
                        print(f"Reached limit of 10 profiles for {company}. Moving to next company.")
                        break
                    
                except Exception as e:
                    print(f"Error processing profile: {e}")
                    traceback.print_exc()
                    continue
            
            print(f"Found {profiles_found} profiles for {company}")
            
        except Exception as e:
            print(f"Error processing company {company}: {e}")
            traceback.print_exc()
            continue
        
        # Wait a bit before moving to the next company to avoid rate limiting
        if j < len(companies_list) - 1:
            time.sleep(3)
    
    File.close()
    print(f"\nStage 1 completed successfully! Total profiles found: {total_profiles_found}")
    
    # If nothing was found, print a warning
    if total_profiles_found == 0:
        print("\nWARNING: No profiles were found. Please check if LinkedIn's UI has changed or if your account has been rate-limited.")
        print("You may want to manually visit LinkedIn and check if everything works properly.")
        print("Check the debug HTML files saved for each company for clues about the current page structure.")

except Exception as e:
    print(f"Critical error in stage1.py: {e}")
    traceback.print_exc()
    sys.exit(1)