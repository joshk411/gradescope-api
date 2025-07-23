from pyscope import GSConnection
from account import GSAccount
from course import GSCourse
from assignment import GSAssignment

import csv

CID_GLOBAL = "1040746"  # Course ID - copy into pyscope.py
AID_GLOBAL = "6405282"  # Assignment ID - copy into course.py

# Gradescope Credentials of Instructor
EMAIL = ""
PASSWORD = ""

# Path to CSV file from "Export Grades"
PATH = ""

if __name__=="__main__":
    # Initial Gradescope API setup
    conn = GSConnection()
    assert(conn.login(EMAIL, PASSWORD))
    print(conn.state)
    assert(conn.get_account())
    course = conn.account.instructor_courses[CID_GLOBAL]
    course._lazy_load_assignments()
    asst = course.assignments[AID_GLOBAL]

    # Parse CSV from "Export Grades" for submission ID and student email
    student_data = []
    with open(PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)          # uses the header row as keys
        for row in reader:
            student_data.append((row["Email"], row["Submission ID"]))
    
    # Iterate through submissions and check for explosion count consistency
    flagged_data = []
    for email, sid in student_data:
        flag = asst.view_prev_submissions(sid)
        if (flag):
            flagged_data.append(email)
    
    # Print flagged submissions (emails) to a file
    with open("flagged_submissions.txt", "w") as f:
        f.write("\n".join(flagged_data) + "\n")