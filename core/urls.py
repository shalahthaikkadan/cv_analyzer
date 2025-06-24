"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# core/urls.py
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
# Import both views from the cv_analyzer app
from cv_analyzer.views import RegisterView, FrontendAppView

urlpatterns = [
    # 1. Frontend App View (serves the index.html as the main page)
    path('', FrontendAppView.as_view(), name='frontend_app'),

    # 2. Django Admin Site
    path('admin/', admin.site.urls),
    
    # 3. API Authentication Endpoints
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # 4. Include all other API endpoints (for jobs, applicants, etc.) 
    #    from the cv_analyzer app, prefixed with /api/
    path('api/', include('cv_analyzer.urls')), 
]