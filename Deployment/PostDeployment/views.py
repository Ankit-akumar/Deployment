from django.shortcuts import render
from django.http import HttpResponse
import subprocess
import os
from Home.models import SiteModel

# Create your views here.


def readDataFromFile(start_string):
    try:
        with open('output_post.txt', 'r') as file:
            start_reading = False

            contents = ""
            for line in file:
                if start_string in line:
                    start_reading = True
                    continue
                if "END_OF_OUTPUT" in line and start_reading:
                    break
                if start_reading:
                    contents += line
            return contents
    
    except FileNotFoundError:
        return f"File 'output_post.txt' not found."


def get_instance_by_field_value(site):
    try:
        instance = SiteModel.objects.get(name=site)
        return instance
    except SiteModel.DoesNotExist:
        return None
    
def executeScript(instance):
    try:            
        username = instance.username
        password = instance.password
        server = instance.kmaster_IP_address
        server_knode1 = instance.knode1_IP_address
        server_knode2 = instance.knode2_IP_address

        script_path = os.path.abspath('PostDeployment/post_deployment_checks.sh')
        subprocess.run(["bash", script_path, username, password, server, server_knode1, server_knode2])

        app_pods = readDataFromFile('app_pods')
        system_pods = readDataFromFile('system_pods')
        postgres_promoted = readDataFromFile('postgres_promoted')
        postgres_replication = readDataFromFile('postgres_replication')
        load_kmaster = readDataFromFile('load_kmaster')
        load_knode1 = readDataFromFile('load_knode1')
        load_knode2 = readDataFromFile('load_knode2')
        certificate_expiry = readDataFromFile('certificate_expiry')
        nfs_status = readDataFromFile('nfs_status')

        context = {
            'heading': 'Post Deployment Check Results',
            'app_pods': app_pods,
            'system_pods': system_pods,
            'postgres_promoted': postgres_promoted,
            'postgres_replication': postgres_replication,
            'load_kmaster': load_kmaster,
            'load_knode1': load_knode1,
            'load_knode2': load_knode2,
            'certificate_expiry': certificate_expiry,
            'nfs_status': nfs_status,
        }

        return context
    except FileNotFoundError:
        print(f"Error: Bash script '{script_path}' not found.")
    except subprocess.CalledProcessError as e:
        print(f"Error: Bash script '{script_path}' failed with exit code {e.returncode}.")
        print("Output:")
        print(e.output.decode())

def postDeploymentChecks(request):
    site = request.GET.get('site')
    print(site)
    
    instance = get_instance_by_field_value(site)
    if instance:
        print("Instance found:", instance)
        context = executeScript(instance)
    else:
        print("Instance not found for the given site value.")
    
    return render(request, 'postDeployment.html', context)






# def executeCommandOnServer(server_ip, command):
#     ssh_command = 'sshpass -p "'+ password +'" ssh -o StrictHostKeyChecking=no "'+ username +'"@"'+ server_ip + '" "' +command +'"'
#     result = subprocess.run(ssh_command, shell=True, capture_output=True, text=True)
#     return result

# def executeSudoCommandOnServer(server_ip, sub_command):
#     command = "echo '"+password+"' | sudo -S "+sub_command+""
#     ssh_command = 'sshpass -p "'+ password +'" ssh -o StrictHostKeyChecking=no "'+ username +'"@"'+ server_ip + '" "' +command +'"'
#     result = subprocess.run(ssh_command, shell=True, capture_output=True, text=True)
#     return result
    
# def getApplicationPods():
#     app_pods = "kubectl get pods | grep -vE 'Running'"
#     result = executeSudoCommandOnServer(server, app_pods)

#     if result.returncode != 0:
#         print(result.stderr)
#         return result.stderr
#     else:
#         print(result.stdout)
#         count = result.stdout.count('\n')
#         if count > 1:
#             return result.stdout
#         else:
#             return "All Application pods are in running state."
    
# def getSystemPods():
#     system_pods = "kubectl get pods -n kube-system | grep -vE 'Running'"
#     result = executeSudoCommandOnServer(server, system_pods)

#     if result.returncode != 0:
#         print(result.stderr)
#         return result.stderr
#     else:
#         print(result.stdout)
#         count = result.stdout.count('\n')
#         if count > 1:
#             return result.stdout
#         else:
#             return "All System pods are in running state."

# def getPostgresPromoted():
#     get_postgres_promoted = "kubectl get pods | grep 'postgres' | awk '{print $1}'"
#     result = executeSudoCommandOnServer(server, get_postgres_promoted)

#     if result.returncode != 0:
#         print(result.stderr)
#         return result.stderr
#     else:
#         print(result.stdout)
#         output = f"Command: {' '.join(result.args)}\n"
#         output += f"stdout:\n{result.stdout}\n"
#         count = output.count('promoted')
#         if count!=0:
#             return "Postgres is Promoted!!"
#         else:
#             return "Postgres is not Promoted"
   
# def getPostgresReplication():
#     # Getting running postgres pod
#     command = "kubectl get pods | grep 'postgres' | grep -ve 'manager' -e 'postgres12' -e 'slave'"
#     result = executeSudoCommandOnServer(server, command)

#     if result.returncode != 0:
#         print(result.stderr)
#         return result.stderr
#     else:
#         print(result.stdout)
#         columns = result.stdout.split()
#         print(columns[0])
#         postgres_pod = columns[0]

#     # Getting running postgres-slave pod
#     command = "kubectl get pods | grep 'postgres-slave'"
#     result = executeSudoCommandOnServer(server, command)

#     if result.returncode != 0:
#         print(result.stderr)
#         return result.stderr
#     else:
#         print(result.stdout)
#         columns = result.stdout.split()
#         print(columns[0])
#         postgres_slave_pod = columns[0]
    
#     # Checking postgres replication is streaming on postgres pod
#     get_replication_state_postgres="kubectl exec -it "+postgres_pod+" bash -- su - postgres -c 'psql -c \"SELECT state FROM pg_stat_replication;\"'"
#     result = executeSudoCommandOnServer(server, get_replication_state_postgres)

#     if result.returncode !=0:
#         print(result.stderr)
#         return result.stderr
#     else:
#         print(result.stdout)
#         if result.stdout.count('streaming') < 1:
#             return "Postgres Replication not working! pg_stat_replication state for postgres pod is not Streaming"
    
#     # Checking postgres replication is streaming on postgres slave pod
#     get_replication_state_postgres_slave="kubectl exec -it "+postgres_slave_pod+" bash -- su - postgres -c 'psql -c \"SELECT state FROM pg_stat_replication;\"'"
#     result = executeSudoCommandOnServer(server, get_replication_state_postgres_slave)

#     if result.returncode !=0:
#         print(result.stderr)
#         return result.stderr
#     else:
#         print(result.stdout)
#         if result.stdout.count('streaming') > 0:
#             return "Postgres Replication is working."
#         else:
#             # If pg_stat_replication state for postgres-slave pod is not Streaming then comparing base file size on both knodes.
#             get_base_file_size="ls -ld /opt/data/postgres/base | cut -d' ' -f5"
#             result = executeSudoCommandOnServer(server_knode1, get_base_file_size)
    
#             base_file_size_knode1 = None
#             base_file_size_knode2 = None
#             if result.returncode != 0:
#                 print(result.stderr)
#                 return result.stderr
#             else:
#                 print(result.stdout)
#                 base_file_size_knode1 = result.stdout

#             result = executeSudoCommandOnServer(server_knode2, get_base_file_size)

#             if result.returncode != 0:
#                 print(result.stderr)
#                 return result.stderr
#             else:
#                 print(result.stdout)
#                 base_file_size_knode2 = result.stdout
    
#             if base_file_size_knode1!= None and base_file_size_knode2 != None and base_file_size_knode1 and base_file_size_knode2 and base_file_size_knode1 == base_file_size_knode2:
#                 return "Postgres Replication is working."
#             elif not base_file_size_knode1 or not base_file_size_knode2:
#                 return "pg_stat_replication state for postgres-slave pod is not Streaming. Could not capture Base file size from knodes."
#             else:
#                 return "Postgres Replication not working! Base file size on knode1 = "+base_file_size_knode1+" and Base file size on knode2 = "+base_file_size_knode2
    

# def getLoadAverage(server_ip):
#     command="uptime"
#     result = executeSudoCommandOnServer(server_ip, command)

#     if result.returncode != 0:
#         print(result.stderr)
#         return result.stderr
#     else:
#         print(result.stdout)
#         substring = re.search(r'average:\s*(.*)', result.stdout).group(1)
#         float_values = [float(value.strip()) for value in substring.split(',')]

#         is_high = False
#         for value in float_values:
#             if value > 2:
#                 is_high = True
        
#         if is_high == True:
#             return "Average Load on the server "+server_ip+" is high in the last 15 minutes - "+substring
#         else:
#             return "Average Load on the server "+server_ip+" is stable "+substring
        
# def getCertificateExpiry():
#     get_residual_time = "kubeadm certs check-expiration | grep 'admin.conf'" 
#     result = executeSudoCommandOnServer(server, get_residual_time)

#     if result.returncode != 0:
#         print(result.stderr)
#         return result.stderr
#     else:
#         print(result.stdout)
#         pattern = r'(\d+)d'
#         match = re.search(pattern, result.stdout)
#         if match:
#             number_of_days = match.group(1)
#             print(f"Number of days to expiry: {number_of_days}")
#             return f"Number of days to expiry: {number_of_days}"
#         else:
#             return "Could not get the number of days to expiry"
        
# def getNfsStatus():
#     get_mounted_status = "df -h | grep 'knode1:/mnt'"
#     result = executeCommandOnServer(server, get_mounted_status)

#     nfs_status = ""
#     if result.returncode != 0:
#         print(result.stderr)
#         return result.stderr
#     else:
#         print(result.stdout)
#         result.stdout = re.sub(r'\s+', '', result.stdout)
#         if len(result.stdout) > 0:
#             nfs_status += "NFS is mounted."
#         else:
#             nfs_status += "NFS is not mounted!"

#     get_service_status="service nfs-server status | grep 'Active: active'"
#     result = executeSudoCommandOnServer(server_knode1, get_service_status)

#     if result.returncode != 0:
#         print(result.stderr)
#         return result.stderr
#     else:
#         print(result.stdout)
#         result.stdout = re.sub(r'\s+', '',result.stdout)
#         if len(result.stdout) > 0:
#             nfs_status += " NFS is Active."
#         else:
#             nfs_status += " NFS is not Active!"
#     return nfs_status


# app_pods = getApplicationPods()
    # system_pods = getSystemPods()
    # postgres_promoted = getPostgresPromoted()
    # postgres_replication = getPostgresReplication()
    # load_kmaster = getLoadAverage(server)
    # load_knode1 = getLoadAverage(server_knode1)
    # load_knode2 = getLoadAverage(server_knode2)
    # certificate_expiry = getCertificateExpiry()
    # nfs_status = getNfsStatus()

    # context = {
    #     'app_pods': app_pods,
    #     'system_pods': system_pods,
    #     'postgres_promoted': postgres_promoted,
    #     'postgres_replication': postgres_replication,
    #     'load_kmaster': load_kmaster,
    #     'load_knode1': load_knode1,
    #     'load_knode2': load_knode2,
    #     'certificate_expiry': certificate_expiry,
    #     'nfs_status': nfs_status,
    # }

    # return render(request, 'postDeployment.html', context)