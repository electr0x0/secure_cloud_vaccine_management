# app/config.py
import os

SECRET_KEY = "secret_key"
ALGORITHM = "HS256"

DB_USER = "postgres"
DB_PASSWORD = "1234"
DB_SERVER = "localhost"
DB_NAME = "vaccine_key_server"
DB_PORT = 5432

# Convert to postgres


SQLALCHEMY_DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_SERVER}:{DB_PORT}/{DB_NAME}"

# Add new configuration
ENCRYPTION_METHOD = "X25519"  # Options: "RSA" or "X25519"