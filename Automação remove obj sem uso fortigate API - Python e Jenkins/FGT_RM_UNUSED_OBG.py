# Autor: Danilo Nogueira Ulbrecht.
# encoding: utf-8
#!/usr/bin/python3
#################################################################################
# Script para exibir ou remover objetos sem uso (ref 0) no Fortigate.           #
# Este script deve ser utilizado no jenkins com uso de choice/string parameters.#
# Tipo de Objetos:                                                              #
# vipgrp                                                                        #
# vip                                                                           #
# addrgrp                                                                       #
# address                                                                       #
# service group                                                                 #
# service custom                                                                #
# Ações:                                                                        #
# exibir                                                                        #
# remover                                                                       #
#################################################################################

from sys import argv
import requests
import json
import urllib.parse # Para codificação no formato HTML URL.
import warnings

warnings.filterwarnings('ignore', message='Unverified HTTPS request')


# A ordem que o Jenkins passa os argumentos IMPORTA, tem que ser a mesma abaixo.
JUSERNAME, JPASSWORD, JFIREWALL_IP, JVDOM, JTYPEOBG, JACTION, JEXCEPTION = argv[1:]

payload = "username="+JUSERNAME+"&secretkey="+JPASSWORD
base_url = "https://"+JFIREWALL_IP
api_call_url = ""

# urls da API por função.
if JTYPEOBG == "vipgrp":
    api_call_url = "/api/v2/cmdb/firewall/vipgrp/"
elif JTYPEOBG == "vip":
    api_call_url = "/api/v2/cmdb/firewall/vip/"
elif JTYPEOBG == "addrgrp":
    api_call_url = "/api/v2/cmdb/firewall/addrgrp/"
elif JTYPEOBG == "address":
    api_call_url = "/api/v2/cmdb/firewall/address/"
elif JTYPEOBG == "service_group":
    api_call_url = "/api/v2/cmdb/firewall.service/group/"
elif JTYPEOBG == "service":
    api_call_url = "/api/v2/cmdb/firewall.service/custom/"

fw_session_api = requests.session()
fw_session_api.post(url=base_url+"/logincheck", data=payload ,verify=False)

# Cookie Referencia: http://kb.fortinet.com/kb/documentLink.do?externalID=FD45595
dict_cookies = requests.utils.dict_from_cookiejar(fw_session_api.cookies)
csrftoken = dict_cookies['ccsrftoken'].strip('"')
fw_session_api.headers.update({'X-CSRFTOKEN': csrftoken})

# Filtro 'with_meta' retorna valores 'q_ref', 'q_static' e 'q_no_edit'.
get_addr_response = fw_session_api.get(base_url+api_call_url
+"?with_meta=1&vdom="+JVDOM)

address_dict_list = json.loads(get_addr_response.content)

addr_obj_without_ref = 0
removed_addr_obj_without_ref = 0
errors_while_deleting = 0

if JACTION == "exibir":
    for dict in address_dict_list['results']:
        if dict["name"] in JEXCEPTION:
            continue
        elif dict["q_static"] == True or dict["q_no_edit"] == True:
            continue
        elif dict["q_ref"] == 0:
            objetoaddr = dict["name"]
            print(objetoaddr)
            addr_obj_without_ref += 1
    print(f"Total de objetos sem uso do tipo {JTYPEOBG} no Firewall = {addr_obj_without_ref}")

if JACTION == "remover":
    for dict in address_dict_list['results']:
        if dict["name"] in JEXCEPTION:
            continue
        elif dict["q_static"] == True or dict["q_no_edit"] == True:
            continue
        elif dict["q_ref"] == 0:
            status_code = fw_session_api.delete(url=base_url+api_call_url
            +urllib.parse.quote(dict["name"], safe='')+"?vdom="+JVDOM).status_code
            addr_obj_without_ref += 1
            if status_code == 200:
                objetodeletado = dict["name"]
                print(f"o objeto {objetodeletado} foi removido com sucesso")
                removed_addr_obj_without_ref += 1
            else:
                objetocomerro = dict["name"]
                print(f"o objeto {objetocomerro} não foi removido, status code {status_code}")
                errors_while_deleting += 1
    print(f"Total de objetos sem uso do tipo {JTYPEOBG} no Firewall = {addr_obj_without_ref}")
    print(f"Total de objetos sem uso do tipo {JTYPEOBG} removidos = {removed_addr_obj_without_ref}")
    print(f"Total de objetos do tipo {JTYPEOBG} que apresentaram erro ao deletar = {errors_while_deleting}" )
    