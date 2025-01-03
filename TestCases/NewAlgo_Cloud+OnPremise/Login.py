import requests
import time
import statistics
from concurrent.futures import ThreadPoolExecutor
import json
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'login_load_test_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

BASE_URL = "http://47.129.237.229:8000"

def load_test_users(results_file):
    """Load test users from previous registration results"""
    with open(results_file, 'r') as f:
        data = json.load(f)
    
    return [(result["email"], result["password"]) 
            for result in data["detailed_results"] 
            if result["success"]]

def login_user(credentials):
    """Make a login request and measure time"""
    email, password = credentials
    start_time = time.time()
    try:
        logger.info(f"Attempting login for email: {email}")
        
        login_data = {
            "email": email,
            "password": password
        }
        
        response = requests.post(f"{BASE_URL}/login", json=login_data)
        end_time = time.time()
        duration = end_time - start_time
        
        if response.status_code != 200:
            logger.error(f"Login failed for {email}")
            logger.error(f"Status Code: {response.status_code}")
            logger.error(f"Response: {response.text}")
        else:
            logger.info(f"Login successful for {email}")
        
        return {
            "success": response.status_code == 200,
            "duration": duration,
            "status_code": response.status_code,
            "email": email,
            "response": response.text,
            "jwt_token": response.json().get("access_token") if response.status_code == 200 else None
        }
    except Exception as e:
        end_time = time.time()
        logger.error(f"Exception during login: {str(e)}")
        return {
            "success": False,
            "duration": end_time - start_time,
            "error": str(e),
            "email": email
        }

def run_login_load_test(results_file, concurrent_requests=10):
    """Run login load test using registered users"""
    logger.info(f"Loading test users from {results_file}")
    test_users = load_test_users(results_file)
    num_requests = len(test_users)
    
    logger.info(f"Starting login load test with {num_requests} users ({concurrent_requests} concurrent)")
    
    total_start_time = time.time()
    
    results = []
    with ThreadPoolExecutor(max_workers=concurrent_requests) as executor:
        futures = [executor.submit(login_user, user) for user in test_users]
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
    
    # Log results
    logger.info("\nLogin Load Test Results:")
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
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"login_load_test_results_{timestamp}.json"
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
    REGISTRATION_RESULTS_FILE = "load_test_results_20241227_205005.json"
    CONCURRENT_REQUESTS = 10
    
    run_login_load_test(REGISTRATION_RESULTS_FILE, CONCURRENT_REQUESTS) 