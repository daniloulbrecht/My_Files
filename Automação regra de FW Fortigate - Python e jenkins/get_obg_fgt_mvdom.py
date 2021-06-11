# Autor: Danilo Nogueira Ulbrecht
# Autor: Cae Masquetti Caetano
# Autor: Murilo Costa
# encoding: utf-8
# Programa para gerar propertyfile de objetos Fortigate para o Jenkins.
# A coleta e feita via SSH para a maioria dos objetos.
# A documentação oficial da API do Fortigate é paga, e nao temos acesso a DOC mais recente, por isso as coletas sao via SSH.
# A unica coleta feita via API é de internet services por que traz mais metadados.

from re import findall
from re import sub
from netmiko import ConnectHandler
from sys import argv
import requests
import json
import warnings

warnings.filterwarnings('ignore', message='Unverified HTTPS request')

# Recebe valores de fora (shell)
JHOSTNAME, JFIREWALL_IP, JVDOM, JUSERNAME, JPASSWORD = argv[1:]
ABS_PATH = "/var/jenkins_home/workspace/FGT_Get_Objects/"

def formata_saida(foutput, firststr="", interfaces=False, fwrule=False):
    """
    Essa Funcao limpa a saida dos comandos extraidas do Fortigate
    e retorna uma string formatada para uso no Jenkins
    """
    if interfaces == True:
        limpa = findall('edit \".*?\"', foutput) # interfaces
        limpamais = []
        for item in limpa: limpamais.append(sub('"', "'", item.strip("edit ")))
        limpa = limpamais
    elif fwrule == True:
        limpa = findall("[0-9]+", foutput) # id das regras em ordem
    else:
        limpa = findall("\'.*?\'", sub('\"', "\'", foutput)) # restante
    conteudo = firststr
    contador = 0
    for item in limpa:
        if item == 'none':
            continue
        contador += 1
        if contador > 1:
            conteudo = conteudo+"\n"+item
        else:
            conteudo = conteudo+item
    return conteudo

# Dados para instaciar sessao ssh com o fw
firewall = {'device_type': 'fortinet',
          'ip': JFIREWALL_IP,
          'username': JUSERNAME,
          'password': JPASSWORD
          }

firewall_session = ConnectHandler(**firewall) # objeto da sessao SSH estabelecida
firewall_session.send_command('config vdom', expect_string='#') # comente essa linha se o seu FW nao for mvdom
firewall_session.send_command('edit '+JVDOM, expect_string='#') # comente essa linha se o seu FW nao for mvdom

# Dicionario com o restante dos comandos
fw_commands_dict = {
"getservices" : ["show firewall service custom | grep edit","show firewall service group | grep edit"],
"getsnats" : "show firewall ippool | grep edit",
"getprofopt" : "show firewall profile-protocol-options | grep edit",
"getavprof" : "show antivirus profile | grep edit",
"getwebfiltprof" : "show webfilter profile | grep edit",
"getdnsfiltprof" : "show dnsfilter profile | grep edit",
"getappprof" : "show application list | grep edit",
"getipsprof" : "show ips sensor | grep edit",
"getwafprof" : "show waf profile | grep edit",
"getsslprof" : "show firewall ssl-ssh-profile | grep edit",
"getint" : ["show system interface | grep -f "+JVDOM, "show system zone"],
"getsrcaddress" : ["show firewall address | grep edit","show firewall addrgrp | grep edit"],
"getfwrulenumbers" : "show firewall policy | grep edit",
"getdstaddress" : ["show firewall address | grep edit","show firewall vip | grep edit", "show firewall addrgrp | grep edit", "show firewall vipgrp | grep edit"]
}

# Para cada comando do dicionario, gera uma database
for dictkey, value in fw_commands_dict.items():
    if "getwafprof" in dictkey:
        output = firewall_session.send_command(value, expect_string='#')
        outputlimpo = formata_saida(output)
    elif "getsslprof" in dictkey:
        output = firewall_session.send_command(value, expect_string='#')
        outputlimpo = formata_saida(output)
    elif "prof" in dictkey:
        output = firewall_session.send_command(value, expect_string='#')
        outputlimpo = formata_saida(output, "Nenhum\n")
    elif "getfwrulenumbers" in dictkey:
        output = firewall_session.send_command(value, expect_string='#')
        outputlimpo = formata_saida(output, "Nenhum\n", fwrule=True)
    elif "getint" in dictkey:
        output = firewall_session.send_config_set(value)
        outputlimpo = formata_saida(output, interfaces=True)
    elif "getdstaddress" in dictkey:
        output = firewall_session.send_config_set(value)
        outputlimpo = formata_saida(output)
    elif "getsrcaddress" in dictkey:
        output = firewall_session.send_config_set(value)
        outputlimpo = formata_saida(output)
    elif "getservices" in dictkey:
        output = firewall_session.send_config_set(value)
        outputlimpo = formata_saida(output)
    else:
        output = firewall_session.send_command(value, expect_string='#')
        outputlimpo = formata_saida(output)

    with open(ABS_PATH+JHOSTNAME+"_"+JVDOM+"_"+dictkey+".txt", "w") as file:
        file.write(outputlimpo)

firewall_session.disconnect() # Encerramento da sessao SSH.

### Coleta via API (internet services) ###
payload = "username="+JUSERNAME+"&secretkey="+JPASSWORD
login_url = "https://"+JFIREWALL_IP+"/logincheck"

fw_session_api = requests.session()
fw_session_api.post(url=login_url, data=payload ,verify=False)

isdb_get_response = fw_session_api.get("https://"+JFIREWALL_IP+"/api/v2/cmdb/firewall/internet-service/"+"?vdom="+JVDOM)

isdb_dict = json.loads(isdb_get_response.text)

lista_isdb = isdb_dict['results']
isdbdst = ""
isdbsrc = ""

for dict in lista_isdb:
    if dict["direction"] == "dst":
        isdbdst += "\n"+"'"+dict["name"]+"'"
    elif dict["direction"] == "src":
        isdbsrc += "\n"+"'"+dict["name"]+"'"
    elif dict["direction"] == "both":
        isdbdst += "\n"+"'"+dict["name"]+"'"
        isdbsrc += "\n"+"'"+dict["name"]+"'"

with open(ABS_PATH+JHOSTNAME+"_"+JVDOM+"_isdbdst.txt", "w") as file:
    file.write(isdbdst[1:])
with open(ABS_PATH+JHOSTNAME+"_"+JVDOM+"_isdbsrc.txt", "w") as file:
    file.write(isdbsrc[1:])

# Coleta zonas SD-WAN via API
sdwanzones_get_response = fw_session_api.get("https://"+JFIREWALL_IP+"/api/v2/cmdb/system/sdwan/zone"+"?vdom="+JVDOM)

sdwanzones_dict = json.loads(sdwanzones_get_response.text)

lista_sdwanzones = sdwanzones_dict['results']

for dict in lista_sdwanzones:
    with open(ABS_PATH+JHOSTNAME+"_"+JVDOM+"_getint.txt", "a") as file:
        file.write("\n"+"'"+dict["name"]+"'")

logout_url = "https://"+JFIREWALL_IP+"/logout"
fw_session_api.get(url=logout_url, verify=False)

# Espaço para uma frase de efeito no final, sqn, thats all folks!
