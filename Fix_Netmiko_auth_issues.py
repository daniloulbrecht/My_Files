"""
Em alguns ambientes a autenticação via TACACS pode falhar e isso causa
a quebra do nosso script.
Abaixo um exemplo para forçar 3 tentativas seguidas de acesso SSH.
"""
from netmiko import Netmiko

def try_netmiko_three_times(fdevice):
    contador = 1
    while contador < 4:
        try:
            fsshconnection = Netmiko(**fdevice)
            contador = 5
        except:
            print("Tentativa de conexão {} falhou, tentando conectar novamente ..."\
            .format(contador))
            contador += 1

    if contador == 4:
        raise Exception("Numero máximo de tentativas de conexão excedidos, verifique se não há problemas de autenticação.")

    return fsshconnection

device = {
    'host': "192.168.255.31",
    'username': "admin",
    'password': "123456",
    'device_type': "cisco_ios"
    }

sshconnection = try_netmiko_three_times(device)
output = sshconnection.send_command('sh version')
print(output)
sshconnection.disconnect()
