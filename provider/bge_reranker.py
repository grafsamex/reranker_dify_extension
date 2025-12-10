import logging
from dify_plugin import ModelProvider

logger = logging.getLogger(__name__)


class BGERerankerProvider(ModelProvider):
    def validate_provider_credentials(self, credentials: dict) -> None:
        """
        Validate provider credentials
        if validate failed, raise exception

        :param credentials: provider credentials, credentials form defined in `provider_credential_schema`.
        """
        api_url = credentials.get("api_url", "")
        if not api_url or not isinstance(api_url, str):
            raise ValueError("api_url must be a non-empty string")
        
        # Try to check health endpoint
        try:
            import requests
            from urllib.parse import urljoin
            health_url = urljoin(api_url.rstrip('/') + '/', 'health')
            response = requests.get(health_url, timeout=5)
            if response.status_code != 200:
                raise ValueError(f"Health check failed: status {response.status_code}")
        except Exception as e:
            raise ValueError(f"Failed to validate API URL: {str(e)}")

