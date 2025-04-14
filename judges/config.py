"""Configuration module for the judges package."""
import os
from dataclasses import dataclass

@dataclass
class ClientConfig:
    client: str = "litellm"
    api_key: str | None = os.getenv("OPENAI_API_KEY")
    base_url: str | None = None

# Single instance of the config
_config = ClientConfig()

def configure_client(client: str = "litellm", api_key: str | None = None, base_url: str | None = None) -> ClientConfig:
    """Configure the judges package with API credentials and settings.
    
    Args:
        client: The client to use (litellm or openai)
        api_key: OpenAI API key (falls back to OPENAI_API_KEY environment variable)
        base_url: Base URL for API requests (useful for Azure OpenAI or other endpoints)
    
    Returns:
        The current configuration
    """
    if client is not None:
        _config.client = client
    if api_key is not None:
        _config.api_key = api_key
    if base_url is not None:
        _config.base_url = base_url

    return _config

def get_config() -> ClientConfig:
    """Get the current configuration."""
    return _config 