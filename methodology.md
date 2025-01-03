## System Architecture

### 1. Hybrid Deployment (Scenario 1)
- Private Key Server deployed on-premises, connected to Cloud Backend via Tailscale WireGuard VPN
- Ensures secure key management through network isolation
- Cloud Backend handles application logic and data storage
- Web Frontend provides user interface and initial data encryption

### 2. Full Cloud Deployment (Scenario 2)
- All components deployed in cloud infrastructure
- Simplified architecture with direct communication between services
- Maintains end-to-end encryption despite co-location

## Cryptographic Implementation

The system implements two cryptographic approaches for performance comparison:

### 1. Traditional RSA
- Asymmetric encryption using RSA with OAEP padding
- SHA-256 for hashing
- Used as performance baseline

### 2. Modern Hybrid Encryption
- X25519 for key exchange
- ChaCha20-Poly1305 for symmetric encryption
- Combines performance benefits of symmetric encryption with secure key exchange

## Performance Evaluation

### 1. Load Testing Parameters
- Concurrent user simulation (10 concurrent requests)
- Multiple test iterations (100 requests per test)
- Measurement of key metrics:
  - Request latency (min, max, average)
  - Throughput (requests per second)
  - System resource utilization

### 2. Test Scenarios
- Data encryption/decryption operations
- User authentication flows
- End-to-end transaction timing
- Cross-deployment model comparison

### 3. Environmental Consistency
- Standardized cloud instance types
- Controlled network conditions
- Identical data payload sizes

The test results demonstrate the performance characteristics of both architectural approaches and cryptographic methods, providing insights into the trade-offs between security, performance, and deployment complexity. 