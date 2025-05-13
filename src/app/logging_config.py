import logging
import sys
from typing import Dict, Any, Optional

def setup_logger():
    logger = logging.getLogger("simple_banking")
    logger.setLevel(logging.INFO)
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_handler.setFormatter(formatter)
    
    logger.addHandler(console_handler)
    
    return logger

logger = setup_logger()

def log_api_error(endpoint: str, error_type: str, detail: str, request_data: Optional[Dict[str, Any]] = None):
    """
    Log API errors with consistent format
    
    Args:
        endpoint: The API endpoint where the error occurred
        error_type: The type of error (e.g., "NOT_FOUND", "BAD_REQUEST")
        detail: Detailed error message
        request_data: Optional request data that caused the error
    """
    error_msg = f"API Error - Endpoint: {endpoint}, Type: {error_type}, Detail: {detail}"
    if request_data:
        error_msg += f", Request Data: {request_data}"
    
    logger.error(error_msg)
