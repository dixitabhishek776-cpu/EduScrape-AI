"""Template for a future institution connector.

Implement this contract only after confirming an official/published or otherwise
authorized data-access method. Do not automate around CAPTCHA, login restrictions,
rate limits, or anti-bot controls.
"""
from core.base_connector import BaseConnector, ConnectorMetadata

class InstitutionConnector(BaseConnector):
    metadata = ConnectorMetadata(
        connector_id="replace_me",
        name="Institution Connector Template",
        version="0.1.0",
        category="university",
        description="Replace with a source-specific description.",
        capabilities=["student_lookup"],
        access_mode="official_api_or_authorized_export"
    )

    def validate_input(self, payload):
        if not payload.get("student_id"):
            return False, "student_id is required"
        return True, "Valid"

    def fetch_records(self, payload):
        raise NotImplementedError(
            "Connect an approved official API or authorized export here."
        )

    def health_check(self):
        return {"status": "template", "message": "Not connected to a live source."}
