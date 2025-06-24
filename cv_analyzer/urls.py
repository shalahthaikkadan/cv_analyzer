from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import JobPositionViewSet, ApplicantViewSet

router = DefaultRouter()
router.register(r'jobs', JobPositionViewSet, basename='jobposition')
router.register(r'applicants', ApplicantViewSet, basename='applicant')

urlpatterns = [
    path('', include(router.urls)),
]
