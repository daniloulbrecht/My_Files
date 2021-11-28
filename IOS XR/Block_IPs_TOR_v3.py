import requests
import warnings
from re import findall
import xmltodict
from ncclient import manager
from netmiko import Netmiko
warnings.filterwarnings('ignore', message='Unverified HTTPS request')


def gera_sessao_netconf(ip, username, password, port=830, hostkey_verify=False, device_params={'name':'iosxr'}, timeout=300):
    fsessao_netconf = manager.connect(host=ip, port=port, username=username, password=password, hostkey_verify=hostkey_verify, device_params=device_params, timeout=timeout)
    return fsessao_netconf


def gera_sessao_ssh(ip, username, password):
    sessao_dict = {
        'host': ip,
        'username': username,
        'password': password,
        'device_type': 'cisco_xr'
    }
    
    sessao = Netmiko(**sessao_dict)
    return sessao


from sys import argv
coreip, username, password = argv[1:]

#### Templates RPC Netconf ####

# filtro que obtem a arvore de rotas estaticas aplicadas no equipamento.
filter = """<filter type="subtree">
<router-static xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-ip-static-cfg">
</router-static>
</filter>"""

# cabeçalho rpc add route.
rpc_add_route_header = '''
<config>
<router-static xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-ip-static-cfg">
<default-vrf>
<address-family>
<vrfipv4>
<vrf-unicast>
<vrf-prefixes>'''

# rodape rpc add route.
rpc_add_route_bottom ='''
</vrf-prefixes>
</vrf-unicast>
</vrfipv4>
</address-family>
</default-vrf>
</router-static>
</config>
'''

#### FIM Templates RPC Netconf ####


# Obtem lista atualizada de ips TOR.
httpssession = requests.session()
url = "https://raw.githubusercontent.com/SecOps-Institute/Tor-IP-Addresses/master/tor-exit-nodes.lst"

try:
    result = httpssession.get(url=url, verify=False)
except:
    with open('errors.txt', 'a') as errors:
        errors.write("Ocorreu um erro ao se conectar a url "+url+"\n")
        exit(1)

if result.status_code != 200:
    with open('errors.txt', 'a') as errors:
        errors.write(str(result.status_code)+"\n")
        exit(1)

# Separa lista v4 da lista v6.
ips_v4 = findall("[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+", result.text)
ips_v6 = findall("[A-Z,a-z,0-9]+:[A-Z,a-z,0-9]+:[A-Z,a-z,0-9]+:[A-Z,a-z,0-9]+:[A-Z,a-z,0-9]+:[A-Z,a-z,0-9]+:[A-Z,a-z,0-9]+:[A-Z,a-z,0-9]+", result.text)

#ips_v4 = [] #Desmaque essa linha para apagar todas as rotas para rede TOR de uma vez.

# Conecta no equipamento via Netconf.
sessao_netconf =  gera_sessao_netconf(coreip, username, password, '10830')
#sessao_netconf.lock(target="candidate")

# sessao netconf, conecta e baixa a lista de rotas estaticas como xml, depois tranforma em dicionario aninhado para melhor indexação.
static_routes_config = sessao_netconf.get_config(source='running', filter = filter).data_xml
#print("-------   Rotas estaticas atuais VRF Default em xml   -------")
#print(static_routes_config)
#print("------- Fim Rotas estaticas atuais VRF Default em xml -------")
dict_current_static_routes = xmltodict.parse(static_routes_config)

# lista de dicionarios de rotas estáticas da vrf default.
static_routes_list = dict_current_static_routes["data"]["router-static"]["default-vrf"]["address-family"]["vrfipv4"]["vrf-unicast"]["vrf-prefixes"]["vrf-prefix"]

tor_lista_atual = []						

# lista todas as rotas para ips tor atuais no equipamento e insere na lista tor_lista_atual.						
for rota in static_routes_list:
    try:
        if rota["vrf-route"]["vrf-next-hop-table"]["vrf-next-hop-interface-name"]["description"] == "rede-tor":
            tor_lista_atual.append(rota["prefix"])
    except:
        pass
		
tor_nets_add = [] # lista de ips para adicionar como rota null 0.
tor_nets_rem = [] # lista de ips para remover (não mais presentes na base do site mas presentes no equipamento).

# Compara lista baixada de ips com a lista aplicada no equipamento, o que não esta aplicado no equipamento vai para tor_nets_add.
for net in ips_v4:
    if net not in tor_lista_atual:
       tor_nets_add.append(net)

# Compara lista de ips tor atual no equipamento com a lista baixada de ips, o que esta no equipamento e não esta na lista baixada vai para tor_nets_rem.
for net in tor_lista_atual:
    if net not in ips_v4:
       tor_nets_rem.append(net)

print("quantidade de ips da rede Tor que serao removidos: "+ str(len(tor_nets_rem)))
print("quantidade de ips da rede Tor que serao adicionados: "+ str(len(tor_nets_add)))

# Cria rotas via Netconf.
if len(tor_nets_add) != 0:
    middle_rpc_add_route = ""		   
    
    # constroi o meio do xml rpc_add_route.
    for ip in tor_nets_add:
       middle_rpc_add_route += '''
<vrf-prefix>
<prefix>{}</prefix>
<prefix-length>32</prefix-length>
<vrf-route>
<vrf-next-hop-table>
<vrf-next-hop-interface-name>
<interface-name>Null0</interface-name>
<tag>666</tag>
<description>rede-tor</description>
</vrf-next-hop-interface-name>
</vrf-next-hop-table>
</vrf-route>
</vrf-prefix>'''.format(ip)
    
    # Junta tudo e cria uma unica chamada que criará todas as rotas de uma vez.
    rpc_add_route = rpc_add_route_header+middle_rpc_add_route+rpc_add_route_bottom
    print(rpc_add_route)
    response = sessao_netconf.edit_config(rpc_add_route, target="candidate")
    print(response)
    sessao_netconf.commit()

#sessao_netconf.unlock(target="candidate")    
sessao_netconf.close_session()	

# Apaga rotas via SSH.
if len(tor_nets_rem) != 0:
    sessao_ssh = gera_sessao_ssh(coreip, username, password)
    
    commands = ['router static','address-family ipv4 unicast']
    
    for ip in tor_nets_rem:
        command = "no "+ip+"/32"
        commands.append(command)

    commands.append("root")		
    output = sessao_ssh.send_config_set(commands)
    print(output)
    output = sessao_ssh.send_command("show commit changes diff")
    print(output)
    outputcommit = sessao_ssh.send_command_timing('commit comment "removido ips rede tor"')
    print(outputcommit)
    if "Do you wish to proceed with this commit anyway? [no]:" in outputcommit:
        commitajunto = sessao_ssh.send_command_timing('yes')
        print(commitajunto)
    sessao_ssh.disconnect()

print("--------- Abaixo IPs adicionados pela automacao ---------")

for ips in tor_nets_add:
    print(ips)

print("---------- Fim IPs adicionados pela automacao  ----------")

print("---------  Abaixo IPs removidos pela automacao  ---------")
for ips in tor_nets_rem:
    print(ips)

print("----------  Fim IPs removidos pela automacao  ----------")    

