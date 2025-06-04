# INSTRUCCIONES PARA INSTALAR LA FUENTE SORIA

## Pasos para completar la instalación:

1. **Descargar la fuente:**
   - Ve a: https://www.fontsquirrel.com/fonts/soria
   - Haz clic en "Download TTF" o "Download" para obtener el archivo ZIP

2. **Extraer y copiar archivos:**
   - Extrae el archivo ZIP descargado
   - Busca los archivos con estas extensiones:
     - `*.ttf` (TrueType Font)
     - `*.woff` (Web Open Font Format)
     - `*.woff2` (Web Open Font Format 2)
   
3. **Colocar en el proyecto:**
   - Copia todos los archivos de fuente a:
     `c:\Users\Jona_\Documents\GitHub\network-analyzer\frontend\public\fonts\`

4. **Nombres esperados de archivos:**
   La configuración busca estos archivos específicos:
   - `soria-regular.ttf` / `soria-regular.woff` / `soria-regular.woff2`
   - `soria-bold.ttf` / `soria-bold.woff` / `soria-bold.woff2`
   - `soria-light.ttf` / `soria-light.woff` / `soria-light.woff2`
   
   Si los nombres son diferentes, renómbralos o actualiza el archivo `soria.css`

## ¿Qué ya está configurado?

✅ Archivo CSS de fuente creado (`public/fonts/soria.css`)
✅ HTML actualizado para cargar la fuente
✅ Tailwind configurado para usar Soria como fuente principal
✅ CSS global actualizado

## Después de copiar los archivos:

La fuente Soria se aplicará automáticamente a toda la aplicación, manteniendo:
- ✅ Todos los pesos de fuente (normal, bold, light)
- ✅ Todos los tamaños existentes
- ✅ Todos los estilos (cursiva, etc.)

¡Solo necesitas descargar y copiar los archivos de fuente!
