from pathlib import Path

from src.resume_processor import process_resume
from src.job_description_parser import parse_job_description
from src.features import extract_features
from src.matching_engine import calculate_weighted_score


def screen_candidate(resume_path, job_path):
    """Generate explainable job-related matching evidence."""

    candidate = process_resume(resume_path)
    job = parse_job_description(job_path)

    features = extract_features(candidate, job)

    required = features["required_skills"]
    preferred = features["preferred_skills"]
    experience = features["experience"]

    similarity = features["sim_embedding"]

    score = calculate_weighted_score(
        required,
        preferred,
        experience
    )

    explanations = {
        "matched_required_skills":
            required["matched_skills"],

        "missing_required_skills":
            required["missing_skills"],

        "matched_preferred_skills":
            preferred["matched_skills"],

        "missing_preferred_skills":
            preferred["missing_skills"],

        "required_skill_match":
            required["match_percentage"],

        "preferred_skill_match":
            preferred["match_percentage"],

        "semantic_similarity":
            similarity,

        "candidate_experience":
            experience["candidate_experience"],

        "minimum_experience":
            experience["minimum_experience"],

        "experience_requirement_met":
            experience["experience_match"],

        "review_required": True,

        "limitations": (
            "Similarity and extracted skills are "
            "not proof of candidate competence. "
            "Human verification is required."
        )
    }

    return {
        "candidate_name": candidate["name"],
        "resume_file": candidate["file_name"],
        "job_title": job["job_title"],
        "required_skills": required,
        "preferred_skills": preferred,
        "experience": experience,
        "score": score,
        "semantic_similarity": similarity,
        "features": features,
        "explanations": explanations,
        "review_required": True,
        "extraction_method":
            candidate["extraction_method"]
    }


if __name__ == "__main__":

    root = Path(__file__).resolve().parent.parent

    result = screen_candidate(
        root / "resumes" / "candidate_01.txt",
        root / "job_descriptions" / "python_developer.txt"
    )

    print("===== ADVANCED AI SCREENING TEST =====")

    print("Candidate:", result["candidate_name"])
    print("Job:", result["job_title"])
    print("Extraction:", result["extraction_method"])
    print("Semantic similarity:", result["semantic_similarity"])

    print("\n===== EXPLAINABLE AI EVIDENCE =====")

    for key, value in result["explanations"].items():
        print(f"{key}: {value}")

    assert result["candidate_name"] == "Rahul Sharma"
    assert result["semantic_similarity"] is not None
    assert -1 <= result["semantic_similarity"] <= 1
    assert result["review_required"] is True

    print("\nADVANCED AI PIPELINE TEST PASSED")
    print("EXPLAINABLE AI TEST PASSED")