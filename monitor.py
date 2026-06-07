from urllib import response
import requests
import json
import time
import os
from dotenv import load_dotenv
from scraper import AmazonSession
from notifier import send_email_alert
from test_email import send_test_email

load_dotenv()

# Configuration
CHECK_INTERVAL_SECONDS = int(os.getenv("CHECK_INTERVAL_SECONDS", 300))
LAT = float(os.getenv("TARGET_LAT", 36.1690921))
LNG = float(os.getenv("TARGET_LNG", -115.1405767))
DISTANCE_MILES = int(os.getenv("TARGET_DISTANCE_MILES", 50))
raw_job_titles = os.getenv("TARGET_JOB_TITLES", "Amazon Fulfillment Center Warehouse Associate")
TARGET_JOB_LIST = [title.strip() for title in raw_job_titles.split(",")]

DB_FILE = "seen_jobs.json"
GRAPHQL_ENDPOINT = "https://hiring.amazon.com/graphql"

def load_seen_jobs():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, 'w') as f:
            json.dump([], f)
    with open(DB_FILE, 'r') as f:
        try:
            return set(json.load(f))
        except json.JSONDecodeError:
            return set()

def save_seen_jobs(seen_set):
    with open(DB_FILE, 'w') as f:
        json.dump(list(seen_set), f)

def get_headers(token):
    return {
        "authorization": token,
        "content-type": "application/json",
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
        "country": "United States",
        "iscanary": "false",
        "priority": "u=1, i",
        "sec-ch-ua-platform": '"Windows"',
        "referrer": "https://hiring.amazon.com/",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

def get_payload():
    """Generates the GraphQL payload"""
    return {
        "operationName": "searchJobCardsByLocation",
        "variables": {
            "searchJobRequest": {
                "locale": "en-US",
                "country": "United States",
                "containFilters": [
                    {"key": "jobTitle", "val": TARGET_JOB_LIST}
                ],
                "geoQueryClause": {
                    "lat": LAT,
                    "lng": LNG,
                    "distance": DISTANCE_MILES,
                    "unit":"mi"},
                "pageSize": 20
            }
        },
        "query": "query searchJobCardsByLocation($searchJobRequest: SearchJobRequest!) { searchJobCardsByLocation(searchJobRequest: $searchJobRequest) { jobCards { jobId jobTitle locationName } } }"
    }

def run_monitor():
    # Send test email on startup
    print("=" * 60)
    print("  SENDING STARTUP TEST EMAIL")
    print("=" * 60)
    print()
    send_test_email()
    print()
    print("=" * 60)
    print("  STARTING JOB MONITOR")
    print("=" * 60)
    print()
    
    session_manager = AmazonSession()
    seen_jobs = load_seen_jobs()
    token = session_manager.get_fresh_token()
    
    if not token:
        print("ERROR: Failed to obtain initial token. Cannot proceed.")
        print("This usually means Amazon changed their website structure.")
        print("Try running the container with updated dependencies or check if the website is accessible.")
        return

    while True:
        titles_str = ", ".join(TARGET_JOB_LIST)
        print(f"[{time.strftime('%H:%M:%S')}] Checking for [{titles_str}] within {DISTANCE_MILES} miles of ({LAT}, {LNG})...")
        
        try:
            response = requests.post(GRAPHQL_ENDPOINT, json=get_payload(), headers=get_headers(token))
            
            if response.status_code in [401, 403]:
                print(f"Token rejected (Status {response.status_code}). Attempting to refresh...")
                time.sleep(10) # Prevent rapid-fire loops
                new_token = session_manager.get_fresh_token()
                if new_token:
                    token = new_token
                    print("✓ Token refreshed successfully")
                else:
                    print("✗ Failed to refresh token - Amazon may have changed their website")
                    print("Waiting 60 seconds before retry...")
                    time.sleep(60)
                continue

            jobs = response.json().get("data", {}).get("searchJobCardsByLocation", {}).get("jobCards", [])

            new_found = False
            for job in jobs:
                if job['jobId'] not in seen_jobs:
                    print(f"New job found! {job['jobTitle']} - {job['locationName']} - {job['jobId']}")
                    send_email_alert(job['jobTitle'], job['locationName'], job['jobId'])
                    seen_jobs.add(job['jobId'])
                    new_found = True
            
            if new_found:
                save_seen_jobs(seen_jobs)
            else:
                print("No new jobs found.")

        except Exception as e:
            print(f"Error occurred: {e}")

        time.sleep(CHECK_INTERVAL_SECONDS)

if __name__ == "__main__":
    run_monitor()
