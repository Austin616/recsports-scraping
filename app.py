import os
from flask import Flask, jsonify
from flask_cors import CORS
from scraper import scrape_all_facilities
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Disable Flask debug mode in production
app.config['DEBUG'] = False

# Shared data store
facilities_data = {}
last_scrape_time = None  # Variable to store the last scrape time

# Initialize the data manually
def initialize_data():
    global facilities_data, last_scrape_time
    facilities_data = scrape_all_facilities()
    last_scrape_time = datetime.utcnow()  # Store the current time as the last scrape time

# Manually initialize data (called once when the app starts)
initialize_data()

@app.route('/facilities', methods=['GET'])
def get_facilities():
    response = {
        "facilities": facilities_data,
        "last_scrape_time": last_scrape_time.strftime('%Y-%m-%d %H:%M:%S') if last_scrape_time else "Not yet scraped"
    }
    return jsonify(response)

@app.route('/scrape', methods=['POST'])
def scrape():
    global facilities_data, last_scrape_time
    facilities_data = scrape_all_facilities()
    last_scrape_time = datetime.utcnow()  # Update the last scrape time
    return jsonify({"message": "Scraping successful", "last_scrape_time": last_scrape_time.strftime('%Y-%m-%d %H:%M:%S')})

@app.route('/', methods=['GET'])
def index():
    return jsonify({"message": "Welcome to the Gym Facilities API!"})

if __name__ == "__main__":
    app.run(debug=False)  # Ensure debug is off for production
