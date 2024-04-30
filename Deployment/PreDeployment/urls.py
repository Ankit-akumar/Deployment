from django.urls import path
from . import views

urlpatterns = [
    # path('', views.executePreDeploymentChecks, name='pre_deployment')
    path('preDeploymentChecks/', views.preDeploymentChecks, name='preDeploymentChecks'),
]