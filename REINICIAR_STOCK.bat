@echo off
title Reiniciar Stock de Insumos
echo ============================================
echo   Reiniciando Stock de Insumos
echo ============================================
echo.
echo Buscando el servidor anterior en el puerto 8000...

set FOUND=0
for /f "tokens=5" %%p in ('netstat -ano ^| findstr ":8000" ^| findstr "LISTENING"') do (
    echo Cerrando proceso anterior ^(PID %%p^)...
    taskkill /F /PID %%p >nul 2>nul
    set FOUND=1
)

if "%FOUND%"=="0" (
    echo No habia ningun servidor corriendo en el puerto 8000.
) else (
    echo Listo, servidor anterior cerrado.
)

echo.
echo Esperando un momento...
timeout /t 2 /nobreak >nul

echo Iniciando el servidor de nuevo...
echo.
call "%~dp0start.bat"
