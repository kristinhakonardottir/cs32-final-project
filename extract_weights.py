import os
from google import genai
from google.genai import types
import json
import csv

# 1. SETUP
client = genai.Client(api_key="YOUR_GEMINI_API_KEY")
MODEL_ID = "gemini-3-flash-preview"

def extract_syllabus_weights(file_path):
    # 2. UPLOAD FILE
    print("Uploading syllabus...")
    syllabus_file = client.files.upload(path=file_path)

    # 3. CONFIGURE PROMPT (Requesting Structured JSON)
    prompt = """
    Read this syllabus and extract every assignment, exam, or participation category.
    Return a JSON list of objects. Each object MUST have:
    - "name": The name of the assignment/category.
    - "weight": The percentage (as a number, e.g., 15 for 15%).
    - "count": How many of these assignments exist (if mentioned).

    Example format: [{"name": "Homework", "weight": 20, "count": 10}]
    """

    # 4. GENERATE CONTENT
    response = client.models.generate_content(
        model=MODEL_ID,
        contents=[syllabus_file, prompt],
        config=types.GenerateContentConfig(
            response_mime_type="application/json"
        )
    )

    # 5. PARSE & CALCULATE
    data = json.loads(response.text)

    total_weight = sum(item['weight'] for item in data)
    print(f"Total Weight Extracted: {total_weight}%")

    # 6. EXPORT TO CSV
    with open('grades_structure.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["name", "weight", "count"])
        writer.writeheader()
        writer.writerows(data)

    print("Exported to grades_structure.csv")

if __name__ == "__main__":
    extract_syllabus_weights("syllabus.pdf")
