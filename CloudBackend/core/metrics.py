from prometheus_client import Counter, Histogram, Gauge

# Custom metrics
ENCRYPTION_TIME = Histogram(
    "encryption_operation_duration_seconds",
    "Time spent performing encryption operations",
    ["operation_type", "status"]
)

ENCRYPTION_REQUESTS = Counter(
    "encryption_requests_total",
    "Total encryption/decryption requests",
    ["operation_type", "status"]
)

KEY_SERVER_LATENCY = Histogram(
    "key_server_request_duration_seconds",
    "Time spent waiting for key server operations",
    ["operation_type"]
)

CONCURRENT_OPERATIONS = Gauge(
    "concurrent_crypto_operations",
    "Number of concurrent cryptographic operations",
    ["operation_type"]
)

# Key Server Health Metrics
KEY_SERVER_ERRORS = Counter(
    "key_server_errors_total",
    "Total number of key server errors",
    ["error_type"]
) 