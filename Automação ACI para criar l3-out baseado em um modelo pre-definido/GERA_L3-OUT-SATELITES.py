import json
from jinja2 import Environment
from jinja2 import FileSystemLoader
from funcoes_para_checagem_de_inputs import eh_um_ipv4_com_mascara
from funcoes_para_checagem_de_inputs import eh_um_ipv4
from funcoes_para_checagem_de_inputs import eh_um_asn_privado
from funcoes_para_checagem_de_inputs import eh_uma_interface_valida

MY_TEMPLATES = Environment(loader=FileSystemLoader('templates'), trim_blocks=True)

ESCOLHETENANT = "3"
ESCOLHELEAF = "7"
while ESCOLHETENANT == "3":
    ESCOLHETENANT = input("Escolha um tenant:	\n1 - Tn-CLIENTE (SPO)\n2 - tn-CLIENTE-RJO\n: ")
    if ESCOLHETENANT == "1":
        TENANT = "Tn-CLIENTE"
        template = MY_TEMPLATES.get_template("Hosp_Template_SP_completo.j2.xml")
        while ESCOLHELEAF == "7":
            ESCOLHELEAF = input("Escolha um border leaf: \n1 - 1001\t2 - 1002\n3 - 2001\t4 - 2002\n: ")
            if ESCOLHELEAF == "1":
                LEAFID = "1001"
                ROUTERID = "172.21.98.239"
            elif ESCOLHELEAF == "2":
                LEAFID = "1002"
                ROUTERID = "172.21.98.238"
            elif ESCOLHELEAF == "3":
                LEAFID = "2001"
                ROUTERID = "172.21.98.237"
            elif ESCOLHELEAF == "4":
                LEAFID = "2002"
                ROUTERID = "172.21.98.236"
            else:
                print("Escolha invalida")
                ESCOLHELEAF = "7"
    elif ESCOLHETENANT == "2":
        TENANT = "tn-CLIENTE-RJO"
        template = MY_TEMPLATES.get_template("Hosp_Template_RJ_completo.j2.xml")
        while ESCOLHELEAF == "7":
            ESCOLHELEAF = input("Escolha um border leaf: \n1 - 3001\t2 - 3003\n: ")
            if ESCOLHELEAF == "1":
                LEAFID = "3001"
                ROUTERID = "172.21.226.239"
            elif ESCOLHELEAF == "2":
                LEAFID = "3003"
                ROUTERID = "172.21.226.237"
            else:
                print("Escolha invalida")
                ESCOLHELEAF = "7"
    else:
        ESCOLHETENANT = "3"
        print("Escolha invalida")

ASNCHECK = False
IPLOCALCHECK = False
IPREMOTECHECK = False
INTERFACECHECK = False

while IPLOCALCHECK == False:
	IPLOCALEMASCARA = input("Digite o IP local com mascara, exemplo 10.10.10.1/30: ")
	checagem = eh_um_ipv4_com_mascara(IPLOCALEMASCARA)
	if checagem == False:
		print("Dados inseridos incorretamente, repita a operacao ...")
	else:
		IPLOCALCHECK = True

while IPREMOTECHECK == False:
	BGPEERIP = input("Digite o IP remoto SEM mascara, exemplo 10.10.10.2: ")
	checagem = eh_um_ipv4(BGPEERIP)
	if checagem == False:
		print("Dados inseridos incorretamente, repita a operacao ...")
	else:
		IPREMOTECHECK = True

while ASNCHECK == False:
	ASNREMOTO = input("Digite o ASN remoto: ")
	checagem = eh_um_asn_privado(ASNREMOTO)
	if checagem == False:
		print("Este nao e um numero de ASN privado valido, repita a operacao ...")
	else:
		ASNCHECK = True

while INTERFACECHECK == False:
	LEAFINTERFACE = input("Digite o ID da interface, exemplo 1/1: ")
	checagem = eh_uma_interface_valida(LEAFINTERFACE)
	if checagem == False:
		print("Dados inseridos incorretamente, range 1/0 - 1/48 ...")
	else:
		INTERFACECHECK = True

NOME_DA_LOCALIDADE = str(input("Digite o nome da localidade sem espaços, use _: "))

payload = template.render(ROUTERID=ROUTERID, LEAFID=LEAFID, LEAFINTERFACE=LEAFINTERFACE, NOME_DA_LOCALIDADE=NOME_DA_LOCALIDADE, ASNREMOTO=ASNREMOTO, IPLOCALEMASCARA=IPLOCALEMASCARA, BGPEERIP=BGPEERIP)

xmlfile = open("L3Out_AS"+ASNREMOTO+"_"+NOME_DA_LOCALIDADE+"_config-file.xml","w")
print ("Criando o arquivo"+" L3Out_AS"+ASNREMOTO+"_"+NOME_DA_LOCALIDADE+"_config-file.xml")
xmlfile.write (payload)
xmlfile.close()
