import re
import aiohttp
import json
import time
import os
from src.core.logger import get_logger
from src.core.config import settings

logger = get_logger(__name__)

async def run_decrypt_test(num_requests: int, concurrent_requests: int, base_url: str, login_results_file: str) -> dict:
    """Run decrypt load test using tokens from login test"""
    # Load tokens from login test results
    with open(login_results_file, 'r') as f:
        login_data = json.load(f)
    
    tokens = []
    for result in login_data["detailed_results"]:
        if result["success"]:
            result_json = json.loads(result["response"])
            if "access_token" in result_json:
                print(result_json["access_token"])
                tokens.append(result_json["access_token"])

    if not tokens:
        raise ValueError("No valid tokens found in login results")

    results = []
    start_time = time.time()

    async with aiohttp.ClientSession() as session:
        for i in range(num_requests):
            token = tokens[i % len(tokens)]
            try:
                req_start = time.time()
                async with session.get(
                    f"{base_url}/api/user/info?token={token}",
                    timeout=30
                ) as response:
                    duration = time.time() - req_start
                    text = await response.text()
                    
                    success = response.status == 200
                    if not success:
                        logger.error(f"Decrypt failed: {text}")

                    results.append({
                        "success": success,
                        "duration": duration,
                        "status_code": response.status,
                        "token": token,
                        "response": text
                    })
                logger.info(f"{i+1}/{num_requests} Decryption completed")

            except Exception as e:
                logger.error(f"Request failed: {str(e)}")
                results.append({
                    "success": False,
                    "duration": 0,
                    "status_code": 500,
                    "token": token,
                    "error": str(e)
                })

    end_time = time.time()
    total_duration = end_time - start_time
    successful = [r for r in results if r["success"]]
    durations = [r["duration"] for r in successful]

    summary = {
        "total_duration": total_duration,
        "successful_requests": len(successful),
        "failed_requests": len(results) - len(successful),
        "avg_duration": sum(durations) / len(durations) if durations else 0,
        "min_duration": min(durations) if durations else 0,
        "max_duration": max(durations) if durations else 0,
        "requests_per_second": len(results) / total_duration
    }
    
    logger.info(f"""Decrypt test completed. Summary:
                \nTotal Duration: {total_duration}
                \nSuccessful Requests: {len(successful)}
                \nFailed Requests: {len(results) - len(successful)}
                \nAverage Duration: {sum(durations) / len(durations) if durations else 0}
                \nMinimum Duration: {min(durations) if durations else 0}
                \nMaximum Duration: {max(durations) if durations else 0}
                \nRequests per Second: {len(results) / total_duration}""")

    # Save results to file
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    
    result = {
                "num_requests": num_requests,
                "concurrent_requests": concurrent_requests,
                "base_url": base_url,
                "timestamp": timestamp,
                "login_results": login_results_file,
                **summary,
                "detailed_results": results
            } 

    return result