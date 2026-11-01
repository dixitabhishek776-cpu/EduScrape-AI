from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

@dataclass
class ConnectorMetadata:
    connector_id: str
    name: str
    version: str
    category: str
    description: str
    capabilities: list[str]
    access_mode: str = "authorized_import"

class BaseConnector(ABC):
    """Stable plugin contract. Connectors return raw records; core normalizes them."""
    metadata: ConnectorMetadata

    @abstractmethod
    def validate_input(self, payload: dict[str, Any]) -> tuple[bool, str]:
        raise NotImplementedError

    @abstractmethod
    def fetch_records(self, payload: dict[str, Any]) -> list[dict[str, Any]]:
        """Fetch only records available through a permitted access method."""
        raise NotImplementedError

    @abstractmethod
    def health_check(self) -> dict[str, Any]:
        raise NotImplementedError
