import requests
import time
import statistics
from concurrent.futures import ThreadPoolExecutor
import json
import os
from src.core.logger import get_logger
from src.core.config import settings

logger = get_logger(__name__)

def login_user(credentials, base_url):
    """Make a login request and measure time"""
    start_time = time.time()
    try:
        logger.info(f"Attempting login for email: {credentials['email']}")
        
        response = requests.post(f"{base_url}/login", json=credentials, timeout=10)
        end_time = time.time()
        duration = end_time - start_time
        
        if response.status_code != 200:
            logger.error(f"Login failed for {credentials['email']}")
            logger.error(f"Status Code: {response.status_code}")
            logger.error(f"Response: {response.text}")
        else:
            logger.info(f"Login successful for {credentials['email']}")
        
        return {
            "success": response.status_code == 200,
            "duration": duration,
            "status_code": response.status_code,
            "email": credentials["email"],
            "response": response.text
        }
    except requests.Timeout:
        end_time = time.time()
        logger.error(f"Request timed out for {credentials['email']}")
        return {
            "success": False,
            "duration": end_time - start_time,
            "status_code": 408,
            "email": credentials["email"],
            "error": "Request timed out"
        }
    except Exception as e:
        end_time = time.time()
        logger.error(f"Exception during login: {str(e)}")
        return {
            "success": False,
            "duration": end_time - start_time,
            "error": str(e),
            "email": credentials["email"]
        }

async def run_login_test(num_requests: int, concurrent_requests: int, base_url: str, previous_test_file: str = None) -> dict:
    """Run login benchmark test"""
    logger.info(f"Starting login test with {num_requests} requests ({concurrent_requests} concurrent)")
    
    # Get credentials from most recent register test
    if previous_test_file:
        try:
            with open(previous_test_file, 'r') as f:
                register_results = json.load(f)
                # Check if we have the new or old format
                if "detailed_results" in register_results:
                    # New format
                    successful_users = [
                        {
                            "email": result["email"],
                            "password": result["password"]
                        }
                        for result in register_results["detailed_results"]
                        if result.get("success", False)
                    ]
                else:
                    # Old format
                    successful_users = [
                        {
                            "email": result["email"],
                            "password": result["password"]
                        }
                        for result in register_results.get("test_results", [])
                        if result.get("success", False)
                    ]
        except Exception as e:
            logger.error(f"Failed to load previous test results: {str(e)}")
            raise
    else:
        from src.core.benchmark_runner import BenchmarkRunner
        runner = BenchmarkRunner()
        register_results = runner.get_most_recent_test_result("register")
        if not register_results:
            raise ValueError("No previous register test results found")
        
        # Extract from new format
        successful_users = [
            {
                "email": result["email"],
                "password": result["password"]
            }
            for result in register_results.get("detailed_results", [])
            if result.get("success", False)
        ]
    
    if not successful_users:
        raise ValueError("No successful registrations found in previous test")
    
    # Adjust num_requests if we don't have enough registered users
    if len(successful_users) < num_requests:
        logger.warning(f"Only {len(successful_users)} registered users available. Adjusting test size.")
        num_requests = len(successful_users)
    
    total_start_time = time.time()
    results = []
    
    # Run requests using ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=concurrent_requests) as executor:
        futures = [
            executor.submit(login_user, user, base_url)
            for user in successful_users[:num_requests]
        ]
        for future in futures:
            results.append(future.result())
    
    # Calculate metrics
    total_duration = time.time() - total_start_time
    successful_requests = [r for r in results if r["success"]]
    failed_requests = [r for r in results if not r["success"]]
    
    durations = [r["duration"] for r in results if r["success"]]
    if durations:
        avg_duration = statistics.mean(durations)
        min_duration = min(durations)
        max_duration = max(durations)
    else:
        avg_duration = min_duration = max_duration = 0
    
    # Log results
    logger.info("\nLoad Test Results:")
    logger.info("=" * 50)
    logger.info(f"Total Time: {total_duration:.2f} seconds")
    logger.info(f"Total Requests: {num_requests}")
    logger.info(f"Successful Requests: {len(successful_requests)}")
    logger.info(f"Failed Requests: {len(failed_requests)}")
    logger.info(f"Requests per Second: {num_requests/total_duration:.2f}")
    logger.info("\nResponse Time Statistics (seconds):")
    logger.info(f"Average: {avg_duration:.3f}")
    logger.info(f"Min: {min_duration:.3f}")
    logger.info(f"Max: {max_duration:.3f}")
    
    return {
        "total_duration": total_duration,
        "successful_requests": len(successful_requests),
        "failed_requests": len(failed_requests),
        "avg_duration": avg_duration,
        "min_duration": min_duration,
        "max_duration": max_duration,
        "requests_per_second": num_requests/total_duration,
        "detailed_results": results
    }

if __name__ == "__main__":
    NUM_REQUESTS = 100 
    CONCURRENT_REQUESTS = 10
    BASE_URL = "http://localhost:8000"
    
    import asyncio
    asyncio.run(run_login_test(NUM_REQUESTS, CONCURRENT_REQUESTS, BASE_URL)) 