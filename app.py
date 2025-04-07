import os
from flask import Flask, jsonify
from flask_cors import CORS
from scraper import scrape_all_facilities

app = Flask(__name__)
CORS(app)

# Disable Flask debug mode in production
app.config['DEBUG'] = False

# Shared data store
facilities_data = {}

# Initialize the data manually
def initialize_data():
    global facilities_data
    facilities_data = scrape_all_facilities()

# Manually initialize data (called once when the app starts)
initialize_data()

@app.route('/facilities', methods=['GET'])
def get_facilities():
    return jsonify(facilities_data)

@app.route('/scrape', methods=['POST'])
def scrape():
    global facilities_data
    facilities_data = scrape_all_facilities()
    return jsonify(facilities_data)

@app.route('/', methods=['GET'])
def index():
    return jsonify({"message": "Welcome to the Gym Facilities API!"})

if __name__ == "__main__":
    app.run(debug=False)  # Ensure debug is off for production
