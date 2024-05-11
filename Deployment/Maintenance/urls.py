from django.urls import path
from . import views

urlpatterns = [
    path('maintenanceChecks/', views.maintenanceChecks, name='maintenanceChecks'),
]