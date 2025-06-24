from django.shortcuts import render

# Create your views here.
from django.views.generic import TemplateView
from rest_framework import viewsets, status, generics, permissions
from rest_framework.response import Response
from django.db import transaction
from .models import JobPosition, Applicant, CVAnalysis
from .serializers import UserSerializer, JobPositionSerializer, ApplicantSerializer
from .services import extract_text_from_file, analyze_cv_with_gemini

class FrontendAppView(TemplateView):
    template_name = "cv_analyzer/index.html"

class RegisterView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

class JobPositionViewSet(viewsets.ModelViewSet):
    serializer_class = JobPositionSerializer

    def get_queryset(self):
        # Only show job positions created by the current logged-in user
        return JobPosition.objects.filter(created_by=self.request.user)

    def perform_create(self, serializer):
        # Automatically assign the current user when a job is created
        serializer.save(created_by=self.request.user)

class ApplicantViewSet(viewsets.ModelViewSet):
    serializer_class = ApplicantSerializer

    def get_queryset(self):
        # Users can only see applicants for jobs they created
        return Applicant.objects.filter(job_position__created_by=self.request.user)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        job_position_id = request.data.get('job_position')
        cv_file = request.FILES.get('cv_file')

        if not job_position_id or not cv_file:
            return Response({"error": "job_position and cv_file are required fields."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            job_position = JobPosition.objects.get(id=job_position_id, created_by=request.user)
        except JobPosition.DoesNotExist:
            return Response({"error": "Job Position not found or you do not have permission."}, status=status.HTTP_404_NOT_FOUND)

        # Create an applicant instance first to save the file
        applicant = Applicant.objects.create(job_position=job_position, cv_file=cv_file)

        try:
            # 1. Extract text from the saved file
            cv_text = extract_text_from_file(applicant.cv_file.path)
            if not cv_text:
                 raise Exception("Could not extract text from the CV file. It might be empty, corrupted, or an image-based PDF.")

            # 2. Call Gemini API for analysis
            analysis_json = analyze_cv_with_gemini(cv_text, job_position.description)
            if 'error' in analysis_json:
                raise Exception(analysis_json.get('details', 'Unknown AI error'))

            # 3. Update applicant details and create the analysis record
            basic_info = analysis_json.get('basic_info', {})
            applicant.full_name = basic_info.get('name', 'N/A')
            applicant.email = basic_info.get('email', 'N/A')
            applicant.phone = basic_info.get('phone', 'N/A')
            applicant.save()

            CVAnalysis.objects.create(
                applicant=applicant,
                raw_text=cv_text,
                scorecard=analysis_json,
                summary=analysis_json.get('final_assessment', {}).get('summary', 'No summary.')
            )

            serializer = self.get_serializer(applicant)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            # If any step fails, the transaction.atomic block will roll back, 
            # but we should still delete the applicant record with the file.
            applicant.delete() 
            return Response({"error": f"An error occurred during analysis: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
