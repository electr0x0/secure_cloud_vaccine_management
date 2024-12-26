import requests
import time
import statistics
import json
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import Dict, List
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'decrypt_test_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def make_user_info_request(jwt_token: str, base_url: str) -> Dict:
    """Make a single request to get user info"""
    try:
        # Pass token as query parameter
        start_time = time.time()
        response = requests.get(
            f"{base_url}/api/user/info",
            params={"token": jwt_token}  # Changed from headers to query params
        )
        duration = time.time() - start_time
        
        if response.status_code != 200:
            logger.error(f"Request failed with status code {response.status_code}")
            logger.error(f"Response: {response.text}")
        else:
            logger.info(f"Successfully retrieved user info")

        return {
            "success": response.status_code == 200,
            "duration": duration,
            "status_code": response.status_code,
            "jwt_token": jwt_token,
            "response": response.text
        }
    except Exception as e:
        logger.error(f"Exception during request: {str(e)}")
        return {
            "success": False,
            "duration": 0,
            "status_code": 500,
            "jwt_token": jwt_token,
            "response": str(e)
        }

def run_decrypt_load_test(login_results_file: str, concurrent_requests: int):
    """Run load test for data decryption endpoint"""
    logger.info(f"Starting decrypt load test using tokens from {login_results_file}")
    
    # Load login results to get JWT tokens
    with open(login_results_file) as f:
        login_data = json.load(f)

    base_url = login_data["test_config"]["base_url"]
    jwt_tokens = [result["jwt_token"] for result in login_data["detailed_results"]]
    
    logger.info(f"Loaded {len(jwt_tokens)} tokens for testing")
    logger.info(f"Using {concurrent_requests} concurrent requests")

    # Run concurrent requests
    total_start_time = time.time()
    results = []
    with ThreadPoolExecutor(max_workers=concurrent_requests) as executor:
        futures = [
            executor.submit(make_user_info_request, token, base_url)
            for token in jwt_tokens
        ]
        for future in futures:
            results.append(future.result())

    # Calculate metrics
    total_duration = time.time() - total_start_time
    successful_requests = len([r for r in results if r["success"]])
    failed_requests = len(results) - successful_requests
    durations = [r["duration"] for r in results if r["success"]]

    if durations:
        avg_duration = statistics.mean(durations)
        median_duration = statistics.median(durations)
        min_duration = min(durations)
        max_duration = max(durations)
        requests_per_second = len(results) / total_duration
    else:
        avg_duration = median_duration = min_duration = max_duration = requests_per_second = 0

    # Prepare test results
    test_results = {
        "test_config": {
            "num_requests": len(jwt_tokens),
            "concurrent_requests": concurrent_requests,
            "base_url": base_url
        },
        "summary": {
            "total_duration": total_duration,
            "successful_requests": successful_requests,
            "failed_requests": failed_requests,
            "requests_per_second": requests_per_second,
            "avg_duration": avg_duration,
            "median_duration": median_duration,
            "min_duration": min_duration,
            "max_duration": max_duration
        },
        "detailed_results": results
    }

    # Save results to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"decrypt_test_results_{timestamp}.json"
    with open(output_file, "w") as f:
        json.dump(test_results, f, indent=2)

    logger.info("\nDecrypt Load Test Results:")
    logger.info("=" * 50)
    logger.info(f"Total Time: {total_duration:.2f} seconds")
    logger.info(f"Total Requests: {len(jwt_tokens)}")
    logger.info(f"Successful Requests: {successful_requests}")
    logger.info(f"Failed Requests: {failed_requests}")
    logger.info(f"Requests per Second: {requests_per_second:.2f}")
    logger.info("\nResponse Time Statistics (seconds):")
    logger.info(f"Average: {avg_duration:.3f}")
    logger.info(f"Median: {median_duration:.3f}")
    logger.info(f"Min: {min_duration:.3f}")
    logger.info(f"Max: {max_duration:.3f}")
    logger.info(f"\nDetailed results saved to {output_file}")

if __name__ == "__main__":
    LOGIN_RESULTS_FILE = "login_load_test_results_20241226_173710.json"
    CONCURRENT_REQUESTS = 10
    
    run_decrypt_load_test(LOGIN_RESULTS_FILE, CONCURRENT_REQUESTS) 