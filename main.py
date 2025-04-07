from flask import Flask, jsonify
from flask_cors import CORS
from scraper import scrape_all_facilities
import os

app = Flask(__name__)
CORS(app)

# Shared data store
facilities_data = {}
facilities_data = scrape_all_facilities()

@app.route('/', methods=['GET'])
def index():
    return jsonify({"message": "Welcome to the UT RecSports Scraper API!"})

@app.route('/facilities', methods=['GET'])
def get_facilities():
    return jsonify(facilities_data)

@app.route('/scrape', methods=['POST'])
def scrape():
    global facilities_data
    facilities_data = scrape_all_facilities()
    return jsonify(facilities_data)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
