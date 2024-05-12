from django.urls import path
from . import views

urlpatterns = [
    path('getFileBackup/', views.getFileBackup, name='getFileBackup'),
]