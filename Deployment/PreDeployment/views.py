from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

def preDeploymentChecks(request):
    site = request.GET.get('site')
    print(site)
    return HttpResponse('')