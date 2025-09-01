"""
URL configuration for quiz_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from accounts.views import RegisterView
from quizzes.views import start_quiz

urlpatterns = [
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('quizzes/', include(('quizzes.urls', 'quizzes'), namespace='quizzes')),
    path('quizzes/<int:pk>/start/', start_quiz, name='quiz-start'),
    path('api/', include(('api.urls', 'api'), namespace='api')),
    path('accounts/', include('django.contrib.auth.urls')),  # login, logout, password views
    path('accounts/register/', RegisterView.as_view(), name='register'),
    path('admin/', admin.site.urls),
]

admin.site.site_header = "Quizzy Admin"
admin.site.site_title = "Quizzy Admin"
admin.site.index_title = "Administration"
