import requests
import json
from re import sub
from re import findall
import warnings
from datetime import datetime
from sys import argv
from Aci_essential import Aci_essential 
from exception_list_DEV_QA import exception_list_DEV_QA as exception_list
warnings.filterwarnings('ignore', message='Unverified HTTPS request')

"""
Script remove o que nao teve endpoint por duas vezes consecutivas
checando o arquivo ultima_consulta_devqa.txt
Recomenda-se agendar a execucao para X dias de forma periodica
Kubernetes removemos o application profile referente ao namespace
Demais removemos o EPG diretamente
A cada remocao e feito backup do fabric com data
A cada remocao e feito backup dos EPGs ou application profiles removidos com data
EPGs ou application profiles que nao desejamos remover mesmo sem enpoints
colocar na lista exception_list_DEV_QA.py
"""

apicip, username, password = argv[1:]		
horariodata_atual = datetime.now()
horariodata_formatada = horariodata_atual.strftime("%d-%m-%Y")
apic_session  = Aci_essential(apicip, username, password)
get_all_endpoints = "uni/.json?query-target=subtree&target-subtree-class=fvCEp&rsp-prop-include=naming-only"
get_all_epgs = "uni/.json?query-target=subtree&target-subtree-class=fvAEPg&rsp-prop-include=naming-only"
all_endpoints = apic_session.get_mo(get_all_endpoints)
all_epgs = apic_session.get_mo(get_all_epgs)
all_dn_with_no_endpoints = []


# Se dentro da excecao, pule o epg. Se nao tem endpoints coloque na lista all_dn_with_no_endpoints.
for epg in all_epgs["imdata"]:
    matchs_exception_list = False
    for item in exception_list:
        if item in epg["fvAEPg"]["attributes"]["dn"]:
            matchs_exception_list = True
    if matchs_exception_list == True:
        continue
    if epg["fvAEPg"]["attributes"]["name"] not in str(all_endpoints):
#        print(f'epg {epg["fvAEPg"]["attributes"]["dn"]} esta vazio')
        all_dn_with_no_endpoints.append(epg["fvAEPg"]["attributes"]["dn"])

# Obs: O nome do epg k8s é o mesmo nos dois tenants k8s, tb e gt.
# Com o if pelo nome do EPG, garantimos que somente quando uma aplicação k8s nao tiver endpoint nos DOIS sites os EPGs serao removidos.

all_dn_with_no_eps_all_tenants = []
all_dn_with_no_eps_k8s = []

# Se nao tem endpoints em nenhum dos dois epgs k8s irmaos e tem K8S no path coloque na lista all_dn_with_no_eps_k8s.
# Se nao tem endpoints, o que restou vai para all_dn_with_no_eps_all_tenants.
for dn in all_dn_with_no_endpoints:
    if "K8S" in dn:
        dn = sub("\/epg\-.*", '', dn)
        all_dn_with_no_eps_k8s.append(dn)
    else:
        all_dn_with_no_eps_all_tenants.append(dn)

epgs_removidos = []
ultima_consulta_str = ""

# Abertura da ultima coleta para confronto.
with open ('ultima_consulta_devqa.txt', 'r') as ultima_consulta:
    for line in ultima_consulta:
        ultima_consulta_str += line

# Backup do fabric
if len(ultima_consulta_str) > 0:
    faz_backup_ACI = {"configExportP":{"attributes":{"dn":"uni/fabric/configexp-defaultOneTime","name":"defaultOneTime",
	"snapshot":"true","targetDn":"","adminSt":"triggered","rn":"configexp-defaultOneTime","status":"created,modified",
	"descr":horariodata_formatada+'_remocao_de_epgs'},"children":[]}}
    apic_session.post_mo("uni/fabric/configexp-defaultOneTime.json", faz_backup_ACI)

# Se epg ou app esta dentro da coleta anterior, deleta o epg ou app e faz um backup com data.
for dn in all_dn_with_no_eps_all_tenants:
    if dn in ultima_consulta_str:
        payload = {"fvAEPg":{"attributes":{"dn":dn,"status":"deleted"},"children":[]}}
        backup = apic_session.get_mo(dn+".json?query-target=self&rsp-subtree=full&rsp-prop-include=config-only")
#        print(f"Efetuando backup do {dn}")
        epg_name = findall('(?<=tn-).*', dn)
        epg_name = sub('\/', '_', epg_name[0])
        file_name = horariodata_formatada+"_"+epg_name+".json"		
        with open (file_name, 'w') as backup_epg:
            backup_epg.write(json.dumps(backup, indent = 4))
#        print(f"Deletando {dn}")
        apic_session.post_mo(dn+".json", payload)
        epgs_removidos.append(dn)			

for dn in all_dn_with_no_eps_k8s:
    if dn in ultima_consulta_str:
        payload = {"fvAp":{"attributes":{"dn":dn,"status":"deleted"},"children":[]}}
        backup = apic_session.get_mo(dn+".json?query-target=self&rsp-subtree=full&rsp-prop-include=config-only")
#        print(f"Efetuando backup do {dn}")
        app_name = findall('(?<=tn-).*', dn)
        app_name = sub('\/', '_', app_name[0]) 
        file_name = horariodata_formatada+"_"+app_name+".json"
        with open (file_name, 'w') as backup_app:
            backup_app.write(json.dumps(backup, indent = 4))
#        print(f"Deletando {dn}")
        apic_session.post_mo(dn+".json", payload)
        epgs_removidos.append(dn)

# Depois de removidos os epgs ou apps removemos da lista mais atual essas entradas,
# deixando somente novos epgs ou apps sem endpoints que serao confrontados
# na proxima consulta.
for epg_app in epgs_removidos:
    try:
        all_dn_with_no_eps_k8s.remove(epg_app)
    except:
        all_dn_with_no_eps_all_tenants.remove(epg_app)


print ("#### ATENCAO: OS EPGS ABAIXO FORAM REMOVIDOS POIS ESTAVAM A 30 DIAS SEM ENDPOINT DESDE A ULTIMA CONSULTA ####")
print(f"Total de EPGs removidos {len(epgs_removidos)}")

for epg_app_removido in epgs_removidos:
    print(epg_app_removido)

print ("#### ATENCAO: OS EPGS ABAIXO SERAO REMOVIDOS DAQUI A 30 DIAS CASO NAO HAJA ENDPOINTS NA PROXIMA CONSULTA ####")
print(f"Total de EPGs que serao removidos {len(all_dn_with_no_eps_k8s)+len(all_dn_with_no_eps_all_tenants)}")

# Escrevemos no arquivo a lista atualizada para ser confrontada na proxima consulta.
with open ('ultima_consulta_devqa.txt', 'w') as ultima_consulta:
    for dn in all_dn_with_no_eps_k8s:
        ultima_consulta.write(dn+"\n")
        print(f'{dn}')
    for dn in all_dn_with_no_eps_all_tenants:
        ultima_consulta.write(dn+"\n")
        print(f'{dn}')

apic_session.logout()
