# Changelog

## Institution Batch Studio upgrade

- Added institution/batch metadata inputs and roster CSV/XLSX validation.
- Added multiple PDF and ZIP batch intake with size/count limits.
- Added roll-number normalization, exact roster matching, duplicate detection and unmatched-document reporting.
- Added PDF text extraction, SGPA/CGPA candidate fields and explicit unverified/layout-review states.
- Added batch workbook export with roster, manifest, coverage and extracted-text review sheets.
- Registered the AKTU One View PDF importer as a human-assisted document connector.
- Added tests, GitHub Actions quality checks, deployment/scope documentation and `.gitignore` safeguards.

## Known limitations

- No automated portal login, CAPTCHA bypass, anti-bot evasion or unauthorized bulk retrieval.
- Subject-wise marks parsing requires validation against the actual institution/university PDF layout.
- Scanned PDF OCR is not included.
- No production multi-tenant authentication, database, encrypted document storage, background queue or audit-log service yet.
