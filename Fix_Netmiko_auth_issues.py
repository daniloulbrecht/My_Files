"""
28/05/2021
Danilo Nogueira Ulbrecht
Em alguns ambientes a autenticação via TACACS pode falhar e isso causa
a quebra do nosso script.
Abaixo um exemplo para forçar 5 tentativas seguidas de acesso SSH.
"""
from netmiko import Netmiko


def try_netmiko_three_times(fdevice, ntimes):
    contador = 1
    while contador < ntimes + 1:
        try:
            fsshconnection = Netmiko(**fdevice)
            contador = ntimes + 2
        except:
            print(
                f"Tentativa de conexão {contador} falhou, tentando"
                + " conectar novamente ...")
            contador += 1
    if contador == ntimes + 1:
        raise RuntimeError("Numero máximo de tentativas de conexão excedidos")
    return fsshconnection


device = {
    "host": "192.168.255.31",
    "username": "admin",
    "password": "123456",
    "device_type": "cisco_ios",
}

sshconnection = try_netmiko_three_times(device, 5)
output = sshconnection.send_command("sh version")
print(output)
sshconnection.disconnect()
