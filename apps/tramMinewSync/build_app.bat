@echo off
echo ====================================================
echo    ESTACIO DE MUNTATGE: MINEW SYNC (FORCE CORE)
echo ====================================================

:: 1. Neteja absoluta
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

:: 2. Generacio de l'executable
python -m PyInstaller --onefile --name TramMinewSync --icon LogoTramuntana.ico main.py

echo.
echo ====================================================
echo    FET! Prova ara el .exe de la carpeta dist.
echo ====================================================
pause