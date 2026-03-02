motor_etl/
│
├── core/                   # La "maquinària" que no canvia
│   ├── __init__.py
│   ├── api_client.py       # Gestió de l'API (Login + Requests)
│   └── db_client.py        # Connexió a SQL Server
│
├── connectors/             # Els teus connectors
│   └── minew_api.py        # connector api minew
│
├── projects/               # Els teus encàrrecs concrets
│   └── projecte_actual/    # El projecte que tens ara
│       ├── __init__.py
│       ├── main.py               <-- El punt d'entrada
│       ├── config_projecte.py
│       └── ...
│
├── .env                    # Fitxer per guardar usuaris i claus (NO es puja a GitHub)
└── requirements.txt        # Llibreries necessàries

Projecte_Minew/
│
├── build_app.bat         <-- AQUÍ (a l'arrel)
├── main.py               <-- El punt d'entrada
├── config_projecte.py
├── requirements.txt
├── core/                 <-- Subcarpeta amb els teus mòduls
│   ├── __init__.py
│   ├── config_loader.py
│   └── ...
└── connectors/           <-- Subcarpeta amb l'API
    ├── __init__.py
    └── minew_api.py