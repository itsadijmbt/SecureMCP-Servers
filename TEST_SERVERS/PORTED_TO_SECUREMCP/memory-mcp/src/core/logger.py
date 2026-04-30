#logger.py
import asyncio
import logging
import os
import time
import inspect
import functools
from contextlib import contextmanager
from httpx import AsyncClient, Client, HTTPStatusError
from datetime import datetime, timezone
import sys
from dotenv import load_dotenv
load_dotenv()

LOGGER_SERVICE_URL= os.getenv("LOGGER_SERVICE_URL", "http://event-logger:8181")
APP_NAME=os.getenv("APP_NAME", "memory-mcp")

class MaapLogger:
    """
    A singleton asynchronous and synchronous remote logger that logs messages both locally and to a remote service.
    Supports logging with dynamic context fields and structured metadata.
    """
    _instance = None
    _thread_local_context = {}  # Simple thread-local context storage
    
    def __new__(cls, *args, **kwargs):
        # Ensure only one instance of the logger is created (singleton pattern)
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance._init_logger(*args, **kwargs)
        return cls._instance

    def _init_logger(self, service_url: str, app_name: str, log_dir: str = "logs", 
                    log_level: str = "INFO", retention_days: int = 3):
        """Initialize the logger with the given parameters."""
        self.service_url = service_url
        self.app_name = app_name
        self.async_client = AsyncClient(timeout=300.0)
        self.sync_client = Client(timeout=300.0)
        self.log_dir = log_dir
        self.retention_days = retention_days
        os.makedirs(self.log_dir, exist_ok=True)
        self.cleanup_old_logs()
        
        # Set up the local logger
        self.local_logger = logging.getLogger(app_name)
        log_level_num = getattr(logging, log_level.upper(), logging.INFO)
        self.local_logger.setLevel(log_level_num)
        
        # Check if handlers already exist to prevent duplicate handlers
        if not self.local_logger.handlers:
            # File handler
            file_handler = logging.FileHandler(os.path.join(self.log_dir, f"{app_name}.log"))
            file_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
            file_handler.setFormatter(file_formatter)
            self.local_logger.addHandler(file_handler)
            
            # Console handler
            console_handler = logging.StreamHandler()
            console_formatter = logging.Formatter("%(levelname)s: %(message)s")
            console_handler.setFormatter(console_formatter)
            self.local_logger.addHandler(console_handler)

    def cleanup_old_logs(self):
        """Remove log files older than the configured retention period."""
        now = time.time()
        cutoff_time = now - (self.retention_days * 24 * 60 * 60)
        
        for filename in os.listdir(self.log_dir):
            file_path = os.path.join(self.log_dir, filename)
            if os.path.isfile(file_path):
                file_modified_time = os.path.getmtime(file_path)
                if file_modified_time < cutoff_time:
                    try:
                        os.remove(file_path)
                        print(f"Removed old log file: {file_path}")
                    except Exception as e:
                        print(f"Error removing file {file_path}: {e}")

    def info(self, message: str, **fields):
        """Log an informational message synchronously with additional fields."""
        self.local_logger.info(message)

    def debug(self, message: str, **fields):
        """Log a debug message synchronously with additional fields."""
        self.local_logger.debug(message)

    def warning(self, message: str, **fields):
        """Log a warning message synchronously with additional fields."""
        self.local_logger.warning(message)

    def error(self, message: str, **fields):
        """Log an error message synchronously with additional fields."""
        self.local_logger.error(message)

def get_logger():
    """Get a singleton logger instance."""
    try:
        return MaapLogger(service_url=LOGGER_SERVICE_URL, app_name=APP_NAME)
    except Exception:
        # Fallback to basic logging if MAAP logger is not available
        import logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            stream=sys.stdout
        )
        return logging.getLogger(APP_NAME)

# Export logger for convenience
logger = get_logger()
