import os
import google.generativeai as genai
from dotenv import load_dotenv
import PyPDF2
import docx
import json

load_dotenv()
# Ensure you have a valid GEMINI_API_KEY in your .env file
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
    """Creates the detailed prompt for the Gemini API to generate a scorecard."""
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
        json_response_text = response.text.strip().replace("```json", "").replace("```", "")
        return json.loads(json_response_text)
    except Exception as e:
        print(f"Error communicating with Gemini API for scorecard: {e}")
        return {{"error": "Failed to analyze CV with AI", "details": str(e)}}

# --- NEW: PROMPT AND FUNCTION FOR MCQ QUIZ ---

def generate_mcq_quiz_prompt(cv_text, job_description):
    """
    Creates a detailed prompt for the Gemini API to generate a multiple-choice quiz.
    """
    return f"""
    **Role:** You are an expert technical interviewer and skills assessor AI. Your task is to create a challenging 10-question multiple-choice quiz to screen a job applicant.

    **Context:**
    1.  **Candidate's CV Text:**
        ---
        {cv_text}
        ---
    2.  **Job Description:**
        ---
        {job_description}
        ---

    **Task:**
    Generate exactly 10 multiple-choice questions based *only* on the skills, technologies, and experiences mentioned in the CV and required by the job description. The questions should test the applicant's practical and theoretical knowledge.

    **Instructions:**
    - **Relevance is Key:** Each question must be directly relevant to a skill in the CV (e.g., Python, Django, Cybersecurity principles, specific tools).
    - **Plausible Distractors:** For each question, provide four options (A, B, C, D). One option must be the correct answer, and the other three must be plausible but incorrect distractors.
    - **Specify Correct Answer:** Clearly indicate which option is the correct one.
    - **Strict JSON Output:** You MUST return ONLY a single, valid JSON object. Do not include any text, notes, or markdown formatting like ```json before or after the JSON object.

    **Required JSON Structure:**
    {{
      "quiz_title": "Technical Screening for [Job Title]",
      "questions": [
        {{
          "question_text": "In Python, what is the primary difference between a list and a tuple?",
          "options": {{
            "A": "Lists are mutable, while tuples are immutable.",
            "B": "Tuples can store mixed data types, while lists cannot.",
            "C": "Lists are faster for lookup operations than tuples.",
            "D": "Lists use parentheses, while tuples use square brackets."
          }},
          "correct_answer": "A"
        }},
        {{
          "question_text": "Based on your experience with Django REST Framework listed on your CV, which class would you use to quickly create a set of CRUD API endpoints for a model?",
          "options": {{
            "A": "APIView",
            "B": "GenericAPIView",
            "C": "ViewSet",
            "D": "ModelViewSet"
          }},
          "correct_answer": "D"
        }}
      ]
    }}
    """

def generate_quiz_with_gemini(cv_text, job_description):
    """Sends the request to Gemini and gets the structured MCQ quiz."""
    prompt = generate_mcq_quiz_prompt(cv_text, job_description)
    try:
        response = model.generate_content(prompt)
        json_response_text = response.text.strip().replace("```json", "").replace("```", "")
        return json.loads(json_response_text)
    except Exception as e:
        print(f"Error communicating with Gemini API for quiz: {e}")
        return {{"error": "Failed to generate quiz with AI", "details": str(e)}}
