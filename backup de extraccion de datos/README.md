# Extracción de Datos Web

Aplicación web para extraer datos de múltiples puntos de Telegram con historial en la nube.

## Arquitectura

- **Frontend**: GitHub Pages (HTML, CSS, JavaScript)
- **Backend**: GitHub Actions (Python scripts)
- **Base de Datos**: Supabase (PostgreSQL)
- **Hosting**: 100% gratuito

## Estructura del Proyecto

```
extraccion-datos-web/
├── .github/
│   └── workflows/
│       └── extract.yml          # GitHub Actions
├── src/
│   ├── index.html               # Página principal
│   ├── style.css                # Estilos
│   └── script.js                # Lógica frontend
├── scripts/
│   ├── main.py                  # Script principal
│   ├── telegram_brisas_pdf.py   # Scripts existentes
│   ├── telegram_tortuga_pdf.py
│   └── telegram_cano_pescado_pdf.py
├── requirements.txt             # Dependencias Python
└── README.md                    # Este archivo
```

## Configuración

### 1. Supabase
1. Crea cuenta en [supabase.com](https://supabase.com)
2. Crea nuevo proyecto
3. Ejecuta este SQL en el editor SQL:

```sql
CREATE TABLE extracciones (
    id SERIAL PRIMARY KEY,
    tipo VARCHAR(50) NOT NULL,
    punto VARCHAR(100) NOT NULL,
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE NOT NULL,
    total_ventas INTEGER,
    total_comision INTEGER,
    total_enviar INTEGER,
    estado VARCHAR(20) DEFAULT 'procesando',
    creado_at TIMESTAMP DEFAULT NOW(),
    completado_at TIMESTAMP
);

CREATE TABLE historial (
    id SERIAL PRIMARY KEY,
    extraccion_id INTEGER REFERENCES extracciones(id),
    mensaje TEXT,
    tipo VARCHAR(20) DEFAULT 'info',
    creado_at TIMESTAMP DEFAULT NOW()
);
```

4. Ve a Settings > API y copia:
   - **Project URL** 
   - **anon public key**

### 2. GitHub
1. Fork este repositorio
2. Ve a Settings > Secrets and variables > Actions
3. Agrega estos secrets:
   - `SUPABASE_URL`: Tu URL de Supabase
   - `SUPABASE_KEY`: Tu API key de Supabase
   - `TELEGRAM_API_ID`: Tu API ID de Telegram
   - `TELEGRAM_API_HASH`: Tu API hash de Telegram
   - `TELEGRAM_PHONE`: Tu teléfono de Telegram

### 3. GitHub Pages
1. Ve a Settings > Pages
2. Source: Deploy from a branch
3. Branch: main, folder: /src

## Uso

1. Abre tu GitHub Pages URL
2. Usa el botón "Extraer Todos" para extracción masiva
3. O selecciona puntos individuales
4. Revisa el historial en la parte inferior

## Automatización

Las extracciones se ejecutan automáticamente mediante GitHub Actions, sin necesidad de tener tu PC encendido."# escobar.net" 
"# escobarnet" 
