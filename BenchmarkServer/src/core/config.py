from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    RESULTS_DIR: str = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "test_results")
    BASE_URL: str = "http://localhost:8000"  # Default base URL
    LOG_LEVEL: str = "INFO"
    LOG_DIR: str = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs")

    def __init__(self):
        super().__init__()
        
        os.makedirs(self.RESULTS_DIR, exist_ok=True)
        os.makedirs(self.LOG_DIR, exist_ok=True)

settings = Settings() 