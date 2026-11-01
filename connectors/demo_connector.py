from pathlib import Path
import pandas as pd
from core.base_connector import BaseConnector, ConnectorMetadata

class DemoCSVConnector(BaseConnector):
    metadata = ConnectorMetadata(
        connector_id="csv_import",
        name="CSV / Excel Import Connector",
        version="1.0.0",
        category="file",
        description="Imports user-provided CSV/XLSX records with a normalized schema.",
        capabilities=["roster_import", "result_import", "batch_analytics"],
        access_mode="user_supplied_file"
    )

    def validate_input(self, payload):
        path = payload.get("path")
        if not path or not Path(path).exists():
            return False, "A valid local file path is required."
        if Path(path).suffix.lower() not in {".csv", ".xlsx"}:
            return False, "Only CSV and XLSX files are supported."
        return True, "Input accepted."

    def fetch_records(self, payload):
        ok, message = self.validate_input(payload)
        if not ok:
            raise ValueError(message)
        path = Path(payload["path"])
        frame = pd.read_csv(path) if path.suffix.lower() == ".csv" else pd.read_excel(path)
        return frame.to_dict(orient="records")

    def health_check(self):
        return {"status": "ready", "message": "Local file connector is ready."}
