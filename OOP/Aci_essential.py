import requests
import json
import time
import warnings
warnings.filterwarnings('ignore', message='Unverified HTTPS request')


class Aci_essential:
    """
    Classe com metodos mais utilizados quando interagimos
    via API com ACI.
    Os metodos possuem reconexao automatica em caso de erros
    de expiracao de token ou falha de autorizacao 401-403
    chamando o metodo login.
    Abaixo lista de metodos:
    login
    logout
    get_mo
    get_class
    post_mo (criar, deletar, incrementar ou atualizar managed objects)
    make_fabkp - Faz backup onetime full do fabric e espera completar
    """
    def __init__(self, apicip, username, password):
        self.apicip = apicip
        self.mobaseurl = "https://"+apicip+"/api/node/mo/"
        self.classbaseurl = "https://"+apicip+"/api/node/class/"
        self.username = username
        self.password = password
        self.login()
    def login(self):
        """
        Funcao para criar um sessao API no ACI
        """
        session_api = requests.session()
        payload = {"aaaUser" :{"attributes": {"name": self.username, "pwd": self.password}}}
        loginresponse = session_api.post(url="https://"+self.apicip+"/api/aaaLogin.json",
        data=json.dumps(payload), verify=False)
        if loginresponse.status_code != 200:
            print(json.dumps(loginresponse.json(), indent = 4))
            exit(1)
        else:
#            print("Login efetuado com sucesso")
            self.session = session_api
    def logout(self):
        """
        Funcao para deslogar a sessao API no ACI
        """
        logoutresponse = self.session.post(url= "https://"+self.apicip+"/api/aaaLogout.json",
        verify=False)
        if logoutresponse.status_code != 200:
            print(json.dumps(logoutresponse.json(), indent = 4))
#        else:
#            print("Logout efetuado com sucesso")
    def get_mo(self, get_url):
        """
        Passe o dn da chamada, somente o que vier depois
        de /api/node/mo/... aonde (...) eh o resto da url a ser informada
        como argumento ex: dn.json ou dn.json/?options,filters.

        Exemplo de dns:

        "uni/.json?query-target=subtree&target-subtree-class=fvCEp&rsp-prop-include=naming-only"
        "uni/tn-Tn-PROD-2-GT/ap-APP-PROD/epg-EPG_NAO_REMOVE_GT.json"

        Sera retornado a resposta como json/dicionario.
        """
        result = self.session.get(url = self.mobaseurl+get_url, verify=False)
        if result.status_code == 403 or result.status_code == 401:
            self.login()
            print ("reconectado")
            result = self.session.get(url = self.mobaseurl+get_url, verify=False)
        if result.status_code != 200:
            print(f"Chamada incorreta, status code {str(result.status_code)}")
        else:
            return result.json()
    def get_class(self, get_url):
        """
        Passe a classe da chamada, somente o que vier depois
        de /api/node/class/... aonde (...) eh o resto da url a ser informada
        como argumento ex: classe.json ou classe.json/?options,filters.
        Sera retornado a resposta como json/dicionario.
        """
        result = self.session.get(url = self.classbaseurl+get_url, verify=False)
        if result.status_code == 403 or result.status_code == 401:
            self.login()
            print ("reconectado")
            result = self.session.get(url = self.classbaseurl+get_url, verify=False)
        if result.status_code != 200:
            print(f"Chamada incorreta, status code {str(result.status_code)}")
        else:
            return result.json()
    def post_mo(self, post_url, payload):
        """
        Passe o dn da chamada, somente o que vier depois
        de /api/node/mo/... aonde (...) eh o resto da url a ser informada
        como argumento ex: dn.json.

        Exemplo de dn:
        "uni/tn-Tn-PROD-2-GT/ap-APP-PROD/epg-EPG_NAO_REMOVE_GT.json"

        Passe o payload em forma de dicionario como ultimo parametro.
        """
        result = self.session.post(url = self.mobaseurl+post_url, data=json.dumps(payload),
        verify=False)
        if result.status_code == 403 or result.status_code == 401:
            self.login()
            print ("reconectado")
            result = self.session.post(url = self.mobaseurl+post_url, data=json.dumps(payload),
            verify=False)
        if result.status_code != 200:
            print(f"Chamada incorreta, status code {str(result.status_code)}")
        else:
            return result.json()
    def make_fabkp(self, description):
        """
		Esse metodo faz backup onetime do fabric inteiro.
		Informe a descricao do backup como argumento. O metodo nao encerra ate
		que o backup com a descricao passada seja listado no ACI,
		por isso passe descricoes unicas e nao as repita, sugestao: Sempre
		coloque o horario com segundos na descricao passada ao metodo.
		isso e util em casos de scripting aonde queremos que o backup seja
		completado primeiro para entao seguirmos com as proximas acoes de forma
		segura.
        """
        post_url = "uni/fabric/configexp-defaultOneTime.json"
        payload = {"configExportP":{"attributes":{"dn":"uni/fabric/configexp-defaultOneTime","name":"defaultOneTime",
        "snapshot":"true","targetDn":"","adminSt":"triggered","rn":"configexp-defaultOneTime","status":"created,modified",
        "descr": description},"children":[]}}
        result = self.session.post(url = self.mobaseurl+post_url, data=json.dumps(payload),
        verify=False)
        if result.status_code == 403 or result.status_code == 401:
            self.login()
            print ("reconectado")
            result = self.session.post(url = self.mobaseurl+post_url, data=json.dumps(payload),
            verify=False)
        check_bkp_call = 'configSnapshot.json?query-target-filter=eq(configSnapshot.descr, "{}")'.format(description)
        check_backup_finished = self.session.get(url = self.classbaseurl+check_bkp_call, verify=False).json()
        counter = 0
        while description not in str(check_backup_finished):
            print("fabric backup in progress, please wait ...")
            time.sleep(10)
            counter =+ 1
            check_backup_finished = self.session.get(url = self.classbaseurl+check_bkp_call, verify=False).json()
            if counter > 12:
                raise RuntimeError("O backup demorou mais de 120s para completar ... abortado")

# unit test
if __name__ == "__main__":
    apicip = '192.168.66.50'
    password = '12345678'
    username = 'admin'
    epg_dict_json = {
        "totalCount":"1",
        "imdata":[
            {
                "fvAEPg":{
                    "attributes":{
                        "annotation":"",
                        "descr":"",
                        "dn":"uni/tn-Prod/ap-APP_Prod/epg-teste",
                        "exceptionTag":"",
                        "floodOnEncap":"disabled",
                        "fwdCtrl":"",
                        "hasMcastSource":"no",
                        "isAttrBasedEPg":"no",
                        "matchT":"AtleastOne",
                        "name":"teste",
                        "nameAlias":"",
                        "pcEnfPref":"unenforced",
                        "prefGrMemb":"exclude",
                        "prio":"unspecified",
                        "shutdown":"no"
                    },
                    "children":[
                        {
                            "fvRsCustQosPol":{
                                "attributes":{
                                    "annotation":"",
                                    "tnQosCustomPolName":""
                                }
                            }
                        },
                        {
                            "fvRsBd":{
                                "attributes":{
                                    "annotation":"",
                                    "tnFvBDName":"BD-Prod"
                                }
                            }
                        }
                    ]
                }
            }
        ]
    }
    epg_delete_dict = {"fvAEPg":{"attributes":{"dn":"uni/tn-Prod/ap-APP_Prod/epg-teste","status":"deleted"},"children":[]}}
    my_aci_session = Aci_essential(apicip, username, password)
    all_endpoints = my_aci_session.get_mo("uni/.json?query-target=subtree&target-subtree-class=fvCEp&rsp-prop-include=naming-only")
    all_nodes = my_aci_session.get_class("fabricNode.json")
    my_aci_session.post_mo("uni/tn-Prod/ap-APP_Prod/epg-teste.json", epg_dict_json)
    my_aci_session.post_mo("uni/tn-Prod/ap-APP_Prod/epg-teste.json", epg_delete_dict)
    my_aci_session.logout()
