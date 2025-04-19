# LinkedIn Bot Project Cleanup

This document explains which files are essential to the LinkedIn Bot project and which ones can be safely removed.

## Essential Files

These files should be kept for the bot to function properly:

### Core Python Files

- `stage1.py`: Collects profiles from target companies
- `stage2.py`: Extracts role information from collected profiles
- `stage3.py`: Connects with professionals, prioritizing HR contacts
- `login.py`: Handles LinkedIn authentication
- `config.py`: Contains configuration settings (credentials, companies, messages)
- `dependencies.py`: Defines required libraries and imports

### Shell Scripts

- `run_all_stages.sh`: Main script that runs the entire process
- `run_stage1.sh`: Runs only Stage 1
- `run_stage2.sh`: Runs only Stage 2
- `run_stage3.sh`: Runs only Stage 3
- `get_chrome_driver.sh`: Downloads ChromeDriver
- `install_chrome.sh`: Installs Chrome browser
- `cleanup.sh`: Removes unnecessary files

### Documentation

- `README.md`: Main project documentation
- `SCRIPTS_README.md`: Script usage guide
- `CLEANUP_INFO.md`: This file

### Other Important Files

- `requirements.txt`: Lists Python dependencies
- `chromedriver`: Chrome WebDriver executable
- `.gitignore`: Git ignore file

### Data Files

- `names_and_positions.csv`: Profiles collected from Stage 1
- `roles_of_person_in_pervious_list.csv`: Role information from Stage 2

## Unnecessary Files (Safe to Remove)

The following types of files have been removed by the cleanup script:

### Debug/Test Files

- `test_personalization.py`
- `check_linkedin.py`
- `fix_stage3.py`

### Backup Files

- `stage3_backup.py`
- `stage3.py.save`

### Old/Redundant Scripts

- `script.sh`
- `run_direct_connect.sh`
- `run_personalized.sh`
- `direct_connect.py`

### Debug Files

- All `*.png` screenshot files
- All `debug_html_*.html` files
- All `company_search_*.html` files
- Other HTML files with unusual names

### Installation Files

- `chromedriver_linux64.zip` (the executable is kept)

## Using the Cleanup Script

To clean up your project directory and remove all unnecessary files:

```bash
./cleanup.sh
```

This script will:

1. Create backups of your important data files
2. Remove all unnecessary files
3. Display a summary of essential files that are kept

After running the cleanup script, your project directory will be organized and contain only the files needed for the LinkedIn Bot to function.
