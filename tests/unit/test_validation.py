"""
Unit tests for validation utilities.
Tests input validation and sanitization functions.
"""

import pytest
from src.utils.validation import (
    validate_url,
    validate_search_query,
    validate_filename,
    validate_file_extension,
    validate_file_size,
    validate_user_input,
    validate_credentials,
    sanitize_html
)
from src.core.exceptions import ValidationError, SecurityError


class TestValidateUrl:
    """Test URL validation function."""
    
    def test_valid_https_url(self):
        """Test valid HTTPS URL."""
        url = "https://example.com/path"
        result = validate_url(url)
        assert result == url
    
    def test_valid_http_url(self):
        """Test valid HTTP URL."""
        url = "http://example.com"
        result = validate_url(url)
        assert result == url
    
    def test_localhost_allowed(self):
        """Test localhost URL when allowed."""
        url = "http://localhost:8080"
        result = validate_url(url, allow_localhost=True)
        assert result == url
    
    def test_localhost_not_allowed(self):
        """Test localhost URL when not allowed."""
        url = "http://localhost:8080"
        with pytest.raises(ValidationError, match="Localhost URLs are not allowed"):
            validate_url(url, allow_localhost=False)
    
    def test_empty_url(self):
        """Test empty URL."""
        with pytest.raises(ValidationError, match="URL cannot be empty"):
            validate_url("")
    
    def test_invalid_scheme(self):
        """Test invalid URL scheme."""
        with pytest.raises(ValidationError, match="URL must use http or https protocol"):
            validate_url("ftp://example.com")
    
    def test_no_hostname(self):
        """Test URL without hostname."""
        with pytest.raises(ValidationError, match="URL must have a valid hostname"):
            validate_url("https://")


class TestValidateSearchQuery:
    """Test search query validation function."""
    
    def test_valid_query(self):
        """Test valid search query."""
        query = "test document"
        result = validate_search_query(query)
        assert result == query
    
    def test_empty_query(self):
        """Test empty search query."""
        with pytest.raises(ValidationError, match="Search query cannot be empty"):
            validate_search_query("")
    
    def test_query_with_whitespace(self):
        """Test query with leading/trailing whitespace."""
        query = "  test document  "
        result = validate_search_query(query)
        assert result == "test document"
    
    def test_dangerous_characters(self):
        """Test query with dangerous characters."""
        with pytest.raises(SecurityError, match="potentially dangerous character"):
            validate_search_query("test<script>")
    
    def test_sql_injection_keywords(self):
        """Test query with SQL injection keywords."""
        with pytest.raises(SecurityError, match="potentially dangerous keyword"):
            validate_search_query("test SELECT * FROM")


class TestValidateFilename:
    """Test filename validation function."""
    
    def test_valid_filename(self):
        """Test valid filename."""
        filename = "document.pdf"
        result = validate_filename(filename)
        assert result == filename
    
    def test_empty_filename(self):
        """Test empty filename."""
        with pytest.raises(ValidationError, match="Filename cannot be empty"):
            validate_filename("")
    
    def test_filename_with_whitespace(self):
        """Test filename with leading/trailing whitespace."""
        filename = "  document.pdf  "
        result = validate_filename(filename)
        assert result == "document.pdf"
    
    def test_invalid_characters(self):
        """Test filename with invalid characters."""
        with pytest.raises(ValidationError, match="invalid character"):
            validate_filename("document<test>.pdf")
    
    def test_reserved_name(self):
        """Test filename with reserved name."""
        with pytest.raises(ValidationError, match="reserved name"):
            validate_filename("CON.txt")


class TestValidateFileExtension:
    """Test file extension validation function."""
    
    def test_valid_extension(self):
        """Test valid file extension."""
        filename = "document.pdf"
        result = validate_file_extension(filename)
        assert result == ".pdf"
    
    def test_no_extension(self):
        """Test filename without extension."""
        with pytest.raises(ValidationError, match="File must have an extension"):
            validate_file_extension("document")
    
    def test_invalid_extension(self):
        """Test invalid file extension."""
        with pytest.raises(ValidationError, match="not allowed"):
            validate_file_extension("document.exe")
    
    def test_custom_allowed_extensions(self):
        """Test with custom allowed extensions."""
        filename = "document.txt"
        result = validate_file_extension(filename, [".txt", ".md"])
        assert result == ".txt"


class TestValidateFileSize:
    """Test file size validation function."""
    
    def test_valid_file_size(self):
        """Test valid file size."""
        size = 1024 * 1024  # 1MB
        result = validate_file_size(size)
        assert result == size
    
    def test_negative_size(self):
        """Test negative file size."""
        with pytest.raises(ValidationError, match="cannot be negative"):
            validate_file_size(-1)
    
    def test_zero_size(self):
        """Test zero file size."""
        with pytest.raises(ValidationError, match="cannot be empty"):
            validate_file_size(0)
    
    def test_too_large_size(self):
        """Test file size too large."""
        size = 100 * 1024 * 1024  # 100MB (larger than default 50MB limit)
        with pytest.raises(ValidationError, match="File too large"):
            validate_file_size(size)


class TestValidateUserInput:
    """Test user input validation function."""
    
    def test_valid_input(self):
        """Test valid user input."""
        text = "Hello world"
        result = validate_user_input(text)
        assert result == text
    
    def test_empty_input(self):
        """Test empty user input."""
        with pytest.raises(ValidationError, match="Input cannot be empty"):
            validate_user_input("")
    
    def test_input_with_html(self):
        """Test input with HTML tags."""
        text = "Hello <script>alert('test')</script> world"
        result = validate_user_input(text)
        assert "<script>" not in result
        assert "Hello  world" in result
    
    def test_input_too_long(self):
        """Test input that's too long."""
        text = "a" * 1000  # Longer than default limit
        with pytest.raises(ValidationError, match="Input too long"):
            validate_user_input(text, max_length=100)


class TestValidateCredentials:
    """Test credentials validation function."""
    
    def test_valid_credentials(self):
        """Test valid SharePoint credentials."""
        client_id = "12345678-1234-1234-1234-123456789012"
        client_secret = "very_long_secret_key_here"
        result_id, result_secret = validate_credentials(client_id, client_secret)
        assert result_id == client_id
        assert result_secret == client_secret
    
    def test_empty_client_id(self):
        """Test empty client ID."""
        with pytest.raises(ValidationError, match="Client ID cannot be empty"):
            validate_credentials("", "secret")
    
    def test_empty_client_secret(self):
        """Test empty client secret."""
        with pytest.raises(ValidationError, match="Client secret cannot be empty"):
            validate_credentials("12345678-1234-1234-1234-123456789012", "")
    
    def test_short_client_secret(self):
        """Test client secret that's too short."""
        with pytest.raises(ValidationError, match="Client secret appears too short"):
            validate_credentials("12345678-1234-1234-1234-123456789012", "short")


class TestSanitizeHtml:
    """Test HTML sanitization function."""
    
    def test_remove_html_tags(self):
        """Test removal of HTML tags."""
        html = "<p>Hello <b>world</b></p>"
        result = sanitize_html(html)
        assert result == "Hello world"
    
    def test_decode_html_entities(self):
        """Test decoding of HTML entities."""
        html = "Hello &amp; goodbye &lt;test&gt;"
        result = sanitize_html(html)
        assert result == "Hello & goodbye <test>"
    
    def test_empty_html(self):
        """Test empty HTML input."""
        result = sanitize_html("")
        assert result == ""
    
    def test_none_input(self):
        """Test None input."""
        result = sanitize_html(None)
        assert result == ""


if __name__ == "__main__":
    pytest.main([__file__])
