# EduScrape AI

**Institution-level academic result intake, validation and analytics**

EduScrape AI helps an institution organize a batch roster, process result documents supplied by an authorized operator, match documents to student roll numbers, review extraction status, analyze academic performance, and export consolidated Excel reports.

## What is included

- Institution Batch Studio for branch/batch/examination metadata.
- CSV/XLSX roster intake with roll-number normalization and duplicate rejection.
- Multi-PDF and ZIP batch intake (up to 500 PDFs; per-PDF size limit 20 MB).
- PDF text extraction with page counts and clear handling of encrypted/scanned/unreadable files.
- Exact normalized roll-number matching against the uploaded roster.
- Duplicate-document, unmatched-document and missing-document visibility.
- Candidate SGPA/CGPA label extraction, clearly marked as **unverified**.
- Batch workbook with Roster, Document Manifest, Batch Coverage and Extracted Text Review sheets.
- Existing academic dashboard, student explorer, branch/semester/subject analytics, descriptive insights and exports.
- Connector contract with Demo CSV and human-assisted AKTU One View PDF importers.

## Important scope and honest limitations

This release does **not** log into AKTU or another examination portal, automatically retrieve a whole branch's private results, bypass CAPTCHA, evade anti-bot controls, or defeat authentication/access restrictions. Portal retrieval requires a supported/authorized interface or an operator to obtain the documents through the normal portal workflow.

The batch engine currently extracts selectable PDF text and matches roll numbers. SGPA/CGPA values are only candidates; they are not verified official values. Subject-wise marks parsing is deliberately marked `LAYOUT_REVIEW_REQUIRED` until a real, representative marksheet layout has been validated. Scanned/image-only PDFs need OCR; OCR is not included in this release. Do not present unverified values as official results.

Process only records the institution is authorized to handle. Use institution-approved consent, retention, access control and security policies. The current Streamlit MVP is not yet a production multi-tenant SaaS: it has no institution login/RBAC, persistent database, encrypted document vault, audit-log service, background worker or subscription/licensing layer.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Termux / Android:

```bash
python -m pip install -r requirements.txt
streamlit run app.py --server.address 0.0.0.0
```

## Roster format

Minimum required column: `roll_number` or `roll_no` or `student_id`.

Recommended columns:

`roll_number, student_name, branch, course, admission_year`

Example:

```csv
roll_number,student_name,branch,course,admission_year
23001,Student One,CSE AI,B.Tech,2023
23002,Student Two,CSE AI,B.Tech,2023
```

## Batch workflow

1. Open **Institution Batch Studio**.
2. Enter institution, admission batch, branch and examination/semester.
3. Upload the authorized roster CSV/XLSX.
4. Upload multiple PDFs or ZIP archives containing PDFs obtained through permitted means.
5. Process the batch and review matched, unmatched, duplicate and unreadable documents.
6. Inspect extracted text and download the institution batch workbook.
7. Validate the exact examination PDF layout before importing official subject marks or publishing rankings.

## Supported common academic dataset

One row represents one student's result in one subject in one examination period.

Required normalized fields:

`student_id, name, institution, course, branch, admission_year, examination_period, subject, marks_obtained, max_marks, result_status`

Optional:

`semester, grade, sgpa, cgpa, source_name, retrieved_at, verification_status`

## Deployment on Streamlit Community Cloud

1. Push the project to a GitHub repository.
2. Create/update the Streamlit app against that repository and set `app.py` as the main file.
3. Streamlit installs dependencies from `requirements.txt` on deployment.
4. Verify the deployed app with synthetic data and institution-approved test PDFs before processing real records.

Never commit student result PDFs, roster data, credentials, API tokens or generated workbooks to GitHub.

## Quality checks

```bash
python -m pytest -q
python -m py_compile app.py batch_processing.py connectors/aktu_pdf_connector.py
```
