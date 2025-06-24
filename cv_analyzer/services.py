import os
import google.generativeai as genai
from dotenv import load_dotenv
import PyPDF2
import docx
import json

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

def extract_text_from_file(file_path):
    """Extracts text from a given PDF or DOCX file."""
    text = ""
    if file_path.lower().endswith('.pdf'):
        try:
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for page in reader.pages:
                    text += page.extract_text()
        except Exception as e:
            print(f"Error reading PDF {file_path}: {e}")
    elif file_path.lower().endswith('.docx'):
        try:
            doc = docx.Document(file_path)
            for para in doc.paragraphs:
                text += para.text + "\n"
        except Exception as e:
            print(f"Error reading DOCX {file_path}: {e}")
    return text

def generate_scorecard_prompt(cv_text, job_description):
    """Creates the detailed prompt for the Gemini API."""
    return f"""
    **Role:** You are an expert HR Analyst AI. Analyze the CV against the job description and generate a detailed scorecard in a single, valid JSON object format. Do not add any text before or after the JSON.

    **CV Text:**
    ---
    {cv_text}
    ---

    **Job Description:**
    ---
    {job_description}
    ---

    **Required JSON Output Format:**
    {{
        "basic_info": {{"name": "string", "email": "string", "phone": "string", "linkedin": "string_or_null", "location": "string"}},
        "work_experience": {{"total_years": "integer", "roles": [{{"title": "string", "company": "string", "duration_months": "integer"}}], "progression": "string", "job_hopping_flag": "boolean", "score": "integer_1_to_10"}},
        "education": {{"highest_degree": "string", "field_of_study": "string", "institution_tier": "string", "score": "integer_1_to_10"}},
        "skills_analysis": {{"hard_skills_match": ["skill1"], "soft_skills_match": ["skill1"], "certifications": ["cert1"], "score": "integer_1_to_10"}},
        "red_flags": [{{"flag": "string", "details": "string"}}],
        "positive_indicators": [{{"indicator": "string", "details": "string"}}],
        "final_assessment": {{"overall_score": "integer_1_to_100", "summary": "string", "cultural_fit_notes": "string"}}
    }}
    """

def analyze_cv_with_gemini(cv_text, job_description):
    """Sends the request to Gemini and gets the structured scorecard."""
    prompt = generate_scorecard_prompt(cv_text, job_description)
    try:
        response = model.generate_content(prompt)
        # Clean the response to ensure it's valid JSON
        json_response_text = response.text.strip().replace("```json", "").replace("```", "")
        return json.loads(json_response_text)
    except Exception as e:
        print(f"Error communicating with Gemini API or parsing JSON: {e}")
        return {{"error": "Failed to analyze CV with AI", "details": str(e)}}
