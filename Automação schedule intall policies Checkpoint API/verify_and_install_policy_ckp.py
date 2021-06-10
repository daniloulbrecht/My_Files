import requests, json
import time
from sys import argv
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


def api_call(ip_addr, port, command, json_payload, sid):
    url = 'https://' + ip_addr + ':' + port + '/web_api/' + command
    if sid == '':
        request_headers = {'Content-Type' : 'application/json'}
    else:
        request_headers = {'Content-Type' : 'application/json', 'X-chkp-sid' : sid}
    r = requests.post(url,data=json.dumps(json_payload), headers=request_headers, verify=False)
    return r.json()


def login(user,password, mngipaddress):
    payload = {'user':user, 'password' : password}
    response = api_call(mngipaddress, '443', 'login',payload, '')
    return response['sid']


def task_progress(mngipaddress, task_id_json, sid, task_complete = False):
    while not task_complete:
        show_task_result = api_call(mngipaddress, '443','show-task', task_id_json ,sid)
        task_name = show_task_result['tasks'][0]['task-name']
        if show_task_result['tasks'][0]['progress-percentage'] != 100:
            print("Executando {} {}{}").format(task_name, show_task_result["tasks"][0]['progress-percentage'], "%")
            time.sleep(1) 
        else:
            print("Tarefa {} {}{}").format(task_name, show_task_result["tasks"][0]['progress-percentage'], "%")
            task_complete = True
            
    return show_task_result


mngipaddress, fwpolicypack, fwtarget, user, password = argv[1:]
sid = login(user, password, mngipaddress)
#print("session id: " + sid)


verify_packages = {"policy-package" : fwpolicypack}
verify_packages_result = api_call(mngipaddress, '443','verify-policy', verify_packages ,sid)
#print(json.dumps(verify_packages_result, indent=4, sort_keys=True))


task_id_json =  {"task-id" : verify_packages_result['task-id']}
show_task_result = task_progress(mngipaddress, task_id_json, sid)

#print(json.dumps(show_task_result, indent=4, sort_keys=True))

if show_task_result["tasks"][0]['status'] == "failed":
    print("Falha na verificacao da politica, verifique os erros abaixo:")
    for erros in show_task_result["tasks"][0]['task-details'][0]['errors']: print("\n"+erros)
    logout_result = api_call(mngipaddress, '443',"logout", {},sid)
    print("\n"+"logout result: " + json.dumps(logout_result, indent=4, sort_keys=True))
    exit(1)


install_policy = {"policy-package": fwpolicypack, "access" : True, "threat-prevention" : False, "targets" : fwtarget}
install_policy_result = api_call(mngipaddress, '443','install-policy', install_policy ,sid)
#print(json.dumps(install_policy_result, indent=4, sort_keys=True))

task_id_json =  {"task-id" : install_policy_result['task-id']}
show_task_result = task_progress(mngipaddress, task_id_json, sid)

#print(json.dumps(show_task_result, indent=4, sort_keys=True))

logout_result = api_call(mngipaddress, '443',"logout", {},sid)
#print("logout result: " + json.dumps(logout_result, indent=4, sort_keys=True))