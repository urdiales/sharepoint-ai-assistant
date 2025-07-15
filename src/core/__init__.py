"""
Core module for the SharePoint AI Assistant.
Contains fundamental components like configuration, logging, constants, and exceptions.
"""

from .config import config_manager, get_sharepoint_config, get_ollama_host
from .constants import (
    SharePointConstants,
    UIConstants,
    LLMConstants,
    SecurityConstants,
    LoggingConstants,
    ErrorConstants,
    EnvironmentConstants
)
from .exceptions import (
    SharePointAIException,
    SharePointConnectionError,
    SharePointAuthenticationError,
    SharePointResourceNotFoundError,
    SharePointTimeoutError,
    FileOperationError,
    FileNotFoundError,
    FileTooLargeError,
    InvalidFileTypeError,
    FileDownloadError,
    LLMError,
    LLMConnectionError,
    LLMTimeoutError,
    LLMResponseError,
    ValidationError,
    ConfigurationError,
    SecurityError,
    RateLimitError
)
from .logging_config import get_logger, log_function_call, log_performance, setup_logging

__all__ = [
    # Configuration
    "config_manager",
    "get_sharepoint_config",
    "get_ollama_host",
    
    # Constants
    "SharePointConstants",
    "UIConstants", 
    "LLMConstants",
    "SecurityConstants",
    "LoggingConstants",
    "ErrorConstants",
    "EnvironmentConstants",
    
    # Exceptions
    "SharePointAIException",
    "SharePointConnectionError",
    "SharePointAuthenticationError", 
    "SharePointResourceNotFoundError",
    "SharePointTimeoutError",
    "FileOperationError",
    "FileNotFoundError",
    "FileTooLargeError",
    "InvalidFileTypeError",
    "FileDownloadError",
    "LLMError",
    "LLMConnectionError",
    "LLMTimeoutError",
    "LLMResponseError",
    "ValidationError",
    "ConfigurationError",
    "SecurityError",
    "RateLimitError",
    
    # Logging
    "get_logger",
    "log_function_call",
    "log_performance",
    "setup_logging"
]
