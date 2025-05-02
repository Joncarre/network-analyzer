@echo off
echo Instalando dependencias del frontend...

rem Crear proyecto con Vite
npm create vite@latest . -- --template react

rem Instalar dependencias
npm install

rem Instalar Tailwind CSS y sus dependencias
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p

rem Instalar otras dependencias del proyecto
npm install axios react-router-dom @headlessui/react @heroicons/react

echo Configuración del frontend completada!
