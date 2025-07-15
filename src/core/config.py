"""
Enhanced configuration management for the SharePoint AI Assistant.
Handles environment variables, validation, and configuration loading.
"""

import os
import sys
import socket
import requests
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from pathlib import Path

from .constants import EnvironmentConstants, SharePointConstants, LLMConstants
from .exceptions import ConfigurationError
from .logging_config import get_logger

# Get logger for this module
logger = get_logger("config")


def check_python_version():
    """
    Check if the current Python version meets the minimum requirement.

    Raises:
        ConfigurationError: If Python version is below 3.11
    """
    required_version = (3, 11)
    current_version = sys.version_info[:2]

    if current_version < required_version:
        error_msg = (
            f"Python {required_version[0]}.{required_version[1]}+ is required. "
            f"Current version: {current_version[0]}.{current_version[1]}.{sys.version_info[2]}\n"
            f"Please install Python 3.11 or higher from https://www.python.org/downloads/"
        )
        logger.error(error_msg)
        raise ConfigurationError(error_msg)

    logger.info(
        f"Python version check passed: {current_version[0]}.{current_version[1]}.{sys.version_info[2]}"
    )


@dataclass
class SharePointConfig:
    """SharePoint configuration settings."""

    site_url: str
    client_id: str
    client_secret: str
    connection_timeout: int = SharePointConstants.CONNECTION_TIMEOUT
    request_timeout: int = SharePointConstants.REQUEST_TIMEOUT
    download_timeout: int = SharePointConstants.DOWNLOAD_TIMEOUT


@dataclass
class LLMConfig:
    """LLM configuration settings."""

    host: str
    model: str
    max_tokens: int = LLMConstants.MAX_TOKENS
    temperature: float = LLMConstants.TEMPERATURE
    timeout: int = LLMConstants.LLM_TIMEOUT


@dataclass
class AppConfig:
    """Main application configuration."""

    debug_mode: bool = False
    log_level: str = "INFO"
    secret_key: Optional[str] = None
    allowed_hosts: list = None


class ConfigManager:
    """Manages application configuration from environment variables and files."""

    def __init__(self):
        """Initialize configuration manager."""
        self._sharepoint_config: Optional[SharePointConfig] = None
        self._llm_config: Optional[LLMConfig] = None
        self._app_config: Optional[AppConfig] = None

        # Load configuration on initialization
        self._load_configuration()

    def _load_configuration(self):
        """Load all configuration from environment variables."""
        try:
            logger.info("Loading application configuration")

            # Load each configuration section
            self._sharepoint_config = self._load_sharepoint_config()
            self._llm_config = self._load_llm_config()
            self._app_config = self._load_app_config()

            logger.info("Configuration loaded successfully")

        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            raise ConfigurationError(f"Configuration loading failed: {e}")

    def _load_sharepoint_config(self) -> SharePointConfig:
        """Load SharePoint configuration from environment variables."""
        site_url = os.getenv(EnvironmentConstants.SHAREPOINT_SITE_URL, "")
        client_id = os.getenv(EnvironmentConstants.SHAREPOINT_CLIENT_ID, "")
        client_secret = os.getenv(EnvironmentConstants.SHAREPOINT_CLIENT_SECRET, "")

        # Validate required fields
        if not site_url:
            logger.warning("SharePoint site URL not configured")
        if not client_id:
            logger.warning("SharePoint client ID not configured")
        if not client_secret:
            logger.warning("SharePoint client secret not configured")

        # Validate URL format if provided
        if site_url and not self._is_valid_url(site_url):
            raise ConfigurationError(
                f"Invalid SharePoint site URL format: {site_url}",
                config_key=EnvironmentConstants.SHAREPOINT_SITE_URL,
            )

        return SharePointConfig(
            site_url=site_url, client_id=client_id, client_secret=client_secret
        )

    def _load_llm_config(self) -> LLMConfig:
        """Load LLM configuration from environment variables with smart host detection."""
        # Use smart host detection if no explicit host is set
        host = self._get_default_ollama_host()
        model = os.getenv(EnvironmentConstants.LLM_MODEL, LLMConstants.DEFAULT_MODEL)

        # Validate host URL format
        if not self._is_valid_url(host):
            raise ConfigurationError(
                f"Invalid LLM host URL format: {host}",
                config_key=EnvironmentConstants.OLLAMA_HOST,
            )

        return LLMConfig(host=host, model=model)

    def _load_app_config(self) -> AppConfig:
        """Load application configuration from environment variables."""
        debug_mode = (
            os.getenv(EnvironmentConstants.DEBUG_MODE, "false").lower() == "true"
        )
        log_level = os.getenv(EnvironmentConstants.LOG_LEVEL, "INFO").upper()
        secret_key = os.getenv(EnvironmentConstants.SECRET_KEY)
        allowed_hosts_str = os.getenv(EnvironmentConstants.ALLOWED_HOSTS, "")

        # Parse allowed hosts
        allowed_hosts = []
        if allowed_hosts_str:
            allowed_hosts = [host.strip() for host in allowed_hosts_str.split(",")]

        # Validate log level
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if log_level not in valid_log_levels:
            raise ConfigurationError(
                f"Invalid log level: {log_level}. Must be one of: {valid_log_levels}",
                config_key=EnvironmentConstants.LOG_LEVEL,
            )

        return AppConfig(
            debug_mode=debug_mode,
            log_level=log_level,
            secret_key=secret_key,
            allowed_hosts=allowed_hosts,
        )

    def _is_running_in_docker(self) -> bool:
        """
        Detect if the application is running inside a Docker container.

        Returns:
            True if running in Docker, False otherwise
        """
        try:
            # Check for .dockerenv file (most reliable method)
            if Path("/.dockerenv").exists():
                return True

            # Check for Docker-specific cgroup entries
            if Path("/proc/1/cgroup").exists():
                with open("/proc/1/cgroup", "r") as f:
                    content = f.read()
                    if "docker" in content or "containerd" in content:
                        return True

            # Check for container-specific environment variables
            container_vars = ["DOCKER_CONTAINER", "KUBERNETES_SERVICE_HOST"]
            if any(os.getenv(var) for var in container_vars):
                return True

        except Exception as e:
            logger.debug(f"Error detecting Docker environment: {e}")

        return False

    def _test_ollama_connection(self, host: str, timeout: int = 5) -> bool:
        """
        Test connection to Ollama service.

        Args:
            host: Ollama host URL to test
            timeout: Connection timeout in seconds

        Returns:
            True if connection successful, False otherwise
        """
        try:
            # Test basic connectivity
            response = requests.get(f"{host}/api/tags", timeout=timeout)
            return response.status_code == 200
        except Exception as e:
            logger.debug(f"Ollama connection test failed for {host}: {e}")
            return False

    def _get_default_ollama_host(self) -> str:
        """
        Intelligently determine the default Ollama host based on environment.

        Returns:
            Default Ollama host URL
        """
        # Check if explicitly set in environment
        explicit_host = os.getenv(EnvironmentConstants.OLLAMA_HOST)
        if explicit_host:
            logger.info(f"Using explicit Ollama host from environment: {explicit_host}")
            return explicit_host

        # Determine candidates based on environment
        if self._is_running_in_docker():
            logger.info("Detected Docker environment")
            candidates = [
                "http://ollama:11434",  # Docker container networking
                "http://host.docker.internal:11434",  # Docker Desktop bridge
                "http://localhost:11434",  # Fallback to localhost
            ]
        else:
            logger.info("Detected local environment")
            candidates = [
                "http://localhost:11434",  # Local Ollama installation
                "http://127.0.0.1:11434",  # Alternative localhost
            ]

        # Test each candidate
        for candidate in candidates:
            logger.debug(f"Testing Ollama connection to: {candidate}")
            if self._test_ollama_connection(candidate):
                logger.info(f"Found working Ollama instance at: {candidate}")
                return candidate

        # If no working instance found, return the most appropriate default
        default_host = candidates[0]
        logger.warning(
            f"No working Ollama instance found, using default: {default_host}"
        )
        return default_host

    def _is_valid_url(self, url: str) -> bool:
        """
        Enhanced URL validation that supports Docker container networking.

        Args:
            url: URL string to validate

        Returns:
            True if URL is valid, False otherwise
        """
        import re

        # Enhanced URL validation pattern that includes:
        # - Traditional domains (example.com)
        # - Localhost variants
        # - IP addresses
        # - Docker container names (single word hostnames)
        # - Docker internal networking
        url_pattern = re.compile(
            r"^https?://"  # http:// or https://
            r"(?:"
            r"(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|"  # Traditional domain
            r"localhost|"  # localhost
            r"127\.0\.0\.1|"  # localhost IP
            r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|"  # IP address
            r"[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?|"  # Simple hostname (Docker containers)
            r"host\.docker\.internal"  # Docker Desktop bridge
            r")"
            r"(?::\d+)?"  # optional port
            r"(?:/?|[/?]\S+)$",
            re.IGNORECASE,
        )

        is_valid = bool(url_pattern.match(url))

        if not is_valid:
            logger.debug(f"URL validation failed for: {url}")

        return is_valid

    @property
    def sharepoint(self) -> SharePointConfig:
        """Get SharePoint configuration."""
        if self._sharepoint_config is None:
            raise ConfigurationError("SharePoint configuration not loaded")
        return self._sharepoint_config

    @property
    def llm(self) -> LLMConfig:
        """Get LLM configuration."""
        if self._llm_config is None:
            raise ConfigurationError("LLM configuration not loaded")
        return self._llm_config

    @property
    def app(self) -> AppConfig:
        """Get application configuration."""
        if self._app_config is None:
            raise ConfigurationError("Application configuration not loaded")
        return self._app_config

    def is_sharepoint_configured(self) -> bool:
        """
        Check if SharePoint is properly configured.

        Returns:
            True if all required SharePoint settings are present
        """
        try:
            config = self.sharepoint
            return bool(config.site_url and config.client_id and config.client_secret)
        except ConfigurationError:
            return False

    def validate_configuration(self) -> Dict[str, Any]:
        """
        Validate all configuration and return validation results.

        Returns:
            Dictionary with validation results for each component
        """
        results = {
            "sharepoint": {"valid": False, "errors": []},
            "llm": {"valid": False, "errors": []},
            "app": {"valid": False, "errors": []},
        }

        # Validate SharePoint configuration
        try:
            sp_config = self.sharepoint
            if not sp_config.site_url:
                results["sharepoint"]["errors"].append("Site URL is required")
            if not sp_config.client_id:
                results["sharepoint"]["errors"].append("Client ID is required")
            if not sp_config.client_secret:
                results["sharepoint"]["errors"].append("Client secret is required")

            results["sharepoint"]["valid"] = len(results["sharepoint"]["errors"]) == 0

        except ConfigurationError as e:
            results["sharepoint"]["errors"].append(str(e))

        # Validate LLM configuration
        try:
            llm_config = self.llm
            if not llm_config.host:
                results["llm"]["errors"].append("LLM host is required")
            if not llm_config.model:
                results["llm"]["errors"].append("LLM model is required")

            results["llm"]["valid"] = len(results["llm"]["errors"]) == 0

        except ConfigurationError as e:
            results["llm"]["errors"].append(str(e))

        # Validate application configuration
        try:
            app_config = self.app
            results["app"]["valid"] = True  # App config is always valid with defaults

        except ConfigurationError as e:
            results["app"]["errors"].append(str(e))

        return results

    def get_config_summary(self) -> Dict[str, Any]:
        """
        Get a summary of current configuration (without sensitive data).

        Returns:
            Dictionary with configuration summary
        """
        summary = {}

        try:
            sp_config = self.sharepoint
            summary["sharepoint"] = {
                "site_url": sp_config.site_url,
                "client_id_configured": bool(sp_config.client_id),
                "client_secret_configured": bool(sp_config.client_secret),
                "timeouts": {
                    "connection": sp_config.connection_timeout,
                    "request": sp_config.request_timeout,
                    "download": sp_config.download_timeout,
                },
            }
        except ConfigurationError:
            summary["sharepoint"] = {"error": "Configuration not loaded"}

        try:
            llm_config = self.llm
            summary["llm"] = {
                "host": llm_config.host,
                "model": llm_config.model,
                "max_tokens": llm_config.max_tokens,
                "temperature": llm_config.temperature,
                "timeout": llm_config.timeout,
            }
        except ConfigurationError:
            summary["llm"] = {"error": "Configuration not loaded"}

        try:
            app_config = self.app
            summary["app"] = {
                "debug_mode": app_config.debug_mode,
                "log_level": app_config.log_level,
                "secret_key_configured": bool(app_config.secret_key),
                "allowed_hosts": app_config.allowed_hosts,
            }
        except ConfigurationError:
            summary["app"] = {"error": "Configuration not loaded"}

        return summary


# Global configuration instance
config_manager = ConfigManager()


# Convenience functions for backward compatibility
def get_sharepoint_config() -> Dict[str, str]:
    """
    Get SharePoint configuration in legacy format.

    Returns:
        Dictionary with SharePoint configuration
    """
    try:
        config = config_manager.sharepoint
        return {
            "site_url": config.site_url,
            "client_id": config.client_id,
            "client_secret": config.client_secret,
        }
    except ConfigurationError:
        logger.warning("SharePoint configuration not available, returning empty config")
        return {"site_url": "", "client_id": "", "client_secret": ""}


def get_ollama_host() -> str:
    """
    Get Ollama host URL.

    Returns:
        Ollama host URL
    """
    try:
        return config_manager.llm.host
    except ConfigurationError:
        logger.warning("LLM configuration not available, returning default host")
        return LLMConstants.DEFAULT_OLLAMA_HOST
