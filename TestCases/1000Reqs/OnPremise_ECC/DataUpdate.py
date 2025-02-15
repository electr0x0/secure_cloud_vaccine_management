import requests
import time
import statistics
import json
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, date
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'update_test_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def make_update_request(jwt_token: str, base_url: str) -> dict:
    """Make a single request to update user info"""
    try:
        # Sample update data following UserUpdate schema
        update_data = {
            "first_name": "Updated",
            "last_name": "User",
            "identity_type": "nid",
            "identity_number": "1234567890",
            "phone_number": "+8801712345678",
            "medical_conditions": [
                {
                    "condition_name": "Allergy",
                    "details": "Pollen allergy",
                    "severity": "Mild",
                    "diagnosed_date": "2024-01-01"
                }
            ],
            "dob": "1990-01-01",
            "token": jwt_token
        }

        start_time = time.time()
        response = requests.post(
            f"{base_url}/api/user/update",
            json=update_data
        )
        duration = time.time() - start_time
        
        if response.status_code != 200:
            logger.error(f"Request failed with status code {response.status_code}")
            logger.error(f"Response: {response.text}")
        else:
            logger.info(f"Successfully updated user info")

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

def run_update_load_test(decrypt_results_file: str, concurrent_requests: int):
    """Run load test for user update endpoint"""
    logger.info(f"Starting update load test using tokens from {decrypt_results_file}")
    
    # Load decrypt results to get JWT tokens
    with open(decrypt_results_file) as f:
        decrypt_data = json.load(f)

    base_url = decrypt_data["test_config"]["base_url"]
    jwt_tokens = [result["jwt_token"] for result in decrypt_data["detailed_results"] if result["success"]]
    
    logger.info(f"Loaded {len(jwt_tokens)} tokens for testing")
    logger.info(f"Using {concurrent_requests} concurrent requests")

    # Run concurrent requests
    total_start_time = time.time()
    results = []
    with ThreadPoolExecutor(max_workers=concurrent_requests) as executor:
        futures = [
            executor.submit(make_update_request, token, base_url)
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
    output_file = f"update_test_results_{timestamp}.json"
    with open(output_file, "w") as f:
        json.dump(test_results, f, indent=2)

    logger.info("\nUpdate Load Test Results:")
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
    DECRYPT_RESULTS_FILE = "decrypt_test_results_20250215_190415.json"
    CONCURRENT_REQUESTS = 100
    
    run_update_load_test(DECRYPT_RESULTS_FILE, CONCURRENT_REQUESTS) 