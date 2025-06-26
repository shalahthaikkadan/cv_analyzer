from celery import shared_task
from .models import Applicant, CVAnalysis
from .services import extract_text_from_file, analyze_cv_with_gemini, generate_quiz_with_gemini

@shared_task
def process_cv_analysis(applicant_id):
    """
    A Celery task to process a CV: extract text, generate a scorecard,
    and generate a personalized MCQ quiz.
    """
    try:
        applicant = Applicant.objects.get(id=applicant_id)
        applicant.analysis_status = 'PROCESSING'
        applicant.save()

        job_position = applicant.job_position
        file_path = applicant.cv_file.path

        raw_text = extract_text_from_file(file_path)
        if not raw_text:
            raise ValueError("Failed to extract text from the CV file.")

        # Generate Scorecard
        scorecard_data = analyze_cv_with_gemini(raw_text, job_position.description)
        if 'error' in scorecard_data:
             print(f"SCORECARD GENERATION FAILED for applicant {applicant_id}: {scorecard_data.get('details')}")
             raise ValueError(f"Scorecard generation failed: {scorecard_data.get('details')}")

        # Generate MCQ Quiz
        quiz_data = generate_quiz_with_gemini(raw_text, job_position.description)
        if 'error' in quiz_data:
            print(f"QUIZ GENERATION FAILED for applicant {applicant_id}: {quiz_data.get('details')}")
            quiz_data = None

        applicant.full_name = scorecard_data.get('basic_info', {}).get('name', 'N/A')
        applicant.email = scorecard_data.get('basic_info', {}).get('email', 'N/A')
        applicant.phone = scorecard_data.get('basic_info', {}).get('phone', 'N/A')
        
        CVAnalysis.objects.update_or_create(
            applicant=applicant,
            defaults={
                'raw_text': raw_text,
                'scorecard': scorecard_data,
                'summary': scorecard_data.get('final_assessment', {}).get('summary', 'No summary provided.'),
                'quiz_data': quiz_data, # Save the generated quiz
            }
        )

        applicant.analysis_status = 'COMPLETED'
        applicant.save()
        print(f"Successfully processed CV for applicant {applicant_id}")

    except Exception as e:
        print(f"CRITICAL ERROR in Celery task for applicant {applicant_id}: {e}")
        try:
            applicant_to_fail = Applicant.objects.get(id=applicant_id)
            applicant_to_fail.analysis_status = 'FAILED'
            applicant_to_fail.save()
        except Applicant.DoesNotExist:
            print(f"Applicant {applicant_id} no longer exists.")
