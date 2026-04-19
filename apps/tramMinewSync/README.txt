Per treballar:

- primer hem de buscar tots els camps personalitzats i guardar-los
- per afegir un "Store Data" nou, omplim els que calguin, però els enviem tots. S'haurà d'iniciar el valor segons el tipus

Per generar executable:

    c:\visualstudiocode\TramPy\apps\TramMinewSync> .\.venv\Scripts\activate
    c:\visualstudiocode\TramPy\apps\TramMinewSync> .\build_app.bat
    c:\visualstudiocode\TramPy\apps\TramMinewSync> python -m PyInstaller --onefile --name TramMinewSync --icon LogoTramuntana.ico main.py

Instalació nova:
    Crear carpeta i posar executable generat abans: 
        C:\VisualStudioCode\TramPy\apps\tramMinewSync\dist\TramMinewSync.exe
    Copiar config.json

Per encriptar una clau de pas:

    minewsync.exe --encrypt

Per crear una estrutura de carpetes del workspace
    tree "ruta" /F /A
