
import re


def extract_labeled_value(text, labels):
    for label in labels:
        match = re.search(
            rf"^[ \t]*{re.escape(label)}:[ \t]*(.+)$",
            text,
            re.IGNORECASE | re.MULTILINE
        )
        if match:
            return match.group(1).strip()

    return "Not Found"


def extract_candidate_name(resume_text):
    return extract_labeled_value(
        resume_text, ["Name", "Full Name"]
    )


def extract_email(resume_text):
    match = re.search(
        r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
        resume_text
    )
    return match.group(0) if match else "Not Found"


def extract_job_role(resume_text):
    return extract_labeled_value(
        resume_text,
        ["Role", "Headline", "Job Title", "Position"]
    )


def extract_experience(resume_text):
    value = extract_labeled_value(
        resume_text,
        ["Experience", "Total Experience", "Years Of Experience"]
    )

    pattern = r"(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)\b"

    matches = re.findall(
        pattern, value, re.IGNORECASE
    )

    if matches:
        return max(float(item) for item in matches)

    summary = extract_summary(resume_text)

    match = re.search(
        pattern + r"\s+(?:of\s+)?(?:work\s+|professional\s+)?experience",
        summary,
        re.IGNORECASE
    )

    if match:
        return float(match.group(1))

    return None


def extract_education(resume_text):
    return extract_labeled_value(
        resume_text,
        ["Education", "Qualification", "Degree"]
    )


def extract_list(resume_text, labels):
    value = extract_labeled_value(
        resume_text, labels
    )

    if value == "Not Found":
        return []

    return [
        item.strip()
        for item in value.split(",")
        if item.strip()
    ]


def extract_skills(resume_text):
    return extract_list(
        resume_text,
        ["Skills", "Technical Skills", "Core Skills"]
    )


def extract_projects(resume_text):
    return extract_list(
        resume_text,
        ["Projects", "Personal Projects"]
    )


def extract_summary(resume_text):
    return extract_labeled_value(
        resume_text,
        ["Summary", "About", "Professional Summary"]
    )


def extract_certifications(resume_text):
    return extract_list(
        resume_text,
        ["Certifications", "Certificates", "Licenses"]
    )


def extract_candidate_information(resume_text):
    return {
        "name": extract_candidate_name(resume_text),
        "email": extract_email(resume_text),
        "role": extract_job_role(resume_text),
        "experience": extract_experience(resume_text),
        "education": extract_education(resume_text),
        "skills": extract_skills(resume_text),
        "projects": extract_projects(resume_text),
        "summary": extract_summary(resume_text),
        "certifications": extract_certifications(resume_text)
    }
