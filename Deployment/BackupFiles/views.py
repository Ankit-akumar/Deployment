from django.shortcuts import render, redirect
from django.http import HttpResponse
from PreDeployment.views import *

# Create your views here.

def getFileBackup(request):
    site = request.GET.get('site')
    file = request.GET.get('file')
    print(site, file)

    instance = get_instance_by_field_value(site)
    if instance:
        URL = instance.dashboard_url
        username = instance.dashboard_username
        password = instance.dashboard_password

        if file == '1':
            # logging into MD and getting driver object
            mdDbDriver = loginMD(URL+"/login/", username, password)
            # downloading MD config
            downloadMDConfig(URL+"/configuration/", mdDbDriver)
            mdDbDriver.quit()
        elif file == '2':
            # logging into sorter dashboard and getting driver object 
            sorterDbDriver = login(URL+"/sorter/login/", "id_username", "id_password", "submit-row", username, password)
            # downloading sorter devices config
            downloadSorterDevicesConfig(URL+"/sorter/data/installation/", sorterDbDriver)
            sorterDbDriver.quit()
        elif file == '3':
            # Logging into sam dashboard and getting driver object
            samDbDriver = login(URL+"/sam/login/", "id_username", "id_password", "submit-row", username, password)
            # downloading sam devices config
            downloadSamDevicesConfig(URL+"/sam/gorsam/system/", samDbDriver)
            samDbDriver.quit()
        else:
            # logging into MD and getting driver object
            mdDbDriver = loginMD(URL+"/login/", username, password)
            # getting the current running map from MD
            currentRunningMap = getMap(URL+"/maps/", mdDbDriver, False)
            print("Map name copied from MD - "+currentRunningMap)
            # downloading map from map-creator
            downloadMap(URL+"/map-creator/", mdDbDriver, currentRunningMap)
            mdDbDriver.quit()

    return redirect('home')