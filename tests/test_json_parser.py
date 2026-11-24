import json
from pathlib import Path

import pytest

from src.resume_parser import extract_resume_text


RESUMES = Path(__file__).resolve().parent.parent / "resumes"


@pytest.mark.parametrize("candidate_id", range(1, 6))
def test_json_resume_extraction(candidate_id):
    path = RESUMES / f"candidate_{candidate_id:02d}.json"

    assert path.exists()
    assert extract_resume_text(path).strip()


@pytest.mark.parametrize("candidate_id", range(1, 6))
def test_four_format_consistency(candidate_id):
    texts = []

    for extension in ["pdf", "docx", "txt", "json"]:
        path = RESUMES / f"candidate_{candidate_id:02d}.{extension}"
        text = extract_resume_text(path)
        texts.append(" ".join(text.split()).casefold())

    assert all(texts)
    assert len(set(texts)) == 1


def test_corrupted_json(tmp_path):
    path = tmp_path / "corrupted.json"
    path.write_text("{invalid json", encoding="utf-8")

    assert extract_resume_text(path) == ""


def test_empty_json_file(tmp_path):
    path = tmp_path / "empty.json"
    path.write_text("", encoding="utf-8")

    assert extract_resume_text(path) == ""


def test_missing_json_file(tmp_path):
    path = tmp_path / "missing.json"

    assert extract_resume_text(path) == ""