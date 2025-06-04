# Script para descargar fuente Soria
Write-Host "Descargando fuente Soria..." -ForegroundColor Green

try {
    # Crear directorio si no existe
    if (!(Test-Path "public\fonts")) {
        New-Item -ItemType Directory -Path "public\fonts" -Force
    }
    
    # URL de descarga de Font Squirrel
    $downloadUrl = "https://www.fontsquirrel.com/fonts/download/soria"
    
    Write-Host "Descargando desde Font Squirrel..."
    Invoke-WebRequest -Uri $downloadUrl -OutFile "soria-font.zip" -UseBasicParsing
    
    Write-Host "Extrayendo archivos..."
    Expand-Archive -Path "soria-font.zip" -DestinationPath "temp-soria" -Force
    
    # Copiar archivos de fuente
    Write-Host "Copiando archivos de fuente..."
    Get-ChildItem -Path "temp-soria" -Filter "*.ttf" | Copy-Item -Destination "public\fonts\"
    Get-ChildItem -Path "temp-soria" -Filter "*.woff*" | Copy-Item -Destination "public\fonts\"
    
    # Limpiar archivos temporales
    Remove-Item "soria-font.zip" -Force
    Remove-Item "temp-soria" -Recurse -Force
    
    Write-Host "¡Fuente Soria instalada correctamente!" -ForegroundColor Green
}
catch {
    Write-Host "Error al descargar automáticamente. Por favor:" -ForegroundColor Red
    Write-Host "1. Ve a https://www.fontsquirrel.com/fonts/soria" -ForegroundColor Yellow
    Write-Host "2. Descarga el archivo ZIP" -ForegroundColor Yellow
    Write-Host "3. Extrae los archivos .ttf, .woff y .woff2" -ForegroundColor Yellow
    Write-Host "4. Cópialos a public/fonts/" -ForegroundColor Yellow
}
