import csv
import os
import re

from database import SessionLocal
from models import Survey

CSV_FILE = r"D:\Survey App\video_survey_scripts.csv"


def make_slug(text, index):
    base = re.sub(r'[^a-zA-Z0-9]+', '-', text.lower()).strip('-')
    return f"{base[:60]}-{index}"


def import_surveys():
    db = SessionLocal()

    print("📂 FILE:", CSV_FILE)
    print("✔ EXISTS:", os.path.exists(CSV_FILE))

    with open(CSV_FILE, newline='', encoding='utf-8-sig') as file:
        reader = csv.DictReader(file)

        inserted = 0
        skipped = 0

        for i, row in enumerate(reader, start=1):

            question = row.get("question")
            video_id = row.get("video_id")

            if not question:
                skipped += 1
                continue

            slug = make_slug(question, i)

            exists = db.query(Survey).filter(Survey.slug == slug).first()
            if exists:
                skipped += 1
                continue

            db.add(Survey(
                video_id=video_id,
                question=question,
                slug=slug
            ))

            inserted += 1

        db.commit()
        db.close()

        print("\n======================")
        print("✅ INSERTED:", inserted)
        print("⏩ SKIPPED:", skipped)
        print("======================")


if __name__ == "__main__":
    import_surveys()