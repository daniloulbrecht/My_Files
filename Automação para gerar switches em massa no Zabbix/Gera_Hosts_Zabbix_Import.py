from jinja2 import Environment
from jinja2 import FileSystemLoader
import csv

# Gera XML com todos os hosts do csv lido

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


xml_zabbix_file = open("xml_zabbix_import_file.xml","w")
xml_zabbix_file.write (CABECALHO)
xml_zabbix_file.close()

csvfile = open("switchs_import.csv","r")
csv_read = csv.DictReader(csvfile, delimiter=';')
SITE = "" ; STACK = "" ; IP = "" ; IPNAT = "" ; VISIBLENAME = "" ; FQDN = ""

for linha in csv_read:
    SITE = linha['SITE'].strip(); STACK = linha['STACK'].strip(); IP = linha['IP'].strip(); IPNAT = linha['IPNAT'].strip(); VISIBLENAME = linha['VISIBLENAME'].strip(); FQDN = linha['FQDN'].strip()
    if STACK == "SIM":
        template = MY_TEMPLATES.get_template("STACK.j2.xml")  # Carrega template stack
        conteudo = template.render(SITE=SITE, STACK=STACK, IP=IP, IPNAT=IPNAT, VISIBLENAME=VISIBLENAME, FQDN=FQDN) # renderiza o template com as variaveis (abra o template para melhor entendimento)
        xml_zabbix_file = open("xml_zabbix_import_file.xml","a+")
        print(f"Criando entrada de importação para o host {VISIBLENAME}")
        xml_zabbix_file.write("\n")
        xml_zabbix_file.write(conteudo)
        xml_zabbix_file.close()
        print (f"Entrada criada para o host {VISIBLENAME}")
    elif STACK == "NAO":
        templatestack = MY_TEMPLATES.get_template("NO-STACK.j2.xml") # Carrega template sem stack
        conteudo = templatestack.render(SITE=SITE, STACK=STACK, IP=IP, IPNAT=IPNAT, VISIBLENAME=VISIBLENAME, FQDN=FQDN)
        xml_zabbix_file = open("xml_zabbix_import_file.xml","a+")
        print (f"Criando entrada de importação para o host {VISIBLENAME}")
        xml_zabbix_file.write("\n")
        xml_zabbix_file.write(conteudo)
        xml_zabbix_file.close()
        print (f"Entrada criada para o host {VISIBLENAME}")

csvfile.close()
xml_zabbix_file = open("xml_zabbix_import_file.xml","a+")
xml_zabbix_file.write("\n")
xml_zabbix_file.write(RODAPE)
xml_zabbix_file.close()
print (f"Arquivo xml_zabbix_import_file.xml finalizado, importe os hosts no Zabbix")
