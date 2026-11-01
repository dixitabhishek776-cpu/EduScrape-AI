# EduScrape AI
**Universal Academic Data Intelligence — interview-ready MVP**

EduScrape AI is a modular academic analytics demonstrator. It includes:
- Plugin-based connector contract and registry
- CSV/XLSX import connector
- Common academic data model
- Student, batch, branch, semester and subject analytics
- Explainable descriptive insights and data-quality checks
- Multi-sheet Excel export
- Interactive Streamlit dashboard
- Synthetic demo data so the app launches immediately

## Important scope
This is a working MVP, not a production integration with every examination website. Each institution requires a separately tested connector and an approved access method (official API, published result file, institution-authorized export, or user-provided documents). It does not bypass CAPTCHA, authentication, rate limits, or other access controls. Process personal academic records only with appropriate authorization and consent.

## Run locally (Termux / Linux / macOS / Windows)
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```
In Termux, if activation is inconvenient:
```bash
python -m pip install -r requirements.txt
streamlit run app.py --server.address 0.0.0.0
```
Open the local URL printed by Streamlit. On Android, use the URL shown in the Termux terminal.

## Deploy on Streamlit Community Cloud
1. Push this folder to a GitHub repository.
2. Create a Streamlit app from that repository.
3. Set the main file path to `app.py`.
4. Streamlit installs dependencies from `requirements.txt`.

Do not commit student data, credentials, tokens, or private exports to GitHub.

## CSV/XLSX input schema
Required (columns can be omitted; missing columns are added as blank):
`student_id, name, institution, course, branch, admission_year, examination_period, subject, marks_obtained, max_marks, result_status`

Optional:
`semester, grade, sgpa, cgpa, source_name, retrieved_at, verification_status`

Aliases such as `roll_number`, `roll_no`, `student_name`, `college`, `department`, `marks`, `status`, and `subject_name` are normalized automatically.

One row should represent one student's result in one subject for one examination period. Use `PASS` / `FAIL` consistently if you want pass-rate calculations. Confirm grading and percentage conversion rules with the institution before reporting official percentages.

## Add a connector
1. Copy `connectors/connector_template.py`.
2. Implement `validate_input`, `fetch_records`, and `health_check`.
3. Return dictionaries with source-native values; normalize them into the common schema.
4. Register the connector in `app.py` or add a safe plugin discovery mechanism.
5. Add fixtures and tests; document permissions, supported fields, limitations and rate limits.

Never automate around CAPTCHA or access controls. For websites requiring verification, pause for an authorized human operator or use an approved integration.

## Project structure
- `core/`: connector contract and registry
- `connectors/`: source adapters
- `analytics/`: academic metrics and insights
- `exports/`: Excel workbook generator
- `tests/`: automated tests
