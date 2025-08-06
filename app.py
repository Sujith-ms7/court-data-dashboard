import sqlite3
import json
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, Response
from flask_cors import CORS

# This line imports the CourtScraper class from your scrapper.py file
from scrapper import CourtScraper 

# --- Database Setup ---
DB_NAME = 'casedata.db'

def init_db():
    """Initializes the database and creates the 'cases' table if it doesn't exist."""
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cases (
            case_id TEXT PRIMARY KEY,
            data TEXT NOT NULL,
            last_updated TIMESTAMP NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# --- Flask App Setup ---
app = Flask(__name__)
CORS(app)

# Create a single, reusable instance of our scraper
scraper = CourtScraper()

def get_case_from_db(case_id: str) -> dict | None:
    """Queries the database for a fresh copy of a specific case."""
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT data, last_updated FROM cases WHERE case_id = ?", (case_id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        data, last_updated_str = row
        last_updated = datetime.fromisoformat(last_updated_str)
        # Data is "fresh" if it's less than 24 hours old
        if datetime.now() - last_updated < timedelta(hours=24):
            print(f"CACHE HIT: Found fresh data for {case_id} in DB.")
            return json.loads(data)
    
    print(f"CACHE MISS: No fresh data for {case_id}. Need to scrape.")
    return None

def save_case_to_db(case_id: str, data: dict):
    """Saves or updates a case's data in the database."""
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute(
        "REPLACE INTO cases (case_id, data, last_updated) VALUES (?, ?, ?)",
        (case_id, json.dumps(data), datetime.now())
    )
    conn.commit()
    conn.close()
    print(f"CACHE WRITE: Saved data for {case_id} to DB.")

@app.route('/api/scrape', methods=['POST'])
def handle_scrape_request() -> Response:
    """API endpoint that uses the database cache before performing a live scrape."""
    case_details = request.get_json()
    case_id = f"{case_details['type']}-{case_details['number']}-{case_details['year']}"

    # 1. Check the database first
    cached_data = get_case_from_db(case_id)
    if cached_data:
        cached_data['source'] = 'Database Cache'
        return jsonify(cached_data)

    # 2. If not in cache, perform a live scrape
    scrape_result = scraper.scrape_case(case_details)
    
    if scrape_result["success"]:
        # 3. Save the new data to the DB before returning it
        save_case_to_db(case_id, scrape_result["data"])
        return jsonify(scrape_result["data"])
    else:
        # If the live scrape fails, return an error
        return jsonify({"message": scrape_result["message"]}), 500

# --- App Startup ---
if __name__ == '__main__':
    init_db()  # Initialize the database when the app starts
    app.run(debug=True)