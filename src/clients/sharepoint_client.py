"""
Enhanced SharePoint client with comprehensive error handling and validation.
Provides robust SharePoint API interactions with retry logic and logging.
"""

import io
import time
from typing import Dict, List, Optional, Any
from contextlib import contextmanager

import pandas as pd
from office365.runtime.auth.client_credential import ClientCredential
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.files.file import File
from office365.runtime.client_request_exception import ClientRequestException

from ..core import (
    config_manager,
    SharePointConstants,
    SharePointConnectionError,
    SharePointAuthenticationError,
    SharePointResourceNotFoundError,
    SharePointTimeoutError,
    FileNotFoundError,
    FileDownloadError,
    get_logger,
    log_performance,
    log_function_call,
)
from ..utils import (
    validate_url,
    validate_credentials,
    validate_library_name,
    validate_search_query,
    validate_filename,
)

# Get logger for this module
logger = get_logger("sharepoint_client")


class SharePointClient:
    """
    Enhanced SharePoint client with error handling, validation, and retry logic.
    """

    def __init__(
        self, site_url: str = None, client_id: str = None, client_secret: str = None
    ):
        """
        Initialize SharePoint client with optional credentials.

        Args:
            site_url: SharePoint site URL (optional, uses config if not provided)
            client_id: SharePoint client ID (optional, uses config if not provided)
            client_secret: SharePoint client secret (optional, uses config if not provided)

        Raises:
            SharePointConnectionError: If connection fails
            SharePointAuthenticationError: If authentication fails
        """
        self.ctx: Optional[ClientContext] = None
        self.site_url: Optional[str] = None
        self.is_connected = False
        self.connection_time: Optional[float] = None

        # Use provided credentials or fall back to configuration
        if site_url and client_id and client_secret:
            self._connect_with_credentials(site_url, client_id, client_secret)
        else:
            self._connect_from_config()

    def _connect_from_config(self):
        """Connect using configuration manager settings."""
        try:
            if not config_manager.is_sharepoint_configured():
                logger.warning(
                    "SharePoint not configured, client will be in offline mode"
                )
                return

            config = config_manager.sharepoint
            self._connect_with_credentials(
                config.site_url, config.client_id, config.client_secret
            )

        except Exception as e:
            logger.error(f"Failed to connect using configuration: {e}")
            raise SharePointConnectionError(
                f"Configuration-based connection failed: {str(e)}"
            )

    @log_function_call(logger)
    def _connect_with_credentials(
        self, site_url: str, client_id: str, client_secret: str
    ):
        """
        Connect to SharePoint with provided credentials.

        Args:
            site_url: SharePoint site URL
            client_id: SharePoint client ID
            client_secret: SharePoint client secret

        Raises:
            SharePointConnectionError: If connection fails
            SharePointAuthenticationError: If authentication fails
        """
        try:
            # Validate inputs
            validated_url = validate_url(site_url)
            validated_client_id, validated_client_secret = validate_credentials(
                client_id, client_secret
            )

            logger.info(f"Connecting to SharePoint site: {validated_url}")

            with log_performance(logger, "SharePoint connection"):
                # Create credentials and context
                credentials = ClientCredential(
                    validated_client_id, validated_client_secret
                )
                self.ctx = ClientContext(validated_url).with_credentials(credentials)

                # Test connection by getting web properties
                web = self.ctx.web
                self.ctx.load(web)
                self.ctx.execute_query()

                # Store connection details
                self.site_url = validated_url
                self.is_connected = True
                self.connection_time = time.time()

                logger.info(
                    f"Successfully connected to SharePoint: {web.properties.get('Title', 'Unknown')}"
                )

        except ClientRequestException as e:
            logger.error(f"SharePoint API error during connection: {e}")
            if "401" in str(e) or "403" in str(e):
                raise SharePointAuthenticationError(f"Authentication failed: {str(e)}")
            else:
                raise SharePointConnectionError(f"SharePoint API error: {str(e)}")

        except Exception as e:
            logger.error(f"Unexpected error during SharePoint connection: {e}")
            raise SharePointConnectionError(f"Connection failed: {str(e)}")

    @contextmanager
    def _handle_sharepoint_errors(self, operation: str):
        """
        Context manager for handling SharePoint API errors.

        Args:
            operation: Description of the operation being performed
        """
        try:
            yield
        except ClientRequestException as e:
            logger.error(f"SharePoint API error during {operation}: {e}")
            error_code = str(e)

            if "401" in error_code or "403" in error_code:
                raise SharePointAuthenticationError(
                    f"Authentication failed during {operation}"
                )
            elif "404" in error_code:
                raise SharePointResourceNotFoundError(
                    f"Resource not found during {operation}"
                )
            elif "timeout" in error_code.lower():
                raise SharePointTimeoutError(f"Request timed out during {operation}")
            else:
                raise SharePointConnectionError(
                    f"SharePoint API error during {operation}: {str(e)}"
                )

        except Exception as e:
            logger.error(f"Unexpected error during {operation}: {e}")
            raise SharePointConnectionError(
                f"Unexpected error during {operation}: {str(e)}"
            )

    def _ensure_connected(self):
        """
        Ensure client is connected to SharePoint.

        Raises:
            SharePointConnectionError: If not connected
        """
        if not self.is_connected or not self.ctx:
            raise SharePointConnectionError(
                "Not connected to SharePoint. Call connect() first."
            )

    @log_function_call(logger)
    def list_document_libraries(self) -> List[Dict[str, Any]]:
        """
        Get all document libraries in the SharePoint site.

        Returns:
            List of document library information dictionaries

        Raises:
            SharePointConnectionError: If not connected or operation fails
        """
        self._ensure_connected()

        try:
            with log_performance(logger, "List document libraries"):
                with self._handle_sharepoint_errors("listing document libraries"):
                    # Get all lists from the site
                    lists = self.ctx.web.lists
                    self.ctx.load(lists)
                    self.ctx.execute_query()

                    # Filter for document libraries (BaseTemplate = 101)
                    libraries = []
                    for lst in lists:
                        if (
                            lst.properties.get("BaseTemplate")
                            == SharePointConstants.DOCUMENT_LIBRARY_TEMPLATE
                        ):
                            library_info = {
                                "title": lst.properties.get("Title", ""),
                                "description": lst.properties.get("Description", ""),
                                "item_count": lst.properties.get("ItemCount", 0),
                                "created": lst.properties.get("Created", ""),
                                "last_modified": lst.properties.get(
                                    "LastItemModifiedDate", ""
                                ),
                                "id": lst.properties.get("Id", ""),
                            }
                            libraries.append(library_info)

                    logger.info(f"Found {len(libraries)} document libraries")
                    return libraries

        except Exception as e:
            logger.error(f"Failed to list document libraries: {e}")
            raise

    @log_function_call(logger)
    def search_documents(self, library_title: str, query_text: str) -> pd.DataFrame:
        """
        Search for documents in a SharePoint library.

        Args:
            library_title: Name of the document library
            query_text: Search query text

        Returns:
            DataFrame with search results

        Raises:
            SharePointConnectionError: If not connected or operation fails
            SharePointResourceNotFoundError: If library not found
        """
        self._ensure_connected()

        # Validate inputs
        validated_library = validate_library_name(library_title)
        validated_query = validate_search_query(query_text)

        try:
            with log_performance(logger, f"Search documents in {validated_library}"):
                with self._handle_sharepoint_errors(
                    f"searching documents in {validated_library}"
                ):
                    # Get the document library
                    try:
                        library = self.ctx.web.lists.get_by_title(validated_library)
                        items = library.items
                        self.ctx.load(items)
                        self.ctx.execute_query()
                    except ClientRequestException as e:
                        if "404" in str(e):
                            raise SharePointResourceNotFoundError(
                                f"Library '{validated_library}' not found"
                            )
                        raise

                    # Search through items
                    results = []
                    query_lower = validated_query.lower()

                    for item in items:
                        file_name = item.properties.get("FileLeafRef", "")

                        # Check if query matches filename
                        if query_lower in file_name.lower():
                            result = {
                                "Name": file_name,
                                "Modified": item.properties.get("Modified", ""),
                                "Author": self._get_author_name(
                                    item.properties.get("Editor", {})
                                ),
                                "Size": item.properties.get("File_x0020_Size", 0),
                                "FileRef": item.properties.get("FileRef", ""),
                                "ContentType": item.properties.get("ContentType", ""),
                                "Created": item.properties.get("Created", ""),
                            }
                            results.append(result)

                    # Limit results
                    if len(results) > SharePointConstants.MAX_SEARCH_RESULTS:
                        logger.warning(
                            f"Search returned {len(results)} results, limiting to {SharePointConstants.MAX_SEARCH_RESULTS}"
                        )
                        results = results[: SharePointConstants.MAX_SEARCH_RESULTS]

                    logger.info(
                        f"Search found {len(results)} documents matching '{validated_query}'"
                    )
                    return pd.DataFrame(results)

        except Exception as e:
            logger.error(f"Failed to search documents: {e}")
            raise

    @log_function_call(logger)
    def download_file(self, library_title: str, file_name: str) -> io.BytesIO:
        """
        Download a file from SharePoint.

        Args:
            library_title: Name of the document library
            file_name: Name of the file to download

        Returns:
            BytesIO object containing file data

        Raises:
            SharePointConnectionError: If not connected or operation fails
            FileNotFoundError: If file not found
            FileDownloadError: If download fails
        """
        self._ensure_connected()

        # Validate inputs
        validated_library = validate_library_name(library_title)
        validated_filename = validate_filename(file_name)

        try:
            with log_performance(logger, f"Download file {validated_filename}"):
                with self._handle_sharepoint_errors(
                    f"downloading file {validated_filename}"
                ):
                    # Find the file URL
                    file_url = self._find_file_url(
                        validated_library, validated_filename
                    )

                    if not file_url:
                        raise FileNotFoundError(
                            f"File '{validated_filename}' not found in library '{validated_library}'"
                        )

                    # Download file content
                    logger.info(f"Downloading file from: {file_url}")
                    response = File.open_binary(self.ctx, file_url)

                    if not response or not response.content:
                        raise FileDownloadError(
                            f"Failed to download file content for '{validated_filename}'"
                        )

                    file_data = io.BytesIO(response.content)
                    logger.info(
                        f"Successfully downloaded {len(response.content)} bytes for '{validated_filename}'"
                    )

                    return file_data

        except (FileNotFoundError, FileDownloadError):
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            logger.error(f"Failed to download file: {e}")
            raise FileDownloadError(
                f"Download failed for '{validated_filename}': {str(e)}"
            )

    @log_function_call(logger)
    def list_items(
        self, list_title: str, filters: Optional[Dict[str, str]] = None
    ) -> pd.DataFrame:
        """
        Get items from a SharePoint list.

        Args:
            list_title: Name of the SharePoint list
            filters: Optional dictionary of field filters

        Returns:
            DataFrame with list items

        Raises:
            SharePointConnectionError: If not connected or operation fails
            SharePointResourceNotFoundError: If list not found
        """
        self._ensure_connected()

        # Validate inputs
        validated_list_title = validate_library_name(
            list_title
        )  # Same validation as library names

        try:
            with log_performance(logger, f"List items from {validated_list_title}"):
                with self._handle_sharepoint_errors(
                    f"listing items from {validated_list_title}"
                ):
                    # Get the list
                    try:
                        sp_list = self.ctx.web.lists.get_by_title(validated_list_title)
                        items = sp_list.items
                        self.ctx.load(items)
                        self.ctx.execute_query()
                    except ClientRequestException as e:
                        if "404" in str(e):
                            raise SharePointResourceNotFoundError(
                                f"List '{validated_list_title}' not found"
                            )
                        raise

                    # Process items
                    results = []
                    for item in items:
                        item_data = dict(item.properties)

                        # Apply filters if provided
                        if filters:
                            matches = True
                            for field, value in filters.items():
                                item_value = str(item_data.get(field, "")).lower()
                                if value.lower() not in item_value:
                                    matches = False
                                    break

                            if not matches:
                                continue

                        results.append(item_data)

                    logger.info(
                        f"Retrieved {len(results)} items from list '{validated_list_title}'"
                    )
                    return pd.DataFrame(results)

        except Exception as e:
            logger.error(f"Failed to list items: {e}")
            raise

    @log_function_call(logger)
    def search_list_items(self, list_title: str, query_text: str) -> pd.DataFrame:
        """
        Search for items in a SharePoint list based on query text.

        Args:
            list_title: Name of the SharePoint list
            query_text: Search query text (e.g., "Status: Pending", "Assigned To: John")

        Returns:
            DataFrame with filtered list items

        Raises:
            SharePointConnectionError: If not connected or operation fails
            SharePointResourceNotFoundError: If list not found
        """
        self._ensure_connected()

        # Validate inputs
        validated_list_title = validate_library_name(list_title)
        validated_query = validate_search_query(query_text)

        try:
            with log_performance(
                logger, f"Search list items in {validated_list_title}"
            ):
                with self._handle_sharepoint_errors(
                    f"searching list items in {validated_list_title}"
                ):
                    # Get all items from the list first
                    sp_list = self.ctx.web.lists.get_by_title(validated_list_title)
                    items = sp_list.items
                    self.ctx.load(items)
                    self.ctx.execute_query()

                    # Parse query text for field:value pairs or general search
                    search_filters = self._parse_search_query(validated_query)

                    # Process and filter items
                    results = []
                    query_lower = validated_query.lower()

                    for item in items:
                        item_data = dict(item.properties)
                        should_include = False

                        # If we have specific field filters, use them
                        if search_filters:
                            matches = True
                            for field, value in search_filters.items():
                                item_value = str(item_data.get(field, "")).lower()
                                if value.lower() not in item_value:
                                    matches = False
                                    break
                            should_include = matches
                        else:
                            # General search across all text fields
                            for key, value in item_data.items():
                                if (
                                    isinstance(value, str)
                                    and query_lower in value.lower()
                                ):
                                    should_include = True
                                    break

                        if should_include:
                            # Clean up the item data for display
                            cleaned_item = self._clean_list_item_data(item_data)
                            results.append(cleaned_item)

                    # Limit results
                    if len(results) > SharePointConstants.MAX_SEARCH_RESULTS:
                        logger.warning(
                            f"List search returned {len(results)} results, limiting to {SharePointConstants.MAX_SEARCH_RESULTS}"
                        )
                        results = results[: SharePointConstants.MAX_SEARCH_RESULTS]

                    logger.info(
                        f"List search found {len(results)} items matching '{validated_query}'"
                    )
                    return pd.DataFrame(results)

        except Exception as e:
            logger.error(f"Failed to search list items: {e}")
            raise

    def _parse_search_query(self, query_text: str) -> Dict[str, str]:
        """
        Parse search query text to extract field:value pairs.

        Args:
            query_text: Search query (e.g., "Status: Pending", "Assigned To: John")

        Returns:
            Dictionary of field-value pairs for filtering
        """
        filters = {}

        # Look for field:value patterns
        if ":" in query_text:
            parts = query_text.split(",")
            for part in parts:
                if ":" in part:
                    field, value = part.split(":", 1)
                    field = field.strip()
                    value = value.strip()

                    # Map common field names to SharePoint internal names
                    field_mapping = {
                        "status": "Status",
                        "assigned to": "AssignedTo",
                        "assigned": "AssignedTo",
                        "title": "Title",
                        "due date": "DueDate",
                        "priority": "Priority",
                        "category": "Category",
                    }

                    mapped_field = field_mapping.get(field.lower(), field)
                    filters[mapped_field] = value

        return filters

    def _clean_list_item_data(self, item_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clean and format list item data for display.

        Args:
            item_data: Raw SharePoint item data

        Returns:
            Cleaned item data dictionary
        """
        # Common fields to include in results
        display_fields = {
            "Title": "Title",
            "AssignedTo": "Assigned To",
            "Status": "Status",
            "DueDate": "Due Date",
            "Priority": "Priority",
            "Category": "Category",
            "Created": "Created",
            "Modified": "Modified",
            "Author": "Author",
        }

        cleaned = {}

        for internal_name, display_name in display_fields.items():
            value = item_data.get(internal_name)

            if value is not None:
                # Handle different data types
                if isinstance(value, dict):
                    # Handle user fields
                    if "Title" in value:
                        cleaned[display_name] = value["Title"]
                    else:
                        cleaned[display_name] = str(value)
                elif isinstance(value, str):
                    # Clean up date strings and other text
                    if "T" in value and len(value) > 10:  # Likely a date
                        try:
                            # Format date nicely
                            from datetime import datetime

                            dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
                            cleaned[display_name] = dt.strftime("%Y-%m-%d")
                        except:
                            cleaned[display_name] = value
                    else:
                        cleaned[display_name] = value
                else:
                    cleaned[display_name] = str(value)

        # If no standard fields found, include the title at minimum
        if not cleaned and "Title" in item_data:
            cleaned["Title"] = item_data["Title"]

        return cleaned

    def _find_file_url(self, library_title: str, file_name: str) -> Optional[str]:
        """
        Find the URL of a file in a SharePoint library.

        Args:
            library_title: Name of the document library
            file_name: Name of the file

        Returns:
            File URL if found, None otherwise
        """
        try:
            library = self.ctx.web.lists.get_by_title(library_title)
            items = library.items
            self.ctx.load(items)
            self.ctx.execute_query()

            for item in items:
                if file_name == item.properties.get("FileLeafRef"):
                    return item.properties.get("FileRef")

            return None

        except Exception as e:
            logger.error(f"Error finding file URL: {e}")
            return None

    def _get_author_name(self, editor_info: Dict[str, Any]) -> str:
        """
        Extract author name from SharePoint editor information.

        Args:
            editor_info: Editor information dictionary

        Returns:
            Author name or 'Unknown' if not available
        """
        if isinstance(editor_info, dict):
            return editor_info.get("Title", "Unknown")
        return "Unknown"

    def get_connection_info(self) -> Dict[str, Any]:
        """
        Get information about the current SharePoint connection.

        Returns:
            Dictionary with connection information
        """
        return {
            "is_connected": self.is_connected,
            "site_url": self.site_url,
            "connection_time": self.connection_time,
            "uptime_seconds": (
                time.time() - self.connection_time if self.connection_time else None
            ),
        }

    def disconnect(self):
        """Disconnect from SharePoint and clean up resources."""
        if self.ctx:
            self.ctx = None

        self.is_connected = False
        self.site_url = None
        self.connection_time = None

        logger.info("Disconnected from SharePoint")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()
