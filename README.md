# Automated Resume Screening Tool



A Python-based resume screening application that extracts candidate information, compares resumes against job requirements, calculates matching scores, ranks candidates, and generates screening reports.



The project includes a Streamlit dashboard and a command-line application.



## Project Overview



The Automated Resume Screening Tool demonstrates how Python can help automate repetitive tasks in the recruitment process.



The application processes sample resumes, identifies candidate skills and experience, compares them with job descriptions, and generates structured screening results.



**Project Type:** Python Automation / HR Technology / Resume Screening



**Purpose:** Educational and portfolio project using synthetic candidate data.



## Key Features



\- Resume text extraction from PDF, DOCX, and TXT files

\- Candidate information extraction

\- Job description parsing

\- Required and preferred skills matching

\- Experience matching

\- Weighted candidate scoring

\- Candidate ranking

\- Automatic shortlisting classification

\- Interactive Streamlit dashboard

\- Multiple resume uploads

\- CSV and JSON report downloads

\- Command-line execution



## Technologies Used



\- Python

\- Streamlit

\- pdfplumber

\- python-docx

\- Pandas

\- NumPy

\- CSV and JSON



## Candidate Matching Method



The application calculates a weighted matching score using three components:



| Criteria | Weight |

|---|---|

| Required Skills | 60% |

| Preferred Skills | 20% |

| Experience | 20% |



Candidates are classified into:



\- **Highly Matched:** 80% or higher

\- **Moderately Matched:** 60% to below 80%

\- **Low Match:** Below 60%

\- **Insufficient Data:** When a score cannot be calculated



These scores are demonstration heuristics and should not be treated as objective measures of candidate suitability.



## Installation



### 1. Clone the repository



```bash

git clone https://github.com/YOUR\_USERNAME/Automated-Resume-Screening-Tool.git

cd Automated-Resume-Screening-Tool

```



Replace `YOUR\_USERNAME` with your GitHub username after creating the repository.



### 2. Create a virtual environment



```bash

python -m venv venv

```



### 3. Activate the virtual environment



On Windows Command Prompt:



```cmd

venv\\Scripts\\activate

```



### 4. Install dependencies



```bash

python -m pip install -r requirements.txt

```



## Running the Application



### Streamlit Dashboard



```bash

python -m streamlit run app.py

```



Upload sample resumes, select a job description, and review the candidate matching results.



### Command-Line Application



```bash

python main.py

```



This processes the sample resumes and generates screening reports.



## Screening Reports



The Streamlit application supports downloading:



\- JSON reports containing detailed candidate screening results

\- CSV reports containing candidate ranks, names, scores, and classifications



The command-line application also generates reports in the `reports` directory.



## Sample Data



The project uses synthetic resumes and example job descriptions for demonstration and testing.



No real applicant tracking system or private recruitment database is required.



## Project Limitations



\- Matching is primarily based on extracted information and predefined scoring rules.

\- Resume formatting can affect text extraction accuracy.

\- Scores do not independently establish a candidate's qualifications or suitability.

\- The application is a demonstration project, not a production hiring decision system.

\- Human review is necessary before making recruitment decisions.



## Future Improvements



\- More advanced natural language processing

\- Semantic similarity matching

\- Improved resume formatting support

\- Additional job descriptions

\- Interactive analytics and visualizations

\- Automated testing

\- Improved error handling



## Project Goal



This project demonstrates practical Python programming skills, file processing, automation, data extraction, rule-based matching, report generation, and interactive dashboard development.



It is intended as a portfolio project for Python development, data analysis, automation, and HR technology opportunities.



## Author



Python Student Project



## License



No license has been selected yet.

