Applicant Insight Engine
An intelligent, two-sided web application designed to streamline the recruitment process. This project uses the Google Gemini API to automatically analyze, score, and rank applicant CVs, and then generates a personalized technical quiz for each candidate.

The core mission is to save recruiters time, reduce bias, and provide deep, actionable insights into a candidate's suitability right from the first screening stage.

Features
Two-Sided Platform: Separate, tailored experiences for Admins/Hiring Managers and Applicants/Candidates.

Secure User Authentication: JWT-based registration and login for all users.

Job Position Management: Admins can create, view, and delete job positions.

AI-Powered CV Analysis: When a CV (.pdf or .docx) is uploaded, a background task is triggered to:

Automated Text Extraction: Parse the uploaded file to extract raw text.

Structured Scorecard Generation: Analyze the CV against the job description to generate a detailed JSON scorecard, evaluating:

Basic Information (Name, Contact, Location)

Work Experience & Career Progression

Education Background

Hard & Soft Skills Match

Potential Red Flags (e.g., job hopping, unexplained gaps)

Positive Indicators (e.g., side projects, leadership experience)

Interactive AI Quiz:

Automatically generates a 10-question multiple-choice quiz tailored to the specific skills found in the applicant's resume.

Applicants can take the quiz through an interactive, step-by-step modal.

Scores are automatically calculated and saved.

Dynamic Admin Dashboard:

View all applicants for a specific job, ranked by their overall AI score.

See key details at a glance: applicant name, uploader's username, quiz score, and CV score.

One-click access to download the original CV or view the full, detailed scorecard.

Asynchronous Processing: Uses Celery and Redis to run the time-consuming AI analysis in the background, ensuring the UI remains fast and responsive for the user.

Tech Stack
Backend: Django, Django REST Framework

Database: SQLite 3 (for development)

Asynchronous Tasks: Celery, Redis

Authentication: djangorestframework-simplejwt (JSON Web Tokens)

AI & Text Processing:

google-generativeai: Python SDK for the Google Gemini API

PyPDF2: For parsing PDF files

python-docx: For parsing DOCX files

Frontend: HTML, Tailwind CSS, Vanilla JavaScript (Single-Page Application architecture)

Setup and Installation
Follow these steps to get the project running locally on your machine.

Prerequisites
Python (3.8 or higher)

Redis (installed and running on its default port)

A Google Gemini API Key (get one from Google AI Studio)

1. Clone the Repository
git clone [https://github.com/your-username/applicant-insight-engine.git](https://github.com/your-username/applicant-insight-engine.git)
cd applicant-insight-engine

2. Create and Activate a Virtual Environment
On Windows:

python -m venv venv
.\venv\Scripts\activate

On macOS/Linux:

python3 -m venv venv
source venv/bin/activate

3. Install Dependencies
You will first need to create a requirements.txt file. In your activated virtual environment, run:

pip install Django djangorestframework djangorestframework-simplejwt celery[redis] google-generativeai python-dotenv PyPDF2 python-docx

Then, create the requirements file:

pip freeze > requirements.txt

4. Set Up Environment Variables
Create a file named .env in the project root and add your Gemini API key:

# .env
GEMINI_API_KEY=YOUR_GEMINI_API_KEY_HERE

5. Run Database Migrations
Apply the database schema:

python manage.py makemigrations
python manage.py migrate

6. Create a Superuser (Admin)
This will allow you to access the Django admin panel at /admin/ and create jobs in the web app.

python manage.py createsuperuser

Follow the prompts to create your admin account.

How to Run
Start the Redis Server: Make sure your Redis server is running in the background.

Start the Celery Worker: Open a new terminal, activate your virtual environment, and run:

celery -A core worker -l info

Start the Django Server: Open another new terminal, activate your virtual environment, and run:

python manage.py runserver

Access the Application:
Open your web browser and navigate to:
http://127.0.0.1:8000/

You can now register new user accounts (for applicants) and log in with your superuser account (for admins) to create jobs and review candidates.

API Endpoints
Method

Endpoint

Description

Auth Required

POST

/api/register/

Create a new user account.

None

POST

/api/token/

Obtain JWT access and refresh tokens.

None

GET

/api/users/me/

Get details for the logged-in user.

Access Token

GET, POST

/api/jobs/

Get a list of all jobs or create a new one.

Access Token

GET, POST

/api/applicants/

Get applicants for a job or upload a new CV.

Access Token

GET

/api/applicants/<id>/quiz/

Fetch the AI-generated quiz for an applicant.

Access Token

POST

/api/applicants/<id>/submit-quiz/

Submit the applicant's answers and get the score.

Access Token

