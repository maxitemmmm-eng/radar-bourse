@echo off
cd /d "%~dp0"
if not exist "tester_ia.py" (
  echo.
  echo Le dossier n'est pas extrait correctement.
  echo Fais clic droit sur radar_bourse.zip, choisis "Extraire tout",
  echo puis lance ce fichier depuis le dossier extrait.
  echo.
  pause
  exit /b 1
)
set "PY="
python --version >nul 2>nul
if not errorlevel 1 set "PY=python"
if not defined PY (
  py -3 --version >nul 2>nul
  if not errorlevel 1 set "PY=py -3"
)
if not defined PY (
  for /d %%D in ("%LOCALAPPDATA%\Programs\Python\Python3*") do (
    if exist "%%D\python.exe" set PY="%%D\python.exe"
  )
)
if not defined PY (
  echo.
  echo Python est introuvable sur ce PC.
  echo Installe-le depuis https://www.python.org/downloads/
  echo IMPORTANT : coche la case "Add Python to PATH" pendant l'installation.
  echo Ensuite, relance ce fichier.
  echo.
  pause
  exit /b 1
)
chcp 65001 >nul
echo Test de l IA sur 5000 cas reels (5 a 15 minutes)…
%PY% -m pip install -q --disable-pip-version-check -r requirements.txt
%PY% tester_ia.py
pause
