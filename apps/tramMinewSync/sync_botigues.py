from preus import obtenir_preus_producte


def sincronitzar_botigues(api, db, cfg, log):
    botigues = api.get(cfg.get("MINEW_API_STORELIST"), "data", params={"active": 1})

    for botiga in botigues:
        store_id = botiga.get("id")
        log.info(f"--- BOTIGA: {botiga.get('name')} (ID: {store_id}) ---")
        
        sd_codi_bot = botiga.get("name")
        
        params = {"storeId": store_id, "page": 1, "size": 1000}
        llista_sd = api.get(cfg.get("MINEW_API_GETSTOREDATA"), "items", params=params)
        
        for storeData in llista_sd:
            if storeData.get("actualitzarViaAPI") != "S":
                continue

            sd_codi_art = storeData.get("codiProducte")
            sd_unitat = storeData.get("unit")
            # sd_codi_bot = storeData.get("codiBotiga")
            sd_preu_normaltxt = str(storeData.get("preuNormalTxt", ""))
            sd_preu_ofertatxt = str(storeData.get("preuOfertaTxt", ""))

            preus = obtenir_preus_producte(
                db, sd_codi_art, sd_unitat, sd_codi_bot,
                cfg.get("MINEW_DB_EMPRESA"), cfg.get("MINEW_DB_BOTIGA", "TIENDA")
            )

            if (sd_preu_normaltxt != preus["preu_normaltxt"] or
                    sd_preu_ofertatxt != preus["preu_ofertatxt"] or
                    str(storeData.get("empresa", "")) != preus["empresa"] or
                    str(storeData.get("pesVariable", "")) != preus["pesVariable"] or
                    str(storeData.get("descripcioCAT", "")) != preus["descripcioCAT"] or
                    str(storeData.get("categoria", "")) != preus["categoria"] or
                    str(storeData.get("grupProducte", "")) != preus["grupProducte"] or
                    str(storeData.get("codiBotiga", "")) != preus["codiBotiga"] or
                    str(storeData.get("codiBarres", "")) != preus["codiBarres"] or
                    str(storeData.get("descompte", "")) != preus["descompte"]):

                payload = {
                    "storeId": store_id,
                    "id": storeData.get("id"),
                    "preuOfertaTxt": preus["preu_ofertatxt"],
                    "preuNormalTxt": preus["preu_normaltxt"],
                    "descripcioCAT": preus["descripcioCAT"],
                    "categoria": preus["categoria"],
                    "grupProducte": preus["grupProducte"],
                    "descompte": preus["descompte"],
                    "empresa": preus["empresa"],
                    "pesVariable": preus["pesVariable"],
                    "codiBarres": preus["codiBarres"],
                    "codiBotiga": preus["codiBotiga"]

                }

                api.post(cfg.get("MINEW_API_UPDSTOREDATA", "/esl/goods/updateToStore"), data=payload)
                log.info(f"✅ [{sd_codi_bot}] Actualitzat {sd_codi_art} {sd_unitat} {sd_codi_bot} ({sd_preu_normaltxt} : {sd_preu_ofertatxt}) -> ({preus['preu_normaltxt']} : {preus['preu_ofertatxt']}) {preus['descripcioCAT']}")
