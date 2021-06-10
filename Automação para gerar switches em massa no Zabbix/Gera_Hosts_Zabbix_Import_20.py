from jinja2 import Environment
from jinja2 import FileSystemLoader
import csv

# Gera de 20 em 20 hosts por XML do csv lido

def finaliza_xml_vinte_hosts(fnumerodoarquivo, FRODAPE, fcontador=0):
    xml_zabbix_file = open("xml_zabbix_import_file"+"_"+str(fnumerodoarquivo)+".xml","a+")
    xml_zabbix_file.write("\n")
    xml_zabbix_file.write(FRODAPE)
    xml_zabbix_file.close()
    print ("Arquivo xml_zabbix_import_file"+"_"+str(fnumerodoarquivo)+".xml, importe os hosts no Zabbix")
    fnumerodoarquivo += 1
    return fnumerodoarquivo, fcontador



MY_TEMPLATES = Environment(loader=FileSystemLoader('Templates'), trim_blocks=True)

CABECALHO = """<?xml version="1.0" encoding="UTF-8"?>
<zabbix_export>
    <version>5.0</version>
    <date>2021-03-28T20:33:19Z</date>
    <groups>
        <group>
            <name>Company/GNDI/NetworkDevices</name>
        </group>
        <group>
            <name>Company/GNDI/NetworkDevices/Satelites</name>
        </group>
    </groups>
    <hosts>"""

RODAPE = """    </hosts>
</zabbix_export>"""


contador = 0
numerodoarquivo = 0
csvfile = open("switchs_import.csv","r")
csv_read = csv.DictReader(csvfile, delimiter=';')
SITE = "" ; STACK = "" ; IP = "" ; IPNAT = "" ; VISIBLENAME = "" ; FQDN = ""

# xml_zabbix_file = open("xml_zabbix_import_file"+"_"+str(numerodoarquivo)+".xml","a+")
# xml_zabbix_file.write (CABECALHO)

for linha in csv_read:
    contador += 1
    if contador == 1:
        xml_zabbix_file = open("xml_zabbix_import_file"+"_"+str(numerodoarquivo)+".xml","a+")
        xml_zabbix_file.write (CABECALHO)

    SITE = linha['SITE'].strip(); STACK = linha['STACK'].strip(); IP = linha['IP'].strip(); IPNAT = linha['IPNAT'].strip(); VISIBLENAME = linha['VISIBLENAME'].strip(); FQDN = linha['FQDN'].strip()

    if STACK == "SIM":
        template = MY_TEMPLATES.get_template("STACK.j2.xml")  # Carrega template stack
        conteudo = template.render(SITE=SITE, STACK=STACK, IP=IP, IPNAT=IPNAT, VISIBLENAME=VISIBLENAME, FQDN=FQDN) # renderiza o template com as variaveis (abra o template para melhor entendimento)
        print(f"Criando entrada de importação para o host {VISIBLENAME}")
        xml_zabbix_file.write("\n")
        xml_zabbix_file.write(conteudo)
        print (f"Entrada criada para o host {VISIBLENAME}")
        if contador == 20:
            xml_zabbix_file.close()
            numerodoarquivo, contador = finaliza_xml_vinte_hosts(numerodoarquivo, RODAPE)
    elif STACK == "NAO":
        templatestack = MY_TEMPLATES.get_template("NO-STACK.j2.xml") # Carrega template sem stack
        conteudo = templatestack.render(SITE=SITE, STACK=STACK, IP=IP, IPNAT=IPNAT, VISIBLENAME=VISIBLENAME, FQDN=FQDN)
        print (f"Criando entrada de importação para o host {VISIBLENAME}")
        xml_zabbix_file.write("\n")
        xml_zabbix_file.write(conteudo)
        print (f"Entrada criada para o host {VISIBLENAME}")
        if contador == 20:
            xml_zabbix_file.close()
            numerodoarquivo, contador = finaliza_xml_vinte_hosts(numerodoarquivo, RODAPE)

xml_zabbix_file.write("\n")
xml_zabbix_file.write(RODAPE)
xml_zabbix_file.close()
csvfile.close()

print ("Arquivo xml_zabbix_import_file"+"_"+str(numerodoarquivo)+".xml, importe os hosts no Zabbix")