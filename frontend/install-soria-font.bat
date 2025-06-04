@echo off
echo Descargando fuente Soria...

REM Crear directorio fonts si no existe
if not exist "public\fonts" mkdir "public\fonts"

REM Usar PowerShell para descargar los archivos de fuente
powershell -Command "& {
    $baseUrl = 'https://www.fontsquirrel.com/fonts/download/soria'
    
    Write-Host 'Descargando archivo ZIP de Soria...'
    try {
        Invoke-WebRequest -Uri $baseUrl -OutFile 'soria-font.zip' -UseBasicParsing
        
        Write-Host 'Extrayendo archivos...'
        Expand-Archive -Path 'soria-font.zip' -DestinationPath 'temp-soria' -Force
        
        Write-Host 'Moviendo archivos de fuente...'
        Get-ChildItem -Path 'temp-soria' -Filter '*.ttf' | ForEach-Object {
            Copy-Item $_.FullName -Destination 'public\fonts\'
        }
        Get-ChildItem -Path 'temp-soria' -Filter '*.woff*' | ForEach-Object {
            Copy-Item $_.FullName -Destination 'public\fonts\'
        }
        
        Write-Host 'Limpiando archivos temporales...'
        Remove-Item 'soria-font.zip' -Force
        Remove-Item 'temp-soria' -Recurse -Force
        
        Write-Host 'Fuente Soria instalada correctamente!' -ForegroundColor Green
    }
    catch {
        Write-Host 'Error al descargar la fuente. Por favor descarga manualmente desde:' -ForegroundColor Red
        Write-Host 'https://www.fontsquirrel.com/fonts/soria' -ForegroundColor Yellow
        Write-Host 'Y coloca los archivos .ttf, .woff y .woff2 en public/fonts/' -ForegroundColor Yellow
    }
}"

pause
