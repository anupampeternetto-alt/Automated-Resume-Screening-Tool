
from pathlib import Path

from src.batch_screening import screen_multiple_candidates
from src.candidate_ranker import rank_candidates


def classify_candidate(score):
    """Classify a candidate using demonstration thresholds."""

    if score is None:
        return "Insufficient Data"

    if score >= 80:
        return "Highly Matched"

    if score >= 60:
        return "Moderately Matched"

    return "Low Match"


def shortlist_candidates(ranked_candidates):
    """Classify ranked candidates for human review."""

    print("\n===== CANDIDATE SHORTLISTING RESULTS =====")

    summary = {
        "Highly Matched": 0,
        "Moderately Matched": 0,
        "Low Match": 0,
        "Insufficient Data": 0
    }

    shortlisted_candidates = []

    for rank, candidate in enumerate(ranked_candidates, start=1):

        score = candidate["score"]["weighted_score"]
        classification = classify_candidate(score)

        summary[classification] += 1

        candidate_result = {
            **candidate,
            "rank": rank,
            "classification": classification
        }

        shortlisted_candidates.append(candidate_result)

        print(f"\nRank: {rank}")
        print("Candidate:", candidate["candidate_name"])
        print("Weighted Score:", score)
        print("Classification:", classification)

    print("\n===== SHORTLISTING SUMMARY =====")

    for category, count in summary.items():
        print(f"{category}: {count}")

    print("Total Classified:", len(shortlisted_candidates))

    return shortlisted_candidates


if __name__ == "__main__":

    project_root = Path(__file__).resolve().parent.parent

    resumes_folder = project_root / "resumes"

    job_path = (
        project_root
        / "job_descriptions"
        / "python_developer.txt"
    )

    results = screen_multiple_candidates(
        resumes_folder,
        job_path
    )

    ranked_candidates = rank_candidates(results)

    shortlisted_candidates = shortlist_candidates(
        ranked_candidates
    )
