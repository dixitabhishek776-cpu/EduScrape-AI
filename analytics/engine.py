import pandas as pd
import numpy as np

class AcademicAnalytics:
    def __init__(self, frame: pd.DataFrame):
        self.df = frame.copy()
        for col in ["marks_obtained", "max_marks", "sgpa", "cgpa", "semester", "admission_year"]:
            if col in self.df:
                self.df[col] = pd.to_numeric(self.df[col], errors="coerce")
        self.df["percentage"] = np.where(
            self.df["max_marks"].fillna(0) > 0,
            self.df["marks_obtained"] / self.df["max_marks"] * 100,
            np.nan
        )

    def summary(self):
        d = self.df
        statuses = d["result_status"].astype(str).str.upper()
        valid_status = statuses.isin(["PASS", "FAIL"])
        return {
            "students": int(d["student_id"].nunique()),
            "records": int(len(d)),
            "avg_marks": float(d["percentage"].mean()) if d["percentage"].notna().any() else 0.0,
            "median_marks": float(d["percentage"].median()) if d["percentage"].notna().any() else 0.0,
            "pass_rate": float((statuses[valid_status] == "PASS").mean() * 100) if valid_status.any() else 0.0,
            "avg_cgpa": float(d["cgpa"].mean()) if d["cgpa"].notna().any() else np.nan,
            "backlog_records": int((statuses == "FAIL").sum())
        }

    def student_rankings(self):
        if self.df.empty:
            return pd.DataFrame()
        grouped = self.df.groupby(["student_id", "name", "institution", "branch"], dropna=False).agg(
            average_marks=("percentage", "mean"),
            max_cgpa=("cgpa", "max"),
            records=("subject", "count"),
            failed_subject_records=("result_status", lambda x: x.astype(str).str.upper().eq("FAIL").sum())
        ).reset_index()
        grouped = grouped.sort_values(["average_marks", "max_cgpa"], ascending=False, na_position="last")
        grouped.insert(0, "rank", range(1, len(grouped) + 1))
        return grouped

    def semester_summary(self):
        if "examination_period" not in self.df or self.df.empty:
            return pd.DataFrame()
        return self.df.groupby("examination_period", dropna=False).agg(
            avg_marks=("percentage", "mean"),
            median_marks=("percentage", "median"),
            records=("student_id", "size"),
            students=("student_id", "nunique")
        ).reset_index().round(2)

    def branch_summary(self):
        if "branch" not in self.df or self.df.empty:
            return pd.DataFrame()
        return self.df.groupby("branch", dropna=False).agg(
            avg_marks=("percentage", "mean"),
            students=("student_id", "nunique"),
            records=("student_id", "size")
        ).reset_index().round(2)

    def subject_summary(self):
        if "subject" not in self.df or self.df.empty:
            return pd.DataFrame()
        d = self.df.copy()
        d["is_pass"] = d["result_status"].astype(str).str.upper().eq("PASS")
        return d.groupby("subject", dropna=False).agg(
            avg_marks=("percentage", "mean"),
            median_marks=("percentage", "median"),
            pass_rate=("is_pass", "mean"),
            students=("student_id", "nunique"),
            records=("student_id", "size")
        ).assign(pass_rate=lambda x: x.pass_rate * 100).reset_index().round(2)

    def data_quality(self):
        d = self.df
        checks = [
            ("Missing student IDs", int(d.student_id.isna().sum())),
            ("Missing names", int(d.name.isna().sum())),
            ("Missing subject names", int(d.subject.isna().sum())),
            ("Missing marks", int(d.marks_obtained.isna().sum())),
            ("Duplicate student-subject-period rows", int(d.duplicated(["student_id","subject","examination_period"]).sum())),
            ("Marks greater than maximum", int((d.marks_obtained > d.max_marks).sum())),
            ("Negative marks", int((d.marks_obtained < 0).sum()))
        ]
        return pd.DataFrame(checks, columns=["check", "count"])

    def insights(self):
        s = self.summary()
        rank = self.student_rankings()
        sub = self.subject_summary()
        out = [
            f"Dataset contains {s['students']} distinct students and {s['records']} subject-result records.",
            f"Mean normalized marks are {s['avg_marks']:.1f}% and median marks are {s['median_marks']:.1f}%.",
            f"Observed pass rate is {s['pass_rate']:.1f}% across records with PASS/FAIL status.",
            f"There are {s['backlog_records']} records marked FAIL; verify each source's result semantics before treating these as confirmed backlogs."
        ]
        if not rank.empty:
            top = rank.iloc[0]
            out.append(f"Highest average-mark record group: {top['name']} ({top['student_id']}) at {top['average_marks']:.1f}% across {int(top['records'])} records.")
        if not sub.empty:
            weakest = sub.sort_values("avg_marks").iloc[0]
            out.append(f"Lowest subject average in this dataset: {weakest['subject']} ({weakest['avg_marks']:.1f}%).")
        q = self.data_quality()
        issues = int(q["count"].sum())
        out.append(f"Data-quality checks found {issues} issue instances. Review the Data Quality sheet before relying on rankings.")
        return out
