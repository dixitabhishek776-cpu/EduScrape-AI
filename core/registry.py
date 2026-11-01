from core.base_connector import BaseConnector

class ConnectorRegistry:
    def __init__(self):
        self._connectors: dict[str, BaseConnector] = {}

    def register(self, connector: BaseConnector):
        key = connector.metadata.connector_id
        if key in self._connectors:
            raise ValueError(f"Connector already registered: {key}")
        self._connectors[key] = connector

    def get(self, connector_id: str) -> BaseConnector:
        if connector_id not in self._connectors:
            raise KeyError(f"Unknown connector: {connector_id}")
        return self._connectors[connector_id]

    def list_connectors(self):
        result = []
        for c in self._connectors.values():
            h = c.health_check()
            result.append({
                "connector_id": c.metadata.connector_id,
                "name": c.metadata.name,
                "version": c.metadata.version,
                "description": c.metadata.description,
                "status": h.get("status", "unknown")
            })
        return result
