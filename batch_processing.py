"""Institution batch document intake with conservative, auditable PDF extraction.

This module does not log into external portals or bypass access controls. It processes
PDFs supplied by an institution/user and never guesses subject marks from unknown layouts.
"""
from __future__ import annotations

import io
import re
import zipfile
from dataclasses import dataclass
from typing import Iterable

import pandas as pd
from pypdf import PdfReader

MAX_PDF_BYTES = 20 * 1024 * 1024
MAX_ZIP_BYTES = 250 * 1024 * 1024
MAX_PDFS = 500

ALIASES = {
    "roll_number": "student_id", "roll_no": "student_id", "roll no": "student_id",
    "roll": "student_id", "student_id": "student_id", "student_name": "name",
    "student": "name", "branch_name": "branch", "department": "branch",
    "course_name": "course", "batch": "admission_year", "year": "admission_year",
}


def normalize_roll(value: object) -> str:
    return re.sub(r"[^A-Z0-9]", "", str(value or "").upper())


def normalize_roster(frame: pd.DataFrame) -> pd.DataFrame:
    df = frame.copy()
    df.columns = [str(c).strip().lower().replace("-", "_").replace(" ", "_") for c in df.columns]
    df = df.rename(columns=ALIASES)
    if "student_id" not in df.columns:
        raise ValueError("Roster must contain a roll_number / roll_no / student_id column.")
    for col in ("name", "branch", "course", "admission_year"):
        if col not in df.columns:
            df[col] = ""
    df["student_id"] = df["student_id"].astype(str).str.strip()
    df = df[df["student_id"].notna() & df["student_id"].ne("")].copy()
    df["_roll_key"] = df["student_id"].map(normalize_roll)
    df = df[df["_roll_key"].ne("")]
    if df["_roll_key"].duplicated().any():
        duplicates = df.loc[df["_roll_key"].duplicated(keep=False), "student_id"].astype(str).tolist()
        raise ValueError("Duplicate roll numbers in roster: " + ", ".join(duplicates[:10]))
    return df.reset_index(drop=True)


def read_roster(upload) -> pd.DataFrame:
    name = str(getattr(upload, "name", "")).lower()
    data = upload.getvalue()
    frame = pd.read_csv(io.BytesIO(data)) if name.endswith(".csv") else pd.read_excel(io.BytesIO(data))
    return normalize_roster(frame)


def collect_pdf_files(uploads: Iterable) -> list[tuple[str, bytes]]:
    """Accept multiple PDFs and ZIP archives; reject unsafe/oversized archive entries."""
    collected: list[tuple[str, bytes]] = []
    for upload in uploads:
        name = str(getattr(upload, "name", "upload.pdf"))
        data = upload.getvalue()
        if name.lower().endswith(".zip"):
            if len(data) > MAX_ZIP_BYTES:
                raise ValueError(f"{name}: ZIP exceeds {MAX_ZIP_BYTES // (1024*1024)} MB limit.")
            try:
                with zipfile.ZipFile(io.BytesIO(data)) as archive:
                    for info in archive.infolist():
                        if info.is_dir() or not info.filename.lower().endswith(".pdf"):
                            continue
                        # Ignore path traversal and nested path names; use basename only.
                        if ".." in info.filename.replace("\\", "/").split("/"):
                            continue
                        if info.file_size > MAX_PDF_BYTES:
                            collected.append((info.filename.split("/")[-1], b""))
                            continue
                        with archive.open(info) as stream:
                            pdf_data = stream.read(MAX_PDF_BYTES + 1)
                        collected.append((info.filename.split("/")[-1], pdf_data))
                        if len(collected) > MAX_PDFS:
                            raise ValueError(f"Batch exceeds {MAX_PDFS} PDF limit.")
            except zipfile.BadZipFile as exc:
                raise ValueError(f"{name} is not a valid ZIP archive.") from exc
        elif name.lower().endswith(".pdf"):
            collected.append((name, data))
        else:
            raise ValueError(f"Unsupported file: {name}. Upload PDF or ZIP.")
        if len(collected) > MAX_PDFS:
            raise ValueError(f"Batch exceeds {MAX_PDFS} PDF limit.")
    return collected


def _extract_text(data: bytes) -> tuple[str, int, str]:
    if not data or len(data) > MAX_PDF_BYTES:
        return "", 0, "INVALID_OR_OVERSIZED"
    if not data.startswith(b"%PDF"):
        return "", 0, "NOT_A_PDF"
    try:
        reader = PdfReader(io.BytesIO(data), strict=False)
        if reader.is_encrypted:
            return "", len(reader.pages), "ENCRYPTED_PDF"
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
        return text.strip(), len(reader.pages), "TEXT_EXTRACTED" if text.strip() else "NO_SELECTABLE_TEXT"
    except Exception:
        return "", 0, "PDF_READ_ERROR"


def _find_roll(text: str, roster: pd.DataFrame) -> tuple[str, str]:
    haystack = normalize_roll(text)
    hits = []
    for _, row in roster.iterrows():
        key = row["_roll_key"]
        if key and key in haystack:
            hits.append(str(row["student_id"]))
    if len(hits) == 1:
        return hits[0], "MATCHED"
    if len(hits) > 1:
        return "", "MULTIPLE_ROLL_MATCHES"
    return "", "ROLL_NOT_FOUND"


def _label_value(text: str, labels: tuple[str, ...]) -> str:
    for label in labels:
        match = re.search(rf"\b{label}\b\s*[:\-]?\s*([0-9]+(?:\.[0-9]+)?)", text, re.I)
        if match:
            return match.group(1)
    return ""


def process_pdf_batch(files: list[tuple[str, bytes]], roster: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, str]]:
    rows = []
    raw_texts: dict[str, str] = {}
    seen_rolls: set[str] = set()
    for filename, data in files:
        text, pages, extraction_status = _extract_text(data)
        matched_roll, match_status = _find_roll(text, roster) if text else ("", extraction_status)
        if matched_roll and matched_roll in seen_rolls:
            match_status = "DUPLICATE_RESULT_DOCUMENT"
        elif matched_roll:
            seen_rolls.add(matched_roll)
        raw_texts[filename] = text
        row = roster.loc[roster["student_id"].astype(str).eq(matched_roll)].head(1)
        student_name = str(row.iloc[0]["name"]) if not row.empty else ""
        rows.append({
            "file_name": filename,
            "student_id": matched_roll,
            "student_name": student_name,
            "page_count": pages,
            "extraction_status": extraction_status,
            "matching_status": match_status,
            "sgpa_candidate": _label_value(text, ("SGPA", "SPI")) if text else "",
            "cgpa_candidate": _label_value(text, ("CGPA", "CPI")) if text else "",
            "subject_marks_status": "LAYOUT_REVIEW_REQUIRED",
            "verification_status": "UNVERIFIED",
        })
    return pd.DataFrame(rows), raw_texts


def build_batch_workbook(roster: pd.DataFrame, manifest: pd.DataFrame, raw_texts: dict[str, str]) -> bytes:
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        roster.drop(columns=["_roll_key"], errors="ignore").to_excel(writer, sheet_name="Roster", index=False)
        manifest.to_excel(writer, sheet_name="Document Manifest", index=False)
        coverage = roster.drop(columns=["_roll_key"], errors="ignore").copy()
        matched = set(manifest.loc[manifest["matching_status"].eq("MATCHED"), "student_id"].astype(str))
        coverage["document_received"] = coverage["student_id"].astype(str).isin(matched)
        coverage.to_excel(writer, sheet_name="Batch Coverage", index=False)
        pd.DataFrame([{"file_name": k, "extracted_text": v} for k, v in raw_texts.items()]).to_excel(
            writer, sheet_name="Extracted Text Review", index=False
        )
        for ws in writer.book.worksheets:
            ws.freeze_panes = "A2"
            ws.auto_filter.ref = ws.dimensions
            for col in ws.columns:
                width = min(max(max(len(str(c.value or "")) for c in col) + 2, 12), 48)
                ws.column_dimensions[col[0].column_letter].width = width
    output.seek(0)
    return output.getvalue()
