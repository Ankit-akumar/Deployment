from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from django.http import HttpResponseRedirect
from .models import SiteModel, CloudSite


# Create your views here.

@csrf_exempt
def home_view(request):    
    site_model_instances = SiteModel.objects.all()
    cloudSite_model_instances = CloudSite.objects.all()

    context = {
        'site_model_instances': site_model_instances, 
        'cloudSite_model_instances': cloudSite_model_instances
    }
        
    if request.method == 'POST':
        form_type = request.POST.get('form_id')

        if form_type == 'deployment-form':
            deployment_type = request.POST.get('deployment_type')
            print(deployment_type)
            site = request.POST.get('site')
            print(site)

            if site:
                if(deployment_type == 'pre_deployment'):
                    url = reverse('PreDeployment:preDeploymentChecks') + f'?site={site}'
                    return HttpResponseRedirect(url)
                elif(deployment_type == 'post_deployment'):
                    url = reverse('PostDeployment:postDeploymentChecks') + f'?site={site}'
                    return HttpResponseRedirect(url)
        
        elif form_type == 'maintenance-form':
            site = request.POST.get('site')
            print(site)

            if(site != 'none'):
                url = reverse('Maintenance:maintenanceChecks') + f'?site={site}'
                return HttpResponseRedirect(url)
            
        elif form_type == 'backupfiles-form':
            file = request.POST.get('file')
            site = request.POST.get('site')

            if(file != 'none' and site != 'none'):
                url = reverse('BackupFiles:getFileBackup') + f'?site={site}&file={file}'
                return HttpResponseRedirect(url)
                
    
    return render(request, 'home.html', context)