import imaplib
import email
from email.header import decode_header
import logging
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration from .env
EMAIL = os.getenv('GMAIL_USER')
PASSWORD = os.getenv('GMAIL_APP_PASSWORD')

# Configure logging to both file and console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("gmail_cleanup.log"),
        logging.StreamHandler()
    ]
)

def empty_folder(obj, folder_name):
    """Permanently deletes items and logs their subject lines."""
    logging.info(f"Starting cleanup of folder: {folder_name}")
    
    # Select the folder (wrapped in quotes for spaces)
    obj.select(f'"{folder_name}"')
    
    result, data = obj.search(None, 'ALL')
    ids = data[0].split()

    if not ids:
        logging.info(f"Folder '{folder_name}' is already empty.")
        return

    logging.info(f"Purging {len(ids)} items from {folder_name}...")

    for num in ids:
        try:
            # Fetch and decode the subject line
            res, msg_data = obj.fetch(num, '(BODY[HEADER.FIELDS (SUBJECT)])')
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    subject_header = msg.get("Subject", "No Subject")
                    decoded = decode_header(subject_header)[0]
                    subject = decoded[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(decoded[1] or "utf-8")
                    logging.info(f"[{folder_name}] Permanently Deleting: {subject}")

            # Mark for deletion
            obj.store(num, '+FLAGS', '\\Deleted')
        except Exception as e:
            logging.error(f"Error processing message {num}: {e}")
    
    # Permanently wipe marked messages
    obj.expunge()
    logging.info(f"Finished cleaning {folder_name}.")

def archive_all(obj):
    """Moves all items from Inbox to All Mail (Archiving)."""
    logging.info("Starting Inbox Archival process...")
    obj.select('INBOX')
    
    while True:
        result, data = obj.search(None, 'ALL')
        ids = data[0].split()
        if not ids:
            logging.info("Inbox is empty! Work complete.")
            break

        for num in ids:
            try:
                res, msg_data = obj.fetch(num, '(BODY[HEADER.FIELDS (SUBJECT)])')
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        subject_header = msg.get("Subject", "No Subject")
                        decoded = decode_header(subject_header)[0]
                        subject = decoded[0]
                        if isinstance(subject, bytes):
                            subject = subject.decode(decoded[1] or "utf-8")
                        logging.info(f"[ARCHIVE] {subject}")

                # Copy to All Mail and mark for deletion from Inbox
                obj.copy(num, '"[Gmail]/All Mail"')
                obj.store(num, '+FLAGS', '\\Deleted')
            except Exception as e:
                logging.error(f"Error archiving message {num}: {e}")
        
        # Apply changes for this batch
        obj.expunge()

if __name__ == "__main__":
    if not EMAIL or not PASSWORD:
        logging.error("Missing credentials. Please check your .env file.")
    else:
        try:
            # Establish ONE connection for the whole session
            logging.info("Connecting to Gmail IMAP server...")
            obj = imaplib.IMAP4_SSL('imap.gmail.com', 993)
            obj.login(EMAIL, PASSWORD)

            # Run the sequence
            archive_all(obj)
            empty_folder(obj, '[Gmail]/Spam')  
            empty_folder(obj, '[Gmail]/Trash') 

            obj.logout()
            logging.info("Full cleanup complete.")
        except Exception as e:
            logging.critical(f"A fatal error occurred: {e}")
