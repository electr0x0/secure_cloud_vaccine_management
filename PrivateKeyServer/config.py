# app/config.py
import os

SECRET_KEY = "secret_key"
ALGORITHM = "HS256"

DB_USER = "electro"
DB_PASSWORD = "1234"
DB_SERVER = "localhost"
DB_NAME = "vaccine_key_server"


SQLALCHEMY_DATABASE_URL = f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_SERVER}/{DB_NAME}"

# Add new configuration
ENCRYPTION_METHOD = "X25519"  # Options: "RSA" or "X25519"