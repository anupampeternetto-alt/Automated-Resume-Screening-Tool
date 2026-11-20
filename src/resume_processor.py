
from pathlib import Path

from src.resume_parser import extract_resume_text
from src.information_extractor import extract_candidate_information


def process_resume(file_path):
    """Read a resume and extract structured candidate information."""

    resume_text = extract_resume_text(str(file_path))

    if not resume_text or not resume_text.strip():
        raise ValueError("No readable text found in resume.")

    candidate = extract_candidate_information(resume_text)

    candidate["file_name"] = Path(file_path).name

    return candidate


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parent.parent
    resumes_folder = project_root / "resumes"

    expected_candidates = {
        "01": ("Rahul Sharma", "Python Developer", 3.0),
        "02": ("Priya Mehta", "Data Analyst", 2.0),
        "03": ("Arjun Verma", "Python Automation Engineer", 4.0),
        "04": ("Sneha Reddy", "Machine Learning Engineer", 3.0),
        "05": ("Karan Malhotra", "HR Executive", 2.0)
    }

    extensions = [".txt", ".docx", ".pdf"]
    passed = 0
    failed = 0

    print("===== FINAL CANDIDATE VALIDATION =====")

    for candidate_id, expected in expected_candidates.items():
        expected_name, expected_role, expected_experience = expected

        for extension in extensions:
            filename = f"candidate_{candidate_id}{extension}"
            file_path = resumes_folder / filename

            try:
                candidate = process_resume(file_path)

                assert candidate["name"] == expected_name
                assert candidate["role"] == expected_role
                assert candidate["experience"] == expected_experience
                assert candidate["email"]
                assert candidate["education"]
                assert candidate["skills"]
                assert candidate["projects"]
                assert candidate["summary"]
                assert candidate["file_name"] == filename

                passed += 1
                print(f"PASS: {filename} - {candidate['name']}")

            except Exception as error:
                failed += 1
                print(f"FAIL: {filename} - {error}")

    print("\n===== FINAL VALIDATION SUMMARY =====")
    print(f"Total tests: {passed + failed}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")

    if failed == 0 and passed == 15:
        print("SUCCESS: All 15 resumes validated!")
    else:
        print("WARNING: Some validation tests failed.")


