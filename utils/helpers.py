"""
Helper utility functions for Anode Tracking System.
"""

import re
from datetime import timedelta
from typing import Optional


def format_time_delta(td: Optional[timedelta]) -> str:
    """Format a timedelta object to HH:MM:SS string.
    
    Args:
        td: timedelta object or None
        
    Returns:
        Formatted time string or empty string if None
    """
    if td is None:
        return ""
    
    total_seconds = int(td.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def validate_anode_number(anode_number: str) -> bool:
    """Validate an anode number format.
    
    Args:
        anode_number: String to validate
        
    Returns:
        True if valid format, False otherwise
    """
    if not anode_number:
        return False
    
    # Allow alphanumeric characters, hyphens, and underscores
    pattern = r"^[A-Za-z0-9\-_]+$"
    return bool(re.match(pattern, anode_number.strip()))


def sanitize_filename(filename: str) -> str:
    """Sanitize a filename by removing invalid characters.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Remove invalid characters for filenames
    invalid_chars = r'[<>:"/\\|?*]'
    return re.sub(invalid_chars, "_", filename)


def truncate_text(text: str, max_length: int = 50) -> str:
    """Truncate text to a maximum length with ellipsis.
    
    Args:
        text: Original text
        max_length: Maximum allowed length
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."