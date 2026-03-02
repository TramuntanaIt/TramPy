import requests
import logging

class BaseAPIClient:
    def __init__(self, base_url, logger=None):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.log = logger or logging.getLogger(__name__)

    def _check_response(self, response):
        """Gestiona errors HTTP i retorna el JSON complet."""
        response.raise_for_status()
        return response.json()

    def get(self, endpoint, params=None):
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = self.session.get(url, params=params)
        return self._check_response(response)

    def post(self, endpoint, data=None):
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        # Si no hi ha data, enviem diccionari buit per evitar errors 5000
        json_payload = data if data is not None else {}
        response = self.session.post(url, json=json_payload)
        return self._check_response(response)