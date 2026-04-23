import hashlib
import json
import requests
from trampy.core.api_client import BaseAPIClient

class MinewAPIClient(BaseAPIClient):
    def __init__(self, base_url, logger=None):
        # Cridem al pare passant-li el logger
        super().__init__(base_url, logger=logger)    
    
    def request_data(self, method, endpoint, data_key="data", **kwargs):
        """
        method: 'get' o 'post'
        endpoint: l'adreça de l'API
        data_key: la clau del JSON que volem retornar (per defecte 'data')
        kwargs: params, json, etc.
        """
        # Cridem al mètode original del Core
        response_json = getattr(super(), method)(endpoint, **kwargs)
        
        internal_code = response_json.get("code")
        total_count = response_json.get("totalCount") or response_json.get("totalNum") or None
        # if internal_code != 200 or total_count == None or total_count == 0:
        if internal_code == 200 or (total_count is not None and total_count > 0):
            # Retornem la clau específica que ens han demanat (data, items, etc.)
            return response_json.get(data_key)
        else:
            msg = response_json.get("msg", "Error desconegut")
            self.log.error(f"API Error (Codi {internal_code}): {msg}")
            raise Exception(f"API Error: {msg}")

    def get(self, endpoint, data_key="data", params=None):
        return self.request_data('get', endpoint, data_key=data_key, params=params)

    def post(self, endpoint, data_key="data", data=None):
        return self.request_data('post', endpoint, data_key=data_key, data=data)

    def put(self, endpoint, data_key="data", data=None):
        return self.request_data('put', endpoint, data_key=data_key, data=data)

    def login(self, username, password):
        """
        Autentica l'usuari i guarda el token a la sessió.
        """
        login_url = f"{self.base_url}/action/login"
        password_md5 = hashlib.md5(password.encode('utf-8')).hexdigest()
        
        # Payload net segons la documentació (username, no loginname)
        payload = {
            "username": username, 
            "password": password_md5
        }

        # Headers mínims necessaris que hem validat
        headers = {
            "Content-Type": "application/json",
            "Accept": "*/*",
            "User-Agent": "PostmanRuntime/7.32.3"
        }

        try:
            # Fem la petició de login
            response = self.session.post(login_url, json=payload, headers=headers)
            response.raise_for_status()
            res_json = response.json()
            
            if res_json.get("code") == 200:
                data = res_json.get("data", {})
                token = data.get("token")
                
                # Un cop tenim el token, el fixem per a totes les futures crides
                # Aquí sí que afegim el charset:utf-8 necessari per a l'API
                self.session.headers.update({
                    "token": token,
                    "Content-Type": "application/json;charset=utf-8",
                    "Accept": "application/json"
                })
                self.log.info(f"Usuari '{username}' autenticat correctament.")
                return True
            else:
                self.log.error(f"Error d'autenticació: {res_json.get('msg')}")
                return False

        except Exception as e:
            self.log.error(f"Error crític en el procés de login: {e}")
            return False