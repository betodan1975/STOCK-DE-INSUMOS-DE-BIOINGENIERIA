@echo off
REM ============================================================
REM Stock de Insumos - Launcher
REM Hace doble click y arranca todo. Si ya esta corriendo, solo
REM abre el navegador.
REM ============================================================
setlocal EnableDelayedExpansion

set "PROJECT_DIR=%~dp0"
set "API_DIR=%PROJECT_DIR%api"
set "VENV_DIR=%API_DIR%\.venv"
set "PYEXE=%VENV_DIR%\Scripts\python.exe"
set "INSTALLED_FLAG=%VENV_DIR%\.installed"
set "URL=http://localhost:8000/"

cd /d "%API_DIR%" 2>nul
if errorlevel 1 (
    echo ERROR: no se encontro la carpeta "%API_DIR%"
    pause
    exit /b 1
)

REM ---- Si la API ya esta corriendo, solo abrir el navegador ----
netstat -ano | findstr "LISTENING" | findstr /C:":8000 " >nul
if !errorlevel! equ 0 (
    echo La API ya esta corriendo. Abriendo el navegador...
    start "" "%URL%"
    exit /b 0
)

REM ---- Crear venv si no existe ----
if not exist "%PYEXE%" (
    echo Creando entorno virtual de Python ^(solo primera vez^)...
    where python >nul 2>nul
    if errorlevel 1 (
        echo.
        echo ERROR: Python no esta instalado o no esta en el PATH.
        echo Bajalo de https://www.python.org/downloads/
        echo IMPORTANTE: durante la instalacion marca la opcion
        echo            "Add Python to PATH".
        echo Despues volve a hacer doble click en este acceso directo.
        echo.
        pause
        exit /b 1
    )
    python -m venv "%VENV_DIR%"
    if errorlevel 1 (
        echo ERROR creando el entorno virtual.
        pause
        exit /b 1
    )
)

REM ---- Instalar dependencias solo la primera vez ----
if not exist "%INSTALLED_FLAG%" (
    echo Instalando dependencias ^(esto puede tardar un rato, solo pasa la primera vez^)...
    "%PYEXE%" -m pip install --upgrade pip
    "%PYEXE%" -m pip install -r "%API_DIR%\requirements.txt"
    if errorlevel 1 (
        echo.
        echo ERROR instalando dependencias. Revisa tu conexion a internet.
        pause
        exit /b 1
    )
    echo OK> "%INSTALLED_FLAG%"
)

REM ---- Inicializar / migrar la base de datos si no existe ----
if not exist "%API_DIR%\stock.db" (
    echo Inicializando base de datos...
    "%PYEXE%" "%API_DIR%\migrate.py"
    "%PYEXE%" "%API_DIR%\reset_admin.py"
)

REM ---- Levantar uvicorn en una ventana minimizada ----
echo Iniciando servidor Stock de Insumos...
start "Stock Insumos API" /MIN "%PYEXE%" -m uvicorn main:app --host 127.0.0.1 --port 8000

REM ---- Esperar a que el puerto este escuchando (max ~20s) ----
set /a tries=0
:wait_loop
"%SystemRoot%\System32\timeout.exe" /t 1 /nobreak >nul 2>nul
if errorlevel 1 ping -n 2 127.0.0.1 >nul
netstat -ano | findstr "LISTENING" | findstr /C:":8000 " >nul
if !errorlevel! equ 0 goto open_browser
set /a tries+=1
if !tries! lss 20 goto wait_loop
echo (!) El servidor tarda mas de lo esperado. Voy a abrir el navegador igual.

:open_browser
start "" "%URL%"

endlocal
exit /b 0
