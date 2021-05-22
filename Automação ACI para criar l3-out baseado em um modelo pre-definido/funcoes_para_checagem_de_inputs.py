from re import match
from re import split as resplit

def eh_um_ipv4(IP):
	"""This beautiful function verifies if a value is an IPv4 or not, if yes returns true,
	otherwise returns false"""
# Primeira condição (primeiro bloco de codigo), verifica se o formato é de um IP,
# se true, quebra o IP e segue para as demais condições (segundo bloco de identação).
	if match("^[0-9]+[.][0-9]+[.][0-9]+[.][0-9]+$", IP):
		FOC, SOC, TOC, FTHOC = IP.split(".")   # Fatiando o IP em octetos...
		if len(FOC) > 3 or len(SOC) > 3 or len(TOC) > 3 or len(FTHOC) > 3:   # Se os octetos possuirem mais do que 3 numeros, retorne false.
			return False
		elif (int(FOC) > 255) or (int(SOC) > 255) or (int(TOC) > 255) or (int(FTHOC) > 255):  # Se os octetos possuirem um numero acima de 255, retorne false.
			return False
		elif (int(FOC) == 0):  # Se primeiro octeto igual a 0, retorne false.
			return False
		else:  # Se não
			return True  # Se der false em todas as condições acima dentro do segundo bloco de identação, o IP é legítimo! retorna true!
	else:  # Se não do primeiro bloco.
		return False  # Retorna false se não for true a condição do primeiro bloco de codigo (primeiro if com regex).


def eh_um_ipv4_com_mascara(IPandMask):
	"""This beautiful function verifies if a value is an IPv4 with mask or not, if yes returns true,
	otherwise returns false"""
# Primeira condição (primeiro bloco de codigo), verifica se o formato é de um IP,
# se true, quebra o IP e segue para as demais condições (segundo bloco de identação).
	if match("^[0-9]+[.][0-9]+[.][0-9]+[.][0-9]+\/[0-9]+$", IPandMask):
		FOC, SOC, TOC, FTHOC, MASK = resplit('[.]|[/]', IPandMask)   # Fatiando o IP em octetos e mascara...
		if len(FOC) > 3 or len(SOC) > 3 or len(TOC) > 3 or len(FTHOC) > 3:   # Se os octetos possuirem mais do que 3 numeros, retorne false.
			return False
		elif (int(FOC) > 255) or (int(SOC) > 255) or (int(TOC) > 255) or (int(FTHOC) > 255):  # Se os octetos possuirem um numero acima de 255, retorne false.
			return False
		elif (int(FOC) == 0):  # Se primeiro octeto igual a 0, retorne false.
			return False
		elif (int(MASK) > 32): # Se mascara maior que 32, retorne false.
			return False
		else:  # Se não
			return True  # Se der false em todas as condições acima dentro do segundo bloco de identação, o IP é legítimo! retorna true!
	else:  # Se não do primeiro bloco.
		return False  # Retorna false se não for true a condição do primeiro bloco de codigo.


def eh_um_asn_privado(ASN):
	"""This beautiful function verifies if a value is an private ASN, if yes returns true,
	otherwise returns false"""
	if match("^64[5][1][2-9]$|^64[5][2-9][0-9]$|^64[6-9][0-9][0-9]$|^65[0-4][0-9][0-9]$|^65[5][0-5][0-9]$|^65[5][6][0-5]$", ASN):
		return True
	else:
		return False


def eh_uma_interface_valida(interface):
	"""This beautiful function verifies if a value is an interface from 1/1 to 1/48, if yes returns true,
	otherwise returns false"""
	if match("^[0-1][/][0-9]$|^[0-1][/][1-4][0-8]$", interface):
		return True
	else:
		return False
