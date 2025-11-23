import requests
import uuid
import random
import time
from concurrent.futures import ThreadPoolExecutor

# Configuration
API_URL = os.environ.get("API_URL", "http://localhost:8000/notifications")
TOTAL_MESSAGES = 1000
CONCURRENCY = 10

def send_notification(i):
    payload = {
        "recipient": f"user{i}@example.com",
        "subject": f"Test Notification {i}",
        "body": f"This is a test message number {i}",
        "fail": random.random() < 0.1 # 10% failure rate
    }
    
    try:
        response = requests.post(API_URL, json=payload)
        if response.status_code == 202:
            return f"Success: {i}"
        else:
            return f"Failed: {i} - {response.status_code}"
    except Exception as e:
        return f"Error: {i} - {str(e)}"

def main():
    print(f"Starting seed of {TOTAL_MESSAGES} messages to {API_URL}")
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=CONCURRENCY) as executor:
        results = list(executor.map(send_notification, range(TOTAL_MESSAGES)))
        
    success_count = sum(1 for r in results if r.startswith("Success"))
    duration = time.time() - start_time
    
    print(f"\nCompleted in {duration:.2f} seconds")
    print(f"Successful: {success_count}")
    print(f"Failed/Error: {TOTAL_MESSAGES - success_count}")
    print(f"Rate: {TOTAL_MESSAGES / duration:.2f} req/s")

if __name__ == "__main__":
    main()
