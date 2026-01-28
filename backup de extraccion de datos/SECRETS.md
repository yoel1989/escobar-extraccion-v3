# Extracción de Datos Web - Lista de Configuración

## Secrets para GitHub

Debes agregar estos valores en tu repositorio GitHub:

1. Ve a **Settings > Secrets and variables > Actions**
2. Haz clic en **New repository secret** para cada uno:

### Secrets necesarios:

```
SUPABASE_URL
https://grytlszzjoqfhpmxgptx.supabase.co

SUPABASE_KEY
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdyeXRsc3p6am9xZmhwbXhncHR4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk1MjM3MDYsImV4cCI6MjA4NTA5OTcwNn0.k6TFapvUyMImQIX73T2mxjSyAm2FYmgFEaD6BCIE4Ks

TELEGRAM_API_ID
26428276

TELEGRAM_API_HASH
8c871a30eb01e4f6964a2869d5f72b16

TELEGRAM_PHONE
+573203287256
```

## Proceso de Subida:

1. **Crea el repositorio** en GitHub
2. **Sube todos los archivos**
3. **Agrega los secrets** (arriba)
4. **Activa GitHub Pages**:
   - Settings > Pages
   - Source: Deploy from a branch
   - Branch: main
   - Folder: /src
5. **Listo!** Tu web estará en: `https://[username].github.io/[reponame]`

## Base de Datos Supabase:

Tu projecto ya está configurado en:
- URL: https://grytlszzjoqfhpmxgptx.supabase.co
- Las tablas se crearán automáticamente con el primer uso

## Notas Importantes:

- Los scripts ya tienen tus credenciales de Telegram
- La web es 100% funcional al subirla
- No necesitas tu PC encendido
- Todo funciona en la nube gratuita