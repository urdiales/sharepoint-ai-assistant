"""
Core constants for the SharePoint AI Assistant.

*** CONFIGURATION CONSTANTS ***
This file contains all the centralized configuration values, magic numbers,
and default settings used throughout the application.

To modify application behavior:
1. Update values in this file rather than hardcoding them elsewhere
2. Add new constants here when introducing new features
3. Use descriptive names and organize by functional area
4. Document any constraints or dependencies in comments

This approach makes the application easier to maintain and configure.
"""


class SharePointConstants:
    """Constants related to SharePoint operations."""

    # Default document libraries available in SharePoint
    DEFAULT_LIBRARIES = ["Documents", "HR Library", "Onboarding Checklist"]

    # Supported file types for preview and processing
    SUPPORTED_FILE_TYPES = [".pdf", ".docx", ".xlsx"]

    # File size limits (in bytes)
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    MAX_PREVIEW_SIZE = 10 * 1024 * 1024  # 10MB for preview

    # Text processing limits
    PREVIEW_TEXT_LIMIT = 1000  # Maximum characters for text preview
    MAX_SEARCH_RESULTS = 100  # Maximum search results to return

    # SharePoint list template IDs
    DOCUMENT_LIBRARY_TEMPLATE = 101
    CUSTOM_LIST_TEMPLATE = 100

    # API timeouts (in seconds)
    CONNECTION_TIMEOUT = 30
    REQUEST_TIMEOUT = 60
    DOWNLOAD_TIMEOUT = 300  # 5 minutes for large files


class UIConstants:
    """Constants related to the user interface."""

    # Application metadata
    PAGE_TITLE = "Local AI SharePoint Assistant"
    PAGE_ICON = "🧠"

    # Server configuration
    DEFAULT_PORT = 8501
    DEFAULT_HOST = "0.0.0.0"

    # UI limits and settings
    CHAT_HISTORY_LIMIT = 50  # Maximum chat messages to keep
    MAX_INPUT_LENGTH = 1000  # Maximum characters in user input

    # Tab names
    CHAT_TAB = "Chat"
    SEARCH_TAB = "Search/Preview"

    # Status messages
    CONNECTED_MESSAGE = "Connected to SharePoint"
    DISCONNECTED_MESSAGE = "Connect to SharePoint first."
    CONNECTION_SUCCESS = "Connected!"


class LLMConstants:
    """Constants related to LLM operations."""

    # Model configuration
    DEFAULT_MODEL = "gemma3"
    DEFAULT_OLLAMA_HOST = "http://localhost:11434"

    # Request limits
    MAX_TOKENS = 4096
    TEMPERATURE = 0.7

    # Timeout settings (in seconds)
    LLM_TIMEOUT = 120
    STREAM_TIMEOUT = 30

    # Memory settings
    MAX_MEMORY_TOKENS = 2000
    MEMORY_BUFFER_SIZE = 10


class SecurityConstants:
    """Security-related constants."""

    # Input validation
    MAX_URL_LENGTH = 2048
    MAX_QUERY_LENGTH = 500
    MAX_FILENAME_LENGTH = 255

    # Rate limiting
    MAX_REQUESTS_PER_MINUTE = 60
    MAX_REQUESTS_PER_HOUR = 1000

    # Allowed file extensions for upload/download
    ALLOWED_EXTENSIONS = {".pdf", ".docx", ".xlsx", ".txt", ".md"}

    # Security headers
    SECURITY_HEADERS = {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
    }


class LoggingConstants:
    """Logging configuration constants."""

    # Log levels
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

    # Log file settings
    MAX_LOG_SIZE = 10 * 1024 * 1024  # 10MB
    BACKUP_COUNT = 5

    # Log formats
    DETAILED_FORMAT = (
        "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"
    )
    SIMPLE_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"

    # Logger names
    MAIN_LOGGER = "sharepoint_ai"
    SHAREPOINT_LOGGER = "sharepoint_ai.sharepoint"
    LLM_LOGGER = "sharepoint_ai.llm"
    UI_LOGGER = "sharepoint_ai.ui"


class ErrorConstants:
    """Error messages and codes."""

    # SharePoint errors
    SHAREPOINT_CONNECTION_ERROR = "Failed to connect to SharePoint"
    SHAREPOINT_AUTH_ERROR = "SharePoint authentication failed"
    SHAREPOINT_NOT_FOUND = "SharePoint resource not found"
    SHAREPOINT_TIMEOUT = "SharePoint request timed out"

    # File operation errors
    FILE_NOT_FOUND = "File not found"
    FILE_TOO_LARGE = "File size exceeds maximum limit"
    INVALID_FILE_TYPE = "Unsupported file type"
    FILE_DOWNLOAD_ERROR = "Failed to download file"

    # LLM errors
    LLM_CONNECTION_ERROR = "Failed to connect to LLM service"
    LLM_TIMEOUT_ERROR = "LLM request timed out"
    LLM_RESPONSE_ERROR = "Invalid LLM response"

    # Validation errors
    INVALID_INPUT = "Invalid input provided"
    MISSING_CREDENTIALS = "Missing required credentials"
    INVALID_URL = "Invalid URL format"

    # Generic errors
    UNEXPECTED_ERROR = "An unexpected error occurred"
    CONFIGURATION_ERROR = "Configuration error"


class EnvironmentConstants:
    """Environment variable names."""

    # SharePoint configuration
    SHAREPOINT_SITE_URL = "SHAREPOINT_SITE_URL"
    SHAREPOINT_CLIENT_ID = "SHAREPOINT_CLIENT_ID"
    SHAREPOINT_CLIENT_SECRET = "SHAREPOINT_CLIENT_SECRET"

    # LLM configuration
    OLLAMA_HOST = "OLLAMA_HOST"
    LLM_MODEL = "LLM_MODEL"

    # Application configuration
    LOG_LEVEL = "LOG_LEVEL"
    DEBUG_MODE = "DEBUG_MODE"

    # Security configuration
    SECRET_KEY = "SECRET_KEY"
    ALLOWED_HOSTS = "ALLOWED_HOSTS"
