import asyncio
from datetime import datetime
from typing import Optional, Dict
import os
import json
from src.core.logger import get_logger
from src.core.config import settings

logger = get_logger(__name__)

class BenchmarkRunner:
    def __init__(self):
        self.current_test_id = None
        
        # Create results directory if it doesn't exist
        if not os.path.exists(settings.RESULTS_DIR):
            os.makedirs(settings.RESULTS_DIR)

    def generate_test_id(self, test_type: str) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{test_type}_{timestamp}"

    async def run_test(self, test_type: str, num_requests: int, concurrent_requests: int, 
                      base_url: str, previous_test_file: str = None) -> Dict:
        """Run a benchmark test"""
        # Generate test ID first
        test_id = self.generate_test_id(test_type)
        self.current_test_id = test_id
        
        # Create initial test state
        test_state = {
            "test_id": test_id,
            "test_type": test_type,
            "start_time": datetime.now().isoformat(),
            "total_requests": num_requests,
            "status": "running",
            "base_url": base_url
        }

       
        result_file = os.path.join(settings.RESULTS_DIR, f"{test_id}.json")

        try:
            # Save initial state
            with open(result_file, 'w') as f:
                json.dump(test_state, f, indent=2)

            
            if test_type == "register":
                from src.tests.register_test import run_register_test
                results = await run_register_test(num_requests, concurrent_requests, base_url)
            elif test_type == "login":
                from src.tests.login_test import run_login_test
                results = await run_login_test(num_requests, concurrent_requests, base_url, previous_test_file)
            elif test_type == "decrypt":
                from src.tests.decrypt_test import run_decrypt_test
                results = await run_decrypt_test(num_requests, concurrent_requests, base_url, previous_test_file)
            else:
                raise ValueError(f"Unknown test type: {test_type}")

            # Update test state with results
            test_state.update({
                "end_time": datetime.now().isoformat(),
                "status": "completed",
                **results
            })

            
            with open(result_file, 'w') as f:
                json.dump(test_state, f, indent=2)

            return test_state

        except Exception as e:
            logger.error(f"Test failed: {str(e)}")
            
            error_state = {
                "test_id": test_id,  # Ensure test_id is included
                "test_type": test_type,
                "start_time": test_state["start_time"],
                "end_time": datetime.now().isoformat(),
                "status": "failed",
                "error": str(e),
                "total_requests": num_requests,
                "base_url": base_url
            }
            
            # Save error state
            with open(result_file, 'w') as f:
                json.dump(error_state, f, indent=2)
            
            return error_state

    async def get_test_result(self, test_id: str) -> Optional[Dict]:
        """Get test result by ID from file"""
        try:
            result_file = os.path.join(settings.RESULTS_DIR, f"{test_id}.json")
            if not os.path.exists(result_file):
                return None
                
            with open(result_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to get test result: {str(e)}")
            return None 

    def get_most_recent_test_result(self, test_type: str) -> Optional[Dict]:
        """Get the most recent test result for a specific test type"""
        try:
            # List all files in results directory
            files = [f for f in os.listdir(settings.RESULTS_DIR) 
                    if f.startswith(test_type) and f.endswith('.json')]
            
            if not files:
                return None
            
            # Sort by timestamp (which is part of the filename)
            files.sort(reverse=True)
            latest_file = files[0]
            
            # Read and return the file contents
            with open(os.path.join(settings.RESULTS_DIR, latest_file), 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to get recent test result: {str(e)}")
            return None 