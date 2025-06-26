import hashlib
from .tasks import process_cv_analysis
from django.views.generic import TemplateView
from rest_framework import viewsets, status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import PermissionDenied, NotFound
from .models import JobPosition, Applicant, CVAnalysis, QuizAttempt
from .serializers import UserSerializer, JobPositionSerializer, ApplicantSerializer

class FrontendAppView(TemplateView):
    """
    Serves the main index.html file as the frontend application.
    """
    template_name = "index.html"

class RegisterView(generics.CreateAPIView):
    """
    Allows any new user to register for an account.
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

class CurrentUserView(APIView):
    """
    Determines the current user by their token and return their data.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

class JobPositionViewSet(viewsets.ModelViewSet):
    """
    Handles creating, listing, and managing Job Positions.
    """
    serializer_class = JobPositionSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = JobPosition.objects.all().order_by('-created_at')

    def perform_create(self, serializer):
        if not self.request.user.is_staff:
            raise PermissionDenied("You do not have permission to create a job position.")
        serializer.save(created_by=self.request.user)

class ApplicantViewSet(viewsets.ModelViewSet):
    """
    Handles creating, listing, and downloading Applicant CVs.
    """
    serializer_class = ApplicantSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        job_position_id = self.request.query_params.get('job_position')
        # Use prefetch_related for one-to-one reverse lookups to optimize performance
        base_queryset = Applicant.objects.all().select_related(
            'cvanalysis', 'created_by'
        ).prefetch_related('quizattempt')

        if user.is_staff:
            queryset = base_queryset
        else:
            queryset = base_queryset.filter(created_by=user)
        
        if job_position_id:
            queryset = queryset.filter(job_position_id=job_position_id)
        
        return queryset.order_by('-uploaded_at')

    def create(self, request, *args, **kwargs):
        job_position_id = request.data.get('job_position')
        cv_file = request.FILES.get('cv_file')

        if not job_position_id or not cv_file:
            return Response({"error": "job_position and cv_file are required fields."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            job_position = JobPosition.objects.get(id=job_position_id)
        except JobPosition.DoesNotExist:
            return Response({"error": "Job Position not found."}, status=status.HTTP_404_NOT_FOUND)

        file_content = cv_file.read()
        cv_hash = hashlib.sha256(file_content).hexdigest()
        cv_file.seek(0) 

        if Applicant.objects.filter(job_position=job_position, cv_hash=cv_hash).exists():
            return Response({"error": "This CV has already been submitted for this job."}, status=status.HTTP_409_CONFLICT)

        applicant = Applicant.objects.create(
            job_position=job_position, 
            cv_file=cv_file,
            cv_hash=cv_hash,
            analysis_status='PENDING',
            created_by=request.user
        )
        process_cv_analysis.delay(applicant.id)
        serializer = self.get_serializer(applicant)
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

class ApplicantQuizView(APIView):
    """
    A view to retrieve the AI-generated quiz questions for an applicant.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk, format=None):
        try:
            applicant = Applicant.objects.get(pk=pk)
            analysis = CVAnalysis.objects.get(applicant=applicant)
        except (Applicant.DoesNotExist, CVAnalysis.DoesNotExist):
            raise NotFound("Applicant or analysis data not found.")

        if not (request.user.is_staff or applicant.created_by == request.user):
            raise PermissionDenied("You do not have permission to view this quiz.")
        
        if applicant.analysis_status != 'COMPLETED' or not analysis.quiz_data or 'questions' not in analysis.quiz_data:
            return Response({"detail": "Quiz is not ready yet."}, status=status.HTTP_202_ACCEPTED)
        
        # Remove correct answers before sending to the user
        quiz_for_user = analysis.quiz_data.copy()
        for question in quiz_for_user.get('questions', []):
            question.pop('correct_answer', None)
            
        return Response(quiz_for_user)

class SubmitQuizView(APIView):
    """
    A view to submit quiz answers and calculate the score.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk, format=None):
        try:
            applicant = Applicant.objects.get(pk=pk)
            analysis = CVAnalysis.objects.get(applicant=applicant)
        except (Applicant.DoesNotExist, CVAnalysis.DoesNotExist):
            raise NotFound("Applicant or analysis data not found.")

        if applicant.created_by != request.user:
            raise PermissionDenied("You cannot submit a quiz for another user.")

        if QuizAttempt.objects.filter(applicant=applicant).exists():
            return Response({"detail": "You have already submitted this quiz."}, status=status.HTTP_400_BAD_REQUEST)

        user_answers = request.data.get('answers', {})
        correct_questions = analysis.quiz_data.get('questions', [])
        
        score = 0
        total_questions = len(correct_questions)

        for i, question_data in enumerate(correct_questions):
            user_answer = user_answers.get(str(i))
            correct_answer = question_data.get('correct_answer')
            if user_answer and user_answer == correct_answer:
                score += 1
        
        attempt = QuizAttempt.objects.create(
            applicant=applicant,
            answers=user_answers,
            score=score,
            total_questions=total_questions
        )

        return Response({
            "score": attempt.score,
            "total_questions": attempt.total_questions
        }, status=status.HTTP_201_CREATED)
