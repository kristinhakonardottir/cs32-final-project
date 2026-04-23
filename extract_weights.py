import os
import json
import csv
from google import genai
from google.genai import types

def extract_syllabus_data():
    # --- 1. SECURE AUTHENTICATION ---
    # This pulls the secret you saved in GitHub Settings
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        print("❌ Error: GEMINI_API_KEY not found in environment.")
        return

    client = genai.Client(api_key=api_key)
    model_id = "gemini-1.5-flash-002" # High-speed model with native PDF support

    # --- 2. UPLOAD SYLLABUS ---
    # Ensure your syllabus file is named 'syllabus.pdf' in your folder
    file_path = "syllabus.pdf"
    if not os.path.exists(file_path):
        print(f"❌ Error: {file_path} not found in the current folder.")
        return

    print(f"📤 Uploading {file_path} to Google AI...")
    syllabus_upload = client.files.upload(file=file_path)

    # --- 3. THE SMART PROMPT ---
    prompt = """
    Analyze this syllabus and extract the grading criteria.
    Return a JSON list of objects. Each object must have:
    - 'category': The name of the assignment or category (e.g., 'Midterm', 'Homework').
    - 'weight': The percentage as a number (e.g., 25 for 25%).

    If the weight is for a group of items (e.g., '10 Quizzes = 20%'),
    list the category as 'Quizzes' and weight as 20.
    """

    # --- 4. GENERATE STRUCTURED DATA ---
    print("🧠 Extracting weights...")
    response = client.models.generate_content(
        model=model_id,
        contents=[syllabus_upload, prompt],
        config=types.GenerateContentConfig(
            response_mime_type="application/json"
        )
    )

    # Convert the AI string response into a Python list
    grading_data = json.loads(response.text)

    # --- 5. CALCULATE TOTAL & EXPORT ---
    total_weight = sum(item['weight'] for item in grading_data)

    # Save to CSV
    output_file = "grade_weights.csv"
    with open(output_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["category", "weight"])
        writer.writeheader()
        writer.writerows(grading_data)

    print("-" * 30)
    print(f"✅ Success! Data saved to {output_file}")
    print(f"📊 Total weight calculated: {total_weight}%")

    if total_weight != 100:
        print("⚠️ Warning: Total weight does not equal 100%. Check the syllabus for extra credit or missing categories.")
    print("-" * 30)

if __name__ == "__main__":
    extract_syllabus_data()
