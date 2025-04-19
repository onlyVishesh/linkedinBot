#!/bin/bash

# LinkedIn Bot - Full Pipeline Script
# This script runs all stages of the LinkedIn connection process:
# 1. Login to LinkedIn
# 2. Stage 1: Gather company profiles
# 3. Stage 2: Extract role information from profiles
# 4. Stage 3: Connect with HR professionals first, then others

# Color codes for better readability
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}==================================${NC}"
echo -e "${BLUE}    LinkedIn Connection Bot    ${NC}"
echo -e "${BLUE}==================================${NC}"

# Create logs directory if it doesn't exist
mkdir -p logs

# Start timestamp
START_TIME=$(date +"%Y-%m-%d %H:%M:%S")
echo -e "${GREEN}Starting LinkedIn Bot at ${START_TIME}${NC}"
echo -e "${GREEN}See detailed logs in the logs directory${NC}"

# Check if Chrome and ChromeDriver are installed
echo -e "${YELLOW}Checking dependencies...${NC}"
if [ ! -f "chromedriver" ]; then
    echo -e "${RED}ChromeDriver not found. Installing...${NC}"
    bash get_chrome_driver.sh
fi

# Step 1: Login to LinkedIn
echo -e "\n${YELLOW}STEP 1: Logging into LinkedIn...${NC}"
python3 login.py 2>&1 | tee logs/login_$(date +"%Y%m%d_%H%M%S").log
if [ $? -ne 0 ]; then
    echo -e "${RED}Login failed. Please check your credentials and try again.${NC}"
    exit 1
fi
echo -e "${GREEN}Successfully logged into LinkedIn${NC}"

# Step 2: Run Stage 1 - Gather company profiles
echo -e "\n${YELLOW}STEP 2: Running Stage 1 - Gathering company profiles...${NC}"
echo -e "${BLUE}This will search for people at companies listed in config.py${NC}"
python3 stage1.py 2>&1 | tee logs/stage1_$(date +"%Y%m%d_%H%M%S").log
if [ $? -ne 0 ]; then
    echo -e "${RED}Stage 1 failed. Check the logs for details.${NC}"
    exit 1
fi
echo -e "${GREEN}Stage 1 completed successfully${NC}"

# Check if the output file exists
if [ ! -f "names_and_positions.csv" ]; then
    echo -e "${RED}Error: names_and_positions.csv not found. Stage 1 may have failed.${NC}"
    exit 1
fi

# Step 3: Run Stage 2 - Extract role information from profiles
echo -e "\n${YELLOW}STEP 3: Running Stage 2 - Extracting role information...${NC}"
echo -e "${BLUE}This will visit profiles to extract work experience and job details${NC}"
python3 stage2.py 2>&1 | tee logs/stage2_$(date +"%Y%m%d_%H%M%S").log
if [ $? -ne 0 ]; then
    echo -e "${RED}Stage 2 failed. Check the logs for details.${NC}"
    exit 1
fi
echo -e "${GREEN}Stage 2 completed successfully${NC}"

# Check if the output file exists
if [ ! -f "roles_of_person_in_pervious_list.csv" ]; then
    echo -e "${RED}Error: roles_of_person_in_pervious_list.csv not found. Stage 2 may have failed.${NC}"
    exit 1
fi

# Step 4: Run Stage 3 - Connect with HR professionals first, then others
echo -e "\n${YELLOW}STEP 4: Running Stage 3 - Connecting with HR professionals...${NC}"
echo -e "${BLUE}This will prioritize HR professionals and send personalized connection requests${NC}"
python3 stage3.py 2>&1 | tee logs/stage3_$(date +"%Y%m%d_%H%M%S").log
if [ $? -ne 0 ]; then
    echo -e "${RED}Stage 3 failed. Check the logs for details.${NC}"
    exit 1
fi
echo -e "${GREEN}Stage 3 completed successfully${NC}"

# End timestamp
END_TIME=$(date +"%Y-%m-%d %H:%M:%S")
echo -e "\n${GREEN}LinkedIn Bot completed at ${END_TIME}${NC}"
echo -e "${BLUE}==================================${NC}"
echo -e "${BLUE}    Process Completed    ${NC}"
echo -e "${BLUE}==================================${NC}"

# Final summary
echo -e "\n${YELLOW}Summary of Actions:${NC}"
echo -e "1. Collected profiles from companies listed in config.py"
echo -e "2. Extracted role information from profiles"
echo -e "3. Prioritized HR professionals and sent personalized connection requests"
echo -e "\n${GREEN}Check the CSV files for collected data:${NC}"
echo -e "- names_and_positions.csv: Contains the profiles found"
echo -e "- roles_of_person_in_pervious_list.csv: Contains work experience details"
echo -e "\n${YELLOW}To run individual stages, use:${NC}"
echo -e "- bash run_stage1.sh"
echo -e "- bash run_stage2.sh"
echo -e "- bash run_stage3.sh" 