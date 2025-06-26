# Applicant Insight Engine

An intelligent HR tool designed to streamline the recruitment process by automatically analyzing, scoring, and providing insights on applicant CVs. This project leverages the Google Gemini API to extract structured data from resumes and score them against a given job description.

## Features

* **Secure User Authentication**: JWT-based authentication for employers (login, register).
* **Job Position Management**: Employers can create, view, update, and delete job positions.
* **AI-Powered CV Analysis**: Upload a CV (`.pdf` or `.docx`) for a specific job.
* **Automated Text Extraction**: Parses uploaded files to extract raw text for analysis.
* **Structured Scorecard Generation**: The Gemini API analyzes the CV against the job description and returns a detailed JSON scorecard, evaluating:
    * Basic Information (Name, Contact, Location)
    * Work Experience & Career Progression
    * Education Background
    * Hard & Soft Skills Match
    * Potential Red Flags (e.g., job hopping)
    * Positive Indicators (e.g., side projects, leadership)
* **Dynamic Frontend**: A single-page application built with HTML, Tailwind CSS, and vanilla JavaScript to interact with the backend API.
* **Admin Interface**: A built-in Django admin panel for easy data management and debugging.

## Tech Stack

* **Backend**: Django, Django REST Framework
* **Database**: SQLite 3 (for development)
* **Authentication**: djangorestframework-simplejwt (JSON Web Tokens)
* **AI & Text Processing**:
    * `google-generativeai`: Python SDK for the Google Gemini API
    * `PyPDF2`: For parsing PDF files
    * `python-docx`: For parsing DOCX files
* **Frontend**: HTML, Tailwind CSS, Vanilla JavaScript

---

## Setup and Installation

Follow these steps to get the project running locally on your machine.

### Prerequisites

* Python (3.8 or higher)
* A Google Gemini API Key (get one from [Google AI Studio](https://aistudio.google.com/app/apikey))

### 1. Clone the Repository

```bash
git clone [https://github.com/your-username/applicant-insight-engine.git](https://github.com/your-username/applicant-insight-engine.git)
cd applicant-insight-engine
```

### 2. Create and Activate a Virtual Environment

* **On Windows:**
    ```bash
    python -m venv venv
    .\venv\Scripts\activate
    ```
* **On macOS/Linux:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```
*(Note: You will need to create a `requirements.txt` file first using `pip freeze > requirements.txt`)*

### 4. Set Up Environment Variables

Create a file named `.env` in the project root and add your Gemini API key:

```
# .env
GEMINI_API_KEY="YOUR_GEMINI_API_KEY_HERE"
```

### 5. Run Database Migrations

Apply the database schema:

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create a Superuser

This will allow you to access the Django admin panel at `/admin/`.

```bash
python manage.py createsuperuser
```

---

## How to Run

1.  **Start the Django Server:**
    ```bash
    python manage.py runserver
    ```

2.  **Access the Application:**
    Open your web browser and navigate to:
    `http://127.0.0.1:8000/`

You can now register an account, create jobs, and upload CVs through the web interface.

## API Endpoints

The frontend communicates with the following backend API endpoints:

| Method | Endpoint                | Description                                        | Authentication |
| :----- | :---------------------- | :------------------------------------------------- | :------------- |
| `POST` | `/api/register/`        | Create a new user account.                         | None           |
| `POST` | `/api/token/`           | Obtain JWT access and refresh tokens.              | None           |
| `POST` | `/api/token/refresh/`   | Refresh an expired access token.                   | Refresh Token  |
| `GET`  | `/api/jobs/`            | Get a list of jobs created by the logged-in user.  | Access Token   |
| `POST` | `/api/jobs/`            | Create a new job position.                         | Access Token   |
| `GET`  | `/api/applicants/`      | Get a list of applicants for the user's jobs.      | Access Token   |
| `POST` | `/api/applicants/`      | Upload a CV for a specific job position and analyze it. | Access Token   |

## Future Improvements

* **Background Task Processing**: Implement **Celery** and **Redis** to handle CV analysis asynchronously, preventing API timeouts and improving user experience.
* **Enhanced Frontend**: Build a more robust frontend with a framework like **React** or **Vue.js** for better state management and component-based architecture.
* **Advanced Filtering**: Add capabilities to search and filter applicants based on scorecard data (e.g., overall score, specific skills).
* **Cloud Storage**: Integrate **Amazon S3** or **Google Cloud Storage** for production-ready media file handling.
* **Production Deployment**: Containerize the application with **Docker** and deploy using a production-grade setup with **Gunicorn** and **Nginx**.
