# INSTRUCCIONES PARA SUBIR A GITHUB LIMPIO

El repositorio actual tiene credenciales en el historial y GitHub lo bloquea.

## OPCIÓN 1: CREAR NUEVO REPOSITORIO

1. **Crea nuevo repositorio** en GitHub: `extraccion-datos-web-v2`
2. **Sube archivos limpios:**
   ```bash
   cd "C:\Users\yoooe\OneDrive\Desktop\backup de extraccion de datos"
   git init
   git remote add origin https://github.com/yoel1989/extraccion-datos-web-v2.git
   git add .
   git commit -m "Sistema web de extracción de datos - versión limpia"
   git push -u origin main
   ```
3. **Configura secrets** en el nuevo repositorio

## OPCIÓN 2: LIMPIAR REPOSITORIO ACTUAL

Si prefieres mantener el mismo repositorio:

1. **Elimina el repositorio actual** en GitHub
2. **Crea uno nuevo** con el mismo nombre
3. **Sigue OPCIÓN 1**

## CREDENCIALES (GUARDAR SEGURAMENTE)

- SUPABASE_URL: https://grytlszzjoqfhpmxgptx.supabase.co
- SUPABASE_KEY: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdyeXRsc3p6am9xZmhwbXhncHR4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk1MjM3MDYsImV4cCI6MjA4NTA5OTcwNn0.k6TFapvUyMImQIX73T2mxjSyAm2FYmgFEaD6BCIE4Ks
- TELEGRAM_API_ID: 26428276
- TELEGRAM_API_HASH: 8c871a30eb01e4f6964a2869d5f72b16
- TELEGRAM_PHONE: +573203287256

## PASOS POSTERIORES

1. Configurar GitHub Pages (Settings > Pages)
2. Configurar Secrets (Settings > Secrets and variables > Actions)
3. Configurar GitHub Actions si es necesario