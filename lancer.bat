@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo Installation / verification des dependances...
python -m pip install -q --disable-pip-version-check -r requirements.txt
if errorlevel 1 (
  echo Erreur : Python ou pip introuvable. Installe Python depuis python.org en cochant "Add Python to PATH".
  pause
  exit /b 1
)
python -m bourse_bot site
pause
