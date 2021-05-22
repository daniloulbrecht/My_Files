from ipaddress import ip_network
import random


def ips_para_hsrp(network, tres_primeiros=True, tres_ultimos=False):
    """ Essa funcao gera ips para uso no hsrp,
    por padrão retorna apenas os 3 primeiros ips e mascara
    """
    net = ip_network(network)
    netip = net.network_address
    mask = net.netmask
    primeiroip, segundoip, tercip = netip + 1, netip + 2, netip + 3
    ultimoip, penultimoip, antepenultimoip = (net.broadcast_address
        - 1, net.broadcast_address - 2, net.broadcast_address - 3)

    if tres_primeiros == True and tres_ultimos == True:
        return (str(mask), str(primeiroip), str(segundoip),
            str(tercip), str(antepenultimoip), str(penultimoip), str(ultimoip))

    elif tres_ultimos == True:
        return str(mask), str(antepenultimoip), str(penultimoip), str(ultimoip)

    else:
        return str(mask), str(primeiroip), str(segundoip), str(tercip)


def gera_lista_ips(network):
    """ Gera uma lista de todos os ips de uma rede (menos rede
    e broadcast)
    """
    net = ip_network(network)
    listadeips = []

    for ip in net.hosts():
        listadeips.append(str(ip))

    return listadeips


def gera_ips_aleatorios(network, ips=3):
    """ Gera uma lista de n ips aleatorios dentro de uma rede,
    o padrão é 3
    """
    net = ip_network(network)
    listadeips = []

    for ip in net.hosts():
        listadeips.append(str(ip))

    random.shuffle(listadeips)
    listadeips = random.sample(listadeips, ips)
    return listadeips


def eh_uma_subnet(network, networklist, result=False, matchednetwork=None):
        """Essa funcao verifica se uma rede é uma subnet de alguma das
        redes de uma lista networklist, caso positivo retorna True e a
        rede correspondente (retorna valor booleano, e rede
        correspondente em str). Caso negativo, retorna False e None
        """
        networkobj = ip_network(network)

        for targetnetwork in networklist:
            targetobg = ip_network(targetnetwork)
            result = networkobj.subnet_of(targetobg)
            #  print (result)
            if result == True:
                matchednetwork = str(targetobg)
                break

        return result, matchednetwork


def eh_uma_supernet(network, networklist, result=False, matchednetworklist=[]):
        """Essa funcao verifica se uma rede é uma supernet de alguma
        das redesde uma lista networklist, caso positivo retorna True
        e a lista de redes correspondentes (retorna valor booleano,
        e rede(s) correspondente(s) em lista). Caso negativo, retorna
        False e None
        """
        networkobj = ip_network(network)

        for targetnetwork in networklist:
            targetobg = ip_network(targetnetwork)

            result = networkobj.supernet_of(targetobg)
            #  print (result)
            if result == True:
                matchednetworklist.append(str(targetobg))

        if matchednetworklist:
            return result, matchednetworklist
        else:
            return result, None


if __name__ == "__main__":
    # Script com exemplos de uso das funções acima!
    rede = input("Digite a rede (exemplo \"192.168.80.0/24\"): ")

    # Exemplos de uso da função gera_ips_aleatorios.
    minhalistaaleatoria = gera_ips_aleatorios(rede, 10)
    print(minhalistaaleatoria)

    minhalistaaleatoria2 = gera_ips_aleatorios(rede)
    print(minhalistaaleatoria2)

    # Exemplo de uso da função gera_lista_ips.
    minhalista = gera_lista_ips(rede)
    print(minhalista)

    # Exemplos de uso da função ips_para_hsrp.
    mascara, pip, sip, tip, antip, penip, ultip = ips_para_hsrp(rede, True, True)
    print(mascara, pip, sip, tip, antip, penip, ultip)

    mascara, pip, sip, tip = ips_para_hsrp(rede)
    print(mascara, pip, sip, tip)

    mascara, antip, penip, ultip = ips_para_hsrp(rede, False, True)
    print(mascara, antip, penip, ultip)

    lista = [
        '10.137.160.0/27',
        '10.137.160.32/27',
        '10.137.160.64/27',
        '10.137.160.96/27',
        '10.137.160.128/25'
        ]

    rede1 = '10.137.160.36/30'
    rede2 = '10.137.160.0/24'
    rede3 = '10.0.0.0/8'

    # Exemplo de uso da função eh_uma_subnet.
    resultado, conflito = eh_uma_subnet(rede3, lista)  # Uma das formas de receber o retorno.
    print(resultado, conflito)

    # Exemplo de uso da função eh_uma_supernet.
    resultado2, conflito2 = eh_uma_supernet(rede2, lista)  # Uma das formas de receber o retorno.
    print (resultado2, conflito2)
