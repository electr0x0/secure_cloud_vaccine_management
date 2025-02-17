import requests
import time
import random
import string
import statistics
from concurrent.futures import ThreadPoolExecutor
import json
from datetime import datetime, timedelta
from src.core.logger import get_logger

logger = get_logger(__name__)

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

def register_user(user_data, base_url):
    """Make a registration request and measure time"""
    start_time = time.time()
    try:
        logger.info(f"Attempting Encryption for user email: {user_data['email']}")
        logger.debug(f"Request payload: {json.dumps(user_data, indent=2)}")
        
        response = requests.post(f"{base_url}/register", json=user_data, timeout=10)
        end_time = time.time()
        duration = end_time - start_time
        
        if response.status_code != 200:
            logger.error(f"Encryption failed for {user_data['email']}")
            logger.error(f"Status Code: {response.status_code}")
            logger.error(f"Response: {response.text}")
        else:
            logger.info(f"Encryption successful for {user_data['email']}")
        
        return {
            "success": response.status_code == 200,
            "duration": duration,
            "status_code": response.status_code,
            "email": user_data["email"],
            "password": user_data["password"],
            "response": response.text
        }
    except requests.Timeout:
        end_time = time.time()
        logger.error(f"Request timed out for {user_data['email']}")
        return {
            "success": False,
            "duration": end_time - start_time,
            "status_code": 408,
            "email": user_data["email"],
            "password": user_data["password"],
            "error": "Request timed out"
        }
    except Exception as e:
        end_time = time.time()
        logger.error(f"Exception during registration: {str(e)}")
        return {
            "success": False,
            "duration": end_time - start_time,
            "error": str(e),
            "email": user_data["email"],
            "password": user_data["password"]
        }

async def run_register_test(num_requests: int, concurrent_requests: int, base_url: str) -> dict:
    """Run register benchmark test"""
    logger.info(f"Starting load test with {num_requests} requests ({concurrent_requests} concurrent)")
    
    # Generate test users
    test_users = [generate_fake_user() for _ in range(num_requests)]
    total_start_time = time.time()
    
    # Run requests using ThreadPoolExecutor
    results = []
    with ThreadPoolExecutor(max_workers=concurrent_requests) as executor:
        futures = [executor.submit(register_user, user, base_url) for user in test_users]
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
    asyncio.run(run_register_test(NUM_REQUESTS, CONCURRENT_REQUESTS, BASE_URL)) 