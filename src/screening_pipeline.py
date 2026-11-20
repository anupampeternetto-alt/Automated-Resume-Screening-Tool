
from pathlib import Path

from src.resume_processor import process_resume
from src.job_description_parser import parse_job_description
from src.matching_engine import (
    match_required_skills,
    match_preferred_skills,
    match_experience,
    calculate_weighted_score,
)


def screen_candidate(resume_path, job_path):
    """Screen one candidate against one job description."""

    candidate = process_resume(resume_path)
    job = parse_job_description(job_path)

    required_result = match_required_skills(
        candidate["skills"],
        job["required_skills"]
    )

    preferred_result = match_preferred_skills(
        candidate["skills"],
        job["preferred_skills"]
    )

    experience_result = match_experience(
        candidate["experience"],
        job["minimum_experience"]
    )

    score_result = calculate_weighted_score(
        required_result,
        preferred_result,
        experience_result
    )

    return {
        "candidate_name": candidate["name"],
        "resume_file": candidate["file_name"],
        "job_title": job["job_title"],
        "required_skills": required_result,
        "preferred_skills": preferred_result,
        "experience": experience_result,
        "score": score_result,
    }


if __name__ == "__main__":

    project_root = Path(__file__).resolve().parent.parent

    resume_path = project_root / "resumes" / "candidate_01.txt"

    job_path = (
        project_root
        / "job_descriptions"
        / "python_developer.txt"
    )

    result = screen_candidate(resume_path, job_path)

    print("\n===== SCREENING PIPELINE TEST =====")
    print("Candidate:", result["candidate_name"])
    print("Resume:", result["resume_file"])
    print("Job:", result["job_title"])

    print("\nRequired Skills:")
    print(result["required_skills"])

    print("\nPreferred Skills:")
    print(result["preferred_skills"])

    print("\nExperience:")
    print(result["experience"])

    print("\nFinal Score:")
    print(result["score"])
