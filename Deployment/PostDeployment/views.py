from django.shortcuts import render
from django.http import HttpResponse
import subprocess
import os

# Create your views here.

def executePostDeploymentChecks(request):
    try:
        script_path = os.path.join(os.path.dirname(__file__), 'deployment_checks.sh')
        subprocess.run(["bash", script_path], check=True)
        print("Bash script executed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error executing the Bash script: {e}")
    return HttpResponse('')