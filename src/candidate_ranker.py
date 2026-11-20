
from pathlib import Path
from src.batch_screening import screen_multiple_candidates


def rank_candidates(results):
    """Rank candidates by weighted score."""

    valid_candidates = []
    insufficient_data = []

    for result in results:
        score = result["score"]["weighted_score"]

        if score is None:
            insufficient_data.append(result)
        else:
            valid_candidates.append(result)

    ranked_candidates = sorted(
        valid_candidates,
        key=lambda candidate: candidate["score"]["weighted_score"],
        reverse=True
    )

    print("\n===== CANDIDATE RANKING RESULTS =====")

    for rank, candidate in enumerate(ranked_candidates, start=1):
        print(f"\nRank: {rank}")
        print("Candidate:", candidate["candidate_name"])
        print("Job:", candidate["job_title"])
        print(
            "Weighted Score:",
            candidate["score"]["weighted_score"]
        )

    print("\n===== RANKING SUMMARY =====")
    print("Total candidates:", len(results))
    print("Ranked candidates:", len(ranked_candidates))
    print("Insufficient data:", len(insufficient_data))

    return ranked_candidates


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
