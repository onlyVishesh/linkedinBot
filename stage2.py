from dependencies import *
from login import *
import time

df = pd.read_csv("names_and_positions.csv")
profileLinks = df['ProfileLinks']
names = df['Name']

headers = ["Name", "Company_Name", "Duration", "Information"]
filename = "roles_of_person_in_pervious_list.csv"
File = open(filename,'a')
writer_object = writer(File)
writer_object.writerow(headers)

count = 0
for j in range(len(profileLinks)):
    if count > 999:
        break
    
    print(f"Processing profile {j+1}/{len(profileLinks)}: {names[j]}")
    
    try:
        # Skip if profile link is "Not found"
        if profileLinks[j] == "Not found" or "linkedin.com" not in profileLinks[j]:
            print(f"Skipping invalid profile link for: {names[j]}")
            continue
            
        driver.get(profileLinks[j])
        time.sleep(3)  # Allow page to load
        
        # Scroll down to load experience section
        driver.execute_script("window.scrollBy(0, 500);")
        time.sleep(2)
        
        # Try to click "see more" buttons for experience section
        try:
            see_more_buttons = driver.find_elements(By.XPATH, "//button[contains(@class, 'inline-show-more-text__button') or contains(@class, 'pv-profile-section__see-more-inline')]")
            for button in see_more_buttons:
                try:
                    driver.execute_script("arguments[0].click();", button)
                    time.sleep(1)
                except:
                    pass
        except:
            pass
            
        src = driver.page_source
        parser = soup(src, "html.parser")
        
        # Try different selectors for experience sections based on current LinkedIn UI
        profiles = []
        
        # Try multiple possible selectors for experience entries
        selectors = [
            "li.pv-entity__position-group-pager",
            "li.artdeco-list__item",
            "div.experience-item",
            "section.experience-section li",
            "#experience-section li"
        ]
        
        for selector in selectors:
            profiles = parser.select(selector)
            if profiles:
                print(f"Found {len(profiles)} experience entries using selector: {selector}")
                break
                
        if not profiles:
            print(f"No experience entries found for {names[j]}")
            continue
            
        for i in range(len(profiles)):
            count += 1
            name = names[j]
            
            # Extract company name
            company_name = ""
            try:
                # Try different selectors for company name
                company_selectors = [
                    "p.pv-entity__secondary-title",
                    "span.pv-entity__secondary-title",
                    "h3.t-16.t-black.t-bold",
                    "span.t-14.t-normal",
                    "span.t-16.t-black.t-bold"
                ]
                
                for selector in company_selectors:
                    company_element = profiles[i].select_one(selector)
                    if company_element:
                        company_name = company_element.get_text()
                        break
                        
                company_name = company_name.replace("\n", "").strip().replace(",", "|").replace("None", "")
            except Exception as e:
                print(f"Error extracting company name: {e}")
                company_name = "Not found"
                
            # Extract duration
            duration = ""
            try:
                # Try different selectors for duration
                duration_selectors = [
                    "span.pv-entity__bullet-item-v2",
                    "span.pv-entity__date-range span:nth-child(2)",
                    "h4.t-14.t-black--light",
                    "span.t-14.t-normal.t-black--light"
                ]
                
                for selector in duration_selectors:
                    duration_element = profiles[i].select_one(selector)
                    if duration_element:
                        duration = duration_element.get_text()
                        break
                        
                duration = duration.replace("\n", "").strip().replace(",", "|").replace("None", "")
            except Exception as e:
                print(f"Error extracting duration: {e}")
                duration = "Not found"
                
            # Extract job description/information
            info = ""
            try:
                # Try different selectors for job description
                info_selectors = [
                    "div.pv-entity__extra-details",
                    "p.pv-entity__description",
                    "div.inline-show-more-text"
                ]
                
                for selector in info_selectors:
                    info_element = profiles[i].select_one(selector)
                    if info_element:
                        info = info_element.get_text()
                        break
                        
                info = info.replace("\n", "").strip().replace(",", "|").replace("None", "")
            except Exception as e:
                print(f"Error extracting job info: {e}")
                info = "Not found"
                
            data = [name, company_name, duration, info]
            writer_object.writerow(data)
            print(f"Added experience: {name} - {company_name} ({duration})")
    except Exception as e:
        print(f"Error processing profile {names[j]}: {e}")
        continue

File.close()
print("Stage 2 completed successfully!")
