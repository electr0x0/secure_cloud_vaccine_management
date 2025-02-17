from flask import Flask, render_template, jsonify, request, send_from_directory
from src.core.benchmark_runner import BenchmarkRunner
from src.core.logger import get_logger
import os
import json
import asyncio
from src.core.config import settings
from datetime import datetime
import requests
from statistics import mean
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'

benchmark_runner = BenchmarkRunner()
logger = get_logger(__name__)

# Create event loop for async operations
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

@app.route('/')
def index():
    """Render main dashboard"""
    return render_template('index.html')


@app.route('/logs')
def get_logs():
    """Get recent logs"""
    try:
        log_file = os.path.join(settings.LOG_DIR, f'benchmark_{datetime.now().strftime("%Y%m%d")}.log')
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                logs = f.readlines()[-100:]  # Get last 100 lines
                # Clean up the logs
                logs = [log.strip() for log in logs if log.strip()]
                return jsonify(logs)
        else:
            return jsonify([])
    except Exception as e:
        logger.error(f"Failed to get logs: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/benchmark/run', methods=['POST'])
def run_benchmark():
    """Start a new benchmark test"""
    try:
        data = request.get_json()
        
        # Validate and convert numeric fields
        try:
            num_requests = int(data.get("num_requests", 0))
            concurrent_requests = int(data.get("concurrent_requests", 0))
        except (ValueError, TypeError):
            return jsonify({"error": "num_requests and concurrent_requests must be valid integers"}), 400

        # Validate required fields
        if not all([data.get("test_type"), num_requests, concurrent_requests, data.get("base_url")]):
            return jsonify({"error": "Missing required fields"}), 400

        # For login/decrypt tests, get the most recent register test results
        previous_test_file = None
        if data["test_type"] == "login":
            register_result = benchmark_runner.get_most_recent_test_result("register")
            if register_result:
                previous_test_file = os.path.join(settings.RESULTS_DIR, f"{register_result['test_id']}.json")
            else:
                return jsonify({"error": "No register test results found. Please run register test first."}), 400
        elif data["test_type"] == "decrypt":
            login_result = benchmark_runner.get_most_recent_test_result("login")
            if login_result:
                previous_test_file = os.path.join(settings.RESULTS_DIR, f"{login_result['test_id']}.json")
            else:
                return jsonify({"error": "No login test results found. Please run login test first."}), 400
        
        # Run the benchmark
        result = loop.run_until_complete(
            benchmark_runner.run_test(
                test_type=data["test_type"],
                num_requests=num_requests,
                concurrent_requests=concurrent_requests,
                base_url=data["base_url"],
                previous_test_file=previous_test_file
            )
        )

        if not result or "test_id" not in result:
            return jsonify({"error": "Invalid test result"}), 500

        response = {
            "message": "Benchmark completed" if result.get("status") == "completed" else "Benchmark failed",
            "test_id": result["test_id"],
            "status": result.get("status", "unknown")
        }

        if result.get("status") == "failed":
            response["error"] = result.get("error", "Unknown error")
            return jsonify(response), 500

        return jsonify(response)

    except Exception as e:
        logger.error(f"Failed to run benchmark: {str(e)}")
        return jsonify({
            "error": str(e),
            "message": "Benchmark failed",
            "status": "failed"
        }), 500

@app.route('/api/benchmark/history')
def get_history():
    """Get history of all benchmark tests"""
    try:
        results = []
        for filename in os.listdir(settings.RESULTS_DIR):
            if filename.endswith('.json'):
                with open(os.path.join(settings.RESULTS_DIR, filename), 'r') as f:
                    test_result = json.load(f)
                    
                    if test_result["test_type"] == "register":
                            test_result["test_type"] = "encrypt"
                    
                    try:              
                            
                        results.append({
                                "test_id": test_result["test_id"],
                                "timestamp": test_result["start_time"].split('T')[0],
                                "test_type": test_result["test_type"],
                                "num_requests": test_result["total_requests"],
                                "successful_requests": test_result.get("successful_requests", 0),
                                "failed_requests": test_result.get("failed_requests", 0),
                                "avg_duration": test_result.get("avg_duration", 0),
                                "requests_per_second": test_result.get("requests_per_second", 0)
                            })
                        
                        
                    except Exception as e:
                        pass

        return jsonify(sorted(results, key=lambda x: x["timestamp"], reverse=True))
    except Exception as e:
        logger.error(f"Failed to get history: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/benchmark/result/<test_id>')
def get_test_result(test_id):
    """Get detailed results for a specific test"""
    try:
        possible_files = [
            f"{test_id}.json",
            f"register_test_{test_id}.json",
            f"login_test_{test_id}.json",
            f"decrypt_test_{test_id}.json"
        ]

        for filename in possible_files:
            result_file = os.path.join(settings.RESULTS_DIR, filename)
            if os.path.exists(result_file):
                with open(result_file, 'r') as f:
                    test_result = json.load(f)
                    if test_result["test_type"] == "register":
                        test_result["test_type"] = "encrypt"
                    return jsonify(test_result)

        return jsonify({"error": "Test result not found"}), 404
    except Exception as e:
        logger.error(f"Failed to get test result: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/metrics')
def get_metrics():
    """Get combined metrics for encrypt/decrypt operations"""
    try:
        # Test server latency (ping)
        target_server = "http://127.0.0.1:8000"  # Hardcoded server
        ping_times = []
        for _ in range(3):  # Take average of 3 pings
            start = time.time()
            try:
                requests.get(target_server, timeout=2)
                ping_times.append((time.time() - start) * 1000)  # Convert to ms
            except:
                ping_times.append(0)
        avg_ping = mean(ping_times) if any(ping_times) else 0

        # Get all test results
        encrypt_tests = []
        decrypt_tests = []
        
        for filename in os.listdir(settings.RESULTS_DIR):
            if not filename.endswith('.json'):
                continue
                
            with open(os.path.join(settings.RESULTS_DIR, filename), 'r') as f:
                test = json.load(f)
                if test["test_type"] == "register":  # This is encrypt
                    encrypt_tests.append(test)
                elif test["test_type"] == "decrypt":
                    decrypt_tests.append(test)

        # Calculate metrics
        def calculate_test_metrics(tests):
            if not tests:
                return {
                    "success_rate": 0,
                    "avg_response_time": 0,
                    "requests_per_second": 0,
                    "total_requests": 0,
                    "total_tests": 0,
                    "test_durations": []  # For timeline graph
                }

            success_rates = []
            response_times = []
            req_per_second = []
            test_durations = []  # For timeline graph

            for test in tests:
                total = test.get("total_requests", 0)
                success = test.get("successful_requests", 0)
                if total > 0:
                    success_rates.append((success / total) * 100)
                response_times.append(test.get("avg_duration", 0))
                req_per_second.append(test.get("requests_per_second", 0))
                
                # Add test duration data
                test_durations.append({
                    "name": test["test_id"],
                    "duration": test.get("total_duration", 0),
                    "requests": total,
                    "timestamp": test["start_time"]
                })

            return {
                "success_rate": mean(success_rates) if success_rates else 0,
                "avg_response_time": mean(response_times) if response_times else 0,
                "requests_per_second": mean(req_per_second) if req_per_second else 0,
                "total_requests": sum(t.get("total_requests", 0) for t in tests),
                "total_tests": len(tests),
                "test_durations": sorted(test_durations, key=lambda x: x["timestamp"])[-10:]  # Last 10 tests
            }

        encrypt_metrics = calculate_test_metrics(encrypt_tests)
        decrypt_metrics = calculate_test_metrics(decrypt_tests)

        return jsonify({
            "server_latency": avg_ping,
            "encrypt": encrypt_metrics,
            "decrypt": decrypt_metrics
        })

    except Exception as e:
        logger.error(f"Failed to get metrics: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(
        debug=True,
        host='0.0.0.0',
        port=5000,
        use_reloader=True
    ) 