"""
Handles SharePoint authentication, list/document search, and file download.
This module provides a client for interacting with SharePoint using the Office 365 REST API.
"""

from office365.runtime.auth.client_credential import ClientCredential
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.files.file import File
from app.config import get_sharepoint_config
import pandas as pd
import io

class SharePointClient:
    def __init__(self):
        # Get SharePoint configuration from environment variables
        config = get_sharepoint_config()
        self.site_url = config["site_url"]
        self.ctx = None
        
        # Only attempt connection if all required credentials are provided
        if self.site_url and config["client_id"] and config["client_secret"]:
            self._connect(config["client_id"], config["client_secret"])

    def _connect(self, client_id, client_secret):
        # Connect to SharePoint site using client credentials authentication
        # This method establishes the connection to the SharePoint site
        creds = ClientCredential(client_id, client_secret)
        self.ctx = ClientContext(self.site_url).with_credentials(creds)

    def list_document_libraries(self):
        # Returns all document libraries in the site
        # Document libraries have BaseTemplate=101 in SharePoint
        lists = self.ctx.web.lists
        self.ctx.load(lists)
        self.ctx.execute_query()
        return [lst for lst in lists if lst.properties["BaseTemplate"] == 101]

    def search_documents(self, library_title, query_text):
        # Search documents in the given library by query_text in title
        # Returns a DataFrame with Name, Modified date, and Author information
        result = []
        
        # Get the specified document library by title
        lib = self.ctx.web.lists.get_by_title(library_title)
        items = lib.items
        self.ctx.load(items)
        self.ctx.execute_query()
        
        # Filter items where the filename (FileLeafRef) contains the query text
        for item in items:
            if query_text.lower() in item.properties.get('FileLeafRef', '').lower():
                result.append({
                    "Name": item.properties.get('FileLeafRef'),
                    "Modified": item.properties.get('Modified'),
                    "Author": item.properties.get('Editor', {}).get('Title', 'Unknown')
                })
        return pd.DataFrame(result)

    def download_file(self, library_title, file_name):
        # Download file contents by name
        # Returns a BytesIO object containing the file data
        lib = self.ctx.web.lists.get_by_title(library_title)
        items = lib.items
        self.ctx.load(items)
        self.ctx.execute_query()
        
        # Find the file URL by matching the filename
        file_url = None
        for item in items:
            if file_name == item.properties.get('FileLeafRef'):
                file_url = item.properties.get('FileRef')
                break
                
        # If file is found, download its binary content
        if file_url:
            response = File.open_binary(self.ctx, file_url)
            return io.BytesIO(response.content)
        return None

    def list_items(self, list_title, filters=None):
        # Query SharePoint list items, optionally filter by field values
        # Returns a DataFrame containing all list items that match the filters
        result = []
        
        # Get the specified list by title
        lst = self.ctx.web.lists.get_by_title(list_title)
        items = lst.items
        self.ctx.load(items)
        self.ctx.execute_query()
        
        # Process each item, applying filters if provided
        for item in items:
            item_data = item.properties
            # Apply filters if provided, otherwise include all items
            if not filters or all(str(item_data.get(f, '')).lower() == v.lower() for f, v in filters.items()):
                result.append(item_data)
        return pd.DataFrame(result)
