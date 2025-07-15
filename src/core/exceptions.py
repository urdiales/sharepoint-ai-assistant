"""
Custom exception classes for the SharePoint AI Assistant.
Provides specific exception types for different error scenarios.
"""

class SharePointAIException(Exception):
    """Base exception class for all SharePoint AI Assistant errors."""
    
    def __init__(self, message: str, error_code: str = None, details: dict = None):
        """
        Initialize the exception with message and optional details.
        
        Args:
            message: Human-readable error message
            error_code: Optional error code for programmatic handling
            details: Optional dictionary with additional error details
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
    
    def __str__(self):
        """Return string representation of the exception."""
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message


class SharePointConnectionError(SharePointAIException):
    """Raised when SharePoint connection fails."""
    
    def __init__(self, message: str = "Failed to connect to SharePoint", **kwargs):
        super().__init__(message, error_code="SP_CONNECTION_ERROR", **kwargs)


class SharePointAuthenticationError(SharePointAIException):
    """Raised when SharePoint authentication fails."""
    
    def __init__(self, message: str = "SharePoint authentication failed", **kwargs):
        super().__init__(message, error_code="SP_AUTH_ERROR", **kwargs)


class SharePointResourceNotFoundError(SharePointAIException):
    """Raised when a SharePoint resource is not found."""
    
    def __init__(self, resource_name: str = None, **kwargs):
        message = f"SharePoint resource not found: {resource_name}" if resource_name else "SharePoint resource not found"
        super().__init__(message, error_code="SP_NOT_FOUND", **kwargs)


class SharePointTimeoutError(SharePointAIException):
    """Raised when SharePoint request times out."""
    
    def __init__(self, message: str = "SharePoint request timed out", **kwargs):
        super().__init__(message, error_code="SP_TIMEOUT", **kwargs)


class FileOperationError(SharePointAIException):
    """Base class for file operation errors."""
    
    def __init__(self, message: str, file_name: str = None, **kwargs):
        if file_name:
            message = f"{message}: {file_name}"
        super().__init__(message, error_code="FILE_ERROR", **kwargs)
        self.file_name = file_name


class FileNotFoundError(FileOperationError):
    """Raised when a file is not found."""
    
    def __init__(self, file_name: str = None, **kwargs):
        message = "File not found"
        super().__init__(message, file_name=file_name, error_code="FILE_NOT_FOUND", **kwargs)


class FileTooLargeError(FileOperationError):
    """Raised when a file exceeds size limits."""
    
    def __init__(self, file_name: str = None, file_size: int = None, max_size: int = None, **kwargs):
        message = "File size exceeds maximum limit"
        if file_size and max_size:
            message += f" ({file_size} > {max_size} bytes)"
        super().__init__(message, file_name=file_name, error_code="FILE_TOO_LARGE", **kwargs)
        self.file_size = file_size
        self.max_size = max_size


class InvalidFileTypeError(FileOperationError):
    """Raised when file type is not supported."""
    
    def __init__(self, file_name: str = None, file_type: str = None, **kwargs):
        message = "Unsupported file type"
        if file_type:
            message += f": {file_type}"
        super().__init__(message, file_name=file_name, error_code="INVALID_FILE_TYPE", **kwargs)
        self.file_type = file_type


class FileDownloadError(FileOperationError):
    """Raised when file download fails."""
    
    def __init__(self, file_name: str = None, **kwargs):
        message = "Failed to download file"
        super().__init__(message, file_name=file_name, error_code="FILE_DOWNLOAD_ERROR", **kwargs)


class LLMError(SharePointAIException):
    """Base class for LLM-related errors."""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(message, error_code="LLM_ERROR", **kwargs)


class LLMConnectionError(LLMError):
    """Raised when LLM service connection fails."""
    
    def __init__(self, message: str = "Failed to connect to LLM service", **kwargs):
        super().__init__(message, error_code="LLM_CONNECTION_ERROR", **kwargs)


class LLMTimeoutError(LLMError):
    """Raised when LLM request times out."""
    
    def __init__(self, message: str = "LLM request timed out", **kwargs):
        super().__init__(message, error_code="LLM_TIMEOUT", **kwargs)


class LLMResponseError(LLMError):
    """Raised when LLM returns invalid response."""
    
    def __init__(self, message: str = "Invalid LLM response", **kwargs):
        super().__init__(message, error_code="LLM_RESPONSE_ERROR", **kwargs)


class ValidationError(SharePointAIException):
    """Raised when input validation fails."""
    
    def __init__(self, message: str = "Invalid input provided", field_name: str = None, **kwargs):
        if field_name:
            message = f"Invalid {field_name}: {message}"
        super().__init__(message, error_code="VALIDATION_ERROR", **kwargs)
        self.field_name = field_name


class ConfigurationError(SharePointAIException):
    """Raised when configuration is invalid or missing."""
    
    def __init__(self, message: str = "Configuration error", config_key: str = None, **kwargs):
        if config_key:
            message = f"Configuration error for '{config_key}': {message}"
        super().__init__(message, error_code="CONFIG_ERROR", **kwargs)
        self.config_key = config_key


class SecurityError(SharePointAIException):
    """Raised when security validation fails."""
    
    def __init__(self, message: str = "Security validation failed", **kwargs):
        super().__init__(message, error_code="SECURITY_ERROR", **kwargs)


class RateLimitError(SharePointAIException):
    """Raised when rate limit is exceeded."""
    
    def __init__(self, message: str = "Rate limit exceeded", retry_after: int = None, **kwargs):
        super().__init__(message, error_code="RATE_LIMIT", **kwargs)
        self.retry_after = retry_after
