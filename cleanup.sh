#!/bin/bash

# LinkedIn Bot - Cleanup Script
# This script removes unnecessary files from the LinkedIn bot project

# Color codes for better readability
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}==================================${NC}"
echo -e "${BLUE}    LinkedIn Bot - Cleanup    ${NC}"
echo -e "${BLUE}==================================${NC}"

echo -e "${YELLOW}Starting cleanup process...${NC}"

# Create a backup directory for important data
echo -e "${YELLOW}Creating backup of important data...${NC}"
mkdir -p data_backup
cp names_and_positions.csv data_backup/ 2>/dev/null
cp roles_of_person_in_pervious_list.csv data_backup/ 2>/dev/null
echo -e "${GREEN}Data backed up to data_backup/ directory${NC}"

# Remove debug/test files
echo -e "${YELLOW}Removing debug and test files...${NC}"
rm -f test_personalization.py
rm -f check_linkedin.py
rm -f fix_stage3.py

# Remove backup files
echo -e "${YELLOW}Removing backup files...${NC}"
rm -f stage3_backup.py
rm -f stage3.py.save

# Remove old/redundant scripts
echo -e "${YELLOW}Removing old and redundant scripts...${NC}"
rm -f script.sh
rm -f run_direct_connect.sh
rm -f run_personalized.sh
rm -f direct_connect.py

# Remove debug HTML files
echo -e "${YELLOW}Removing debug HTML files...${NC}"
rm -f debug_html_*.html
rm -f company_search_*.html

# Remove screenshot files
echo -e "${YELLOW}Removing screenshot files...${NC}"
rm -f *.png

# Clean up any other unnecessary files with unusual names
echo -e "${YELLOW}Cleaning up other unnecessary files...${NC}"
rm -f company_search_*_members.html
rm -f company_search_*_physics*.html
rm -f company_search_*_mos*.html
rm -f company_search_**ai_revolution**.html

# Remove chromedriver zip file (keep the executable)
rm -f chromedriver_linux64.zip

echo -e "${GREEN}Cleanup complete!${NC}"
echo -e "${BLUE}==================================${NC}"

# Summary of remaining essential files
echo -e "${YELLOW}Remaining essential files:${NC}"
echo -e "1. Core Python Files:"
echo -e "   - stage1.py: Profile collection"
echo -e "   - stage2.py: Role information extraction"
echo -e "   - stage3.py: HR-prioritized connection requests"
echo -e "   - login.py: LinkedIn authentication"
echo -e "   - config.py: Configuration settings"
echo -e "   - dependencies.py: Required libraries"
echo -e "2. Shell Scripts:"
echo -e "   - run_all_stages.sh: Run the entire process"
echo -e "   - run_stage1.sh, run_stage2.sh, run_stage3.sh: Run individual stages"
echo -e "   - get_chrome_driver.sh, install_chrome.sh: Setup scripts"
echo -e "3. Documentation:"
echo -e "   - README.md: Main documentation"
echo -e "   - SCRIPTS_README.md: Script usage guide"
echo -e "4. Other Important Files:"
echo -e "   - requirements.txt: Python dependencies"
echo -e "   - chromedriver: Chrome WebDriver executable"
echo -e "   - names_and_positions.csv, roles_of_person_in_pervious_list.csv: Data files" 