from pathlib import Path

from src.resume_parser import extract_resume_text
from src.nlp_extractor import extract_hybrid_information


def process_resume(file_path):
    """Extract structured resume information using hybrid NLP."""

    path = Path(file_path)
    resume_text = extract_resume_text(str(path))

    if not resume_text or not resume_text.strip():
        raise ValueError("No readable text found in resume.")

    candidate = extract_hybrid_information(resume_text)
    candidate["file_name"] = path.name

    return candidate


if __name__ == "__main__":

    root = Path(__file__).resolve().parent.parent

    expected = {
        "01": ("Rahul Sharma", "Python Developer", 3.0),
        "02": ("Priya Mehta", "Data Analyst", 2.0),
        "03": ("Arjun Verma", "Python Automation Engineer", 4.0),
        "04": ("Sneha Reddy", "Machine Learning Engineer", 3.0),
        "05": ("Karan Malhotra", "HR Executive", 2.0)
    }

    extensions = [".txt", ".docx", ".pdf", ".json"]

    passed = 0
    failed = 0

    for number, values in expected.items():
        for extension in extensions:

            filename = f"candidate_{number}{extension}"

            try:
                candidate = process_resume(
                    root / "resumes" / filename
                )

                assert candidate["name"] == values[0]
                assert candidate["role"] == values[1]
                assert candidate["experience"] == values[2]
                assert candidate["skills"]
                assert candidate["projects"]
                assert candidate["email"] != "Not Found"
                assert candidate["education"] != "Not Found"
                assert candidate["summary"] != "Not Found"
                assert candidate["file_name"] == filename
                assert "nlp_entities" in candidate
                assert "extraction_method" in candidate

                passed += 1

            except Exception as error:
                failed += 1
                print(f"FAIL: {filename}: {error}")

    print("===== HYBRID NLP VALIDATION =====")
    print("Total:", passed + failed)
    print("Passed:", passed)
    print("Failed:", failed)

    assert passed == 20 and failed == 0

    print("ALL 20 HYBRID NLP TESTS PASSED")