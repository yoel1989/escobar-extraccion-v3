#!/usr/bin/env python3
"""
Script principal para ejecutar extracciones de datos
"""

import asyncio
import argparse
import json
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Importar scripts de los puntos
import importlib.util

# Cargar variables de entorno
load_dotenv()

# Configurar credenciales por defecto si no están en entorno
os.environ.setdefault('SUPABASE_URL', 'https://grytlszzjoqfhpmxgptx.supabase.co')
os.environ.setdefault('SUPABASE_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdyeXRsc3p6am9xZmhwbXhncHR4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk1MjM3MDYsImV4cCI6MjA4NTA5OTcwNn0.k6TFapvUyMImQIX73T2mxjSyAm2FYmgFEaD6BCIE4Ks')
os.environ.setdefault('API_ID', '26428276')
os.environ.setdefault('API_HASH', '8c871a30eb01e4f6964a2869d5f72b16')
os.environ.setdefault('PHONE', '+573203287256')

# Configuración de puntos
PUNTOS_CONFIG = {
    'brisas': {
        'module': 'telegram_brisas_pdf',
        'script': 'telegram_brisas_pdf.py'
    },
    'tortuga': {
        'module': 'telegram_tortuga_pdf', 
        'script': 'telegram_tortuga_pdf.py'
    },
    'cano_pescado': {
        'module': 'telegram_cano_pescado_pdf',
        'script': 'telegram_cano_pescado_pdf.py'
    },
    'cerritos': {
        'module': 'telegram_cerritos_pdf',
        'script': 'telegram_cerritos_pdf.py'
    },
    'manantiales_1': {
        'module': 'telegram_manantiales_1_pdf',
        'script': 'telegram_manantiales_1_pdf.py'
    },
    'manantiales_2': {
        'module': 'telegram_manantiales_2_pdf',
        'script': 'telegram_manantiales_2_pdf.py'
    },
    'miravalle': {
        'module': 'telegram_miravalle_pdf',
        'script': 'telegram_miravalle_pdf.py'
    },
    'san_miguel': {
        'module': 'telegram_san_miguel_pdf',
        'script': 'telegram_san_miguel_pdf.py'
    },
    'cachicamo': {
        'module': 'telegram_cachicamo_pdf',
        'script': 'telegram_cachicamo_pdf.py'
    },
    'cano_lajas': {
        'module': 'telegram_cano_lajas_pdf',
        'script': 'telegram_cano_lajas_pdf.py'
    },
    'tropezon': {
        'module': 'telegram_tropezon_pdf',
        'script': 'telegram_tropezon_pdf.py'
    }
}

class ExtraccionLogger:
    def __init__(self, extraccion_id):
        self.extraccion_id = extraccion_id
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_KEY')
        
    async def log(self, mensaje, tipo='info'):
        """Enviar log a Supabase"""
        try:
            import requests
            
            url = f"{self.supabase_url}/rest/v1/historial"
            headers = {
                'apikey': self.supabase_key,
                'Authorization': f'Bearer {self.supabase_key}',
                'Content-Type': 'application/json',
                'Prefer': 'return=representation'
            }
            
            data = {
                'extraccion_id': self.extraccion_id,
                'mensaje': mensaje,
                'tipo': tipo
            }
            
            response = requests.post(url, headers=headers, json=data)
            print(f"Log enviado: {mensaje} ({response.status_code})")
            
        except Exception as e:
            print(f"Error enviando log: {e}")

def load_punto_module(punto_name):
    """Cargar dinámicamente el módulo de un punto"""
    config = PUNTOS_CONFIG.get(punto_name)
    if not config:
        raise ValueError(f"Punto no configurado: {punto_name}")
    
    script_path = f"scripts/{config['script']}"
    if not os.path.exists(script_path):
        raise FileNotFoundError(f"Script no encontrado: {script_path}")
    
    spec = importlib.util.spec_from_file_location(config['module'], script_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    return module

async def extract_punto(punto_name, start_date, end_date, logger):
    """Extraer datos de un punto específico"""
    try:
        await logger.log(f"Iniciando extracción de {punto_name}", 'info')
        
        # Cargar módulo del punto
        module = load_punto_module(punto_name)
        
        # Ejecutar extracción
        mensajes = await module.obtener_todos_los_mensajes(start_date, end_date)
        
        if mensajes:
            archivo_pdf, ventas, nombre_sitio = module.crear_pdf(mensajes, start_date, end_date)
            
            await logger.log(f"Extracción de {punto_name} completada: {len(mensajes)} registros", 'success')
            await logger.log(f"PDF generado: {archivo_pdf}", 'info')
            await logger.log(f"Total ventas: ${ventas.get('total_valor', 0):,}", 'info')
            
            return {
                'punto': punto_name,
                'nombre_sitio': nombre_sitio,
                'registros': len(mensajes),
                'pdf': archivo_pdf,
                'ventas': ventas,
                'estado': 'completado'
            }
        else:
            await logger.log(f"No se encontraron mensajes para {punto_name}", 'warning')
            return {
                'punto': punto_name,
                'registros': 0,
                'estado': 'sin_datos'
            }
            
    except Exception as e:
        error_msg = f"Error extrayendo {punto_name}: {str(e)}"
        await logger.log(error_msg, 'error')
        return {
            'punto': punto_name,
            'estado': 'error',
            'error': str(e)
        }

async def main():
    parser = argparse.ArgumentParser(description='Ejecutar extracciones de datos')
    parser.add_argument('--extraccion-id', required=True, help='ID de extracción')
    parser.add_argument('--puntos', required=True, help='Puntos a extraer (separados por coma)')
    parser.add_argument('--start-date', required=True, help='Fecha de inicio (YYYY-MM-DD)')
    parser.add_argument('--end-date', required=True, help='Fecha de fin (YYYY-MM-DD)')
    
    args = parser.parse_args()
    
    # Inicializar logger
    logger = ExtraccionLogger(args.extraccion_id)
    await logger.log("Iniciando proceso de extracción", 'info')
    
    # Parsear puntos
    puntos = [p.strip() for p in args.puntos.split(',')]
    
    await logger.log(f"Puntos a procesar: {', '.join(puntos)}", 'info')
    await logger.log(f"Periodo: {args.start_date} - {args.end_date}", 'info')
    
    # Ejecutar extracciones
    resultados = []
    total_ventas = 0
    total_comision = 0
    total_enviar = 0
    
    for punto in puntos:
        resultado = await extract_punto(punto, args.start_date, args.end_date, logger)
        resultados.append(resultado)
        
        # Acumular totales
        if resultado['estado'] == 'completado':
            ventas = resultado.get('ventas', {})
            total_ventas += ventas.get('total_valor', 0)
            total_comision += ventas.get('total_comision', 0)
            total_enviar += ventas.get('total_a_enviar', 0)
    
    # Generar resumen final
    resumen = {
        'extraccion_id': args.extraccion_id,
        'puntos_procesados': len(puntos),
        'puntos_completados': len([r for r in resultados if r['estado'] == 'completado']),
        'total_registros': sum(r.get('registros', 0) for r in resultados),
        'total_ventas': total_ventas,
        'total_comision': total_comision,
        'total_enviar': total_enviar,
        'resultados': resultados,
        'fecha_inicio': args.start_date,
        'fecha_fin': args.end_date,
        'timestamp': datetime.now().isoformat()
    }
    
    # Guardar resultados
    with open('results.json', 'w') as f:
        json.dump(resumen, f, indent=2, default=str)
    
    await logger.log(f"Extracción completada: {resumen['puntos_completados']}/{resumen['puntos_procesados']} puntos", 'success')
    await logger.log(f"Total general: ${total_ventas:,} ventas, ${total_enviar:,} a enviar", 'info')
    
    # Imprimir resumen
    print("\n" + "="*60)
    print("RESUMEN DE EXTRACCIÓN")
    print("="*60)
    print(f"Extracción ID: {args.extraccion_id}")
    print(f"Puntos procesados: {resumen['puntos_completados']}/{resumen['puntos_procesados']}")
    print(f"Total registros: {resumen['total_registros']}")
    print(f"Total ventas: ${total_ventas:,}")
    print(f"Total comisiones: ${total_comision:,}")
    print(f"Total a enviar: ${total_enviar:,}")
    print("="*60)
    
    for resultado in resultados:
        estado_icon = "✅" if resultado['estado'] == 'completado' else "❌" if resultado['estado'] == 'error' else "⚠️"
        print(f"{estado_icon} {resultado['punto']}: {resultado['estado']} ({resultado.get('registros', 0)} registros)")

if __name__ == "__main__":
    asyncio.run(main())