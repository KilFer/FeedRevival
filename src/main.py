import os
import logging
import threading
import time
import schedule
from dotenv import load_dotenv
from front_server import app
from email_processor import process_emails

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=os.getenv('LOG_LEVEL', 'INFO'),
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_email_processor():
    logger.info("Running email processor")
    process_emails()

def run_scheduler():
    schedule.every(15).minutes.do(run_email_processor)
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    # Start the email processor scheduler in a separate thread
    scheduler_thread = threading.Thread(target=run_scheduler)
    scheduler_thread.start()

    # Run the Flask app
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 8255)))
