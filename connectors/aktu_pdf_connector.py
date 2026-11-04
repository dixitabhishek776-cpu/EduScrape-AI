from io import BytesIO
from typing import Any

from pypdf import PdfReader

from core.base_connector import BaseConnector, ConnectorMetadata


class AKTUPDFConnector(BaseConnector):
    """Human-assisted AKTU One View PDF text importer; never logs into the portal."""
    metadata = ConnectorMetadata(
        connector_id="aktu_pdf",
        name="AKTU One View PDF Importer",
        version="1.1.0",
        category="academic_results",
        description="Extracts selectable text from institution/user-provided AKTU result PDFs.",
        capabilities=["pdf_text_extraction", "page_count", "raw_text_review"],
        access_mode="authorized_import",
    )

    def validate_input(self, payload: dict[str, Any]) -> tuple[bool, str]:
        data = payload.get("pdf_bytes")
        if not isinstance(data, bytes) or not data.startswith(b"%PDF"):
            return False, "Upload a valid PDF document."
        if len(data) > 20 * 1024 * 1024:
            return False, "PDF exceeds the 20 MB limit."
        return True, "Valid PDF input."

    def fetch_records(self, payload: dict[str, Any]) -> list[dict[str, Any]]:
        valid, message = self.validate_input(payload)
        if not valid:
            raise ValueError(message)
        reader = PdfReader(BytesIO(payload["pdf_bytes"]), strict=False)
        if reader.is_encrypted:
            raise ValueError("Please provide an unlocked PDF you are authorized to process.")
        text = "\n".join(page.extract_text() or "" for page in reader.pages).strip()
        status = "TEXT_EXTRACTED" if text else "NO_SELECTABLE_TEXT_OCR_REQUIRED"
        return [{
            "raw_text": text,
            "page_count": len(reader.pages),
            "source_name": "AKTU One View PDF",
            "extraction_status": status,
            "verification_status": "UNVERIFIED",
        }]

    def health_check(self) -> dict[str, Any]:
        return {"status": "ready", "access_mode": "authorized_import"}
