
import streamlit as st
import pandas as pd
import plotly.express as px
import tempfile
import json
from pathlib import Path

from src.database import initialize_database
from src.ingest import ingest_resume
from src.job_store import save_job
from src.feature_store import save_features
from src.screening_pipeline import screen_candidate
from src.job_description_parser import parse_job_description

st.set_page_config(
    page_title="AI Resume Screening Tool",
    page_icon="📄",
    layout="wide"
)

ROOT = Path(__file__).resolve().parent

st.title("AI-Powered Resume Screening Tool")
st.caption(
    "Intelligent Recruitment Analytics | NLP | "
    "Semantic Matching | Explainable AI"
)

st.info(
    "Decision-support prototype. All results require "
    "human verification. Scores are not hiring decisions."
)

with st.sidebar:
    st.header("Screening Configuration")

    job_files = sorted(
        (ROOT / "job_descriptions").glob("*.txt")
    )

    if not job_files:
        st.error("No job descriptions found.")
        st.stop()

    selected_job = st.selectbox(
        "Select Job Role",
        job_files,
        format_func=lambda p: p.stem.replace(
            "_", " "
        ).title()
    )

    uploaded_files = st.file_uploader(
        "Upload synthetic resumes",
        type=["pdf", "docx", "txt", "json"],
        accept_multiple_files=True
    )

    persist = st.checkbox(
        "Save screening features to SQLite",
        value=False
    )

    run = st.button(
        "Run AI Screening",
        type="primary",
        use_container_width=True
    )

    st.divider()
    st.caption("AI Technologies")
    st.write("spaCy NLP")
    st.write("Sentence Transformers")
    st.write("Cosine Similarity")
    st.write("SQLite")
    st.write("Plotly Analytics")

with st.expander("Selected Job Description"):
    st.json(parse_job_description(selected_job))

if run:
    st.session_state["results"] = []
    st.session_state["errors"] = []
    st.session_state["screened_job"] = selected_job.name

    if not uploaded_files:
        st.warning("Please upload at least one resume.")
    else:
        job_record = None

        if persist:
            try:
                initialize_database()
                job_record = save_job(selected_job)
            except Exception as error:
                st.error(f"Database setup failed: {error}")
                st.stop()

        progress = st.progress(0)

        for index, uploaded in enumerate(uploaded_files):
            try:
                with tempfile.TemporaryDirectory() as folder:
                    path = Path(folder) / Path(uploaded.name).name
                    path.write_bytes(uploaded.getvalue())

                    result = screen_candidate(
                        path, selected_job
                    )

                    result["database_status"] = "Not requested"

                    if persist:
                        try:
                            candidate = ingest_resume(path)

                            saved = save_features(
                                candidate["candidate_id"],
                                job_record["job_id"],
                                result["features"]
                            )

                            result["database_status"] = saved["status"]

                        except Exception as error:
                            result["database_status"] = (
                                f"Storage failed: {error}"
                            )

                    st.session_state["results"].append(result)

            except Exception as error:
                st.session_state["errors"].append(
                    f"{uploaded.name}: {error}"
                )

            progress.progress(
                (index + 1) / len(uploaded_files)
            )

        progress.empty()

results = st.session_state.get("results", [])
errors = st.session_state.get("errors", [])

for error in errors:
    st.error(error)

if results:
    st.caption(
        "Results for: "
        + st.session_state["screened_job"]
    )

    st.header("Screening Overview")

    rows = []

    for number, result in enumerate(results, start=1):
        evidence = result["explanations"]

        rows.append({
            "Record": f"Resume {number}",
            "Candidate": result["candidate_name"],
            "Resume": result["resume_file"],
            "Required Skills (%)":
                evidence["required_skill_match"],
            "Preferred Skills (%)":
                evidence["preferred_skill_match"],
            "Semantic Similarity":
                result["semantic_similarity"],
            "Experience (Years)":
                evidence["candidate_experience"],
            "Human Review": "Required",
            "Database": result["database_status"]
        })

    df = pd.DataFrame(rows)

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Processed Resumes", len(results))
    col2.metric("Processing Errors", len(errors))
    col3.metric("Human Review Required", len(results))
    col4.metric(
        "Database Saved",
        sum(
            r["database_status"] == "SAVED"
            for r in results
        )
    )

    st.divider()

    overview, analytics, evidence_tab, reports = st.tabs([
        "Screening Overview",
        "AI Analytics",
        "Explainable AI",
        "Reports"
    ])

    with overview:
        st.subheader("Candidate Evidence")
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

    with analytics:
        st.subheader("Job-Related Skill Evidence")

        chart_data = df.melt(
            id_vars=["Record"],
            value_vars=[
                "Required Skills (%)",
                "Preferred Skills (%)"
            ],
            var_name="Skill Category",
            value_name="Match Percentage"
        )

        fig = px.bar(
            chart_data,
            x="Record",
            y="Match Percentage",
            color="Skill Category",
            barmode="group",
            range_y=[0, 100],
            title="Required and Preferred Skill Evidence"
        )

        st.plotly_chart(fig, use_container_width=True)

        fig2 = px.bar(
            df,
            x="Record",
            y="Semantic Similarity",
            range_y=[-1, 1],
            title="Semantic Similarity Evidence"
        )

        st.plotly_chart(fig2, use_container_width=True)

        st.caption(
            "Semantic similarity measures text relevance, "
            "not competence or probability of hiring success."
        )

    with evidence_tab:
        st.subheader("Explainable AI Evidence")

        for number, result in enumerate(results, start=1):
            with st.expander(
                f"Resume {number}: {result['candidate_name']}"
            ):
                st.json(result["explanations"])

                st.write(
                    "Extraction method:",
                    result["extraction_method"]
                )

                st.warning("Human verification required.")

    with reports:
        st.subheader("Export Screening Evidence")

        st.download_button(
            "Download CSV Report",
            df.to_csv(index=False),
            file_name="ai_screening_report.csv",
            mime="text/csv"
        )

        st.download_button(
            "Download JSON Report",
            json.dumps(results, indent=4, default=str),
            file_name="ai_screening_report.json",
            mime="application/json"
        )

else:
    st.info(
        "Upload sample resumes, select a job role, "
        "and click Run AI Screening."
    )

st.divider()
st.caption(
    "AI-Enabled Resume Screening | "
    "Python Portfolio Project | Human-in-the-loop"
)
