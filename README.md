# Vaccine Cloud Server

This repository contains a multi-component application for managing vaccination-related data. It includes:

1. **CloudBackend**: Backend service for managing users, vaccinations, and data processing.
2. **PrivateKeyServer**: Service for handling cryptographic operations and key management.
3. **CloudFrontend**: Frontend application for user interactions.

---

## Prerequisites

Ensure the following software is installed on your system:

- **Python**
- **Node.js**
- **npm**
- **MySQL Server**

---

## Setup Instructions

### 1. Backend Configuration

#### CloudBackend
1. Navigate to `./CloudBackend/config.py`.
2. Update the database connection settings:
   ```python
   DB_USER = "root"
   DB_PASSWORD = "1211"
   DB_SERVER = "192.168.0.134"
   DB_NAME = "vaccine_cloud_server"
   ```

#### PrivateKeyServer
1. Navigate to `./PrivateKeyServer/config.py`.
2. Update the database connection settings:
   ```python
   DB_USER = "root"
   DB_PASSWORD = "1211"
   DB_SERVER = "192.168.0.134"
   DB_NAME = "vaccine_key_server"
   ```

---

### 2. Virtual Environment and Dependencies

1. Create a virtual environment:
   ```bash
   python -m venv venv
   ```
2. Activate the virtual environment:
   - **Windows**: 
     ```bash
     venv\Scripts\activate
     ```
   - **Mac/Linux**:
     ```bash
     source venv/bin/activate
     ```
3. Install required Python packages:
   ```bash
   python -m pip install -r requirements.txt
   ```

---

### 3. Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd ./CloudFrontend/vaccine-frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the frontend development server:
   ```bash
   npm run dev
   ```

---

### 4. Running the Application

1. Start the **CloudBackend** service:
   ```bash
   python ./CloudBackend/main.py
   ```
2. Start the **PrivateKeyServer** service:
   ```bash
   python ./PrivateKeyServer/main.py
   ```

---

## Accessing the Application

### Backend API Documentation
- **CloudServer**: [127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **KeyServer**: [127.0.0.1:8001/docs](http://127.0.0.1:8001/docs)

### Frontend
- Access the frontend at: [127.0.0.1:3000](http://127.0.0.1:3000)

---

## Additional Information

- Ensure the MySQL server is running and configured correctly with the provided credentials.
- If you encounter issues, verify the `config.py` files in both backend services for accurate database configurations.
- For further assistance, refer to the API documentation available in the provided links.