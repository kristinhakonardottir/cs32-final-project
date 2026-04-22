import google.generativeai as genai
import json
import os

# You can get a free API key at https://aistudio.google.com/
# For now, we will assume it's stored in an environment variable or a string
API_KEY = "YOUR_API_KEY_HERE"
genai.configure(api_key=API_KEY)

def extract_weights(syllabus_text):
    """
    Uses a Gemini Transformer model to extract grading weights.
    """
    model = genai.GenerativeModel('gemini-1.5-flash')

    prompt = f"""
    You are a specialized academic data extractor.
    Analyze this syllabus text and extract the grading categories and their weights.
    Return ONLY a raw JSON object where keys are the category names and
    values are decimals (e.g., 0.25 for 25%).

    SYLLABUS TEXT:
    {syllabus_text}
    """

    response = model.generate_content(prompt)

    # Clean the response text (remove markdown backticks if present)
    clean_json = response.text.strip().replace('```json', '').replace('```', '')

    try:
        return json.loads(clean_json)
    except Exception as e:
        print(f"Error parsing AI response: {e}")
        return {}
