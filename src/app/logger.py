import logging
import sys
from typing import Dict, Any

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("simple-banking")

def log_api_error(endpoint: str, error_type: str, details: Dict[str, Any] = {}):
    """
    Log API errors with detailed information for debugging
    
    Args:
        endpoint: The API endpoint where the error occurred
        error_type: Type of error (e.g., "not_found", "insufficient_funds")
        details: Additional context about the error
    """
    
    logger.error(
        f"API Error in {endpoint} - {error_type}",
        extra={"details": details}
    )

def log_api_request(endpoint: str, request_data: Dict[str, Any] = {}):
    """
    Log API requests for debugging and auditing
    
    Args:
        endpoint: The API endpoint being called
        request_data: Request data (sanitized of sensitive information)
    """
    
    logger.info(
        f"API Request to {endpoint}",
        extra={"request_data": request_data}
    )
