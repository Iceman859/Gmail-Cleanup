# Gmail Cleanup Utility
A Python script to archive your inbox and purge Spam/Trash via IMAP.

## Setup Instructions
1. Install requirements:
   `pip install python-dotenv`

2. Create a `.env` file in the same directory as the script.
3. Add your credentials to `.env`:
   GMAIL_USER=your_email@gmail.com
   GMAIL_APP_PASSWORD=your_16_char_app_password

4. Create a `.gitignore` file and add `.env` to it. 
   **CRITICAL:** Do NOT upload your .env file to GitHub.

5. Run the script:
   `python gmail_cleaner.py`
