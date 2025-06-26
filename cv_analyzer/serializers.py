from django.contrib.auth.models import User
from rest_framework import serializers
from .models import JobPosition, Applicant, CVAnalysis, QuizAttempt

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'is_staff']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user

class JobPositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobPosition
        fields = ['id', 'title', 'description', 'created_by', 'created_at']
        read_only_fields = ['created_by']

# Serializer for the quiz attempt results
class QuizAttemptSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizAttempt
        fields = ['score', 'total_questions']

# Serializer for the main CV analysis data
class CVAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = CVAnalysis
        fields = ['scorecard', 'summary', 'quiz_data']

# Main serializer for the Applicant model
class ApplicantSerializer(serializers.ModelSerializer):
    # Nest the analysis data within the applicant
    cvanalysis = CVAnalysisSerializer(read_only=True)
    # Nest the quiz attempt data (if it exists)
    quizattempt = QuizAttemptSerializer(read_only=True)
    # Include the username for easy display on the frontend
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    # This field provides the direct URL to the CV file for downloading
    cv_file = serializers.FileField(read_only=True)

    class Meta:
        model = Applicant
        fields = [
            'id', 'job_position', 'full_name', 'email', 'phone', 
            'analysis_status', 'uploaded_at', 'created_by_username',
            'cvanalysis', 'quizattempt', # Include the nested serializers
            'cv_file' # Add the file URL field
        ]
