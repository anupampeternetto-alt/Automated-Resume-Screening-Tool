
from functools import lru_cache
from math import isfinite

from sentence_transformers import SentenceTransformer

from src.matching_engine import (
    match_required_skills,
    match_preferred_skills,
    match_experience,
)


MODEL_NAME = "all-MiniLM-L6-v2"


@lru_cache(maxsize=1)
def get_embedding_model():
    return SentenceTransformer(MODEL_NAME)


def calculate_semantic_similarity(text_a, text_b):

    if not isinstance(text_a, str):
        raise TypeError("First input must be text.")

    if not isinstance(text_b, str):
        raise TypeError("Second input must be text.")

    if not text_a.strip() or not text_b.strip():
        raise ValueError("Similarity inputs cannot be empty.")

    model = get_embedding_model()

    embeddings = model.encode(
        [text_a, text_b],
        normalize_embeddings=True
    )

    similarity = float(
        embeddings[0] @ embeddings[1]
    )

    if not isfinite(similarity):
        raise ValueError("Invalid similarity value.")

    return max(-1.0, min(1.0, similarity))


def build_skills_text(skills):

    return ", ".join(
        sorted({
            skill.strip().casefold()
            for skill in skills
            if isinstance(skill, str) and skill.strip()
        })
    )


def extract_features(candidate, job):

    candidate_skills = candidate.get("skills", [])
    required_skills = job.get("required_skills", [])
    preferred_skills = job.get("preferred_skills", [])

    required = match_required_skills(
        candidate_skills,
        required_skills
    )

    preferred = match_preferred_skills(
        candidate_skills,
        preferred_skills
    )

    experience = match_experience(
        candidate.get("experience"),
        job.get("minimum_experience")
    )

    candidate_text = build_skills_text(
        candidate_skills
    )

    job_text = build_skills_text(
        required_skills + preferred_skills
    )

    similarity = None

    if candidate_text and job_text:
        similarity = calculate_semantic_similarity(
            candidate_text,
            job_text
        )

    return {
        "sim_embedding": similarity,
        "rule_musthave_hits": len(
            required["matched_skills"]
        ),
        "rule_musthave_total": (
            len(required["matched_skills"])
            + len(required["missing_skills"])
        ),
        "years_exp": experience[
            "candidate_experience"
        ],
        "gap_penalty": 0.0,
        "required_skills": required,
        "preferred_skills": preferred,
        "experience": experience,
        "review_required": True
    }


if __name__ == "__main__":

    candidate = {
        "skills": [
            "Python", "SQL", "Pandas",
            "Git", "Machine Learning"
        ],
        "experience": 3.0
    }

    job = {
        "required_skills": [
            "Python", "SQL", "Pandas"
        ],
        "preferred_skills": [
            "Git", "Docker"
        ],
        "minimum_experience": 2.0
    }

    result = extract_features(candidate, job)

    print("===== FEATURE ENGINEERING TEST =====")

    for key, value in result.items():
        print(f"{key}: {value}")

    assert result["rule_musthave_hits"] == 3
    assert result["rule_musthave_total"] == 3
    assert result["years_exp"] == 3.0
    assert result["gap_penalty"] == 0.0
    assert -1 <= result["sim_embedding"] <= 1
    assert result["review_required"] is True

    print("\nFEATURE ENGINEERING TEST PASSED")
