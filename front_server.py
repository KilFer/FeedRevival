from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
import string
import logging
import random
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=os.getenv('LOG_LEVEL', 'INFO'), format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

# MongoDB connection
client = MongoClient(os.getenv('MONGO_URI'))
db = client[os.getenv('MONGO_DB_NAME')]
feeds_collection = db[os.getenv('MONGO_COLLECTION_NAME')]


def generate_id(length=12):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = request.form['name']
        feed_id = generate_id()

        # Save to MongoDB
        new_feed = {
            '_id': feed_id,
            'name': name
        }
        feeds_collection.insert_one(new_feed)

        logger.info(f"New feed created: {new_feed}")  # Print to console
        return redirect(url_for('generated', name=name, feed_id=feed_id))
    return render_template('index.html')


@app.route('/generated')
def generated():
    name = request.args.get('name', '')
    feed_id = request.args.get('feed_id', '')
    return render_template('generated.html', name=name, feed_id=feed_id)
