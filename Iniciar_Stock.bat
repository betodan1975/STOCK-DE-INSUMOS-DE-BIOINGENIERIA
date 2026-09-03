@echo off
title Stock de Insumos - API
cd /d "%~dp0api"
set "PYEXE=%~dp0api\.venv\Scripts\python.exe"
echo.
echo  ============================================
echo   Stock de Insumos API
echo  ============================================
echo.
if not exist "%PYEXE%" (
    echo  ERROR: no se encontro el entorno virtual en .venv
    echo  Use el acceso directo "start.bat" en su lugar.
    pause
    exit /b 1
)
echo  Verificando dependencias...
"%PYEXE%" -m pip install -r requirements.txt --quiet --disable-pip-version-check
echo.
echo  Abre el navegador en:  http://localhost:8000/
echo  Usuario: admin   Contrasena: admin1234
echo.
echo  Para detener: cerra esta ventana o Ctrl+C
echo.
start "" cmd /c "timeout /t 2 >nul && start http://localhost:8000/"
"%PYEXE%" -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
echo.
echo  El servidor se detuvo. Si esto fue un error, el mensaje deberia
echo  aparecer arriba.
pause
