# LinkedIn Connection Bot

An automated solution for making strategic LinkedIn connections with personalized messages, prioritizing HR professionals.

## Overview

This LinkedIn Bot automates the process of connecting with professionals from your target companies. It focuses on:

1. **HR Prioritization**: Identifies and prioritizes HR professionals who might be hiring for relevant positions
2. **Personalized Messages**: Sends custom connection requests tailored to each recipient's role
3. **Smart Targeting**: Connects with professionals from your specified target companies

> **⚠️ IMPORTANT**: LinkedIn only allows approximately 5 personalized note connections per month for standard accounts. I am working on a fix that will first send connection requests without notes and store them. Then, when they accept, the next time you run the code it will send custom messages to these connections before sending new connection requests.

## Features

- **HR Detection**: Automatically identifies HR professionals using job title analysis
- **Message Customization**: Creates different messages for HR vs. non-HR professionals
- **Keyword Optimization**: Extracts keywords from job descriptions to customize technical messages
- **Connection Management**: Limits connections to stay within LinkedIn's restrictions
- **Company Targeting**: Directly navigates to company pages for efficient profile discovery
- **Error Handling**: Robust error management with debugging screenshots
- **Session Management**: Detects session timeouts and provides clear instructions

## Requirements

- Python 3.6 or higher
- Chrome browser
- ChromeDriver (automatically installed by the script)
- Python packages:
  - selenium
  - webdriver-manager
  - beautifulsoup4
  - lxml
  - pandas

## Setup

1. Update `config.py` with your credentials and preferences:
   ```python
   username = "Your_email"
   password = "LinkedIn_Password"
   
   # your dream companies list, you can add more companies also
   companies_list = ["amazon", "google", "microsoft"]
   
   # General message template (under 200 characters)
   message = """Your Message"""
   
   # HR-specific message template (under 200 characters)
   hr_message = """Your HR Message"""
   ```

2. Run the setup script:
   ```bash
   bash get_chrome_driver.sh
   ```

3. Launch the bot:
   ```bash
   bash run_stage.sh
   ```

## How It Works

1. **Login**: Securely logs into your LinkedIn account
2. **Company Processing**: Navigates to each company in your list
3. **Profile Analysis**: Scans employee profiles on company pages
4. **HR Prioritization**: Identifies HR professionals and processes them first
5. **Smart Messaging**:
   - For HR: Sends specialized messages mentioning your relevant skills for their hiring needs
   - For Others: Personalizes messages based on their role and company

## Message Customization Logic

The bot creates personalized messages based on:

- **Recipient's first name**: "Hi [First Name]"
- **Role detection**: Different message templates for HR vs. non-HR professionals
- **Company name**: Includes company name when available
- **Technical keywords**: For developers/engineers, highlights matching technical skills

## Best Practices

- **Be realistic**: Start with a small number of target companies
- **Monitor connections**: Check your LinkedIn notifications for responses
- **Personalize config**: Update the message templates to reflect your authentic voice
- **Stay within limits**: LinkedIn limits connection requests; the script respects these limits
- **Be patient**: Allow sufficient time between runs to avoid account restrictions

## Troubleshooting

- **Login issues**: Verify your LinkedIn credentials in config.py
- **ChromeDriver errors**: Run the get_chrome_driver.sh script to update
- **Page navigation failures**: Check company names in your companies_list (use lowercase, no spaces)
- **Connection errors**: LinkedIn may temporarily limit connection requests; wait 24 hours
- **Session timeouts**: Re-run login.py to start a fresh session

## Advanced Configuration

- Modify the `is_hr_role()` function in stage.py to customize HR role detection
- Adjust timeout and delay values in the code if you have a slower internet connection
- Add additional companies to your target list in config.py

## Future Enhancements

- Implement follow-up message automation
- Add connection acceptance tracking
- Create report generation for connection statistics
- Implement multi-stage connection strategy for LinkedIn's new connection limits
- Store pending connection requests and send personalized messages once accepted

## Disclaimer

This tool is for educational purposes only. Use responsibly and in accordance with LinkedIn's terms of service. Excessive automation may lead to account restrictions.

## Thanks

