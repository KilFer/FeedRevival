import os
import imaplib
import email
from email.header import decode_header
from pymongo import MongoClient
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=os.getenv('LOG_LEVEL', 'INFO'),
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# MongoDB connection
client = MongoClient(os.getenv('MONGO_URI'))
db = client[os.getenv('MONGO_DB_NAME')]
feeds_collection = db[os.getenv('MONGO_COLLECTION_NAME')]
emails_collection = db['emails']


# Initialize server info
def connect_to_imap():
    mail = imaplib.IMAP4_SSL(os.getenv('IMAP_SERVER'))
    mail.login(os.getenv('IMAP_USER'), os.getenv('IMAP_PASSWORD'))
    return mail


# Get email an generate mongo data for the email
def process_email(mail, folder, email_id):
    _, msg_data = mail.fetch(email_id, "(RFC822)")
    email_body = msg_data[0][1]
    email_message = email.message_from_bytes(email_body)

    subject, encoding = decode_header(email_message["Subject"])[0]
    if isinstance(subject, bytes):
        subject = subject.decode(encoding or "utf-8")

    sender = email_message["From"]
    date = email_message["Date"]

    body = ""
    if email_message.is_multipart():
        for part in email_message.walk():
            if part.get_content_type() == "text/plain":
                body = part.get_payload(decode=True).decode()
    else:
        body = email_message.get_payload(decode=True).decode()

    return {
        "folder": folder,
        "subject": subject,
        "sender": sender,
        "date": date,
        "body": body,
        "email_id": email_id.decode()
    }


def process_emails():
    mail = connect_to_imap()

    for feed in feeds_collection.find():
        folder = feed['_id']
        logger.info(f"Processing folder: {folder}")

        try:
            mail.select(folder)
            _, search_data = mail.search(None, "UNSEEN")

            for num in search_data[0].split():
                email_data = process_email(mail, folder, num)
                emails_collection.insert_one(email_data)
                logger.info(f"Saved email: {email_data['subject']}")

                # Mark the email as seen?
                mail.store(num, '+FLAGS', '(\Seen)')

        except Exception as e:
            logger.error(f"Error processing folder {folder}: {str(e)}")

    mail.logout()


if __name__ == "__main__":
    process_emails()