import requests
import time
import statistics
import json
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import Dict, List
import logging
import signal
import sys

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
    session = None
    try:
        # Create session with timeout
        session = requests.Session()
        # Add both connect and read timeouts
        session.timeout = (5, 30)  # (connect timeout, read timeout)
        
        headers = {
            'Connection': 'close'  # Ensure connection is closed after request
        }
        
        start_time = time.time()
        response = session.get(
            f"{base_url}/api/user/info",
            params={"token": jwt_token},
            headers=headers
        )
        duration = time.time() - start_time
        
        return {
            "success": response.status_code == 200,
            "duration": duration,
            "status_code": response.status_code,
            "jwt_token": jwt_token,
            "response": response.text
        }
    except requests.Timeout:
        logger.error("Request timed out")
        return {
            "success": False,
            "duration": 0,
            "status_code": 408,
            "jwt_token": jwt_token,
            "response": "Request timed out"
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
    finally:
        if session:
            session.close()

def run_decrypt_load_test(login_results_file: str, concurrent_requests: int):
    """Run load test for data decryption endpoint"""
    executor = None
    try:
        logger.info(f"Starting decrypt load test using tokens from {login_results_file}")
        
        # Load login results to get JWT tokens
        with open(login_results_file) as f:
            login_data = json.load(f)

        base_url = login_data["test_config"]["base_url"]
        jwt_tokens = [result["jwt_token"] for result in login_data["detailed_results"]]
        
        logger.info(f"Loaded {len(jwt_tokens)} tokens for testing")
        logger.info(f"Using {concurrent_requests} concurrent requests")

        # Run concurrent requests with timeout
        total_start_time = time.time()
        results = []
        
        executor = ThreadPoolExecutor(max_workers=concurrent_requests)
        futures = []
        
        # Submit all requests
        for token in jwt_tokens:
            future = executor.submit(make_user_info_request, token, base_url)
            futures.append(future)
        
        # Collect results with timeout
        for future in futures:
            try:
                result = future.result(timeout=60)
                results.append(result)
            except Exception as e:
                logger.error(f"Request failed: {str(e)}")
                results.append({
                    "success": False,
                    "duration": 0,
                    "status_code": 500,
                    "jwt_token": None,
                    "response": str(e)
                })

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

    except Exception as e:
        logger.error(f"Test execution failed: {str(e)}")
        raise
    finally:
        if executor:
            # Shutdown executor with timeout
            executor.shutdown(wait=True, cancel_futures=True)

if __name__ == "__main__":
    def signal_handler(signum, frame):
        logger.info("Received interrupt signal. Cleaning up...")
        sys.exit(1)
    
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        LOGIN_RESULTS_FILE = "login_load_test_results_20250216_184759.json"
        CONCURRENT_REQUESTS = 50  # Consider reducing this number
        
        run_decrypt_load_test(LOGIN_RESULTS_FILE, CONCURRENT_REQUESTS)
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        sys.exit(1) 