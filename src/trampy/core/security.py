import hashlib
import base64
import socket
from cryptography.fernet import Fernet

class SecretManager:
    def __init__(self):
        self.key = self._generate_machine_key()
        self.cipher = Fernet(self.key)

    def _generate_machine_key(self):
        # Basat en Hostname com hem acordat
        host = socket.gethostname()
        key = hashlib.sha256(host.encode()).digest()
        return base64.urlsafe_b64encode(key)

    def encrypt(self, text: str) -> str:
        """Encripta un text i li posa el prefix 'enc:'"""
        if not text: return ""
        encrypted = self.cipher.encrypt(text.encode()).decode()
        return f"enc:{encrypted}"

    def decrypt(self, text: str) -> str:
        # 1. Comprovació de seguretat: si no és un string, no fem res
        if not isinstance(text, str):
            return text

        # 2. LA CLAU: Sabem que s'ha de desencriptar si té el prefix
        if text.startswith("enc:"):
            try:
                # Treiem els primers 4 caràcters ("enc:") i desencriptem la resta
                encrypted_part = text[4:]
                decrypted_data = self.cipher.decrypt(encrypted_part.encode())
                return decrypted_data.decode()
            except Exception as e:
                # Si falla (per exemple, si el hostname ha canviat), avisem
                return f"[ERROR: No es pot desencriptar el valor]"
        
        # 3. Si no comença per "enc:", el retornem tal qual (és text pla)
        return text