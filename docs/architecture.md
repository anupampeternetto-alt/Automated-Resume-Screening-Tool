# Automated Resume Screening Tool — System Architecture



## 1. Project Overview



An AI-enabled, industry-oriented resume screening system designed to simulate recruitment workflows using synthetic candidate data.



## 2. Problem Statement



Manual resume screening is time-consuming and inconsistent. This project combines keyword matching, natural language processing and semantic similarity to assist recruiters in reviewing candidate qualifications.



## 3. Technology Stack



- Python 3.11

- Pandas and NumPy

- Scikit-learn

- spaCy and RapidFuzz

- Sentence Transformers and PyTorch

- all-MiniLM-L6-v2

- PDFMiner, pdfplumber and python-docx

- FastAPI and Pydantic

- SQLAlchemy and SQLite

- Next.js

- Docker

- Pytest and HTTPX

- Streamlit for existing prototype support



## 4. System Architecture



Recruiter Dashboard

→ FastAPI Backend

→ Resume Ingestion

→ Text Extraction and Cleaning

→ Skill and Entity Extraction

→ TF-IDF and Semantic Embeddings

→ Hybrid Scoring

→ Candidate Ranking

→ Database Storage

→ Report Generation and Human Review



## 5. Input



- Synthetic PDF, DOCX and TXT resumes

- Job descriptions

- Required and preferred skills

- Job-related experience and education requirements



## 6. Processing



- Resume text extraction

- Text normalization

- Skill and entity extraction

- Keyword matching

- TF-IDF vectorization

- Semantic embedding generation

- Cosine similarity calculation

- Weighted candidate scoring

- Explainable ranking recommendations



## 7. Output



- Candidate matching scores

- Matched and missing skills

- Ranked candidate reports

- Screening recommendations for recruiter review

- CSV exports

- Audit records



## 8. Verified AI Model



Model: sentence-transformers/all-MiniLM-L6-v2



Execution device: CPU



Embedding dimensions: 384



Embedding test shape: (2, 384)



Relevant candidate cosine similarity: 0.8529



Unrelated candidate cosine similarity: 0.1811



Semantic matching test: PASSED



These results demonstrate basic semantic matching functionality and do not represent overall model accuracy.



## 9. Environment Verification



- Python 3.11.9: PASSED

- All 20 dependency imports: PASSED

- Dependency compatibility: PASSED

- SQLAlchemy database query: PASSED

- PyTorch tensor computation: PASSED

- AI embedding generation: PASSED

- Semantic matching: PASSED



## 10. Responsible AI and Security



- Use synthetic candidate data for development.

- Exclude protected personal characteristics from scoring.

- Evaluate potential bias and ranking consistency.

- Provide transparent scoring explanations.

- Retain human oversight of recruitment decisions.

- Protect candidate information.

- Maintain audit logs.

- Do not commit credentials or private resumes to GitHub.



## 11. Deployment Plan



The planned system will use a modular FastAPI backend, Next.js frontend, SQLite database and Docker-based deployment.



## 12. Project Status



Environment and AI model verification are completed.



The remaining architecture components will be implemented and tested through subsequent project milestones.


