import requests
import time
import random
import string
import statistics
from concurrent.futures import ThreadPoolExecutor
import json
from datetime import datetime, timedelta
import logging
import subprocess
import platform
import socket
from urllib.parse import urlparse
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import psutil

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

def get_server_latency(url):
    """Measure server latency using TCP connection timing"""
    try:
        parsed_url = urlparse(url)
        host = parsed_url.hostname
        port = parsed_url.port or (443 if parsed_url.scheme == 'https' else 80)
        
        if not host:
            logger.error("Could not extract hostname from URL")
            return None
            
        # Measure TCP connection time
        start_time = time.time()
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)  # 2 second timeout
            sock.connect((host, port))
            latency_ms = (time.time() - start_time) * 1000  # Convert to milliseconds
            sock.close()
            return latency_ms
        except socket.error as e:
            logger.error(f"TCP connection failed to {host}:{port} - {str(e)}")
            return None
            
    except Exception as e:
        logger.error(f"Error measuring server latency: {str(e)}")
        return None

def get_network_stats():
    """Get current network statistics"""
    try:
        net_io = psutil.net_io_counters()
        return {
            "bytes_sent": net_io.bytes_sent,
            "bytes_recv": net_io.bytes_recv,
            "packets_sent": net_io.packets_sent,
            "packets_recv": net_io.packets_recv,
            "errin": net_io.errin,
            "errout": net_io.errout,
            "dropin": net_io.dropin,
            "dropout": net_io.dropout
        }
    except Exception as e:
        logger.error(f"Error getting network stats: {str(e)}")
        return None

def get_dns_resolution_time(host):
    """Measure DNS resolution time"""
    try:
        start_time = time.time()
        # Clear DNS cache by creating a new resolver
        resolver = socket.getaddrinfo(host, None)
        dns_time = time.time() - start_time
        return dns_time
    except Exception as e:
        logger.error(f"Error measuring DNS resolution time: {str(e)}")
        return None

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
    session = requests.Session()
    retry_strategy = Retry(
        total=3,
        backoff_factor=0.5,
        status_forcelist=[500, 502, 503, 504]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    metrics = {
        "timing": {},
        "network": {},
        "server": {}
    }
    
    # Parse URL once
    parsed_url = urlparse(BASE_URL)
    host = parsed_url.hostname
    
    # Measure DNS resolution time (only for 10% of requests)
    if random.random() < 0.1 and host:
        metrics["timing"]["dns_resolution"] = get_dns_resolution_time(host)
    
    # Get initial network stats
    start_net_stats = get_network_stats()
    
    # Measure server latency (only for 10% of requests)
    if random.random() < 0.1:
        metrics["server"]["latency"] = get_server_latency(BASE_URL)
    
    total_start_time = time.time()
    try:
        logger.info(f"Attempting registration for email: {user_data['email']}")
        
        # Prepare request
        request = requests.Request('POST', f"{BASE_URL}/register", json=user_data)
        prepared_request = session.prepare_request(request)
        
        # Measure connection time
        connect_start = time.time()
        response = session.send(prepared_request, stream=True)
        connect_time = time.time() - connect_start
        
        # Measure time to first byte
        first_byte_start = time.time()
        first_chunk = next(response.iter_content(chunk_size=1, decode_unicode=True))
        time_to_first_byte = time.time() - first_byte_start
        
        # Read the rest of the response
        content = first_chunk + response.text
        response_end_time = time.time()
        
        # Calculate timing metrics
        total_duration = response_end_time - total_start_time
        server_processing_time = total_duration - connect_time - time_to_first_byte
        
        # Get final network stats and calculate differences
        end_net_stats = get_network_stats()
        if start_net_stats and end_net_stats:
            metrics["network"] = {
                "bytes_sent": end_net_stats["bytes_sent"] - start_net_stats["bytes_sent"],
                "bytes_recv": end_net_stats["bytes_recv"] - start_net_stats["bytes_recv"],
                "packets_sent": end_net_stats["packets_sent"] - start_net_stats["packets_sent"],
                "packets_recv": end_net_stats["packets_recv"] - start_net_stats["packets_recv"]
            }
        
        # Record timing metrics
        metrics["timing"].update({
            "total_duration": total_duration,
            "connect_time": connect_time,
            "time_to_first_byte": time_to_first_byte,
            "server_processing_time": server_processing_time
        })
        
        # Record server response metrics
        metrics["server"].update({
            "status_code": response.status_code,
            "content_length": len(content),
            "server_name": response.headers.get("server", "unknown")
        })
        
        if response.status_code != 200:
            logger.error(f"Registration failed for {user_data['email']}")
            logger.error(f"Status Code: {response.status_code}")
            logger.error(f"Response: {content}")
        else:
            logger.info(f"Registration successful for {user_data['email']}")
        
        return {
            "success": response.status_code == 200,
            "duration": total_duration,
            "status_code": response.status_code,
            "email": user_data["email"],
            "password": user_data["password"],
            "response": content,
            "metrics": metrics
        }
        
    except Exception as e:
        end_time = time.time()
        logger.error(f"Exception during registration: {str(e)}")
        metrics["timing"]["total_duration"] = end_time - total_start_time
        return {
            "success": False,
            "duration": end_time - total_start_time,
            "error": str(e),
            "email": user_data["email"],
            "metrics": metrics
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
    
    # Calculate basic statistics
    durations = [r["duration"] for r in results]
    avg_duration = statistics.mean(durations)
    median_duration = statistics.median(durations)
    min_duration = min(durations)
    max_duration = max(durations)
    
    # Aggregate timing metrics
    timing_metrics = {
        "total_duration": [],
        "dns_resolution": [],
        "connect_time": [],
        "server_processing_time": [],
        "time_to_first_byte": []
    }
    
    network_metrics = {
        "bytes_sent": [],
        "bytes_recv": [],
        "packets_sent": [],
        "packets_recv": []
    }
    
    server_latencies = []
    
    for result in results:
        metrics = result.get("metrics", {})
        
        # Collect timing metrics
        for key in timing_metrics.keys():
            if key in metrics.get("timing", {}):
                timing_metrics[key].append(metrics["timing"][key])
        
        # Collect network metrics
        for key in network_metrics.keys():
            if key in metrics.get("network", {}):
                network_metrics[key].append(metrics["network"][key])
        
        # Collect server latency
        if "latency" in metrics.get("server", {}):
            server_latencies.append(metrics["server"]["latency"])
    
    # Calculate statistics for each metric
    def calculate_stats(values):
        if not values:
            return None
        return {
            "mean": statistics.mean(values),
            "median": statistics.median(values),
            "min": min(values),
            "max": max(values),
            "std_dev": statistics.stdev(values) if len(values) > 1 else 0
        }
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"load_test_results_{timestamp}.json"
    
    detailed_metrics = {
        "test_config": {
            "num_requests": num_requests,
            "concurrent_requests": concurrent_requests,
            "base_url": BASE_URL,
            "timestamp": timestamp
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
        "timing_stats": {
            key: calculate_stats(values)
            for key, values in timing_metrics.items()
        },
        "network_stats": {
            key: calculate_stats(values)
            for key, values in network_metrics.items()
        },
        "server_stats": {
            "latency": calculate_stats(server_latencies)
        },
        "detailed_results": results
    }
    
    # Log summary statistics
    logger.info("\nLoad Test Results:")
    logger.info("=" * 50)
    logger.info(f"Total Time: {total_duration:.2f} seconds")
    logger.info(f"Total Requests: {num_requests}")
    logger.info(f"Successful Requests: {len(successful_requests)}")
    logger.info(f"Failed Requests: {len(failed_requests)}")
    logger.info(f"Requests per Second: {num_requests/total_duration:.2f}")
    
    logger.info("\nTiming Statistics (seconds):")
    for metric, stats in detailed_metrics["timing_stats"].items():
        if stats:
            logger.info(f"\n{metric.replace('_', ' ').title()}:")
            logger.info(f"  Average: {stats['mean']:.3f}")
            logger.info(f"  Median: {stats['median']:.3f}")
            logger.info(f"  Min: {stats['min']:.3f}")
            logger.info(f"  Max: {stats['max']:.3f}")
            logger.info(f"  Std Dev: {stats['std_dev']:.3f}")
    
    if detailed_metrics["server_stats"]["latency"]:
        logger.info("\nServer Latency (ms):")
        stats = detailed_metrics["server_stats"]["latency"]
        logger.info(f"  Average: {stats['mean']:.2f}")
        logger.info(f"  Median: {stats['median']:.2f}")
        logger.info(f"  Min: {stats['min']:.2f}")
        logger.info(f"  Max: {stats['max']:.2f}")
        logger.info(f"  Std Dev: {stats['std_dev']:.2f}")
    
    # Save detailed results to file
    with open(results_file, 'w') as f:
        json.dump(detailed_metrics, f, indent=2)
    
    logger.info(f"\nDetailed results saved to {results_file}")

if __name__ == "__main__":
    NUM_REQUESTS = 1000
    CONCURRENT_REQUESTS = 100
    run_load_test(NUM_REQUESTS, CONCURRENT_REQUESTS)