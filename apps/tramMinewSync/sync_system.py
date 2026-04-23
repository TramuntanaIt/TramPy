from preus import obtenir_preus_producte


def sincronitzar_system(api, db, cfg, log):
    log.info("--- SYSTEM DATA ---")

    params = {"page": 1, "size": 1000}
    llista_sd = api.get(cfg.get("MINEW_API_GETSYSTEMDATA"), "rows", params=params)

    for sysData in llista_sd:
        if sysData.get("actualitzarViaAPI") != "S":
            continue

        sd_codi_art = sysData.get("codiProducte")
        sd_unitat = sysData.get("unit")
        sd_preu_normaltxt = str(sysData.get("preuNormalTxt", ""))
        sd_preu_ofertatxt = str(sysData.get("preuOfertaTxt", ""))

        # Sense botiga específica: codi_botiga=None, només consulta preu general
        preus = obtenir_preus_producte(
            db, sd_codi_art, sd_unitat, None,
            cfg.get("MINEW_DB_EMPRESA"), cfg.get("MINEW_DB_BOTIGA", "TIENDA")
        )

        if (sd_preu_normaltxt != preus["preu_normaltxt"] or
                sd_preu_ofertatxt != preus["preu_ofertatxt"] or
                str(sysData.get("empresa", "")) != preus["empresa"] or
                str(sysData.get("pesVariable", "")) != preus["pesVariable"] or
                str(sysData.get("descripcioCAT", "")) != preus["descripcioCAT"] or
                str(sysData.get("categoria", "")) != preus["categoria"] or
                str(sysData.get("grupProducte", "")) != preus["grupProducte"] or
                str(sysData.get("codiBarres", "")) != preus["codiBarres"] or
                str(sysData.get("descompte", "")) != preus["descompte"]):

            payload = {
                "id": sysData.get("id"),
                "preuOfertaTxt": preus["preu_ofertatxt"],
                "preuNormalTxt": preus["preu_normaltxt"],
                "descripcioCAT": preus["descripcioCAT"],
                "categoria": preus["categoria"],
                "grupProducte": preus["grupProducte"],
                "descompte": preus["descompte"],
                "empresa": preus["empresa"],
                "pesVariable": preus["pesVariable"],
                "codiBarres": preus["codiBarres"]
            }

            api.put(cfg.get("MINEW_API_UPDSYSTEMDATA", "/sys/goods/modify"), data=payload)
            log.info(f"✅ [SYS] Actualitzat {sd_codi_art} {sd_unitat} ({sd_preu_normaltxt} : {sd_preu_ofertatxt}) -> ({preus['preu_normaltxt']} : {preus['preu_ofertatxt']}) {preus['descripcioCAT']}")
