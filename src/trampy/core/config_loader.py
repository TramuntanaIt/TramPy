import os
import sys
import json
from dotenv import load_dotenv
from trampy.core.security import SecretManager

class BaseConfigLoader:
    def __init__(self, filename="config.json"):
        self.base_path = self._get_base_path()
        self.config_file = os.path.join(self.base_path, filename)
        self.security = SecretManager()
        self.data = {}

    def _get_base_path(self):
        if getattr(sys, 'frozen', False):
            return os.path.dirname(sys.executable)
        return os.path.dirname(os.path.abspath(sys.argv[0]))

    def ensure_config_exists(self, default_structure):
        """Si no existeix el fitxer, el crea amb l'estructura donada."""
        if not os.path.exists(self.config_file):
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(default_structure, f, indent=4)
            print(f"⚠️ Fitxer {self.config_file} creat. Configura'l i reinicia.")
            sys.exit(0)

    def load(self):
        # 1. Carregar .env primer (carrega variables al sistema os.environ)
        load_dotenv()

        # 2. Llegir el JSON si existeix
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.data.update(json.load(f))
        
        # 3. PRIORITAT: Si una clau existeix al .env, sobreescriu el JSON
        for key, value in os.environ.items():
            if key not in self.data:
                self.data[key] = value

    def get(self, key, default=None):
        val = self.data.get(key, default)
        if isinstance(val, str):
            return self.security.decrypt(val)
        return val
    
    def encrypt_value(self, text):
        return self.security.encrypt(text)