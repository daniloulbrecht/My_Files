#!/usr/bin/python
# -*- coding: utf-8 -*-
from ipaddress_myfunctions import ips_para_hsrp
from ipaddress_myfunctions import eh_uma_subnet
from ipaddress_myfunctions import eh_uma_supernet
from re import match
from netmiko import Netmiko
from getpass import getpass
from sys import exit
from time import sleep

ag1_ip = '192.168.255.32'
ag2_ip = '192.168.255.33'
vlanlivre = False
mynetpool = ['10.148.0.0/20']

username = 'nomedousuario'
password = getpass('Type {} password:\n'.format(username))
rede = input("Digite a rede da interface vlan (exemplo 10.148.0.224/27 ou 10.148.0.224/27 255.255.255.224):\n")
result, netmatch = eh_uma_subnet(rede, mynetpool)

while result == False:
    print("A rede {} não pertence a supernet {}, digite a rede novamente!"
          .format(rede, mynetpool[0]))
    rede = input("Digite a rede da interface vlan (exemplo 10.148.0.224/27 ou 10.148.0.224/27 255.255.255.224):\n")
    result, netmatch = eh_uma_subnet(rede, mynetpool)

device1 = {
    'host': ag1_ip,
    'username': username,
    'password': password,
    'device_type': 'cisco_nxos'
    }

device2 = {
    'host': ag2_ip,
    'username': username,
    'password': password,
    'device_type': 'cisco_nxos'
    }

instancia1 = Netmiko(**device1)
instancia2 = Netmiko(**device2)

int_vlans_na_caixa1 = []
int_vlans_na_caixa2 = []
ipintbriefag1 = instancia1.send_command('sh ip int brief vrf all | inc Vlan')
ipintbriefag2 = instancia2.send_command('sh ip int brief vrf all | inc Vlan')

for item in ipintbriefag1.split():
    if match("Vlan", item):
        int_vlans_na_caixa1.append(item)

for item in ipintbriefag2.split():
    if match("Vlan", item):
        int_vlans_na_caixa2.append(item)

for n in range (3501, 3600):
    vlan = "Vlan"+str(n)
    if vlan not in int_vlans_na_caixa1 and vlan not in int_vlans_na_caixa2:
        vlanlivre = True
        vlanid = str(n)
        print("A vlan LIVRE selecionada do pool 3501-3599 foi a vlan "+vlanid)
        break

if vlanlivre == False:
    print("Não existem vlans livres para uso no pool 3501-3599 ... Abortando")
    exit()

outputag1 = instancia1.send_command('sh ip route 10.148.0.0/20 longer-prefixes direct | exclude via')
# outputag2 = instancia2.send_command('sh ip route direct vrf BACKEND | exclude via')

connected_nets = []

for ipstring in outputag1.split():
    if match("[0-9]+[.][0-9]+[.][0-9]+[.][0-9]+[/][0-9]+", ipstring):
        connected_nets.append(str(ipstring.strip(',')))

resultado, conflitosub = eh_uma_subnet(rede, connected_nets)

if resultado == True:
    print("A rede {} é uma subnet da rede {}, por favor utilize outra rede, abortando ...".format(rede, conflitosub))
    exit()

resultado, conflitosuper = eh_uma_supernet(rede, connected_nets)

if resultado == True:
    print("A rede {} é uma supernet das redes abaixo, por favor utilize outra rede, abortando ...".format(rede))
    for redeconflitante in conflitosuper:
        print("Rede conflitante: " + redeconflitante)
    exit()

mascara, pip, sip, tip, antip, penip, ultip = ips_para_hsrp(rede, True, True)

ag1config = [
    'interface Vlan'+vlanid,
    'description TBOX_VLAN'+vlanid,
    'no shutdown',
    'vrf member BACKEND',
    'no ip redirects',
    'ip address '+penip+' '+mascara,
    'no ipv6 redirects',
    'hsrp version 2',
    'hsrp 1',
    'preempt',
    'priority 101',
    'ip '+pip
    ]

ag2config = [
    'interface Vlan'+vlanid,
    'description TBOX_VLAN'+vlanid,
    'no shutdown',
    'vrf member BACKEND',
    'no ip redirects',
    'ip address '+ultip+' '+mascara,
    'no ipv6 redirects',
    'hsrp version 2',
    'hsrp 1',
    'preempt',
    'ip '+pip
    ]

Execucao = instancia1.send_config_set(ag1config)
print("\n"+80*"#")
print("\n\t\t\tCONFIGURANDO, AGUARDE POR FAVOR ...")
print("\n"+80*"#")
print(Execucao)

Execucao = instancia2.send_config_set(ag2config)
print(Execucao)

print("\n"+80*"#")
print("\n\t\t\tSALVANDO, AGUARDE POR FAVOR ...")
print("\n"+80*"#")

salvando = instancia1.save_config() ; print(salvando)
salvando = instancia2.save_config() ; print(salvando)

print("\n"+80*"#")
print("\n\t\t\tSCRIPT EXECUTADO COM SUCESSO")
print("\n"+80*"#")

print("\n"+80*"#")
print("\n\t\tAGUARDE 25 SEG PARA ESTABELECIMENTO DO HSRP")
print("\n"+80*"#")

sleep(25)

hsrpoutput = instancia1.send_command('show hsrp brief | inc '+vlanid)

print(hsrpoutput)

instancia1.disconnect()
instancia2.disconnect()
