from django.db import models
from django.contrib.auth.models import User
import os

class JobPosition(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
    def delete(self, *args, **kwargs):
        for applicant in self.applicants.all():
            applicant.delete()
        super(JobPosition, self).delete(*args, **kwargs)

class Applicant(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ]

    job_position = models.ForeignKey(JobPosition, related_name='applicants', on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    cv_file = models.FileField(upload_to='cvs/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    analysis_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    cv_hash = models.CharField(max_length=64, blank=True, null=True, db_index=True)
    created_by = models.ForeignKey(User, related_name='uploaded_applicants', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.full_name or 'New Applicant'} for {self.job_position.title}"

    def delete(self, *args, **kwargs):
        if self.cv_file:
            if os.path.isfile(self.cv_file.path):
                os.remove(self.cv_file.path)
        super(Applicant, self).delete(*args, **kwargs)

class CVAnalysis(models.Model):
    applicant = models.OneToOneField(Applicant, on_delete=models.CASCADE, primary_key=True)
    raw_text = models.TextField(blank=True, null=True)
    scorecard = models.JSONField()
    # This field will now store the quiz questions and correct answers
    quiz_data = models.JSONField(blank=True, null=True)
    summary = models.TextField()
    analyzed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Analysis for {self.applicant.full_name}"

# --- NEW: MODEL TO STORE QUIZ ATTEMPTS AND SCORES ---
class QuizAttempt(models.Model):
    applicant = models.OneToOneField(Applicant, on_delete=models.CASCADE)
    # Stores the user's selected answers, e.g., {"0": "A", "1": "D"}
    answers = models.JSONField()
    score = models.IntegerField()
    total_questions = models.IntegerField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Quiz Attempt for {self.applicant.full_name} - Score: {self.score}/{self.total_questions}"
