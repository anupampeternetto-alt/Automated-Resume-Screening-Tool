
import csv
import json
from pathlib import Path

from src.batch_screening import screen_multiple_candidates
from src.candidate_ranker import rank_candidates
from src.candidate_shortlister import shortlist_candidates


def generate_reports(candidates, reports_folder):
    """Export screening results to CSV and JSON."""

    reports_folder.mkdir(parents=True, exist_ok=True)

    csv_path = reports_folder / "screening_report.csv"
    json_path = reports_folder / "screening_report.json"

    report_data = []

    for candidate in candidates:
        required = candidate["required_skills"]
        preferred = candidate["preferred_skills"]
        experience = candidate["experience"]
        score = candidate["score"]

        record = {
            "rank": candidate["rank"],
            "candidate_name": candidate["candidate_name"],
            "job_title": candidate["job_title"],
            "required_skills_score": required["match_percentage"],
            "preferred_skills_score": preferred["match_percentage"],
            "matched_required_skills": required["matched_skills"],
            "missing_required_skills": required["missing_skills"],
            "matched_preferred_skills": preferred["matched_skills"],
            "missing_preferred_skills": preferred["missing_skills"],
            "candidate_experience": experience["candidate_experience"],
            "minimum_experience": experience["minimum_experience"],
            "experience_match": experience["experience_match"],
            "weighted_score": score["weighted_score"],
            "classification": candidate["classification"]
        }

        report_data.append(record)

    with json_path.open("w", encoding="utf-8") as file:
        json.dump(report_data, file, indent=4)

    csv_records = []

    for record in report_data:
        csv_record = {}

        for key, value in record.items():
            if isinstance(value, list):
                csv_record[key] = ", ".join(value)
            else:
                csv_record[key] = value

        csv_records.append(csv_record)

    if csv_records:
        with csv_path.open(
            "w", newline="", encoding="utf-8-sig"
        ) as file:
            writer = csv.DictWriter(
                file,
                fieldnames=csv_records[0].keys()
            )
            writer.writeheader()
            writer.writerows(csv_records)

    print("\n===== REPORT GENERATION SUMMARY =====")
    print("Total candidates:", len(report_data))
    print("CSV Report:", csv_path)
    print("JSON Report:", json_path)
    print("SUCCESS: Screening reports generated!")

    return report_data


if __name__ == "__main__":

    project_root = Path(__file__).resolve().parent.parent

    resumes_folder = project_root / "resumes"
    reports_folder = project_root / "reports"

    job_path = (
        project_root
        / "job_descriptions"
        / "python_developer.txt"
    )

    results = screen_multiple_candidates(
        resumes_folder,
        job_path
    )

    ranked = rank_candidates(results)

    shortlisted = shortlist_candidates(ranked)

    generate_reports(shortlisted, reports_folder)
