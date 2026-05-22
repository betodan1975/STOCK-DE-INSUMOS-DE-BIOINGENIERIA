# ============================================================
# Stock de Insumos - Crear acceso directo en el Escritorio
# ============================================================
# Ejecutar UNA SOLA VEZ:
#   1) Click derecho sobre este archivo
#   2) "Run with PowerShell" / "Ejecutar con PowerShell"
#
# Si Windows bloquea la ejecucion, abri PowerShell en esta carpeta y corre:
#   powershell -ExecutionPolicy Bypass -File .\crear_acceso_directo.ps1
# ============================================================

$ErrorActionPreference = "Stop"

# Carpeta donde vive este script (= raiz del proyecto)
$projectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$startBat   = Join-Path $projectDir "start.bat"
$desktop    = [Environment]::GetFolderPath("Desktop")
$lnkPath    = Join-Path $desktop "Stock Insumos.lnk"

if (-not (Test-Path $startBat)) {
    Write-Host ""
    Write-Host "ERROR: no se encontro start.bat en:" -ForegroundColor Red
    Write-Host "  $startBat" -ForegroundColor Red
    Write-Host ""
    Read-Host "Presiona Enter para salir"
    exit 1
}

try {
    $shell = New-Object -ComObject WScript.Shell
    $lnk   = $shell.CreateShortcut($lnkPath)
    $lnk.TargetPath       = $startBat
    $lnk.WorkingDirectory = $projectDir
    # Icono "caja / inventario" del shell32 estandar de Windows. Si no te gusta,
    # podes cambiarlo despues con: click derecho en el acceso directo -> Propiedades -> Cambiar icono.
    $lnk.IconLocation     = "shell32.dll,165"
    $lnk.Description      = "Abrir Stock de Insumos en el navegador"
    $lnk.WindowStyle      = 7   # 7 = minimizado
    $lnk.Save()
}
catch {
    Write-Host ""
    Write-Host "ERROR creando el acceso directo:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-Host ""
    Read-Host "Presiona Enter para salir"
    exit 1
}

Write-Host ""
Write-Host "Listo!" -ForegroundColor Green
Write-Host "Se creo el acceso directo:"
Write-Host "  $lnkPath" -ForegroundColor Cyan
Write-Host ""
Write-Host "De ahora en mas, hace DOBLE CLICK en el icono"
Write-Host "  'Stock Insumos'"
Write-Host "del Escritorio para abrir la app."
Write-Host ""
Read-Host "Presiona Enter para cerrar"
