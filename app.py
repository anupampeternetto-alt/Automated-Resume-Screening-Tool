import streamlit as st
import sys
import tempfile
import json
import csv
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from resume_processor import process_resume
from screening_pipeline import screen_candidate
from candidate_ranker import rank_candidates
from job_description_parser import parse_job_description
from matching_engine import (
    match_required_skills,
    match_preferred_skills,
    match_experience,
    calculate_weighted_score,
)

st.set_page_config(
    page_title="Automated Resume Screening Tool",
    page_icon="📄",
    layout="wide"
)

st.title("Automated Resume Screening Tool")

st.write(
    "An intelligent Python-based application for "
    "resume screening, candidate matching, "
    "ranking, and shortlisting."
)

st.divider()

st.subheader("Screening Dashboard")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Candidates", 5)

with col2:
    st.metric("Highly Matched", 1)

with col3:
    st.metric("Moderately Matched", 2)

st.success("Streamlit dashboard initialized successfully!")

# Resume Upload Interface
st.divider()

st.header("Upload Candidate Resumes")

uploaded_files = st.file_uploader(
    "Choose resume files",
    type=["pdf", "docx", "txt"],
    accept_multiple_files=True
)

if uploaded_files:
    st.success(
        f"{len(uploaded_files)} resume(s) uploaded successfully!"
    )

    for uploaded_file in uploaded_files:
        st.write(f"File Name: {uploaded_file.name}")
        st.write(f"File Size: {uploaded_file.size} bytes")

# Process Uploaded Resumes
if uploaded_files:
    st.subheader("Extracted Candidate Information")

    for uploaded_file in uploaded_files:
        try:
            suffix = Path(uploaded_file.name).suffix.lower()

            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir) / f"uploaded_resume{suffix}"
                temp_path.write_bytes(uploaded_file.getvalue())

                candidate_data = process_resume(temp_path)

            candidate_data["file_name"] = uploaded_file.name

            st.markdown(f"**Resume: {uploaded_file.name}**")
            st.json(candidate_data)

            st.success("Candidate information extracted successfully!")

        except Exception as error:
            st.error(
                f"Failed to process {uploaded_file.name}: {error}"
            )
# Job Description Selection
st.divider()
st.header("Select Job Description")

project_root = Path(__file__).resolve().parent
job_folder = project_root / "job_descriptions"

job_files = sorted(job_folder.glob("*.txt"))

if job_files:
    selected_job = st.selectbox(
        "Choose a job:",
        job_files,
        format_func=lambda file: file.stem.replace("_", " ").title()
    )

    job_data = parse_job_description(selected_job)

    st.subheader("Selected Job Details")
    st.json(job_data)
else:
    st.warning("No job descriptions found.")                     # Candidate Matching Scores
st.divider()
st.header("Candidate Matching Scores")

if uploaded_files and job_files:
    screening_results = []

    for uploaded_file in uploaded_files:
        try:
            suffix = Path(uploaded_file.name).suffix.lower()

            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir) / uploaded_file.name
                temp_path.write_bytes(uploaded_file.getvalue())

                result = screen_candidate(temp_path, selected_job)

            screening_results.append(result)

            st.subheader(uploaded_file.name)
            st.json(result)

        except Exception as error:
            st.error(f"Screening failed: {error}")
else:
    st.info("Upload resumes and select a job to see matching scores.")                                                                                                                      # Candidate Ranking
st.divider()
st.header("Candidate Rankings")

if uploaded_files and job_files:
    ranked_results = sorted(
        screening_results,
        key=lambda candidate: candidate.get("score", {}).get("weighted_score") or 0,
        reverse=True
    )

    for rank, candidate in enumerate(ranked_results, start=1):
        st.write(
            f"Rank {rank}: "
            f"{candidate.get('candidate_name', 'Unknown')} - "
            f"{candidate.get('score', {}).get('weighted_score')}%"
        )
else:
    st.info("Upload resumes to see candidate rankings.")         # Candidate Shortlisting
st.divider()
st.header("Candidate Shortlisting")

if uploaded_files and job_files:
    for candidate in ranked_results:
        score = candidate.get("score", {}).get("weighted_score")

        if score is None:
            status = "Insufficient Data"
        elif score >= 80:
            status = "Highly Matched"
        elif score >= 60:
            status = "Moderately Matched"
        else:
            status = "Low Match"

        st.write(
            f"{candidate.get('candidate_name', 'Unknown')}: "
            f"{status} ({score}%)"
        )
else:
    st.info("Upload resumes to see shortlisting results.")       # JSON Report Download
st.divider()
st.header("Download Screening Reports")

if uploaded_files and job_files:
    json_report = json.dumps(
        ranked_results,
        indent=4,
        default=str
    )

    st.download_button(
        label="Download JSON Report",
        data=json_report,
        file_name="candidate_screening_report.json",
        mime="application/json"
    )
else:
    st.info("Upload resumes to download reports.")               # CSV Report Download
if uploaded_files and job_files:
    import io

    csv_output = io.StringIO()
    writer = csv.writer(csv_output)

    writer.writerow([
        "Rank",
        "Candidate Name",
        "Resume File",
        "Job Title",
        "Matching Score",
        "Status"
    ])

    for rank, candidate in enumerate(ranked_results, start=1):
        score = candidate.get("score", {}).get("weighted_score")

        if score is None:
            status = "Insufficient Data"
        elif score >= 80:
            status = "Highly Matched"
        elif score >= 60:
            status = "Moderately Matched"
        else:
            status = "Low Match"

        writer.writerow([
            rank,
            candidate.get("candidate_name", "Unknown"),
            candidate.get("resume_file", ""),
            candidate.get("job_title", ""),
            score,
            status
        ])

    st.download_button(
        label="Download CSV Report",
        data=csv_output.getvalue(),
        file_name="candidate_screening_report.csv",
        mime="text/csv"
    )                                                                          