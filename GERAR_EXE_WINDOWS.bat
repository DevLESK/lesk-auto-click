@echo off
setlocal
cd /d "%~dp0"
echo =====================================
echo   LESK Tools - Compilar EXE Windows
echo =====================================
where py >nul 2>nul
if errorlevel 1 (
  echo Python Launcher nao encontrado. Instale Python 3.12 com py launcher.
  pause
  exit /b 1
)
py -3 -m pip install -r requirements.txt
if errorlevel 1 goto :erro
py -3 -m unittest discover -s tests -v
if errorlevel 1 goto :erro
py -3 -m PyInstaller --clean --noconfirm AutoClick.spec
if errorlevel 1 goto :erro
echo.
echo EXE gerado em dist\AutoClick.exe
echo Nao distribua ate validar as 3 funcoes e as licencas.
pause
exit /b 0
:erro
echo.
echo Falhou a compilacao ou os testes. Nao distribua esta versao.
pause
exit /b 1
