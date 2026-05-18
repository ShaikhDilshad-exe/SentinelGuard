"""
Configuration Module
Manages application configuration and environment variables.
"""

from pathlib import Path
from typing import Any
import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


class Config:
    """Application configuration"""
    
    def __init__(self):
        """Load configuration from environment"""
        # API Configuration
        self.API_HOST = os.getenv("API_HOST", "0.0.0.0")
        self.API_PORT = int(os.getenv("API_PORT", "8000"))
        self.API_DEBUG = os.getenv("API_DEBUG", "False").lower() == "true"
        
        # Database Configuration
        self.DB_URL = os.getenv("DB_URL", "sqlite:///sentinel_guard.db")
        
        # ML Model Configuration
        self.ML_MODEL_PATH = os.getenv("ML_MODEL_PATH", "./models/threat_detector.pkl")
        self.SIGNATURE_DB_PATH = os.getenv("SIGNATURE_DB_PATH", "./data/signatures.db")
        
        # Monitoring Configuration
        # We ensure MONITORING_INTERVAL and WATCH_PATHS match the project's real-time needs
        self.MONITORING_INTERVAL = int(os.getenv("MONITORING_INTERVAL", "5"))
        
# WATCH_PATHS are typically separated by commas or semicolons in .env
        paths_raw = os.getenv("WATCH_PATHS", r"C:\\Users\\Heramb\\Sentinel_Test")
        self.WATCH_PATHS = [p.strip() for p in paths_raw.replace(";", ",").split(",") if p.strip()]
        
        # Logging Configuration
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
        log_file = os.getenv("LOG_FILE", "./logs/sentinel_guard.log")
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        self.LOG_FILE = log_file
        
        # JWT Configuration
        self.JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
        self.JWT_ALGORITHM = "HS256"
        self.JWT_EXPIRATION = int(os.getenv("JWT_EXPIRATION", "3600"))
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return getattr(self, key, default)


# Global config instance
config = Config()

# Exporting these for easier access in monitoring modules
WATCH_PATHS = config.WATCH_PATHS
MONITORING_INTERVAL = config.MONITORING_INTERVAL