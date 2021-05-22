#encoding: utf-8
#!/usr/bin/python3
# Author : Danilo Nogueira Ulbrecht
# Script para automatizar a criação de regras de Firewall.
# Funciona apenas com objetos já existentes na database.

from sys import argv
from datetime import datetime
from netmiko import Netmiko
from re import findall
from re import sub

horariodata_atual = datetime.now()
horariodata_formatada = horariodata_atual.strftime("%d/%m/%Y %H:%M")

# A ordem que o Jenkins passa os argumentos IMPORTA, tem que ser a mesma abaixo.
JFIREWALL_IP, JVDOM, JNAME, JSRC_INTF, JDST_INTF, JSRC_ADDR, JDST_ADDR, JSERVICE, JACTION, JINSPECTION_MODE, \
JSNAT, JSNAT_POOL, JSNAT_POOL_NAME, JPROTOCOL_OPTIONS, JAV_PROFILE, JWEB_FILTER, JDNS_FILTER, \
JAPP_CONTROL, JIPS_PROFILE, JWAF_PROFILE, JSSL_INSP_PROF, JLOG, JUSERNAME, JPASSWORD, JMOVE_BEFORE, \
JSRC_INTERNETSERVICES, JDST_INTERNETSERVICES, JSECURITY_PROFILES = argv[1:]

# Dicionario com os comandos.
fw_rule_dict = {
"NAME": "set name "+JNAME,
"SRC_INTF": "set srcintf "+sub("," , " ", JSRC_INTF),
"DST_INTF": "set dstintf "+sub("," , " ", JDST_INTF),
"SRC_ADDR": "set srcaddr "+sub("," , " ", JSRC_ADDR),
"DST_ADDR": "set dstaddr "+sub("," , " ", JDST_ADDR),
"SERVICE": "set service "+sub("," , " ", JSERVICE),
"ACTION": "set action "+JACTION,
"SECURITY_PROFILES": "set utm-status "+JSECURITY_PROFILES,
"INSPECTION_MODE": "set inspection-mode "+JINSPECTION_MODE,
"SNAT": "set nat "+JSNAT,
"SNAT_POOL": "set ippool "+JSNAT_POOL,
"SNAT_POOL_NAME": "set poolname "+JSNAT_POOL_NAME,
"PROTOCOL_OPTIONS": "set profile-protocol-options "+JPROTOCOL_OPTIONS,
"AV_PROFILE":"set av-profile "+JAV_PROFILE,
"WEB_FILTER":"set webfilter-profile "+JWEB_FILTER,
"DNS_FILTER":"set dnsfilter-profile "+JDNS_FILTER,
"APP_CONTROL":"set application-list "+JAPP_CONTROL,
"IPS_PROFILE":"set ips-sensor "+JIPS_PROFILE,
"WAF_PROFILE":"set waf-profile "+JWAF_PROFILE,
"SSL_INSP_PROF":"set ssl-ssh-profile "+JSSL_INSP_PROF,
"LOG": "set logtraffic "+JLOG
}

# Se source é internet services, remove source padrão.
if JSRC_INTERNETSERVICES == "SIM":
    fw_rule_dict.pop("SRC_ADDR")
    fw_rule_dict.update({"SRC_INTERNETSERVICES": "set internet-service-src enable"})
    fw_rule_dict.update({"SRC_INTERNETSERVICES_NAME": "set internet-service-src-name "+sub("," , " ", JSRC_ADDR)})

# Se destination é internet services, remove destination padrão.
if JDST_INTERNETSERVICES == "SIM":
    fw_rule_dict.pop("DST_ADDR")
    fw_rule_dict.update({"DST_INTERNETSERVICES": "set internet-service enable"})
    fw_rule_dict.update({"DST_INTERNETSERVICES_NAME": "set internet-service-name "+sub("," , " ", JDST_ADDR)})

# lista de comandos.
fw_rule_string_list = []

for key, value in fw_rule_dict.items():
    if value.endswith("Nenhum"):
        continue # Se valor de qualquer key for "Nenhum" ignora (sai da lista de comandos)
    else:
        fw_rule_string_list.append(value) # Se valor passou pelo filtro acima, insira na lista de comandos.

# Comandos padrão adicionados na lista de comandos.
fw_rule_string_list.append("set schedule always")
fw_rule_string_list.append("set status enable")
fw_rule_string_list.append('set comments "Criado via automacao Jenkins-Python em '+horariodata_formatada+'"')
fw_rule_string_list.append("show")
fw_rule_string_list.append("next")

# Abre sessão SSH com o firewall, aplica os comandos da lista e desconecta.
firewall = {'device_type': 'fortinet',
          'ip': JFIREWALL_IP,
          'username': JUSERNAME,
          'password': JPASSWORD
          }

firewall_session = Netmiko(**firewall)

firewall_session.send_command('config vdom', expect_string='#') # comente essa linha se o seu FW nao for mvdom
firewall_session.send_command('edit '+JVDOM, expect_string='#') # comente essa linha se o seu FW nao for mvdom
firewall_session.send_command('config firewall policy', expect_string='#')
firewall_session.send_command('edit 0', expect_string='#')
output_rule = firewall_session.send_config_set(fw_rule_string_list, cmd_verify=False)

print(output_rule)

# Movimentação da nova regra.
id = "Nenhum"
regra = findall("edit [0-9]+\\n", output_rule)
edit, id = str(regra[0]).split(" ")
id = id.strip()

if id != "Nenhum" and JMOVE_BEFORE != "Nenhum":
  firewall_session.send_command('move '+id+' before '+JMOVE_BEFORE, expect_string='#')
  output_move = firewall_session.send_command('show | grep edit', expect_string='#')
  print(output_move)
  firewall_session.disconnect()
else:
  firewall_session.disconnect()