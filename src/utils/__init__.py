"""
Utilities module for the SharePoint AI Assistant.
Contains validation, file processing, and other utility functions.
"""

from .validation import (
    validate_url,
    validate_search_query,
    validate_filename,
    validate_file_extension,
    validate_file_size,
    validate_user_input,
    validate_credentials,
    validate_library_name,
    sanitize_html
)

from .file_utils import (
    preview_pdf,
    preview_docx,
    preview_xlsx,
    get_file_info,
    format_file_size,
    is_file_type_supported,
    get_preview_function
)

__all__ = [
    # Validation functions
    "validate_url",
    "validate_search_query",
    "validate_filename",
    "validate_file_extension",
    "validate_file_size",
    "validate_user_input",
    "validate_credentials",
    "validate_library_name",
    "sanitize_html",
    
    # File utility functions
    "preview_pdf",
    "preview_docx",
    "preview_xlsx",
    "get_file_info",
    "format_file_size",
    "is_file_type_supported",
    "get_preview_function"
]
