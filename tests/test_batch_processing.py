import pandas as pd
import pytest

from batch_processing import normalize_roster, normalize_roll, _find_roll


def test_normalize_roster_accepts_roll_number_alias():
    roster = normalize_roster(pd.DataFrame({
        "Roll Number": ["23CS001", "23CS002"],
        "Student Name": ["A", "B"],
        "Department": ["CSE AI", "CSE AI"],
    }))
    assert roster["student_id"].tolist() == ["23CS001", "23CS002"]
    assert roster["_roll_key"].tolist() == ["23CS001", "23CS002"]


def test_normalize_roster_rejects_duplicate_rolls():
    with pytest.raises(ValueError, match="Duplicate roll numbers"):
        normalize_roster(pd.DataFrame({"roll_no": ["23-CS-01", "23CS01"]}))


def test_roll_matching_requires_unique_roster_match():
    roster = normalize_roster(pd.DataFrame({"student_id": ["23CS001", "23CS002"]}))
    assert _find_roll("Candidate Roll No: 23-CS-002", roster) == ("23CS002", "MATCHED")
    assert _find_roll("No roll number present", roster) == ("", "ROLL_NOT_FOUND")


def test_normalize_roll_removes_separators():
    assert normalize_roll("23-CS/001") == "23CS001"
