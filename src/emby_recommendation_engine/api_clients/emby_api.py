import httpx
from loguru import logger
import attrs
from typing import Optional, Dict, Any


class EmbyAPIError(Exception):
    """Custom exception for Emby API errors"""


@attrs.define
class EmbyAPIClient:
    """A client for interacting with the Emby API."""

    base_url: str = attrs.field(converter=lambda x: x.rstrip("/"))
    api_key: str = attrs.field(repr=False)
    user_id: Optional[str] = attrs.field(default=None)

    async def get_user_library(self, limit: int = 100) -> Dict[str, Any]:
        """Get user's library items - the one endpoint we need for now"""
        if not self.user_id:
            raise EmbyAPIError("User ID is required")

        url = f"{self.base_url}/emby/Users/{self.user_id}/Items"
        params = {"Limit": limit}
        headers = {"X-Emby-Token": self.api_key}

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, params=params, headers=headers)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                logger.error(f"Emby API error: {e}")
                raise EmbyAPIError(f"Failed to fetch library: {e}")


def create_emby_client(base_url: str, api_key: str, user_id: str) -> EmbyAPIClient:
    """Create an Emby API client"""
    return EmbyAPIClient(base_url=base_url, api_key=api_key, user_id=user_id)
