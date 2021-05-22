import json
from funcoes_para_checagem_de_inputs import eh_um_asn_privado

def CriaSetclauseembranco(TENANT, ASN, DIRECAO, NUMBER):
    CLAUSULATIPOSETIN = {'rtctrlAttrP': {'attributes': {'annotation': '', 'descr': '', 'dn': 'uni/tn-Tn-CLIENTE/attr-Route-Map_AS65113_OUT_Clause_0_set', 'name': 'Route-Map_AS65113_OUT_Clause_0_set', 'nameAlias': ''}}}
    CLAUSULATIPOSETIN['rtctrlAttrP']['attributes']['dn'] = ("uni/tn-{0}/attr-RMap_AS{1}_{2}_{3}_set".format(TENANT, ASN, DIRECAO, NUMBER))
    CLAUSULATIPOSETIN['rtctrlAttrP']['attributes']['name'] = ("RMap_AS{0}_{1}_{2}_set".format(ASN, DIRECAO, NUMBER))
    JSONFILE = (json.dumps(CLAUSULATIPOSETIN, sort_keys=True, indent=4))
    return JSONFILE

def CriaSetclause(TENANT, ASN, DIRECAO, NUMBER):
    if DIRECAO == "IN":
        CLAUSULATIPOSETIN = {'rtctrlAttrP': {'attributes': {'annotation': '', 'descr': '', 'dn': 'uni/tn-tn-CLIENTE-RJO/attr-RMap_AS65101_IN_0_set', 'name': 'qualquernome', 'nameAlias': ''}, 'children': []}}
        CLAUSULATIPOSETIN['rtctrlAttrP']['attributes']['dn'] = ("uni/tn-{0}/attr-RMap_AS{1}_{2}_{3}_set".format(TENANT, ASN, DIRECAO, NUMBER))
        CLAUSULATIPOSETIN['rtctrlAttrP']['attributes']['name'] = ("RMap_AS{0}_{1}_{2}_set".format(ASN, DIRECAO, NUMBER))
        LOCALPREFERENCE = 6666
        while LOCALPREFERENCE not in range (99, 1001):
            LOCALPREFERENCE = input("No momento para clause de IN a unica opção de set nesse script é Local Preference (de 99 a 1000), qual valor gostaria de aplicar nessa clause? (default 300): ") or "300"
            LOCALPREFERENCE = int(LOCALPREFERENCE)
            # recebe LP.
    
        LOCALPREFERENCE = str(LOCALPREFERENCE)  # Converte novamente para string para poder concatenar no final.
        
        CHILDREN = [{'rtctrlSetPref': {'attributes': {'annotation': '', 'descr': '', 'localPref': LOCALPREFERENCE, 'name': '', 'nameAlias': '', 'type': 'local-pref'}}}]
        CLAUSULATIPOSETIN['rtctrlAttrP']['children'] = CHILDREN
        JSONFILE = (json.dumps(CLAUSULATIPOSETIN, sort_keys=True, indent=4))
        return JSONFILE
    else:
        if TENANT == "tn-CLIENTE-RJO":
            ASNLOCAL = "65021"
        else:
            ASNLOCAL = "65011"

        CLAUSULATIPOSETOUT = {'rtctrlAttrP': {'attributes': {'annotation': '', 'descr': '', 'dn': 'uni/tn-tn-CLIENTE-RJO/attr-RMap_AS65101_IN_0_set', 'name': 'qualquernome', 'nameAlias': ''}, 'children': []}}
        CLAUSULATIPOSETOUT['rtctrlAttrP']['attributes']['dn'] = ("uni/tn-{0}/attr-RMap_AS{1}_{2}_{3}_set".format(TENANT, ASN, DIRECAO, NUMBER))
        CLAUSULATIPOSETOUT['rtctrlAttrP']['attributes']['name'] = ("RMap_AS{0}_{1}_{2}_set".format(ASN, DIRECAO, NUMBER))
        TEMPDICT = {'rtctrlSetASPath': {'attributes': {'annotation': '', 'criteria': 'prepend', 'descr': '', 'lastnum': '0', 'name': '', 'nameAlias': '', 'type': 'as-path'}, 'children': []}}
        LISTAKEYCHILDREN1 = []
        LISTAKEYCHILDREN2 = []
        REPEATPREPEND = 666
        while REPEATPREPEND not in range (2, 6):
            REPEATPREPEND = input("No momento para clause de OUT a unica opção de set nesse script é fazer prepending (de 2 a 5). Quantas vezes deseja repetir o prepend (default x2)? ") or "2"
            REPEATPREPEND = int(REPEATPREPEND)
            # recebe prepend.
            
        for i in range (0, REPEATPREPEND):
            LISTAKEYCHILDREN2.append({'rtctrlSetASPathASN': {'attributes': {'annotation': '', 'asn': ASNLOCAL, 'descr': '', 'name': '', 'nameAlias': '', 'order': str(i)}}})

        TEMPDICT['rtctrlSetASPath']['children'] = LISTAKEYCHILDREN2
        LISTAKEYCHILDREN1.append(TEMPDICT)
        CLAUSULATIPOSETOUT['rtctrlAttrP']['children'] = LISTAKEYCHILDREN1
        JSONFILE = (json.dumps(CLAUSULATIPOSETOUT, sort_keys=True, indent=4))
        return JSONFILE

def EscolheTenant(ESCOLHA = "3"):

	while ESCOLHA == "3":

		ESCOLHA = input("Escolha um tenant:	\n1 - Tn-CLIENTE (SPO)\n2 - tn-CLIENTE-RJO\n: ")

		if ESCOLHA == "1":
			TENANT = "Tn-CLIENTE"
			return TENANT
		elif ESCOLHA == "2":
			TENANT = "tn-CLIENTE-RJO"
			return TENANT
		else:
			ESCOLHA = "3"
			print("Escolha invalida")

def CriaMatchclause(TENANT, ASN, DIRECAO, NUMBER, ARQUIVO):

	# criando json e depois vamos mudar alguns values dentro do dicionario aninhado.
	CLAUSULATIPOMATCH = {'rtctrlSubjP': {'attributes': {'annotation': '', 'descr': '', 'dn': 'uni/tn-tn-CLIENTE-RJO/subj-RMap_ASN_IN_0_match', 'name': 'RMap_ASN_IN_0_match', 'nameAlias': ''}, 'children': []}}

	# dicionario         key1          key2       key3          value
	CLAUSULATIPOMATCH['rtctrlSubjP']['attributes']['dn'] = ("uni/tn-{0}/subj-RMap_AS{1}_{2}_{3}_match".format(TENANT, ASN, DIRECAO, NUMBER))
	CLAUSULATIPOMATCH['rtctrlSubjP']['attributes']['name'] = ("RMap_AS{0}_{1}_{2}_match".format(ASN, DIRECAO, NUMBER))

	LISTAKEYCHILDREN = []  # essa lista será adicionada como value da key children do nosso json-dicionario CLAUSULATIPOMATCH.

	for rede in ARQUIVO:  # para cada rede do arquivo, adicione uma entrada dessa rede na lista. Todas as redes depois serão um unico value do tipo lista na key children do dicionario CLAUSULATIPOMATCH.
		if "*" in rede:   # se contem asterisco, selecione yes para aggregate.
			LISTAKEYCHILDREN.append({'rtctrlMatchRtDest': {'attributes': {'aggregate': 'yes', 'annotation': '', 'descr': '', 'ip': rede.strip("*\n"), 'name': '', 'nameAlias': ''}}})
		else:
			LISTAKEYCHILDREN.append({'rtctrlMatchRtDest': {'attributes': {'aggregate': 'no', 'annotation': '', 'descr': '', 'ip': rede.strip(), 'name': '', 'nameAlias': ''}}})

	CLAUSULATIPOMATCH['rtctrlSubjP']['children'] = LISTAKEYCHILDREN  # declaramos o value da key children como sendo a nossa lista inteira LISTAKEYCHILDREN (essa lista possui outros dicionarios dentro).

	JSONFILE = (json.dumps(CLAUSULATIPOMATCH, sort_keys=True, indent=4))  # transformando em json identado em 4 espaços.
	return JSONFILE


TENANT = EscolheTenant()

ASNCHECK = False
while ASNCHECK == False:
	ASN = input("Digite o ASN privado remoto: ")
	checagem = eh_um_asn_privado(ASN)
	if checagem == False:
		print("Este nao e um numero de ASN privado valido, repita a operacao ...")
	else:
		ASNCHECK = True

DIRECAO = "nenhuma"
while (DIRECAO != "IN") and (DIRECAO != "OUT"):
	DIRECAO = input("Digite a direção da route-map, in ou out (default IN): ").upper() or "IN"

NUMBER = 999
while NUMBER not in range (-1, 100):
    NUMBER = input("Digite o numero da clausula de 0 a 100 (default '0'): ") or "0"
    NUMBER = int(NUMBER)
# recebe asn.
    
NUMBER = str(NUMBER)  # Converte novamente para string para poder concatenar no final.


ARQUIVO = open(f"redes{DIRECAO}.txt", "r") # abre arquivo que contem as redes em modo leitura.

print (ARQUIVO.read())  # le o arquivo e exibe na tela.
print("Redes marcadas com * no arquivo serão criadas com a opção aggregate habilitada\n")
RESPOSTA = input(f"O script ira criar a clausula de route-map {DIRECAO} do tipo match com a lista de redes exibida acima, deseja seguir (y/n)? ")

ARQUIVO.seek(0)  # rebobina arquivo.

if RESPOSTA == "n":
	print("Abortando ...")
	exit()

JSONMATCHCLAUSE = CriaMatchclause(TENANT, ASN, DIRECAO, NUMBER, ARQUIVO)
ARQUIVO.close()  # fecha arquivo

GERACLAUSESET = input("\nDeseja criar uma clausula de set customizada? \nObs: Disponivel nesse script apenas as opcoes de prepend para out ou local preference para in.\n y or n (default n): ") or "n"

if GERACLAUSESET == "n":
    JSONSETCLAUSE = CriaSetclauseembranco(TENANT, ASN, DIRECAO, NUMBER)
    print ("Criando o arquivo RMap_AS"+ASN+"_"+DIRECAO+"_"+NUMBER+"_match_config-file.json")
    jsonfile = open("RMap_AS"+ASN+"_"+DIRECAO+"_"+NUMBER+"_match_config-file.json","w")
    jsonfile.write (JSONMATCHCLAUSE)
    jsonfile.close()
    print ("Criando o arquivo RMap_AS"+ASN+"_"+DIRECAO+"_"+NUMBER+"_set_config-file.json")
    jsonfile = open("RMap_AS"+ASN+"_"+DIRECAO+"_"+NUMBER+"_set_config-file.json","w")
    jsonfile.write (JSONSETCLAUSE)
    jsonfile.close()
else:
    JSONSETCLAUSE = CriaSetclause(TENANT, ASN, DIRECAO, NUMBER)
    print ("Criando o arquivo RMap_AS"+ASN+"_"+DIRECAO+"_"+NUMBER+"_match_config-file.json")
    jsonfile = open("RMap_AS"+ASN+"_"+DIRECAO+"_"+NUMBER+"_match_config-file.json","w")
    jsonfile.write (JSONMATCHCLAUSE)
    jsonfile.close()
    print ("Criando o arquivo RMap_AS"+ASN+"_"+DIRECAO+"_"+NUMBER+"_set_config-file.json")
    jsonfile = open("RMap_AS"+ASN+"_"+DIRECAO+"_"+NUMBER+"_set_config-file.json","w")
    jsonfile.write (JSONSETCLAUSE)
    jsonfile.close()
