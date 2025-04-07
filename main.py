from flask import Flask, request, jsonify
from flask_cors import CORS
import json
from scraper import scrape_all_facilities

app = Flask(__name__)
CORS(app)

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

if __name__ == "__main__":
    app.run(debug=True)
