"""
Logging utilities for Merrywinter Security Consulting Bot
"""

import logging
import os
from datetime import datetime

def setup_logger(name='MerrywinterBot', level=logging.INFO):
    """Setup logging configuration"""
    
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Prevent duplicate handlers
    if logger.handlers:
        logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(
        '[%(asctime)s] [%(levelname)s] %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    
    # Create file handler (for local development)
    if not os.getenv('RENDER'):  # Only log to file when not on Render
        log_filename = f"logs/bot_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_filename, encoding='utf-8')
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    # Add console handler
    logger.addHandler(console_handler)
    
    return logger

# Create a default logger instance
logger = setup_logger()