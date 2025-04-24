#!/bin/bash

# LinkedIn Bot - Stage 3 (HR-Prioritized Connection Requests)
# This script runs only Stage 3 of the LinkedIn connection process

# Color codes for better readability
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}==================================${NC}"
echo -e "${BLUE}        LinkedIn Bot - Stage      ${NC}"
echo -e "${BLUE}==================================${NC}"

# Create logs directory if it doesn't exist
mkdir -p logs

# Start timestamp
START_TIME=$(date +"%Y-%m-%d %H:%M:%S")
echo -e "${GREEN}Starting Stage at ${START_TIME}${NC}"

# Check for prerequisite files
echo -e "${YELLOW}Checking prerequisites...${NC}"
if [ ! -f "names_and_positions.csv" ]; then
    echo -e "${YELLOW}Warning: names_and_positions.csv not found.${NC}"
    echo -e "${YELLOW}Some features may not work properly. Consider running Stage 1 first.${NC}"
fi

if [ ! -f "roles_of_person_in_pervious_list.csv" ]; then
    echo -e "${YELLOW}Warning: roles_of_person_in_pervious_list.csv not found.${NC}"
    echo -e "${YELLOW}HR prioritization may not work optimally. Consider running Stage 2 first.${NC}"
fi

# Check if Chrome and ChromeDriver are installed
echo -e "${YELLOW}Checking dependencies...${NC}"
if [ ! -f "chromedriver" ]; then
    echo -e "${RED}ChromeDriver not found. Installing...${NC}"
    bash get_chrome_driver.sh
fi

# Login to LinkedIn (needed for any stage)
echo -e "\n${YELLOW}Logging into LinkedIn...${NC}"
python3 login.py 2>&1 | tee logs/login_$(date +"%Y%m%d_%H%M%S").log
if [ $? -ne 0 ]; then
    echo -e "${RED}Login failed. Please check your credentials and try again.${NC}"
    exit 1
fi
echo -e "${GREEN}Successfully logged into LinkedIn${NC}"

# Run Stage - Connect with HR professionals first, then others
echo -e "\n${YELLOW}Running Stage - Connecting with HR professionals...${NC}"
echo -e "${BLUE}This will prioritize HR professionals and send personalized connection requests${NC}"
echo -e "${BLUE}Using data from previous stages to customize messages (if available)${NC}"
python3 stage.py 2>&1 | tee logs/stage_$(date +"%Y%m%d_%H%M%S").log
if [ $? -ne 0 ]; then
    echo -e "${RED}Stage failed. Check the logs for details.${NC}"
    exit 1
fi

# End timestamp
END_TIME=$(date +"%Y-%m-%d %H:%M:%S")
echo -e "\n${GREEN}Stage completed at ${END_TIME}${NC}"
echo -e "${BLUE}==================================${NC}"

# Summary
echo -e "\n${YELLOW}Summary:${NC}"
echo -e "- Connected with professionals from companies in config.py"
echo -e "- Prioritized HR professionals when possible"
echo -e "- Sent personalized connection requests with custom messages"
echo -e "\n${GREEN}Process complete. Check log files for details on connections made.${NC}" 