"""
SharePoint AI Assistant - Enhanced Version
A robust, production-ready SharePoint AI Assistant with comprehensive error handling.
"""

__version__ = "1.0.0"
__author__ = "SharePoint AI Assistant Team"
__description__ = "Enhanced SharePoint AI Assistant with comprehensive error handling and validation"

# Import main components for easy access
from .core import (
    config_manager,
    get_logger,
    setup_logging,
    SharePointConstants,
    LLMConstants,
    UIConstants
)

from .clients import SharePointClient
from .services import LLMService, create_llm_agent
from .ui import main as ui_main

__all__ = [
    "__version__",
    "__author__",
    "__description__",
    "config_manager",
    "get_logger",
    "setup_logging",
    "SharePointConstants",
    "LLMConstants",
    "UIConstants",
    "SharePointClient",
    "LLMService",
    "create_llm_agent",
    "ui_main"
]
