#!/usr/bin/env bash

echo "Running LinkedIn Direct Connect Script..."
echo "This script will connect with people at the companies specified in config.py"
echo ""

# Make sure prerequisites are installed
pip install -r requirements.txt

# Run the direct connect script
python3 direct_connect.py

echo ""
echo "Direct Connect completed. Check the logs above for details." 