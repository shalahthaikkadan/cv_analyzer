from django.contrib.auth.models import User
from rest_framework import serializers
from .models import JobPosition, Applicant, CVAnalysis

# Serializer for User Registration
class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        return user

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'first_name', 'last_name')

# Serializer for the CV Analysis data
class CVAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = CVAnalysis
        fields = '__all__'

# Serializer for Applicants, which includes the nested analysis
class ApplicantSerializer(serializers.ModelSerializer):
    scorecard_data = CVAnalysisSerializer(read_only=True, source='cvanalysis')

    class Meta:
        model = Applicant
        fields = ['id', 'job_position', 'full_name', 'email', 'phone', 'cv_file', 'uploaded_at', 'scorecard_data']
        read_only_fields = ['full_name', 'email', 'phone'] 

# Serializer for Job Positions, which includes nested applicants
class JobPositionSerializer(serializers.ModelSerializer):
    applicants = ApplicantSerializer(many=True, read_only=True)

    class Meta:
        model = JobPosition
        fields = ['id', 'title', 'description', 'created_by', 'created_at', 'applicants']
        read_only_fields = ['created_by']
