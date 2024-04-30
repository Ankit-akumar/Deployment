from django.urls import path
from . import views

urlpatterns = [
    path('postDeploymentChecks/', views.postDeploymentChecks, name='postDeploymentChecks'),
]