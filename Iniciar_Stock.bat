@echo off
title Stock de Insumos - API
cd /d "%~dp0api"
echo.
echo  ============================================
echo   Stock de Insumos API
echo  ============================================
echo.
echo  Abre el navegador en:  http://localhost:8000/
echo  Usuario: admin   Contrasena: admin1234
echo.
echo  Para detener: cerra esta ventana o Ctrl+C
echo.
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
pause
