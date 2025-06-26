from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    JobPositionViewSet,
    ApplicantViewSet,
    RegisterView,
    CurrentUserView,
    ApplicantQuizView,
    SubmitQuizView,
)

router = DefaultRouter()
router.register(r'jobs', JobPositionViewSet, basename='jobposition')
router.register(r'applicants', ApplicantViewSet, basename='applicant')

urlpatterns = [
    path('', include(router.urls)),
    path('register/', RegisterView.as_view(), name='register'),
    path('users/me/', CurrentUserView.as_view(), name='current-user'),
    
    # URL to get the quiz questions
    path('applicants/<int:pk>/quiz/', ApplicantQuizView.as_view(), name='applicant-quiz'),
    # URL to submit the completed quiz
    path('applicants/<int:pk>/submit-quiz/', SubmitQuizView.as_view(), name='submit-quiz'),
]
