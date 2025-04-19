#!/bin/bash

# LinkedIn Bot - Stage 1 (Profile Collection)
# This script runs only Stage 1 of the LinkedIn connection process

# Color codes for better readability
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}==================================${NC}"
echo -e "${BLUE}    LinkedIn Bot - Stage 1    ${NC}"
echo -e "${BLUE}==================================${NC}"

# Create logs directory if it doesn't exist
mkdir -p logs

# Start timestamp
START_TIME=$(date +"%Y-%m-%d %H:%M:%S")
echo -e "${GREEN}Starting Stage 1 at ${START_TIME}${NC}"

# Check if Chrome and ChromeDriver are installed
echo -e "${YELLOW}Checking dependencies...${NC}"
if [ ! -f "chromedriver" ]; then
    echo -e "${RED}ChromeDriver not found. Installing...${NC}"
    bash get_chrome_driver.sh
fi

# Step 1: Login to LinkedIn
echo -e "\n${YELLOW}Logging into LinkedIn...${NC}"
python3 login.py 2>&1 | tee logs/login_$(date +"%Y%m%d_%H%M%S").log
if [ $? -ne 0 ]; then
    echo -e "${RED}Login failed. Please check your credentials and try again.${NC}"
    exit 1
fi
echo -e "${GREEN}Successfully logged into LinkedIn${NC}"

# Step 2: Run Stage 1 - Gather company profiles
echo -e "\n${YELLOW}Running Stage 1 - Gathering company profiles...${NC}"
echo -e "${BLUE}This will search for people at companies listed in config.py${NC}"
python3 stage1.py 2>&1 | tee logs/stage1_$(date +"%Y%m%d_%H%M%S").log
if [ $? -ne 0 ]; then
    echo -e "${RED}Stage 1 failed. Check the logs for details.${NC}"
    exit 1
fi

# Check if the output file exists
if [ ! -f "names_and_positions.csv" ]; then
    echo -e "${RED}Error: names_and_positions.csv not found. Stage 1 may have failed.${NC}"
    exit 1
fi

# End timestamp
END_TIME=$(date +"%Y-%m-%d %H:%M:%S")
echo -e "\n${GREEN}Stage 1 completed at ${END_TIME}${NC}"
echo -e "${BLUE}==================================${NC}"

# Summary
echo -e "\n${YELLOW}Summary:${NC}"
echo -e "- Collected profiles from companies listed in config.py"
echo -e "- Output saved to names_and_positions.csv"
echo -e "\n${GREEN}To continue to Stage 2, run:${NC}"
echo -e "bash run_stage2.sh" 