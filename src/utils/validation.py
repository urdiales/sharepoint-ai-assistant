"""
Input validation utilities for the SharePoint AI Assistant.
Provides functions to validate and sanitize user inputs.
"""

import re
import os
from typing import Optional, List, Dict, Any
from urllib.parse import urlparse

from ..core import (
    SecurityConstants,
    SharePointConstants,
    ValidationError,
    SecurityError,
    get_logger
)

# Get logger for this module
logger = get_logger("validation")


def validate_url(url: str, allow_localhost: bool = True) -> str:
    """
    Validate and sanitize URL input.
    
    Args:
        url: URL string to validate
        allow_localhost: Whether to allow localhost URLs
    
    Returns:
        Validated and sanitized URL
    
    Raises:
        ValidationError: If URL is invalid
    """
    if not url:
        raise ValidationError("URL cannot be empty", field_name="url")
    
    if len(url) > SecurityConstants.MAX_URL_LENGTH:
        raise ValidationError(
            f"URL too long (max {SecurityConstants.MAX_URL_LENGTH} characters)",
            field_name="url"
        )
    
    # Basic URL validation
    try:
        parsed = urlparse(url.strip())
        
        # Check scheme
        if parsed.scheme not in ['http', 'https']:
            raise ValidationError("URL must use http or https protocol", field_name="url")
        
        # Check hostname
        if not parsed.hostname:
            raise ValidationError("URL must have a valid hostname", field_name="url")
        
        # Check localhost restriction
        if not allow_localhost and parsed.hostname in ['localhost', '127.0.0.1', '::1']:
            raise ValidationError("Localhost URLs are not allowed", field_name="url")
        
        # Reconstruct clean URL
        clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        if parsed.query:
            clean_url += f"?{parsed.query}"
        
        logger.debug(f"Validated URL: {clean_url}")
        return clean_url
        
    except Exception as e:
        raise ValidationError(f"Invalid URL format: {str(e)}", field_name="url")


def validate_search_query(query: str) -> str:
    """
    Validate and sanitize search query input.
    
    Args:
        query: Search query string
    
    Returns:
        Validated and sanitized query
    
    Raises:
        ValidationError: If query is invalid
    """
    if not query:
        raise ValidationError("Search query cannot be empty", field_name="query")
    
    # Remove leading/trailing whitespace
    query = query.strip()
    
    if len(query) > SecurityConstants.MAX_QUERY_LENGTH:
        raise ValidationError(
            f"Query too long (max {SecurityConstants.MAX_QUERY_LENGTH} characters)",
            field_name="query"
        )
    
    # Check for potentially dangerous characters
    dangerous_chars = ['<', '>', '"', "'", '&', ';', '|', '`']
    for char in dangerous_chars:
        if char in query:
            raise SecurityError(f"Query contains potentially dangerous character: {char}")
    
    # Basic SQL injection protection
    sql_keywords = ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'DROP', 'UNION', 'EXEC']
    query_upper = query.upper()
    for keyword in sql_keywords:
        if keyword in query_upper:
            raise SecurityError(f"Query contains potentially dangerous keyword: {keyword}")
    
    logger.debug(f"Validated search query: {query}")
    return query


def validate_filename(filename: str) -> str:
    """
    Validate and sanitize filename input.
    
    Args:
        filename: Filename to validate
    
    Returns:
        Validated and sanitized filename
    
    Raises:
        ValidationError: If filename is invalid
    """
    if not filename:
        raise ValidationError("Filename cannot be empty", field_name="filename")
    
    # Remove leading/trailing whitespace
    filename = filename.strip()
    
    if len(filename) > SecurityConstants.MAX_FILENAME_LENGTH:
        raise ValidationError(
            f"Filename too long (max {SecurityConstants.MAX_FILENAME_LENGTH} characters)",
            field_name="filename"
        )
    
    # Check for invalid characters
    invalid_chars = ['<', '>', ':', '"', '|', '?', '*', '\\', '/']
    for char in invalid_chars:
        if char in filename:
            raise ValidationError(f"Filename contains invalid character: {char}", field_name="filename")
    
    # Check for reserved names (Windows)
    reserved_names = ['CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 
                     'COM6', 'COM7', 'COM8', 'COM9', 'LPT1', 'LPT2', 'LPT3', 'LPT4', 
                     'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9']
    
    name_without_ext = os.path.splitext(filename)[0].upper()
    if name_without_ext in reserved_names:
        raise ValidationError(f"Filename uses reserved name: {name_without_ext}", field_name="filename")
    
    logger.debug(f"Validated filename: {filename}")
    return filename


def validate_file_extension(filename: str, allowed_extensions: Optional[List[str]] = None) -> str:
    """
    Validate file extension.
    
    Args:
        filename: Filename to check
        allowed_extensions: List of allowed extensions (defaults to SecurityConstants.ALLOWED_EXTENSIONS)
    
    Returns:
        File extension (including dot)
    
    Raises:
        ValidationError: If extension is not allowed
    """
    if allowed_extensions is None:
        allowed_extensions = list(SecurityConstants.ALLOWED_EXTENSIONS)
    
    # Get file extension
    _, ext = os.path.splitext(filename.lower())
    
    if not ext:
        raise ValidationError("File must have an extension", field_name="filename")
    
    if ext not in [e.lower() for e in allowed_extensions]:
        raise ValidationError(
            f"File extension '{ext}' not allowed. Allowed: {', '.join(allowed_extensions)}",
            field_name="filename"
        )
    
    logger.debug(f"Validated file extension: {ext}")
    return ext


def validate_file_size(file_size: int, max_size: Optional[int] = None) -> int:
    """
    Validate file size.
    
    Args:
        file_size: File size in bytes
        max_size: Maximum allowed size in bytes (defaults to SharePointConstants.MAX_FILE_SIZE)
    
    Returns:
        Validated file size
    
    Raises:
        ValidationError: If file size is invalid
    """
    if max_size is None:
        max_size = SharePointConstants.MAX_FILE_SIZE
    
    if file_size < 0:
        raise ValidationError("File size cannot be negative", field_name="file_size")
    
    if file_size == 0:
        raise ValidationError("File cannot be empty", field_name="file_size")
    
    if file_size > max_size:
        raise ValidationError(
            f"File too large ({file_size} bytes > {max_size} bytes)",
            field_name="file_size"
        )
    
    logger.debug(f"Validated file size: {file_size} bytes")
    return file_size


def validate_user_input(text: str, max_length: Optional[int] = None) -> str:
    """
    Validate and sanitize general user text input.
    
    Args:
        text: User input text
        max_length: Maximum allowed length (defaults to SecurityConstants.MAX_QUERY_LENGTH)
    
    Returns:
        Validated and sanitized text
    
    Raises:
        ValidationError: If input is invalid
    """
    if max_length is None:
        max_length = SecurityConstants.MAX_QUERY_LENGTH
    
    if not text:
        raise ValidationError("Input cannot be empty", field_name="text")
    
    # Remove leading/trailing whitespace
    text = text.strip()
    
    if len(text) > max_length:
        raise ValidationError(
            f"Input too long (max {max_length} characters)",
            field_name="text"
        )
    
    # Basic XSS protection - remove/escape HTML tags
    text = re.sub(r'<[^>]*>', '', text)
    
    # Remove null bytes and other control characters
    text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
    
    logger.debug(f"Validated user input: {text[:50]}...")
    return text


def validate_credentials(client_id: str, client_secret: str) -> tuple[str, str]:
    """
    Validate SharePoint credentials.
    
    Args:
        client_id: SharePoint client ID
        client_secret: SharePoint client secret
    
    Returns:
        Tuple of validated (client_id, client_secret)
    
    Raises:
        ValidationError: If credentials are invalid
    """
    if not client_id:
        raise ValidationError("Client ID cannot be empty", field_name="client_id")
    
    if not client_secret:
        raise ValidationError("Client secret cannot be empty", field_name="client_secret")
    
    # Remove whitespace
    client_id = client_id.strip()
    client_secret = client_secret.strip()
    
    # Basic format validation for client ID (typically GUID format)
    guid_pattern = re.compile(
        r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$'
    )
    
    if not guid_pattern.match(client_id):
        logger.warning("Client ID does not match expected GUID format")
    
    # Check minimum length for client secret
    if len(client_secret) < 10:
        raise ValidationError("Client secret appears too short", field_name="client_secret")
    
    logger.debug("Validated SharePoint credentials")
    return client_id, client_secret


def sanitize_html(text: str) -> str:
    """
    Remove HTML tags and entities from text.
    
    Args:
        text: Text that may contain HTML
    
    Returns:
        Sanitized text without HTML
    """
    if not text:
        return ""
    
    # Remove HTML tags
    text = re.sub(r'<[^>]*>', '', text)
    
    # Decode common HTML entities
    html_entities = {
        '&amp;': '&',
        '&lt;': '<',
        '&gt;': '>',
        '&quot;': '"',
        '&#39;': "'",
        '&nbsp;': ' '
    }
    
    for entity, char in html_entities.items():
        text = text.replace(entity, char)
    
    return text


def validate_library_name(library_name: str) -> str:
    """
    Validate SharePoint library name.
    
    Args:
        library_name: Library name to validate
    
    Returns:
        Validated library name
    
    Raises:
        ValidationError: If library name is invalid
    """
    if not library_name:
        raise ValidationError("Library name cannot be empty", field_name="library_name")
    
    library_name = library_name.strip()
    
    # Check against known valid libraries
    if library_name not in SharePointConstants.DEFAULT_LIBRARIES:
        logger.warning(f"Library '{library_name}' not in default list: {SharePointConstants.DEFAULT_LIBRARIES}")
    
    # Basic validation
    if len(library_name) > 100:
        raise ValidationError("Library name too long", field_name="library_name")
    
    # Check for invalid characters
    invalid_chars = ['<', '>', ':', '"', '|', '?', '*', '\\', '/']
    for char in invalid_chars:
        if char in library_name:
            raise ValidationError(f"Library name contains invalid character: {char}", field_name="library_name")
    
    logger.debug(f"Validated library name: {library_name}")
    return library_name
