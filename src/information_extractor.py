
import re


def extract_candidate_name(resume_text):
    """Extract a candidate's name from a labeled resume."""
    match = re.search(
        r"^Name:\s*(.+)$",
        resume_text,
        re.IGNORECASE | re.MULTILINE
    )

    if match:
        return match.group(1).strip()

    return "Not Found"

def extract_email(resume_text):
    """Extract the first email address from resume text."""
    match = re.search(
        r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
        resume_text
    )

    if match:
        return match.group(0)

    return "Not Found"

def extract_job_role(resume_text):
    """Extract the job role from a labeled resume."""
    match = re.search(
        r"^Role:\s*(.+)$",
        resume_text,
        re.IGNORECASE | re.MULTILINE
    )

    if match:
        return match.group(1).strip()

    return "Not Found"

def extract_experience(resume_text):
    """Extract years of experience from a labeled resume."""
    match = re.search(
        r"^Experience:\s*(\d+(?:\.\d+)?)\s*(?:years?|yrs?)\b",
        resume_text,
        re.IGNORECASE | re.MULTILINE
    )

    if match:
        return float(match.group(1))

    return None

def extract_education(resume_text):
    """Extract education from a labeled resume."""
    match = re.search(
        r"^Education:\s*(.+)$",
        resume_text,
        re.IGNORECASE | re.MULTILINE
    )

    if match:
        return match.group(1).strip()

    return "Not Found"

def extract_skills(resume_text):
    """Extract skills from a labeled resume."""
    match = re.search(
        r"^Skills:\s*(.+)$",
        resume_text,
        re.IGNORECASE | re.MULTILINE
    )

    if match:
        skills_text = match.group(1).strip()
        skills_list = [
            skill.strip()
            for skill in skills_text.split(",")
            if skill.strip()
        ]
        return skills_list

    return []

def extract_projects(resume_text):
    """Extract projects from a labeled resume."""
    match = re.search(
        r"^Projects:\s*(.+)$",
        resume_text,
        re.IGNORECASE | re.MULTILINE
    )

    if match:
        return [
            project.strip()
            for project in match.group(1).split(",")
            if project.strip()
        ]

    return []

def extract_summary(resume_text):
    """Extract the professional summary from a labeled resume."""
    match = re.search(
        r"^Summary:\s*(.+)$",
        resume_text,
        re.IGNORECASE | re.MULTILINE
    )

    if match:
        return match.group(1).strip()

    return "Not Found"

def extract_candidate_information(resume_text):
    """Extract all candidate information into a dictionary."""
    return {
        "name": extract_candidate_name(resume_text),
        "email": extract_email(resume_text),
        "role": extract_job_role(resume_text),
        "experience": extract_experience(resume_text),
        "education": extract_education(resume_text),
        "skills": extract_skills(resume_text),
        "projects": extract_projects(resume_text),
        "summary": extract_summary(resume_text)
    }


if __name__ == "__main__":
    sample_resume = """
Name: Rahul Sharma
Email: rahul.sharma@example.com
Role: Python Developer
Experience: 3 years
Education: B.Tech in Computer Science
Skills: Python, Pandas, NumPy, SQL, Git, Machine Learning, Data Analysis
Projects: Data Analysis Dashboard, Python Automation Scripts
Summary: Python Developer with 3 years of experience in Python programming, data analysis, automation, and SQL database operations.
"""

    candidate = extract_candidate_information(sample_resume)

    print("===== STRUCTURED CANDIDATE INFORMATION =====")

    for key, value in candidate.items():
        print(f"{key}: {value}")

    assert candidate["name"] == "Rahul Sharma"
    assert candidate["email"] == "rahul.sharma@example.com"
    assert candidate["role"] == "Python Developer"
    assert candidate["experience"] == 3.0
    assert candidate["education"] == "B.Tech in Computer Science"
    assert len(candidate["skills"]) == 7
    assert len(candidate["projects"]) == 2
    assert candidate["summary"].startswith("Python Developer")

    print("\nSUCCESS: All 8 extraction checks passed!")

