"""
URL configuration for Deployment project.

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

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include("Home.urls"), name='home'),
    path('accounts/', include("django.contrib.auth.urls")),
    path('pre_deployment/', include(("PreDeployment.urls", 'PreDeployment'), namespace='PreDeployment')),
    path('post_deployment/', include(("PostDeployment.urls", 'PostDeployment'), namespace='PostDeployment')),
    path('maintenance/', include(('Maintenance.urls', 'Maintenance'), namespace='Maintenance')),
    path('backup_files/', include(('BackupFiles.urls', 'BackupFiles'), namespace='BackupFiles')),
]

#path('pre_deployment/<str:site>/', include("PreDeployment.urls"), name='pre_deployment'),