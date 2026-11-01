import io
import pandas as pd
from analytics.engine import AcademicAnalytics

def build_workbook(frame: pd.DataFrame) -> bytes:
    analytics = AcademicAnalytics(frame)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        frame.to_excel(writer, sheet_name="Student Database", index=False)
        analytics.student_rankings().to_excel(writer, sheet_name="Student Rankings", index=False)
        analytics.semester_summary().to_excel(writer, sheet_name="Semester Analysis", index=False)
        analytics.subject_summary().to_excel(writer, sheet_name="Subject Analytics", index=False)
        analytics.branch_summary().to_excel(writer, sheet_name="Branch Comparison", index=False)
        analytics.data_quality().to_excel(writer, sheet_name="Data Quality", index=False)
        pd.DataFrame({"Insight": analytics.insights()}).to_excel(writer, sheet_name="AI Insights", index=False)
        for ws in writer.book.worksheets:
            ws.freeze_panes = "A2"
            ws.auto_filter.ref = ws.dimensions
            for col in ws.columns:
                max_len = max((len(str(cell.value)) if cell.value is not None else 0) for cell in col)
                ws.column_dimensions[col[0].column_letter].width = min(max(max_len + 2, 12), 42)
    output.seek(0)
    return output.getvalue()
