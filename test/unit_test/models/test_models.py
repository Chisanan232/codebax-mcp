"""Test CLI models and data transfer objects."""

import pytest
from pydantic import ValidationError

from codebax_mcp.models.cli import LogLevel, MCPTransportType, ServerConfig


class TestServerConfig:
    """Test cases for the ServerConfig model."""

    def test_default_values(self) -> None:
        """Test default configuration values."""
        config = ServerConfig()

        assert config.host == "127.0.0.1"
        assert config.port == 8000
        assert config.log_level == LogLevel.INFO
        assert config.reload is False
        assert config.env_file == ".env"
        assert config.token is None
        assert config.transport == MCPTransportType.SSE

    def test_custom_values(self) -> None:
        """Test configuration with custom values."""
        config = ServerConfig(
            host="127.0.0.1",
            port=9000,
            log_level=LogLevel.DEBUG,
            reload=True,
            env_file="/custom/.env",
            token="test_token",
            transport=MCPTransportType.HTTP_STREAMING,
        )

        assert config.host == "127.0.0.1"
        assert config.port == 9000
        assert config.log_level == LogLevel.DEBUG
        assert config.reload is True
        assert config.env_file == "/custom/.env"
        assert config.token == "test_token"
        assert config.transport == MCPTransportType.HTTP_STREAMING

    def test_port_validation(self) -> None:
        """Test port number validation."""
        # Valid ports
        config = ServerConfig(port=1)
        assert config.port == 1

        config = ServerConfig(port=65535)
        assert config.port == 65535

        # Invalid ports
        with pytest.raises(ValidationError):
            ServerConfig(port=0)

        with pytest.raises(ValidationError):
            ServerConfig(port=65536)

    def test_string_values(self) -> None:
        """Test configuration with string enum values."""
        config = ServerConfig(log_level="debug", transport="http-streaming")

        assert config.log_level == LogLevel.DEBUG
        assert config.transport == MCPTransportType.HTTP_STREAMING

    def test_extra_fields_forbidden(self) -> None:
        """Test that extra fields are forbidden."""
        with pytest.raises(ValidationError):
            ServerConfig(invalid_field="value")

    def test_model_dump(self) -> None:
        """Test model serialization."""
        config = ServerConfig(
            host="127.0.0.1", port=9000, log_level=LogLevel.DEBUG, transport=MCPTransportType.HTTP_STREAMING
        )

        data = config.model_dump()

        assert data["host"] == "127.0.0.1"
        assert data["port"] == 9000
        assert data["log_level"] == "debug"
        assert data["transport"] == "http-streaming"


class TestLogLevel:
    """Test cases for the LogLevel enum."""

    def test_log_level_values(self) -> None:
        """Test all log level values."""
        assert LogLevel.DEBUG.value == "debug"
        assert LogLevel.INFO.value == "info"
        assert LogLevel.WARNING.value == "warning"
        assert LogLevel.ERROR.value == "error"
        assert LogLevel.CRITICAL.value == "critical"

    def test_log_level_comparison(self) -> None:
        """Test log level comparisons."""
        assert LogLevel.DEBUG.value == "debug"
        assert LogLevel.INFO == LogLevel.INFO


class TestMCPTransportType:
    """Test cases for the MCPTransportType enum."""

    def test_transport_type_values(self) -> None:
        """Test all transport type values."""
        assert MCPTransportType.SSE.value == "sse"
        assert MCPTransportType.HTTP_STREAMING.value == "http-streaming"

    def test_transport_type_comparison(self) -> None:
        """Test transport type comparisons."""
        assert MCPTransportType.SSE.value == "sse"
        assert MCPTransportType.HTTP_STREAMING == MCPTransportType.HTTP_STREAMING


class TestModelIntegration:
    """Integration tests for models."""

    def test_server_config_with_enums(self) -> None:
        """Test ServerConfig with enum values."""
        config = ServerConfig(log_level=LogLevel.DEBUG, transport=MCPTransportType.HTTP_STREAMING)

        # Test that enums work correctly
        assert config.log_level == LogLevel.DEBUG
        assert config.transport == MCPTransportType.HTTP_STREAMING

        # Test string conversion
        assert str(config.log_level) == "debug"
        assert str(config.transport) == "http-streaming"
