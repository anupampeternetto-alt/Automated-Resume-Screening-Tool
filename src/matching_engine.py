
def match_required_skills(candidate_skills, required_skills):
    """Compare candidate skills with required job skills."""

    candidate_set = {
        skill.strip().casefold()
        for skill in candidate_skills
        if skill.strip()
    }

    required_lookup = {
        skill.strip().casefold(): skill.strip()
        for skill in required_skills
        if skill.strip()
    }

    matched_skills = []
    missing_skills = []

    for normalized_skill, original_skill in required_lookup.items():
        if normalized_skill in candidate_set:
            matched_skills.append(original_skill)
        else:
            missing_skills.append(original_skill)

    total_required = len(required_lookup)

    if total_required == 0:
        match_percentage = None
    else:
        match_percentage = (
            len(matched_skills) / total_required
        ) * 100

    return {
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "match_percentage": match_percentage
    }

def match_preferred_skills(candidate_skills, preferred_skills):
    """Compare candidate skills with preferred job skills."""

    candidate_set = {
        skill.strip().casefold()
        for skill in candidate_skills
        if skill.strip()
    }

    preferred_lookup = {
        skill.strip().casefold(): skill.strip()
        for skill in preferred_skills
        if skill.strip()
    }

    matched_skills = []
    missing_skills = []

    for normalized_skill, original_skill in preferred_lookup.items():
        if normalized_skill in candidate_set:
            matched_skills.append(original_skill)
        else:
            missing_skills.append(original_skill)

    total_preferred = len(preferred_lookup)

    if total_preferred == 0:
        match_percentage = None
    else:
        match_percentage = (
            len(matched_skills) / total_preferred
        ) * 100

    return {
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "match_percentage": match_percentage
    }

def match_experience(candidate_experience, minimum_experience):
    """Check whether candidate meets minimum experience."""

    if candidate_experience is None or minimum_experience is None:
        return {
            "candidate_experience": candidate_experience,
            "minimum_experience": minimum_experience,
            "experience_gap": None,
            "experience_match": None
        }

    candidate_experience = float(candidate_experience)
    minimum_experience = float(minimum_experience)

    if candidate_experience < 0 or minimum_experience < 0:
        raise ValueError("Experience cannot be negative")

    experience_gap = candidate_experience - minimum_experience

    experience_match = (
        candidate_experience >= minimum_experience
    )

    return {
        "candidate_experience": candidate_experience,
        "minimum_experience": minimum_experience,
        "experience_gap": experience_gap,
        "experience_match": experience_match
    }

def calculate_weighted_score(
    required_result,
    preferred_result,
    experience_result
):
    """Calculate an explainable weighted match score."""

    required_score = required_result["match_percentage"]
    preferred_score = preferred_result["match_percentage"]
    experience_match = experience_result["experience_match"]

    weights = {
        "required": 0.60,
        "preferred": 0.20,
        "experience": 0.20
    }

    # Missing data must not be treated as a failed match.
    if (
        required_score is None
        or preferred_score is None
        or experience_match is None
    ):
        return {
            "weighted_score": None,
            "status": "Insufficient data"
        }

    if not (0 <= required_score <= 100):
        raise ValueError("Invalid required skills percentage")

    if not (0 <= preferred_score <= 100):
        raise ValueError("Invalid preferred skills percentage")

    if not isinstance(experience_match, bool):
        raise ValueError("Experience match must be a boolean")

    experience_score = 100.0 if experience_match else 0.0

    weighted_score = (
        required_score * weights["required"]
        + preferred_score * weights["preferred"]
        + experience_score * weights["experience"]
    )

    return {
        "required_skills_score": required_score,
        "preferred_skills_score": preferred_score,
        "experience_score": experience_score,
        "weighted_score": round(weighted_score, 2),
        "status": "Calculated"
    }


if __name__ == "__main__":
    candidate_skills = [
        "Python", "Pandas", "NumPy", "SQL",
        "Git", "Machine Learning", "Data Analysis"
    ]

    required_skills = [
        "Python", "SQL", "Git", "Pandas", "NumPy"
    ]

    result = match_required_skills(
        candidate_skills, required_skills
    )

    print("===== REQUIRED SKILLS MATCHING TEST =====")
    print("Matched Skills:", result["matched_skills"])
    print("Missing Skills:", result["missing_skills"])
    print("Match Percentage:", result["match_percentage"])

    if result["match_percentage"] == 100.0:
        print("SUCCESS: All required skills matched!")
    else:
        print("CHECK: Some required skills are missing!")

    preferred_skills = [
        "Machine Learning",
        "Data Analysis",
        "REST APIs",
        "Automation"
    ]

    preferred_result = match_preferred_skills(
        candidate_skills,
        preferred_skills
    )

    print("\n===== PREFERRED SKILLS MATCHING TEST =====")
    print("Matched Skills:", preferred_result["matched_skills"])
    print("Missing Skills:", preferred_result["missing_skills"])
    print("Match Percentage:", preferred_result["match_percentage"])

    if preferred_result["match_percentage"] == 50.0:
        print("SUCCESS: Preferred skills matching test passed!")
    else:
        print("CHECK: Preferred skills matching result differs!")

    print("\n===== EXPERIENCE MATCHING TEST =====")

    test_cases = [
        (3.0, 2.0, True),
        (2.0, 2.0, True),
        (1.0, 2.0, False)
    ]

    all_passed = True

    for candidate_years, required_years, expected in test_cases:

        result = match_experience(
            candidate_years,
            required_years
        )

        print("\nCandidate Experience:",
              result["candidate_experience"])

        print("Minimum Experience:",
              result["minimum_experience"])

        print("Experience Gap:",
              result["experience_gap"])

        print("Requirement Met:",
              result["experience_match"])

        if result["experience_match"] == expected:
            print("SUCCESS: Experience test passed!")
        else:
            print("FAILED: Experience test failed!")
            all_passed = False

    if all_passed:
        print("\nSUCCESS: All 3 experience tests passed!")
    else:
        print("\nFAILED: Some experience tests failed!")


    print("\n===== WEIGHTED MATCHING SCORE TEST =====")

    required_result = match_required_skills(
        candidate_skills,
        required_skills
    )

    preferred_result = match_preferred_skills(
        candidate_skills,
        preferred_skills
    )

    experience_result = match_experience(3.0, 2.0)

    final_result = calculate_weighted_score(
        required_result,
        preferred_result,
        experience_result
    )

    for key, value in final_result.items():
        print(f"{key}: {value}")

    assert final_result["weighted_score"] == 90.0
    assert final_result["status"] == "Calculated"

    print("SUCCESS: Weighted scoring test passed!")
