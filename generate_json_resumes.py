from pathlib import Path
import json

resume_folder = Path("resumes")
txt_files = sorted(resume_folder.rglob("candidate_*.txt"))

assert len(txt_files) == 5, "Expected five TXT resumes."

created = 0

for txt_file in txt_files:
    text = txt_file.read_text(encoding="utf-8-sig")
    candidate = {}

    for line in text.splitlines():
        if ":" not in line:
            continue

        key, value = line.split(":", 1)
        key = key.strip().lower().replace(" ", "_")
        value = value.strip()

        if key in ("skills", "projects"):
            candidate[key] = [
                item.strip()
                for item in value.split(",")
                if item.strip()
            ]
        else:
            candidate[key] = value

    json_file = txt_file.with_suffix(".json")

    json_file.write_text(
        json.dumps(candidate, indent=4, ensure_ascii=False),
        encoding="utf-8"
    )

    created += 1
    print(f"CREATED: {json_file.name}")

print("\n===== JSON GENERATION SUMMARY =====")
print(f"JSON resumes created: {created}")

assert created == 5
print("ALL FIVE JSON RESUMES CREATED SUCCESSFULLY")