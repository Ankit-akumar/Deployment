from django.shortcuts import render
from django.http import HttpResponse
from PostDeployment.views import *

# Create your views here.

def maintenanceChecks(request):
    site = request.GET.get('site')
    print(site)
    
    instance = get_instance_by_field_value(site)

    if instance:
        print("Instance found:", instance)
        context = executeScript(instance)
        context['heading'] = 'Maintenance Check Results'
    else:
        print("Instance not found for the given site value.")
    
    return render(request, 'postDeployment.html', context)