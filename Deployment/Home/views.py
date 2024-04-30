from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from django.http import HttpResponseRedirect


# Create your views here.

@csrf_exempt
def home_view(request):    
    if request.method == 'POST':
        deployment_type = request.POST.get('deployment_type')
        print(deployment_type)
        site = request.POST.get('site')
        print(site)
        if(deployment_type == 'pre_deployment'):
            url = reverse('PreDeployment:preDeploymentChecks') + f'?site={site}'
            return HttpResponseRedirect(url)
        elif(deployment_type == 'post_deployment'):
            url = reverse('PostDeployment:postDeploymentChecks') + f'?site={site}'
            return HttpResponseRedirect(url)
    
    return render(request, 'home.html')