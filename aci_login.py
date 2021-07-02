import requests
import json
import warnings
warnings.filterwarnings('ignore', message='Unverified HTTPS request')


def aci_auth_session(fapicip, fuser, fpassword, fcontentype='json'):
    """
    Funcao para criar um sessao API no ACI que ja contem o token
    bem como o content-type das operacoes posteriores (post, put),
    dessa forma nao e necessario repetir esses parametros nas chamadas
    apenas chamar url e payload (body).
    """
    fsession_api = requests.session()
    fpayload = {"aaaUser" :{"attributes": {"name": fuser, "pwd": fpassword}}}
    floginresponse = fsession_api.post(url="https://"+fapicip+"/api/aaaLogin.json", data=json.dumps(fpayload) ,verify=False).json()
    ftoken = floginresponse['imdata'][0]['aaaLogin']['attributes']['token']
    if fcontentype == 'xml':
        fsession_api.headers.update({'APIC-cookie': ftoken, "Content-Type": "application/xml"})
    else:
        fsession_api.headers.update({'APIC-cookie': ftoken, "Content-Type": "application/json"})
    return fsession_api


#def aci_auth_logout()
Em construcao

if __name__ == "__main__":
    user = 'admin'
    password = '12345678'
    ip = '192.168.66.3'
    apic_session = aci_auth_session(ip, user, password)
    bdsdict = apic_session.get(url = 'https://'+ip+'/api/node/mo/uni/tn-DCLessons.json?query-target=children&target-subtree-class=fvBD').json()
    print(json.dumps(bdsdict, indent = 4))
