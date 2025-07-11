"""
Loads configuration and secrets for the application.
This module centralizes access to environment variables used throughout the app.
"""

import os

def get_sharepoint_config():
    # Retrieve SharePoint configuration from environment variables
    # Returns a dictionary with site_url, client_id, and client_secret
    return {
        "site_url": os.getenv("SHAREPOINT_SITE_URL", ""),
        "client_id": os.getenv("SHAREPOINT_CLIENT_ID", ""),
        "client_secret": os.getenv("SHAREPOINT_CLIENT_SECRET", "")
    }

def get_ollama_host():
    # Ollama server host, default to Docker Compose service or localhost
    # This allows flexibility in deployment configurations
    return os.getenv("OLLAMA_HOST", "http://ollama:11434")
