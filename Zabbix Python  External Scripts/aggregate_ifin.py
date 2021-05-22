#!/usr/bin/python
# Shebang para o sistema encontrar o interpretador.
# aggregate_ifin.py # Nome do script.

from subprocess import check_output  # Importa a funcao check_output do modulo subprocess.
from re import sub  # Importa a funcao sub do modulo re.
from sys import argv  # Importa a funcao argv do modulo sys, essa funcao ira receber os argumentos passados pelo Zabbix.
from sys import exit  # Importa a funcao exit do modulo sys, essa funcao ira encerrar o script.

# 1    #2 < - valores indexadores recebidos.
IP, COMMUNITY = argv[1:]  # IP recebe argumento index1 e COMMUNITY recebe argumento index2.

saida = check_output(["snmpwalk", "-v2c", "-c", COMMUNITY, IP, "1.3.6.1.2.1.31.1.1.1.6"])  # Executa o comando shell com oid ifHCInOctets.
saida_lista = saida.splitlines()  # Tranforma cada linha de saida em um item da lista saida_lista.
total = int()  # Declaramos a varivel total do tipo numero inteiro.

# Para cada item da lista saida_lista faca: total recebe total + item da lista (regex para limpar a saida e pegar somente o ultimo valor, snmpvalue).
for item in saida_lista:
        total = total + int(sub(".*Counter64: ", "", item))

print(total)  # Print total, zabbix coleta esse retorno.

exit()  # Encerra o script.
