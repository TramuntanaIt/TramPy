from trampy.core.config_loader import BaseConfigLoader

class ProjectConfig(BaseConfigLoader):
    def __init__(self, filename="config.json"):
        super().__init__(filename)
        
        # Definim l'estructura que volem per a aquest projecte
        plantilla = {
            # Per encriptar els passwords s'ha d'executar l'aplicació amb el paràmetre --encrypt
            "MINEW_API_URL=http": "//api_ip:9194/",
            "MINEW_API_USER": "api_user",
            "MINEW_API_PASS": "enc:api_encrypted_pass",

            "MINEW_API_LOGIN": "action/login",
            "MINEW_API_STORELIST": "esl/store/list?active=1",
            "MINEW_API_DYNAMICFIELDS": "esl/scene/findDongTaiZiDuan",
            "MINEW_API_GETSTOREDATA": "esl/goods/getByStoreId",

            "MINEW_DB_SERVER": "db_ip",
            "MINEW_DB_NAME": "db_name",
            "MINEW_DB_USER": "db_user",
            "MINEW_DB_PASS": "enc:db_encrypted_pass",
            "MINEW_DB_BOTIGA": "db_defaultPriceLocation"            
        }
        
        self.ensure_config_exists(plantilla)
        self.load()