from pathlib import Path
import json
import pdfplumber
from docx import Document


def extract_text_from_json(file_path):
    """Extract text from a structured JSON resume."""
    try:
        with open(file_path, "r", encoding="utf-8-sig") as file:
            data = json.load(file)

        if not isinstance(data, dict):
            raise ValueError("JSON resume must be an object.")

        extracted_text = []

        for key, value in data.items():
            if value is None:
                continue

            if isinstance(value, list):
                value = ", ".join(str(item) for item in value)

            elif isinstance(value, dict):
                value = json.dumps(value, ensure_ascii=False)

            else:
                value = str(value)

            if value.strip():
                label = key.replace("_", " ").title()
                extracted_text.append(f"{label}: {value}")

        return "\n".join(extracted_text)

    except (OSError, ValueError, UnicodeError) as error:
        print(f"JSON Error: {error}")
        return ""


def extract_text_from_txt(file_path):
    """Extract text from a TXT resume."""
    try:
        with open(file_path, "r", encoding="utf-8-sig") as file:
            return file.read().strip()

    except (OSError, UnicodeError) as error:
        print(f"TXT Error: {error}")
        return ""


def extract_text_from_docx(file_path):
    """Extract text from DOCX paragraphs and tables."""
    try:
        from docx.oxml.ns import qn
        from docx.text.paragraph import Paragraph
        from docx.table import Table

        document = Document(file_path)
        extracted_text = []

        # Preserve the order of paragraphs and tables.
        for element in document.element.body.iterchildren():

            if element.tag == qn("w:p"):
                paragraph = Paragraph(element, document)
                text = paragraph.text.strip()

                if text:
                    extracted_text.append(text)

            elif element.tag == qn("w:tbl"):
                table = Table(element, document)

                for row in table.rows:
                    for cell in row.cells:
                        text = cell.text.strip()

                        if text:
                            extracted_text.append(text)

        return "\n".join(extracted_text)

    except Exception as error:
        print(f"DOCX Error: {error}")
        return ""


def extract_text_from_pdf(file_path):
    """Extract text from a PDF resume."""
    try:
        pages = []

        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()

                if text:
                    pages.append(text.strip())

        return "\n".join(pages)

    except Exception as error:
        print(f"PDF Error: {error}")
        return ""


def extract_resume_text(file_path):
    """Automatically extract text based on the resume format."""
    path = Path(file_path)

    extension = path.suffix.lower()

    if extension == ".txt":
        return extract_text_from_txt(path)

    elif extension == ".docx":
        return extract_text_from_docx(path)

    elif extension == ".pdf":
        return extract_text_from_pdf(path)

    elif extension == ".json":
        return extract_text_from_json(path)

    else:
        print(f"Unsupported file format: {extension}")
        return ""


if __name__ == "__main__":
    resume_folder = Path("resumes")

    supported_extensions = {
        ".txt",
        ".docx",
        ".pdf",
        ".json"
    }

    resume_files = sorted(
        file_path
        for file_path in resume_folder.rglob("*")
        if file_path.is_file()
        and file_path.suffix.lower() in supported_extensions
    )

    print("===== AUTOMATED RESUME PARSER TEST =====")
    print(f"Total resume files found: {len(resume_files)}")

    successful = 0
    failed = 0

    for file_path in resume_files:
        print(f"\nTesting: {file_path.name}")

        extracted_text = extract_resume_text(file_path)

        if extracted_text.strip():
            successful += 1
            print("Status: SUCCESS")
            print(f"Characters extracted: {len(extracted_text)}")
            print(f"Preview: {extracted_text[:80]}")

        else:
            failed += 1
            print("Status: FAILED")

    print("\n===== FINAL TEST SUMMARY =====")
    print(f"Total files: {len(resume_files)}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
