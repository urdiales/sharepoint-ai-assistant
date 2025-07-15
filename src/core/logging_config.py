"""
Logging configuration for the SharePoint AI Assistant.
Sets up structured logging with different levels and handlers.
"""

import logging
import logging.handlers
import os
from pathlib import Path
from typing import Optional

from .constants import LoggingConstants, EnvironmentConstants


def setup_logging(
    log_level: str = None,
    log_dir: str = "logs",
    enable_console: bool = True,
    enable_file: bool = True
) -> logging.Logger:
    """
    Set up logging configuration for the application.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: Directory to store log files
        enable_console: Whether to enable console logging
        enable_file: Whether to enable file logging
    
    Returns:
        Configured logger instance
    """
    # Get log level from environment or use provided value
    if log_level is None:
        log_level = os.getenv(EnvironmentConstants.LOG_LEVEL, LoggingConstants.INFO)
    
    # Convert string level to logging constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Create logs directory if it doesn't exist
    if enable_file:
        log_path = Path(log_dir)
        log_path.mkdir(exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # Clear any existing handlers
    root_logger.handlers.clear()
    
    # Create formatters
    detailed_formatter = logging.Formatter(LoggingConstants.DETAILED_FORMAT)
    simple_formatter = logging.Formatter(LoggingConstants.SIMPLE_FORMAT)
    
    # Console handler
    if enable_console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(numeric_level)
        console_handler.setFormatter(simple_formatter)
        root_logger.addHandler(console_handler)
    
    # File handlers
    if enable_file:
        # Main application log file with rotation
        main_log_file = log_path / "sharepoint_ai.log"
        file_handler = logging.handlers.RotatingFileHandler(
            main_log_file,
            maxBytes=LoggingConstants.MAX_LOG_SIZE,
            backupCount=LoggingConstants.BACKUP_COUNT
        )
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(detailed_formatter)
        root_logger.addHandler(file_handler)
        
        # Error log file (only ERROR and CRITICAL messages)
        error_log_file = log_path / "errors.log"
        error_handler = logging.handlers.RotatingFileHandler(
            error_log_file,
            maxBytes=LoggingConstants.MAX_LOG_SIZE,
            backupCount=LoggingConstants.BACKUP_COUNT
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(detailed_formatter)
        root_logger.addHandler(error_handler)
    
    # Get main application logger
    logger = logging.getLogger(LoggingConstants.MAIN_LOGGER)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module.
    
    Args:
        name: Logger name (usually module name)
    
    Returns:
        Logger instance
    """
    return logging.getLogger(f"{LoggingConstants.MAIN_LOGGER}.{name}")


def log_function_call(logger: logging.Logger):
    """
    Decorator to log function calls with parameters and execution time.
    
    Args:
        logger: Logger instance to use
    
    Returns:
        Decorator function
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            import time
            import functools
            
            # Log function entry
            logger.debug(f"Entering {func.__name__} with args={args}, kwargs={kwargs}")
            
            start_time = time.time()
            try:
                # Execute function
                result = func(*args, **kwargs)
                
                # Log successful completion
                execution_time = time.time() - start_time
                logger.debug(f"Completed {func.__name__} in {execution_time:.3f}s")
                
                return result
                
            except Exception as e:
                # Log exception
                execution_time = time.time() - start_time
                logger.error(f"Error in {func.__name__} after {execution_time:.3f}s: {str(e)}")
                raise
        
        return wrapper
    return decorator


def log_performance(logger: logging.Logger, operation: str):
    """
    Context manager to log performance metrics for operations.
    
    Args:
        logger: Logger instance to use
        operation: Name of the operation being measured
    
    Usage:
        with log_performance(logger, "SharePoint API call"):
            # Your code here
            pass
    """
    class PerformanceLogger:
        def __init__(self, logger: logging.Logger, operation: str):
            self.logger = logger
            self.operation = operation
            self.start_time = None
        
        def __enter__(self):
            self.start_time = time.time()
            self.logger.debug(f"Starting {self.operation}")
            return self
        
        def __exit__(self, exc_type, exc_val, exc_tb):
            import time
            execution_time = time.time() - self.start_time
            
            if exc_type is None:
                self.logger.info(f"Completed {self.operation} in {execution_time:.3f}s")
            else:
                self.logger.error(f"Failed {self.operation} after {execution_time:.3f}s: {exc_val}")
    
    return PerformanceLogger(logger, operation)


def configure_third_party_loggers():
    """
    Configure logging levels for third-party libraries to reduce noise.
    """
    # Reduce verbosity of common third-party libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("office365").setLevel(logging.WARNING)
    logging.getLogger("langchain").setLevel(logging.WARNING)
    logging.getLogger("streamlit").setLevel(logging.WARNING)


# Initialize logging when module is imported
def initialize_logging():
    """Initialize logging configuration on module import."""
    try:
        # Set up basic logging configuration
        logger = setup_logging()
        
        # Configure third-party loggers
        configure_third_party_loggers()
        
        logger.info("Logging system initialized successfully")
        
    except Exception as e:
        # Fallback to basic logging if setup fails
        logging.basicConfig(
            level=logging.INFO,
            format=LoggingConstants.SIMPLE_FORMAT
        )
        logging.error(f"Failed to initialize advanced logging: {e}")


# Auto-initialize when module is imported
initialize_logging()
