# Secure Vaccination Management System

A comprehensive cloud-based vaccination management system with on-premise key management for enhanced security. The system consists of multiple components working together to provide secure storage and access to vaccination records.

## System Architecture

The system is composed of three main components:

1. **CloudBackend**: Main API server handling user management and vaccination records
2. **PrivateKeyServer**: On-premise key management server for encryption/decryption
3. **CloudFrontend**: Next.js web application for user interface

Extra components:

4. **BenchmarkServer**: Performance testing and monitoring server (Flask based web app for interfacing and grafana with prometheus and node exporter for visualizing the metrics)

### Security Architecture

- Currently configurable to use either hybrid encryption (X25519/RSA) or RSA for data protection
- Sensitive data encrypted before storage
- Private keys managed in separate on-premise server
- JWT-based authentication
- Tailscale network for secure communication

## Prerequisites

- Python 3.9+
- Node.js 18+
- PostgreSQL 16+
- Tailscale VPN (for PrivateKeyServer)

## Component Setup

### 1. Cloud Backend

```bash

#First clone the repository
git clone https://github.com/electr0x0/cloud_vaccine.git
cd cloud_vaccine



#Make sure you have postgres server running and configure the .env file with the correct credentials


# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

cd CloudBackend

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Start server
python main.py
```

### 2. Private Key Server

```bash
cd PrivateKeyServer

# Configure database
# Edit config.py with your PostgreSQL settings

# Start server
python main.py
```

### 3. Cloud Frontend

```bash
cd CloudFrontend/vaccine-frontend

# Install dependencies
pnpm install

# Start development server
pnpm run dev

# Build for production
pnpm run build
```

### 4. Benchmark Server

```bash
cd BenchmarkServer


#Change baseurl in src/core/config.py if required

# Start server
python app.py
```

## API Documentation

### Cloud Backend API (Port 8000)

- **Authentication**
  - POST `/register`: Register new user
  - POST `/login`: User login
  
- **User Management**
  - GET `/api/user/info`: Get user information
  - PUT `/api/user/update`: Update user information

- **Vaccination Records**
  - GET `/api/vaccinations/history`: Get vaccination history
  - POST `/api/vaccinations/vaccination-history`: Update vaccination record

### Private Key Server API (Port 8001)

- **Key Management**
  - POST `/generate-key-pair`: Generate new key pair
  - POST `/decrypt-data`: Decrypt user data

### Benchmark Server API (Port 5000)

- **Performance Testing**
  - POST `/api/benchmark/run`: Run benchmark test
  - GET `/api/benchmark/history`: Get test history
  - GET `/api/metrics`: View performance metrics

### For further details on the API, you can goto server/docs | redocs for viewing the api docs


## Security Features

1. **Data Encryption**
   - All sensitive user data encrypted at rest
   - Support for both RSA and X25519 encryption
   - ChaCha20Poly1305 for symmetric encryption

2. **Access Control**
   - JWT-based authentication
   - Role-based access control
   - IP-based access restrictions for PrivateKeyServer with Tailscale Middleware

3. **Network Security**
   - Tailscale VPN for secure communication
   - CORS protection
   - Rate limiting


### The CloudBackend and PrivateKeyServer can be run on the same machine for testing purposes, configure the tailscale middleware for that case.

## Monitoring

The system includes comprehensive monitoring through:

- Prometheus metrics
- Real-time performance dashboards
- Detailed logging
- Benchmark testing capabilities
- Grafana Dashboard for visualizing the metrics



## Development

### Running Tests

See the benchmark server for running the tests and visualizing the metrics.

Some of our test results are provided in the Graphs folder.


## Production Deployment

1. Set up PostgreSQL databases for both servers
2. Configure environment variables
3. Set up Tailscale network
4. Deploy CloudBackend and Frontend to cloud provider
5. Deploy PrivateKeyServer on-premise
6. Configure SSL/TLS
7. Set up monitoring and logging

A terraform script is provided for deploying the system in EC2 instances.

## License

MIT License