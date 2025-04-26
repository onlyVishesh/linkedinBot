# LinkedIn Bot Script Usage Guide

This document explains how to use the script files to automate the LinkedIn connection process, with a focus on targeting HR professionals.

## Overview

The LinkedIn Bot consists of three stages:

1. **Stage**: Connects with professionals, prioritizing HR contacts first, using personalized messages

## Script Files

The following script files are available:

- `run_stage.sh`: Runs only Stage 3

## Prerequisites

Before running any scripts, make sure:

1. You have updated your LinkedIn credentials in `config.py`
2. You have added your target companies to the `companies_list` in `config.py`
3. You have installed the required Python packages with `pip install -r requirements.txt`

## Running the Full Process

To run the entire LinkedIn connection process:

```bash
./run_stage.sh
```

This will:

1. Log in to LinkedIn using your credentials
2. Gather profiles from the companies listed in `config.py`
3. Extract role information from these profiles
4. Connect with professionals, prioritizing HR contacts first

## Logs

All logs are saved in the `logs` directory with timestamps for easy tracking of activity. If something goes wrong, check the logs for details.

## Customizing Messages

You can customize the connection messages in `config.py`:

- `message`: General message template for non-HR contacts
- `hr_message`: Specialized message template for HR professionals

Both messages should be kept under 200 characters.

## Important Notes

1. LinkedIn has connection limits. The script is set to stop after 100 connection requests to avoid restrictions.
2. Running the scripts too frequently may trigger LinkedIn's security measures.
3. Always use these scripts responsibly and in accordance with LinkedIn's terms of service.

## Troubleshooting

If you encounter issues:

1. Check the log files in the `logs` directory
2. Ensure your LinkedIn credentials are correct
3. Make sure you have a stable internet connection
4. Verify that chromedriver matches your Chrome version
