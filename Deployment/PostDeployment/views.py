from django.shortcuts import render
from django.http import Http404
import subprocess
import os
from Home.models import SiteModel, CloudSite

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup as bs
import re
import time
import json
import os

# Create your views here.

def readDataFromBackupFile():
    with open('backup/depBkp.json','r') as file:
        data = json.load(file)

        if 'subscription_urls' in data:
            subscription_urls = data['subscription_urls']
            print(subscription_urls)

        if 'currentRunningMap' in data:
            currentRunningMap = data['currentRunningMap']
            print(currentRunningMap)
        
        result_dict = {}
        result_dict['currentRunningMap'] = currentRunningMap
        result_dict['subscription_urls'] = subscription_urls
        return result_dict

def login(url, usernameId, passwordId, submitId, username, password):
        driver = webdriver.Chrome()
        driver.get(url)
        try:
            WebDriverWait(driver,30).until(
                EC.presence_of_element_located((By.CLASS_NAME, submitId))
            )
        except Exception as e:
            print("Error encountered while login at "+url+" : ", e)
        finally:
            driver.find_element(By.ID, usernameId).send_keys(username)
            driver.find_element(By.ID, passwordId).send_keys(password)
            driver.find_element(By.CLASS_NAME, submitId).click()
            time.sleep(3)
            return driver
        
def loginMD(url, username, password):
        driver = webdriver.Chrome()
        driver.get(url)
        try:
            WebDriverWait(driver,30).until(
                EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'LOGIN')]"))
            )
        except Exception as e:
            print("While waiting for the page of load encountered this error:", e)
        finally:
            driver.find_element(By.CLASS_NAME, "username-textbox").send_keys(username)
            driver.find_element(By.CLASS_NAME, "password-textbox").send_keys(password)
            driver.find_element(By.XPATH, "//button[contains(text(), 'LOGIN')]").click()
            time.sleep(2)
            return driver
        
def stopSystem(driver, URL):
    driver.get(URL+'system/')
    stop_btn = driver.find_element(By.XPATH, "(//input[@class='emergency-stop-button'])")
    if stop_btn:
        stop_btn.click()


def uploadMap(URL, mdDriver, currentRunningMap):
    driver = mdDriver
    driver.get(URL)
    time.sleep(5)
    driver.find_element(By.CLASS_NAME, 'search-map.form-control').send_keys(currentRunningMap)
    time.sleep(1)
    pattern = re.compile(r'\b' + re.escape(currentRunningMap) + r'\b')
    pageSource = driver.page_source
    soup = bs(pageSource, 'html.parser')
    currentRunningMapText = soup.find('td', string=pattern)
    if currentRunningMapText:
        mapId = currentRunningMapText.find_previous_sibling('td').text.strip()
        print("Map ID copied from Map-creator - "+mapId)
        if mapId:
            driver.get(URL+'view/'+mapId)
            time.sleep(5)
            driver.find_element(By.CLASS_NAME, 'upload-map').click()
            time.sleep(1)
            input_element_bfs = driver.find_element(By.XPATH, "//input[@class='form-control' and @placeholder='bfs']")
            input_element_port = driver.find_element(By.XPATH, "//input[@class='form-control' and @placeholder='4000']")
            if input_element_bfs and input_element_port:
                
                # SMS should be checked, IMS unchecked and Sister unchecked
                input_element_sms = driver.find_element(By.XPATH, "//input[@class='form-check-input' and @value='sms']")
                if input_element_sms:
                    input_element_sms_is_checked = input_element_sms.get_attribute("checked")
                    if input_element_sms_is_checked is None:
                        input_element_sms.click()
                    
                    input_element_ims = driver.find_element(By.XPATH, "//input[@class='form-check-input' and @value='ims-backend']")
                    if input_element_ims:
                        input_element_ims_is_checked = input_element_ims.get_attribute('checked')
                        if input_element_ims_is_checked:
                            input_element_ims.click()
                    else:
                        print('IMS not found')

                    input_element_sister = driver.find_element(By.XPATH, "//input[@class='form-check-input' and @value='induct-manager']")
                    if input_element_sister:
                        input_element_sister_is_checked = input_element_sister.get_attribute('checked')
                        if input_element_sister_is_checked:
                            input_element_sister.click()
                    
                        time.sleep(2)
                        driver.find_element(By.CSS_SELECTOR, "button.btn.btn-success").click()
                        time.sleep(10)
                    else:
                        print('Sister not found')
                else:
                     print('SMS not found')
            else:
                print('bfs and port not found')


def updateSubscriptionUrls(sorterDriver, subscription_urls, URL):
    driver = sorterDriver
    driver.get(URL)

    pageSource = driver.page_source
    soup = bs(pageSource, 'html.parser')
    eventList = soup.find_all('th', class_='field-pk')

    keysList = []
    for event in eventList:
        keysList.append(subscription_urls[event.get_text()])
    
    i = 1
    for key in keysList:
        x_path = "(//input[@class='vTextField'])["+str(i)+"]"
        input_element = driver.find_element(By.XPATH, x_path)
        input_element.clear()
        input_element.send_keys(key)
        i+=1

    time.sleep(2)

    submit_btn = driver.find_element(By.XPATH, "(//input[@type='submit'])")
    if submit_btn:
        print('found')
        print(submit_btn.get_attribute('name'))

def updateDashboardData(URL, username, password):
    result_dict = readDataFromBackupFile()
    driver = login(URL+"sorter/login/", "id_username", "id_password", "submit-row", username, password)
    updateSubscriptionUrls(driver, result_dict['subscription_urls'], URL+'sorter/data/subscription/')
    driver = loginMD(URL+"login/", username, password)
    stopSystem(driver, URL)
    uploadMap(URL+'map-creator/', driver, result_dict['currentRunningMap'])


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
        return instance, 'onprem'
    except SiteModel.DoesNotExist:
        try:
            instance = CloudSite.objects.get(name=site)
            return instance, 'cloud'
        except CloudSite.DoesNotExist:
            return None

def checkCloudServerHealth(instance):
    try:            
        username = instance.username
        password = instance.password
        hostname = instance.hostname
        cluster_name = instance.cluster_name
        namespace_name = instance.namespace_name

        script_path = os.path.abspath('PostDeployment/post_deployment_checks_cloud.sh')
        subprocess.run(["bash", script_path, username, password, hostname, cluster_name, namespace_name])

        app_pods = readDataFromFile('app_pods')
        system_pods = readDataFromFile('system_pods')
        load_average = readDataFromFile('load_average')

        context = {
            'server_type': 'cloud',
            'heading': instance.name+' Post Deployment Check Results',
            'app_pods': app_pods,
            'system_pods': system_pods,
            'load_average': load_average
        }
        return context

    except FileNotFoundError:
        print(f"Error: Bash script '{script_path}' not found.")
    except subprocess.CalledProcessError as e:
        print(f"Error: Bash script '{script_path}' failed with exit code {e.returncode}.")
        print("Output:")
        print(e.output.decode())


def checkServerHealth(instance):
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
            'server_type': 'onprem',
            # 'heading': 'Post Deployment Check Results',
            'heading': instance.name+' Post Deployment Check Results',
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
    
    instance, server_type = get_instance_by_field_value(site)
    if instance:
        print("Instance found:", instance)
        if server_type == 'onprem':
            context = checkServerHealth(instance)
        else:
            context = checkCloudServerHealth(instance)
        # updateDashboardData(instance.dashboard_url, instance.dashboard_username, instance.dashboard_password)
    else:
        print("Instance not found for the given site value.")
        raise Http404('Selected site not found in the Database.')
    
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