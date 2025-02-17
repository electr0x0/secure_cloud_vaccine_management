import requests
import time
import random
import string
import statistics
from concurrent.futures import ThreadPoolExecutor
import json
from datetime import datetime, timedelta
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'load_test_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

BASE_URL = "http://127.0.0.1:8000"

def generate_random_string(length):
    """Generate a random string of fixed length"""
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for _ in range(length))

def generate_fake_user():
    """Generate fake user data"""
    email = f"{generate_random_string(8)}@test.com"
    return {
        "first_name": generate_random_string(6),
        "last_name": generate_random_string(6),
        "email": email,
        "password": generate_random_string(8),
        "user_type": "1",
        "identity_type": "nid",
        "identity_number": f"{random.randint(10000000000000000, 99999999999999999) if random.choice([True, False]) else random.randint(1000000000, 9999999999)}",
        "phone_number": f"+880{random.randint(10000000000, 99999999999)}",
        "dob": (datetime.now() - timedelta(days=random.randint(7300, 25550))).strftime("%Y-%m-%d"),
        "medical_conditions": [],
        "terms": True
    }

def register_user(user_data):
    """Make a registration request and measure time"""
    start_time = time.time()
    try:
        logger.info(f"Attempting registration for email: {user_data['email']}")
        logger.debug(f"Request payload: {json.dumps(user_data, indent=2)}")
        
        response = requests.post(f"{BASE_URL}/register", json=user_data)
        end_time = time.time()
        duration = end_time - start_time
        
        if response.status_code != 200:
            logger.error(f"Registration failed for {user_data['email']}")
            logger.error(f"Status Code: {response.status_code}")
            logger.error(f"Response: {response.text}")
        else:
            logger.info(f"Registration successful for {user_data['email']}")
        
        return {
            "success": response.status_code == 200,
            "duration": duration,
            "status_code": response.status_code,
            "email": user_data["email"],
            "password": user_data["password"],
            "response": response.text
        }
    except Exception as e:
        end_time = time.time()
        logger.error(f"Exception during registration: {str(e)}")
        return {
            "success": False,
            "duration": end_time - start_time,
            "error": str(e),
            "email": user_data["email"]
        }

def run_load_test(num_requests, concurrent_requests=10):
    """Run load test with specified number of requests"""
    logger.info(f"Starting load test with {num_requests} requests ({concurrent_requests} concurrent)")
    
    
    test_users = [generate_fake_user() for _ in range(num_requests)]
    
    
    total_start_time = time.time()
    
    
    results = []
    with ThreadPoolExecutor(max_workers=concurrent_requests) as executor:
        futures = [executor.submit(register_user, user) for user in test_users]
        for future in futures:
            results.append(future.result())
    
    # Calculate metrics
    total_duration = time.time() - total_start_time
    successful_requests = [r for r in results if r["success"]]
    failed_requests = [r for r in results if not r["success"]]
    
    durations = [r["duration"] for r in results]
    avg_duration = statistics.mean(durations)
    median_duration = statistics.median(durations)
    min_duration = min(durations)
    max_duration = max(durations)
    
    
    logger.info("\nLoad Test Results:")
    logger.info("=" * 50)
    logger.info(f"Total Time: {total_duration:.2f} seconds")
    logger.info(f"Total Requests: {num_requests}")
    logger.info(f"Successful Requests: {len(successful_requests)}")
    logger.info(f"Failed Requests: {len(failed_requests)}")
    logger.info(f"Requests per Second: {num_requests/total_duration:.2f}")
    logger.info("\nResponse Time Statistics (seconds):")
    logger.info(f"Average: {avg_duration:.3f}")
    logger.info(f"Median: {median_duration:.3f}")
    logger.info(f"Min: {min_duration:.3f}")
    logger.info(f"Max: {max_duration:.3f}")
    
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"load_test_results_{timestamp}.json"
    with open(results_file, 'w') as f:
        json.dump({
            "test_config": {
                "num_requests": num_requests,
                "concurrent_requests": concurrent_requests,
                "base_url": BASE_URL
            },
            "summary": {
                "total_duration": total_duration,
                "successful_requests": len(successful_requests),
                "failed_requests": len(failed_requests),
                "requests_per_second": num_requests/total_duration,
                "avg_duration": avg_duration,
                "median_duration": median_duration,
                "min_duration": min_duration,
                "max_duration": max_duration
            },
            "detailed_results": results
        }, f, indent=2)
    
    logger.info(f"\nDetailed results saved to {results_file}")

if __name__ == "__main__":
    NUM_REQUESTS = 10
    CONCURRENT_REQUESTS = 5
    
    run_load_test(NUM_REQUESTS, CONCURRENT_REQUESTS)