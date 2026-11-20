

from pathlib import Path
import re


def read_job_description(file_path):
    """Read a job description from a text file."""
    path = Path(file_path)

    with path.open("r", encoding="utf-8-sig") as file:
        job_text = file.read()

    return job_text


def extract_field(job_text, field_name):
    """Extract a single-line field by its label."""
    pattern = rf"^{re.escape(field_name)}:\s*(.+)$"

    match = re.search(
        pattern,
        job_text,
        flags=re.MULTILINE | re.IGNORECASE
    )

    if match:
        return match.group(1).strip()

    return None


def extract_minimum_experience(job_text):
    """Extract minimum experience as a number."""
    experience_text = extract_field(
        job_text, "Minimum Experience"
    )

    if experience_text:
        match = re.search(r"\d+(?:\.\d+)?", experience_text)

        if match:
            return float(match.group())

    return None


def extract_skills(job_text, field_name):
    """Extract comma-separated skills into a list."""
    skills_text = extract_field(job_text, field_name)

    if not skills_text:
        return []

    return [
        skill.strip()
        for skill in skills_text.split(",")
        if skill.strip()
    ]

def parse_job_description(file_path):
    """Convert a job description into structured data."""

    job_text = read_job_description(file_path)

    # Extract responsibilities
    responsibilities_match = re.search(
        r"^Responsibilities:\s*\n(.*?)(?=^Job Summary:|\Z)",
        job_text,
        flags=re.MULTILINE | re.DOTALL | re.IGNORECASE
    )

    responsibilities = []

    if responsibilities_match:
        responsibilities = [
            line.strip()
            for line in responsibilities_match.group(1).splitlines()
            if line.strip()
        ]

    # Extract job summary
    summary_match = re.search(
        r"^Job Summary:\s*\n(.*?)(?=\Z)",
        job_text,
        flags=re.MULTILINE | re.DOTALL | re.IGNORECASE
    )

    job_summary = ""

    if summary_match:
        job_summary = summary_match.group(1).strip()

    # Create structured dictionary
    job_data = {
        "job_title": extract_field(job_text, "Job Title"),
        "department": extract_field(job_text, "Department"),
        "employment_type": extract_field(
            job_text, "Employment Type"
        ),
        "minimum_experience": extract_minimum_experience(
            job_text
        ),
        "education": extract_field(job_text, "Education"),
        "required_skills": extract_skills(
            job_text, "Required Skills"
        ),
        "preferred_skills": extract_skills(
            job_text, "Preferred Skills"
        ),
        "responsibilities": responsibilities,
        "job_summary": job_summary
    }

    return job_data


if __name__ == "__main__":

    job_folder = Path("job_descriptions")
    job_files = sorted(job_folder.glob("*.txt"))

    required_fields = [
        "job_title",
        "department",
        "employment_type",
        "minimum_experience",
        "education",
        "required_skills",
        "preferred_skills",
        "responsibilities",
        "job_summary"
    ]

    total_files = len(job_files)
    successful = 0
    failed = 0

    print("===== JOB DESCRIPTION BATCH TEST =====")

    for job_file in job_files:

        print(f"\n===== TESTING {job_file.name} =====")

        try:
            job_data = parse_job_description(job_file)

            for key, value in job_data.items():
                print(f"{key}: {value}")

            missing_fields = [
                field for field in required_fields
                if not job_data.get(field)
            ]

            if not missing_fields:
                successful += 1
                print(f"SUCCESS: {job_file.name} passed!")
            else:
                failed += 1
                print(
                    f"FAILED: {job_file.name} "
                    f"missing {missing_fields}"
                )

        except Exception as error:
            failed += 1
            print(f"FAILED: {job_file.name}: {error}")

    print("\n===== FINAL JOB DESCRIPTION TEST SUMMARY =====")
    print(f"Total files: {total_files}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")

    if total_files == 5 and successful == 5 and failed == 0:
        print("SUCCESS: All 5 job descriptions validated!")
    else:
        print("FAILED: Job description validation incomplete!")

