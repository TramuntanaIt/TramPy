import sys
from trampy.core.logger import setup_custom_logger
from trampy.core.db_client import UniversalDBClient
from config_loader_minew import ProjectConfig
from trampy.connectors.minew_api import MinewAPIClient
from sync_system import sincronitzar_system
from sync_botigues import sincronitzar_botigues

log = setup_custom_logger("MINEW_SYNC")
cfg = ProjectConfig("config.json")


def mode_encriptacio():
    """Funció per ajudar al client a encriptar les claus des de la terminal."""
    print("\n" + "="*50)
    print("      GENERADOR DE CLAUS SEGURES (MOTOR ETL)")
    print("="*50)
    raw_text = input("\nEscriu el text (password) que vols encriptar: ").strip()

    if raw_text:
        secret = cfg.encrypt_value(raw_text)
        print(f"\n✅ COPIA AIXÒ AL TEU config.json:\n{secret}")
        print("\nNota: Aquesta clau només és vàlida per a aquest servidor.")
    else:
        print("\n❌ No s'ha introduït cap text.")
    print("="*50 + "\n")


def executar_sincronitzacio():
    try:
        api = MinewAPIClient(base_url=cfg.get("MINEW_API_URL"), logger=log)
        db = UniversalDBClient(
            dbServer=cfg.get("MINEW_DB_SERVER"),
            dbName=cfg.get("MINEW_DB_NAME"),
            dbUser=cfg.get("MINEW_DB_USER"),
            dbPass=cfg.get("MINEW_DB_PASS")
        )

        api.login(cfg.get("MINEW_API_USER"), cfg.get("MINEW_API_PASS"))

        sincronitzar_system(api, db, cfg, log)
        sincronitzar_botigues(api, db, cfg, log)

    except Exception as e:
        log.error(f"Error en el procés: {e}", exc_info=True)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--encrypt":
        mode_encriptacio()
    else:
        executar_sincronitzacio()
