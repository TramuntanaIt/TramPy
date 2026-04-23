def obtenir_preus_producte(db, codi_art, unitat, codi_botiga, empresa_cfg, botiga_general):
    """
    Consulta preus a la BD i retorna un dict amb els valors calculats i formatats.
    Si codi_botiga és None, s'omet la consulta de preu específic de botiga.
    """
    preu_botiga_normal = None
    preu_botiga_oferta = None
    preu_general_normal = None
    preu_general_oferta = None
    descripcioCAT = None
    pesVariable = None
    categoria = None
    grupProducte = None
    empresa = empresa_cfg
    botiga = None
    codiBarres = None

    if codi_botiga:
        cursor = db.execute_stored_procedure("BC_PreuProducteUMBotigaSP", [codi_art, unitat, codi_botiga, empresa])
        if cursor:
            row = cursor.fetchone()
            if row:
                preu_botiga_normal = row.PreuNormal
                preu_botiga_oferta = row.PreuOferta
                descripcioCAT = row.Descripcio
                empresa = row.Empresa
                pesVariable = row.PesVariable
                categoria = row.Categoria
                grupProducte = row.GrupProducte
                if preu_botiga_normal or preu_botiga_oferta:
                    botiga = row.Botiga
                codiBarres = row.codiBarres
            cursor.close()

    cursor = db.execute_stored_procedure("BC_PreuProducteUMBotigaSP", [codi_art, unitat, botiga_general, empresa])
    if cursor:
        row = cursor.fetchone()
        if row:
            preu_general_normal = row.PreuNormal
            preu_general_oferta = row.PreuOferta
            if descripcioCAT is None:
                descripcioCAT = row.Descripcio
            empresa = row.Empresa
            pesVariable = row.PesVariable
            categoria = row.Categoria
            grupProducte = row.GrupProducte
            botiga = row.Botiga
            codiBarres = row.codiBarres
        cursor.close()

    preu_oferta = preu_botiga_oferta or preu_botiga_normal or preu_general_oferta or 0
    preu_normal = preu_botiga_normal or preu_general_normal or 0

    if not preu_oferta:
        preu_oferta = preu_normal
        preu_normal = 0

    preu_normaltxt = f"{preu_normal:.2f}€" if preu_normal else ""

    preu_ofertatxt = ""
    if preu_oferta and preu_oferta != preu_normal:
        preu_ofertatxt = f"{preu_oferta:.2f}€"

    descompte = ""
    if preu_normal and preu_oferta and preu_normal > preu_oferta:
        dte_real = ((preu_normal - preu_oferta) / preu_normal) * 100
        descompte = f"{int(dte_real)}%"

    botigatxt = botiga if botiga != botiga_general else ""

    return {
        "preu_normaltxt": preu_normaltxt,
        "preu_ofertatxt": preu_ofertatxt,
        "descompte": descompte,
        "descripcioCAT": descripcioCAT or "",
        "empresa": empresa or "",
        "pesVariable": pesVariable or "",
        "categoria": categoria,
        "grupProducte": grupProducte,
        "codiBotiga": botigatxt,
        "codiBarres": codiBarres
    }
