from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from django.http import HttpResponseRedirect
from .models import SiteModel


# Create your views here.

@csrf_exempt
def home_view(request):    
    site_model_instances = SiteModel.objects.all()
    for site_instance in site_model_instances:
        print(site_instance.name)
        
    if request.method == 'POST':
        form_type = request.POST.get('form_id')

        if form_type == 'deployment-form':
            deployment_type = request.POST.get('deployment_type')
            print(deployment_type)
            site = request.POST.get('site')
            print(site)

            if(deployment_type != 'none' and site != 'none'):
                if(deployment_type == 'pre_deployment'):
                    url = reverse('PreDeployment:preDeploymentChecks') + f'?site={site}'
                    return HttpResponseRedirect(url)
                elif(deployment_type == 'post_deployment'):
                    url = reverse('PostDeployment:postDeploymentChecks') + f'?site={site}'
                    return HttpResponseRedirect(url)
        
        if form_type == 'maintenance-form':
            site = request.POST.get('site')
            print(site)

            if(site != 'none'):
                url = reverse('Maintenance:maintenanceChecks') + f'?site={site}'
                return HttpResponseRedirect(url)

    
    return render(request, 'home.html', {'site_model_instances': site_model_instances})