
from pathlib import Path
from src.screening_pipeline import screen_candidate


def screen_multiple_candidates(resumes_folder, job_path):
    """Screen all TXT resumes against one job."""

    results = []
    resume_files = sorted(resumes_folder.glob("*.txt"))

    print("===== MULTI-CANDIDATE SCREENING =====")
    print(f"Total resumes found: {len(resume_files)}")

    for resume_file in resume_files:
        print(f"\nProcessing: {resume_file.name}")

        try:
            result = screen_candidate(
                resume_file,
                job_path
            )

            results.append(result)

            print("Candidate:", result["candidate_name"])
            print("Job:", result["job_title"])

            print(
                "Required Skills:",
                result["required_skills"]["match_percentage"]
            )

            print(
                "Preferred Skills:",
                result["preferred_skills"]["match_percentage"]
            )

            print(
                "Experience Match:",
                result["experience"]["experience_match"]
            )

            print(
                "Weighted Score:",
                result["score"]["weighted_score"]
            )

            print("Status:", result["score"]["status"])

        except Exception as error:
            print(f"FAILED: {resume_file.name}: {error}")

    print("\n===== BATCH SCREENING SUMMARY =====")
    print("Total resumes:", len(resume_files))
    print("Successfully screened:", len(results))
    print("Failed:", len(resume_files) - len(results))

    return results


if __name__ == "__main__":

    project_root = Path(__file__).resolve().parent.parent

    resumes_folder = project_root / "resumes"

    job_path = (
        project_root
        / "job_descriptions"
        / "python_developer.txt"
    )

    screen_multiple_candidates(
        resumes_folder,
        job_path
    )
