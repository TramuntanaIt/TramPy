import sys
from trampy.core.logger import setup_custom_logger
from trampy.core.db_client import UniversalDBClient
from config_loader_minew import ProjectConfig
from trampy.connectors.minew_api import MinewAPIClient
from deep_translator import GoogleTranslator

# 1. Configuració inicial i Logger
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
        # Aquí cfg.get ja retorna el password desencriptat automàticament
        api = MinewAPIClient(base_url=cfg.get("MINEW_API_URL"), logger=log)
        db = UniversalDBClient(
            dbServer=cfg.get("MINEW_DB_SERVER"),
            dbName=cfg.get("MINEW_DB_NAME"),
            dbUser=cfg.get("MINEW_DB_USER"),
            dbPass=cfg.get("MINEW_DB_PASS")
        )

        api.login(cfg.get("MINEW_API_USER"), cfg.get("MINEW_API_PASS"))
        
        # --- PAS 2: Buscar botigues actives ---
        botigues = api.get(cfg.get("MINEW_API_STORELIST"), "data", params={"active": 1})
        
        for botiga in botigues:
            store_id = botiga.get("id")
            log.info(f"--- BOTIGA: {botiga.get('name')} (ID: {store_id}) ---")

            params = {"storeId": store_id, "page": 1, "size": 1000}
            llista_sd = api.get(cfg.get("MINEW_API_GETSTOREDATA"), "items", params=params)

            for storeData in llista_sd:
                if storeData.get("actualitzarViaAPI") != "S":
                    continue

                sd_codi_art = storeData.get("codiProducte")
                sd_unitat = storeData.get("unit")
                sd_codi_bot = storeData.get("codiBotiga")
                sd_preu_normaltxt = str(storeData.get("preuNormalTxt", ""))
                sd_preu_ofertatxt = str(storeData.get("preuOfertaTxt", ""))
                
                # SQL: Obtenir preus (Botiga i General)
                db_preu_botiga_normal = None
                db_preu_botiga_oferta = None
                db_preu_general_normal = None
                db_preu_general_oferta = None
                db_descripcioCAT = None
                db_pesVariable = None
                db_categoria = None
                db_grupProducte = None
                db_empresa = cfg.get("MINEW_DB_EMPRESA")

                # Consulta Preu Botiga
                params_sp = [sd_codi_art, sd_unitat, sd_codi_bot, db_empresa]
                cursor = db.execute_stored_procedure("BC_PreuProducteUMBotigaSP", params_sp)
                if cursor:
                    row = cursor.fetchone()
                    if row:
                        db_preu_botiga_normal = row.PreuNormal
                        db_preu_botiga_oferta = row.PreuOferta
                        db_descripcioCAT = row.Descripcio
                        db_empresa = row.Empresa
                        db_pesVariable = row.PesVariable
                        db_categoria = row.Categoria
                        db_grupProducte = row.GrupProducte

                    cursor.close()

                # Consulta Preu General (TIENDA)
                params_tienda = [sd_codi_art, sd_unitat, cfg.get("MINEW_DB_BOTIGA", "TIENDA"), db_empresa]
                cursor = db.execute_stored_procedure("BC_PreuProducteUMBotigaSP", params_tienda)
                if cursor:
                    row = cursor.fetchone()
                    if row:
                        db_preu_general_normal = row.PreuNormal
                        db_preu_general_oferta = row.PreuOferta
                        if db_descripcioCAT is None:
                            db_descripcioCAT = row.Descripcio
                        db_empresa = row.Empresa
                        db_pesVariable = row.PesVariable
                        db_categoria = row.Categoria
                        db_grupProducte = row.GrupProducte
                    cursor.close()

                # Empresa
                api_empresa = db_empresa

                # Pes Variable
                api_pesVariable = db_pesVariable

                # Lògica de selecció de preus
                db_preu_oferta = db_preu_botiga_oferta or db_preu_botiga_normal or db_preu_general_oferta or 0
                db_preu_normal = db_preu_botiga_normal or db_preu_general_normal or 0

                if not db_preu_oferta:
                    db_preu_oferta = db_preu_normal
                    db_preu_normal = 0

                # Format per a l'API
                # api_preu_normal = f"{db_preu_normal:.2f}" if db_preu_normal else ""
                # api_preu_normal_moneda = "€" if api_preu_normal else ""
                api_preu_normaltxt = f"{db_preu_normal:.2f}€" if db_preu_normal else ""
                
                # api_preu_oferta = ""
                # api_preu_oferta_moneda = ""
                api_preu_ofertatxt = ""
                if db_preu_oferta and db_preu_oferta != db_preu_normal:
                    # api_preu_oferta = f"{db_preu_oferta:.2f}"
                    api_preu_ofertatxt = f"{db_preu_oferta:.2f}€"
                    # api_preu_oferta_moneda = "€"

                # Descompte truncat
                api_descompte = ""
                if db_preu_normal and db_preu_oferta and db_preu_normal > db_preu_oferta:
                    dte_real = ((db_preu_normal - db_preu_oferta) / db_preu_normal) * 100
                    api_descompte = f"{int(dte_real)}%"
                    #dte_truncat = int(dte_real * 10) / 10
                    #api_descompte = f"{dte_truncat:.0f}%"

                api_descripcioCAT = db_descripcioCAT or ""
                # api_descripcioFR = storeData.get("descripcioFR") or ""
                api_categoria = db_categoria
                api_grupProducte = db_grupProducte

                # --- LÒGICA DE TRADUCCIÓ ---
                # if api_descripcioCAT and (not api_descripcioFR or api_descripcioFR.strip() == ""):
                #     try:
                #         api_descripcioFR = GoogleTranslator(source='ca', target='fr').translate(api_descripcioCAT)
                #     except Exception as e:
                #         log.error(f"Error traduint {sd_codi_art}: {e}")

                # Comparació de canvis i enviament
                if (sd_preu_normaltxt != api_preu_normaltxt or
                    sd_preu_ofertatxt != api_preu_ofertatxt or
                    # str(storeData.get("preuFinal", "")) != api_preu_oferta or 
                    # str(storeData.get("preuAntic", "")) != api_preu_normal or
                    str(storeData.get("empresa", "")) != api_empresa or
                    str(storeData.get("pesVariable", "")) != api_pesVariable or
                    str(storeData.get("descripcioCAT", "")) != api_descripcioCAT or
                    # str(storeData.get("descripcioFR", "")) != api_descripcioFR or
                    str(storeData.get("categoria", "")) != api_categoria or
                    str(storeData.get("grupProducte", "")) != api_grupProducte or
                    str(storeData.get("descompte", "")) != api_descompte):
                    
                    payload = {
                        "storeId": store_id,
                        "id": storeData.get("id"),
                        "preuOfertaTxt": api_preu_ofertatxt,
                        "preuNormalTxt": api_preu_normaltxt,
                        "descripcioCAT": api_descripcioCAT,
                        "categoria": api_categoria,
                        "grupProducte": api_grupProducte,
                        # "descripcioFR": api_descripcioFR,
                        "descompte": api_descompte,
                        "empresa": api_empresa,
                        "pesVariable": api_pesVariable
                    }
                    
                    api.post(cfg.get("MINEW_API_UPDATEGOODS", "/esl/goods/updateToStore"), data=payload)
                    log.info(f"✅ Actualitzat {sd_codi_art} {sd_unitat} {sd_codi_bot} ({sd_preu_normaltxt} : {sd_preu_ofertatxt}) -> ({api_preu_normaltxt} : {api_preu_ofertatxt}) {api_descripcioCAT}")

    except Exception as e:
        log.error(f"Error en el procés: {e}", exc_info=True)

if __name__ == "__main__":
    # Verifiquem si s'ha demanat encriptació abans de res
    if len(sys.argv) > 1 and sys.argv[1] == "--encrypt":
        mode_encriptacio()
    else:
        executar_sincronitzacio()