import pandas as pd
from analytics.engine import AcademicAnalytics

def test_summary_and_rankings():
    df = pd.DataFrame([
        {"student_id":"A","name":"Alpha","institution":"X","branch":"CSE","subject":"Math",
         "marks_obtained":80,"max_marks":100,"result_status":"PASS","examination_period":"Sem 1","cgpa":8.2},
        {"student_id":"B","name":"Beta","institution":"X","branch":"IT","subject":"Math",
         "marks_obtained":40,"max_marks":100,"result_status":"FAIL","examination_period":"Sem 1","cgpa":5.1}
    ])
    a = AcademicAnalytics(df)
    s = a.summary()
    assert s["students"] == 2
    assert s["pass_rate"] == 50
    assert len(a.student_rankings()) == 2
