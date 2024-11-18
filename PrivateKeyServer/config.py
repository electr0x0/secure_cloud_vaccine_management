# app/config.py
import os

SECRET_KEY = "secret_key"
ALGORITHM = "HS256"

DB_USER = "root"
DB_PASSWORD = "1211"
DB_SERVER = "192.168.0.134"
DB_NAME = "vaccine_key_server"


SQLALCHEMY_DATABASE_URL = f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_SERVER}/{DB_NAME}"