from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Access environment variables
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 200))

KEYSERVER = os.getenv("KEYSERVER")

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_SERVER = os.getenv("DB_SERVER")
DB_NAME = os.getenv("DB_NAME")

SERVER_HOST = os.getenv("SERVER_HOST")
SERVER_PORT = os.getenv("SERVER_PORT")
FRONTEND_URL = os.getenv("FRONTEND_URL")
ENVIRONMENT = os.getenv("ENVIRONMENT")

print(f"SERVER_HOST: {SERVER_HOST}")
print(f"SERVER_PORT: {SERVER_PORT}")
print(f"FRONTEND_URL: {FRONTEND_URL}")
print(f"ENVIRONMENT: {ENVIRONMENT}")
SQLALCHEMY_DATABASE_URL = f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_SERVER}/{DB_NAME}"

# Add encryption method configuration
ENCRYPTION_METHOD = "X25519"  # Default to RSA for backward compatibility