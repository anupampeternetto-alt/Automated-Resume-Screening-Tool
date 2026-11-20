
from pathlib import Path

from src.batch_screening import screen_multiple_candidates
from src.candidate_ranker import rank_candidates
from src.candidate_shortlister import shortlist_candidates
from src.report_generator import generate_reports


def main():
    """Run the complete resume screening workflow."""

    project_root = Path(__file__).resolve().parent

    resumes_folder = project_root / "resumes"
    jobs_folder = project_root / "job_descriptions"
    reports_folder = project_root / "reports"

    job_path = jobs_folder / "python_developer.txt"

    if not resumes_folder.is_dir():
        print("ERROR: Resumes folder not found.")
        return

    if not job_path.is_file():
        print("ERROR: Job description not found.")
        return

    print("===== AUTOMATED RESUME SCREENING TOOL =====")
    print("Selected Job: Python Developer")

    results = screen_multiple_candidates(
        resumes_folder,
        job_path
    )

    if not results:
        print("No candidates were successfully screened.")
        return

    ranked = rank_candidates(results)

    shortlisted = shortlist_candidates(ranked)

    report_data = generate_reports(
        shortlisted,
        reports_folder
    )

    print("\n===== FINAL APPLICATION SUMMARY =====")
    print("Candidates processed:", len(results))
    print("Candidates classified:", len(shortlisted))
    print("Report records:", len(report_data))
    print("Reports folder:", reports_folder)
    print("SUCCESS: Application completed!")


if __name__ == "__main__":
    main()
