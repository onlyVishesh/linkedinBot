#!/bin/bash

# LinkedIn Bot - Stage 2 (Role Information Extraction)
# This script runs only Stage 2 of the LinkedIn connection process

# Color codes for better readability
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}==================================${NC}"
echo -e "${BLUE}    LinkedIn Bot - Stage 2    ${NC}"
echo -e "${BLUE}==================================${NC}"

# Create logs directory if it doesn't exist
mkdir -p logs

# Start timestamp
START_TIME=$(date +"%Y-%m-%d %H:%M:%S")
echo -e "${GREEN}Starting Stage 2 at ${START_TIME}${NC}"

# Check for prerequisite files
echo -e "${YELLOW}Checking prerequisites...${NC}"
if [ ! -f "names_and_positions.csv" ]; then
    echo -e "${RED}Error: names_and_positions.csv not found.${NC}"
    echo -e "${RED}Please run Stage 1 first using run_stage1.sh${NC}"
    exit 1
fi

# Check if Chrome and ChromeDriver are installed
echo -e "${YELLOW}Checking dependencies...${NC}"
if [ ! -f "chromedriver" ]; then
    echo -e "${RED}ChromeDriver not found. Installing...${NC}"
    bash get_chrome_driver.sh
fi

# Step 1: Login to LinkedIn (needed for any stage)
echo -e "\n${YELLOW}Logging into LinkedIn...${NC}"
python3 login.py 2>&1 | tee logs/login_$(date +"%Y%m%d_%H%M%S").log
if [ $? -ne 0 ]; then
    echo -e "${RED}Login failed. Please check your credentials and try again.${NC}"
    exit 1
fi
echo -e "${GREEN}Successfully logged into LinkedIn${NC}"

# Step 2: Run Stage 2 - Extract role information
echo -e "\n${YELLOW}Running Stage 2 - Extracting role information...${NC}"
echo -e "${BLUE}This will visit profiles to extract work experience and job details${NC}"
python3 stage2.py 2>&1 | tee logs/stage2_$(date +"%Y%m%d_%H%M%S").log
if [ $? -ne 0 ]; then
    echo -e "${RED}Stage 2 failed. Check the logs for details.${NC}"
    exit 1
fi

# Check if the output file exists
if [ ! -f "roles_of_person_in_pervious_list.csv" ]; then
    echo -e "${RED}Error: roles_of_person_in_pervious_list.csv not found. Stage 2 may have failed.${NC}"
    exit 1
fi

# End timestamp
END_TIME=$(date +"%Y-%m-%d %H:%M:%S")
echo -e "\n${GREEN}Stage 2 completed at ${END_TIME}${NC}"
echo -e "${BLUE}==================================${NC}"

# Summary
echo -e "\n${YELLOW}Summary:${NC}"
echo -e "- Extracted role information from profiles in names_and_positions.csv"
echo -e "- Output saved to roles_of_person_in_pervious_list.csv"
echo -e "\n${GREEN}To continue to Stage 3, run:${NC}"
echo -e "bash run_stage3.sh" 