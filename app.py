from __future__ import annotations

import io
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from core.registry import ConnectorRegistry
from connectors.demo_connector import DemoCSVConnector
from analytics.engine import AcademicAnalytics
from exports.workbook import build_workbook
from core.schemas import REQUIRED_COLUMNS, OPTIONAL_COLUMNS

st.set_page_config(page_title="EduScrape AI", page_icon="🎓", layout="wide")

st.markdown("""
<style>
:root { --primary-color: #7c3aed; }
.block-container {padding-top: 1.4rem; padding-bottom: 2rem;}
.hero {padding: 1.35rem 1.5rem; border-radius: 18px;
background: linear-gradient(120deg, #211044 0%, #4c1d95 58%, #7c3aed 100%);
color: white; margin-bottom: 1rem;}
.hero h1 {font-size: 2.25rem; margin: 0;}
.hero p {opacity: .9; margin: .4rem 0 0 0;}
.metric-note {font-size: .82rem; color: #777;}
div[data-testid="stMetric"] {border: 1px solid rgba(128,93,224,.22); padding: 12px; border-radius: 12px;}
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def registry():
    r = ConnectorRegistry()
    r.register(DemoCSVConnector())
    return r

def make_demo_data():
    import numpy as np
    rng = np.random.default_rng(42)
    rows = []
    branches = ["CSE", "IT", "ECE", "AI & ML"]
    subjects = ["Mathematics", "Programming", "Physics", "Data Structures", "Communication"]
    for i in range(1, 121):
        roll = f"24006501{i:04d}"
        branch = branches[(i - 1) % len(branches)]
        base = float(rng.normal(72, 11))
        for sem in range(1, 5):
            sgpa = max(4.0, min(10.0, round((base + rng.normal(sem * 1.2, 5)) / 10, 2)))
            for sub in subjects:
                marks = int(max(0, min(100, rng.normal(base + sem, 12))))
                rows.append({
                    "student_id": roll, "name": f"Student {i:03d}",
                    "institution": "Demo Institute of Technology", "course": "B.Tech",
                    "branch": branch, "admission_year": 2024,
                    "examination_period": f"Semester {sem}", "semester": sem,
                    "subject": sub, "marks_obtained": marks, "max_marks": 100,
                    "grade": "", "sgpa": sgpa, "cgpa": round(max(4.0, min(10.0, sgpa + rng.normal(0, .25))), 2),
                    "result_status": "PASS" if marks >= 40 else "FAIL",
                    "source_name": "Built-in demonstration dataset",
                    "retrieved_at": datetime.now(timezone.utc).isoformat(),
                    "verification_status": "DEMO"
                })
    return pd.DataFrame(rows)

def normalize_upload(df: pd.DataFrame):
    df = df.copy()
    aliases = {
        "roll_number":"student_id", "roll no":"student_id", "roll_no":"student_id",
        "student_name":"name", "student":"name", "college":"institution",
        "department":"branch", "year":"admission_year", "semester_name":"examination_period",
        "marks":"marks_obtained", "total_marks":"max_marks", "status":"result_status",
        "subject_name":"subject"
    }
    df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]
    df = df.rename(columns=aliases)
    for col in REQUIRED_COLUMNS:
        if col not in df.columns:
            df[col] = None
    for col in OPTIONAL_COLUMNS:
        if col not in df.columns:
            df[col] = None
    return df

st.markdown("""
<div class="hero">
  <h1>🎓 EduScrape AI</h1>
  <p>Universal Academic Data Intelligence · Plugin-based connectors · Explainable analytics · Excel reporting</p>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ Workspace")
    page = st.radio("Navigate", ["Overview", "Student Explorer", "Batch Analytics", "Subject Intelligence", "AI Insights", "Data & Connectors", "Export Center"])
    st.divider()
    st.caption("Prototype mode · Privacy-first")
    st.info("Use only records you are authorized to process. This prototype does not bypass CAPTCHA, logins, rate limits or access controls.")

if "records" not in st.session_state:
    st.session_state.records = make_demo_data()
if "dataset_label" not in st.session_state:
    st.session_state.dataset_label = "Built-in demonstration dataset"

df = st.session_state.records.copy()
analytics = AcademicAnalytics(df)
summary = analytics.summary()

if page == "Overview":
    st.subheader("Academic intelligence at a glance")
    st.caption(f"Active dataset: **{st.session_state.dataset_label}** · {len(df):,} subject-result rows")
    c1,c2,c3,c4,c5 = st.columns(5)
    c1.metric("Students", f"{summary['students']:,}")
    c2.metric("Subjects / records", f"{summary['records']:,}")
    c3.metric("Average marks", f"{summary['avg_marks']:.1f}%")
    c4.metric("Pass rate", f"{summary['pass_rate']:.1f}%")
    c5.metric("Average CGPA", f"{summary['avg_cgpa']:.2f}" if pd.notna(summary["avg_cgpa"]) else "—")
    left,right = st.columns(2)
    with left:
        sem = analytics.semester_summary()
        if not sem.empty:
            st.plotly_chart(px.line(sem, x="examination_period", y="avg_marks", markers=True, title="Average marks by examination period"), use_container_width=True)
    with right:
        branch = analytics.branch_summary()
        if not branch.empty:
            st.plotly_chart(px.bar(branch, x="branch", y="avg_marks", color="branch", title="Branch-wise average marks"), use_container_width=True)
    st.subheader("Recent records")
    st.dataframe(df.head(12), use_container_width=True, hide_index=True)

elif page == "Student Explorer":
    st.subheader("🔎 Student Explorer")
    ids = sorted(df["student_id"].dropna().astype(str).unique().tolist())
    selected = st.selectbox("Select student roll number / student ID", ids)
    student = df[df.student_id.astype(str) == str(selected)]
    if not student.empty:
        first = student.iloc[0]
        a,b,c,d = st.columns(4)
        a.metric("Student", str(first.get("name") or "Not provided"))
        b.metric("Branch", str(first.get("branch") or "—"))
        c.metric("CGPA", f"{pd.to_numeric(student.cgpa, errors='coerce').dropna().max():.2f}" if pd.to_numeric(student.cgpa, errors='coerce').notna().any() else "—")
        d.metric("Subject records", len(student))
        st.write(f"**Institution:** {first.get('institution') or '—'}  ·  **Course:** {first.get('course') or '—'}  ·  **Admission year:** {first.get('admission_year') or '—'}")
        subj = student.copy()
        subj["marks_obtained"] = pd.to_numeric(subj.marks_obtained, errors="coerce")
        st.plotly_chart(px.bar(subj, x="subject", y="marks_obtained", color="examination_period", barmode="group", title="Subject-wise marks"), use_container_width=True)
        st.dataframe(student, use_container_width=True, hide_index=True)
    else:
        st.warning("No records found for this student.")

elif page == "Batch Analytics":
    st.subheader("📊 Batch & cohort analytics")
    branches = ["All"] + sorted(df.branch.dropna().astype(str).unique().tolist())
    chosen = st.selectbox("Branch filter", branches)
    filtered = df if chosen == "All" else df[df.branch.astype(str) == chosen]
    cohort = AcademicAnalytics(filtered)
    s = cohort.summary()
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Students", s["students"])
    c2.metric("Average marks", f"{s['avg_marks']:.2f}%")
    c3.metric("Pass rate", f"{s['pass_rate']:.2f}%")
    c4.metric("Median marks", f"{s['median_marks']:.2f}%")
    rank = cohort.student_rankings()
    st.subheader("Student leaderboard")
    st.dataframe(rank.head(25), use_container_width=True, hide_index=True)
    l,r = st.columns(2)
    with l:
        st.plotly_chart(px.histogram(rank, x="average_marks", nbins=20, title="Student average-mark distribution"), use_container_width=True)
    with r:
        st.plotly_chart(px.box(filtered, x="branch", y="marks_obtained", title="Marks spread by branch"), use_container_width=True)
    st.subheader("Semester progression")
    st.dataframe(cohort.semester_summary(), use_container_width=True, hide_index=True)

elif page == "Subject Intelligence":
    st.subheader("📚 Subject Intelligence")
    sub = analytics.subject_summary()
    if not sub.empty:
        st.plotly_chart(px.bar(sub, x="subject", y="avg_marks", color="pass_rate", title="Subject average and pass rate"), use_container_width=True)
        st.dataframe(sub, use_container_width=True, hide_index=True)
        weakest = sub.sort_values("avg_marks").head(3)
        strongest = sub.sort_values("avg_marks", ascending=False).head(3)
        x,y = st.columns(2)
        with x:
            st.markdown("**Subjects needing attention**")
            st.dataframe(weakest, use_container_width=True, hide_index=True)
        with y:
            st.markdown("**Strongest subjects**")
            st.dataframe(strongest, use_container_width=True, hide_index=True)
    else:
        st.info("Subject field is not available in this dataset.")

elif page == "AI Insights":
    st.subheader("🧠 Explainable Academic Insights")
    insights = analytics.insights()
    for item in insights:
        st.markdown(f"- {item}")
    st.caption("These are descriptive indicators derived from the uploaded dataset, not predictions of official outcomes or judgments about individual ability.")
    rank = analytics.student_rankings()
    if not rank.empty:
        st.plotly_chart(px.scatter(rank, x="average_marks", y="records", hover_name="student_id", color="branch", title="Student record coverage vs average marks"), use_container_width=True)

elif page == "Data & Connectors":
    st.subheader("🔌 Data ingestion & connector registry")
    st.write("Load a CSV/XLSX roster or result export that you are authorized to process. The same normalized schema feeds every analytics module.")
    uploaded = st.file_uploader("Upload CSV or Excel", type=["csv", "xlsx"])
    if uploaded:
        try:
            raw = pd.read_csv(uploaded) if uploaded.name.lower().endswith(".csv") else pd.read_excel(uploaded)
            normalized = normalize_upload(raw)
            st.write("Preview after schema normalization")
            st.dataframe(normalized.head(20), use_container_width=True, hide_index=True)
            if st.button("Use this dataset", type="primary"):
                st.session_state.records = normalized
                st.session_state.dataset_label = uploaded.name
                st.success(f"Loaded {len(normalized):,} records.")
                st.rerun()
        except Exception as e:
            st.error(f"Could not read file: {e}")
    st.divider()
    st.markdown("#### Installed connectors")
    for item in registry().list_connectors():
        st.markdown(f"**{item['name']}** · `{item['connector_id']}` · v{item['version']} · {item['status']}")
        st.caption(item["description"])
    st.info("Connector SDK is included. Live website integrations must be implemented and reviewed individually using official APIs, published downloads, or authorized human-assisted workflows. No CAPTCHA or access-control bypass is included.")

elif page == "Export Center":
    st.subheader("📦 Export Center")
    st.write("Generate a multi-sheet workbook containing normalized records, student rankings, semester trends, subject analytics and data-quality checks.")
    if st.button("Build Excel workbook", type="primary"):
        workbook = build_workbook(df)
        st.download_button("⬇️ Download EduScrape academic report (.xlsx)", data=workbook,
                           file_name="eduscrape_academic_report.xlsx",
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("Download normalized CSV", csv, "eduscrape_normalized_records.csv", "text/csv")

st.divider()
st.caption("EduScrape AI · Interview-ready demonstrator · Always verify source rules, grading schemes and student consent before processing real records.")
