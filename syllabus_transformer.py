import google.generativeai as genai
import json

API_KEY = "AIzaSyABC9koWOBHi00-aFW5rAbmp7snwnG6rFs"
genai.configure(api_key=API_KEY)

def extract_and_save_weights(syllabus_path):
    with open(syllabus_path, 'r') as f:
        syllabus_text = f.read()

    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"""
    Analyze this syllabus and extract grading categories and weights.
    Return ONLY a JSON object. Example: {{"Problem Sets": 0.50, "Final Project": 0.30}}
    Text: {syllabus_text}
    """

    response = model.generate_content(prompt)
    clean_json = response.text.strip().replace('```json', '').replace('```', '')

    try:
        weights = json.loads(clean_json)
        # Save to a file for the other script to use
        with open('weights.json', 'w') as f:
            json.dump(weights, f, indent=4)
        print("✅ Weights extracted and saved to weights.json")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    extract_and_save_weights('syllabus.txt')
