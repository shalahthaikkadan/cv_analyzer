from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User

class JobPosition(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Applicant(models.Model):
    job_position = models.ForeignKey(JobPosition, related_name='applicants', on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    cv_file = models.FileField(upload_to='cvs/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name or 'New Applicant'} for {self.job_position.title}"

class CVAnalysis(models.Model):
    applicant = models.OneToOneField(Applicant, on_delete=models.CASCADE, primary_key=True)
    raw_text = models.TextField(blank=True, null=True)
    scorecard = models.JSONField() # Stores structured JSON from Gemini
    summary = models.TextField()
    analyzed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Analysis for {self.applicant.full_name}"