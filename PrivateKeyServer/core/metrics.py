
from prometheus_client import Counter, Histogram

# Raw Encryption/Decryption Metrics
RAW_CRYPTO_TIME = Histogram(
    "raw_crypto_operation_duration_seconds",
    "Time spent on raw cryptographic operations",
    ["operation_type"]  # 'encryption' or 'decryption'
)

# Active Key Pairs Counter
ACTIVE_KEY_PAIRS = Counter(
    "key_pairs_generated_total",
    "Total number of key pairs generated"
)