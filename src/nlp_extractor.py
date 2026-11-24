
import re
from functools import lru_cache

import spacy
from spacy.matcher import PhraseMatcher
from rapidfuzz import process, fuzz

from src.information_extractor import (
    extract_candidate_information,
    extract_skills,
)


TECHNICAL_SKILLS = [
    "Python", "Java", "JavaScript", "TypeScript",
    "C", "C++", "C#", "SQL", "HTML", "CSS",
    "Pandas", "NumPy", "Matplotlib", "Seaborn",
    "Scikit-learn", "TensorFlow", "PyTorch",
    "Machine Learning", "Deep Learning",
    "Natural Language Processing", "NLP",
    "Data Analysis", "Data Science",
    "FastAPI", "Flask", "Django", "Streamlit",
    "Git", "GitHub", "Docker", "Kubernetes",
    "AWS", "Azure", "Google Cloud",
    "SQLite", "PostgreSQL", "MySQL", "MongoDB",
    "Power BI", "Tableau", "Excel",
    "React", "Node.js", "REST API",
    "Linux", "Automation", "APIs",
    "Project Management", "Agile", "Scrum",
    "DSA", "Salesforce", "NoSQL", "Spring",
    "GCP", "Jenkins", "Terraform",
    "DevOps", "Cybersecurity", "Statistics",
    "Microsoft Office", "Business Analysis"
]


@lru_cache(maxsize=1)
def get_nlp():
    return spacy.load("en_core_web_sm")


@lru_cache(maxsize=1)
def get_skill_matcher():
    nlp = get_nlp()

    matcher = PhraseMatcher(
        nlp.vocab,
        attr="LOWER"
    )

    patterns = [
        nlp.make_doc(skill)
        for skill in TECHNICAL_SKILLS
    ]

    matcher.add(
        "TECHNICAL_SKILL",
        patterns
    )

    return matcher


def extract_technical_skills(text):
    nlp = get_nlp()
    doc = nlp.make_doc(text)
    matcher = get_skill_matcher()

    canonical = {
        skill.casefold(): skill
        for skill in TECHNICAL_SKILLS
    }

    skills = set()

    for _, start, end in matcher(doc):
        value = doc[start:end].text.casefold()

        if value in canonical:
            skills.add(canonical[value])

    return sorted(
        skills,
        key=str.casefold
    )


def extract_fuzzy_skills(text, cutoff=85):
    """Suggest corrections for misspelled listed skills."""

    listed_skills = extract_skills(text)

    canonical = {
        skill.casefold(): skill
        for skill in TECHNICAL_SKILLS
    }

    suggestions = []
    seen = set()

    for skill in listed_skills:
        token = skill.strip().casefold()

        if len(token) < 5 or token in canonical:
            continue

        match = process.extractOne(
            token,
            canonical.keys(),
            scorer=fuzz.ratio,
            score_cutoff=cutoff
        )

        if match:
            suggested_skill = canonical[match[0]]

            pair = (
                token,
                suggested_skill.casefold()
            )

            if pair in seen:
                continue

            seen.add(pair)

            suggestions.append({
                "original": skill,
                "suggested_skill": suggested_skill,
                "confidence": round(match[1], 2),
                "requires_review": True
            })

    return suggestions


def extract_nlp_entities(text):
    nlp = get_nlp()
    doc = nlp(text)

    excluded = {
        skill.casefold()
        for skill in TECHNICAL_SKILLS
    }

    entities = {
        "persons": [],
        "organizations": [],
        "locations": [],
        "dates": []
    }

    labels = {
        "PERSON": "persons",
        "ORG": "organizations",
        "GPE": "locations",
        "LOC": "locations",
        "DATE": "dates"
    }

    for entity in doc.ents:
        value = entity.text.strip()

        if not value or entity.label_ not in labels:
            continue

        if any(
            re.search(
                r"(?<!\w)" +
                re.escape(skill) +
                r"(?!\w)",
                value.casefold()
            )
            for skill in excluded
        ):
            continue

        if re.search(
            r"\b(?:B\.Tech|M\.Tech|MBA|BBA|Summary|"
            r"Education|Skills|Projects)\b",
            value,
            re.IGNORECASE
        ):
            continue

        category = labels[entity.label_]

        if value not in entities[category]:
            entities[category].append(value)

    return entities


def extract_hybrid_information(resume_text):

    if not isinstance(resume_text, str):
        raise TypeError(
            "Resume text must be a string."
        )

    if not resume_text.strip():
        raise ValueError(
            "Resume text cannot be empty."
        )

    candidate = extract_candidate_information(
        resume_text
    )

    detected_skills = extract_technical_skills(
        resume_text
    )

    combined_skills = {}

    for skill in (
        candidate.get("skills", []) +
        detected_skills
    ):
        combined_skills[skill.casefold()] = skill

    candidate["skills"] = sorted(
        combined_skills.values(),
        key=str.casefold
    )

    candidate["nlp_entities"] = extract_nlp_entities(
        resume_text
    )

    candidate["fuzzy_skill_suggestions"] = (
        extract_fuzzy_skills(resume_text)
    )

    candidate["extraction_method"] = (
        "Hybrid Regex + spaCy NLP + Skill Dictionary"
    )

    return candidate
