import asyncio
from telethon import TelegramClient
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import re

# CONFIGURACIÓN - RELLENA ESTO!
API_ID = 26428276
API_HASH = '8c871a30eb01e4f6964a2869d5f72b16'
PHONE = '+573203287256'
GROUP_ID = -4742063053

# PRECIOS Y COMISIONES DE LOS PINES
PRECIOS_PINES = {
    "1Hora": 2000,
    "1Dia": 10000,
    "15Dias": 25000,
    "30Dias": 45000
}

COMISIONES_POR_PIN = {
    "1Hora": 500,
    "1Dia": 500,
    "15Dias": 500,
    "30Dias": 5000
}

def calcular_comision_alcanza(total_ventas):
    """Calcula la comisión por alcanzar metas"""
    if total_ventas >= 1000000:
        return 100000
    elif total_ventas >= 500000:
        return 50000
    else:
        return 0

async def obtener_todos_los_mensajes(fecha_inicio, fecha_fin):
    """Conecta a Telegram y obtiene TODOS los mensajes entre fechas"""
    client = TelegramClient('session_name', API_ID, API_HASH)
    
    await client.start(phone=PHONE)
    print("[OK] Conectado a Telegram")
    
    try:
        # Convertir fechas a datetime
        inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d')
        fin = datetime.strptime(fecha_fin, '%Y-%m-%d')
        
        # Obtener el grupo/canal
        entity = await client.get_entity(GROUP_ID)
        
        print(f"[FECHA] Buscando TODOS los mensajes del {fecha_inicio} al {fecha_fin}...")
        
        todos_los_mensajes = []
        mensajes_procesados = []
            
            # Obtener todos los mensajes primero
      # Obtener todos los mensajes primero
        async for message in client.iter_messages(entity):
            if not message.text:
                continue
                
            message_date = message.date.astimezone().replace(tzinfo=None)
            
            # Si la fecha es anterior al inicio, salir del loop
            if message_date.date() < inicio.date():
                break
                
            # Si está dentro del rango, procesar (INCLUYENDO las fechas exactas)
            if message_date.date() >= inicio.date() and message_date.date() <= fin.date():
                mensaje_texto = message.text
                
                # EXCLUIR solo mensajes con "Desconectado"
                if "Desconectado" in mensaje_texto or "desconectado" in mensaje_texto:
                    continue
                
                # PROCESAR TODOS los demás mensajes sin importar el formato
                datos = extraer_datos_flexible(mensaje_texto)
                if datos:
                    # FILTRAR ADICIONALMENTE por la fecha dentro del mensaje
                    if datos['fecha'] != "SIN FECHA":
                        try:
                            fecha_mensaje = datetime.strptime(datos['fecha'], '%Y-%m-%d')
                            if inicio.date() <= fecha_mensaje.date() <= fin.date():
                                mensajes_procesados.append(datos)
                                todos_los_mensajes.append(mensaje_texto)
                        except:
                            # Si no puede parsear la fecha, incluir por defecto
                            mensajes_procesados.append(datos)
                            todos_los_mensajes.append(mensaje_texto)
                    else:
                        # Si no tiene fecha, incluir por defecto
                        mensajes_procesados.append(datos)
                        todos_los_mensajes.append(mensaje_texto)
        
        print(f"[MENSAJE] Total de mensajes encontrados: {len(todos_los_mensajes)}")
        print(f"[DATOS] Mensajes procesados (excluyendo 'Desconectado'): {len(mensajes_procesados)}")
        
        return mensajes_procesados
        
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        return []
    finally:
        await client.disconnect()

def extraer_datos_flexible(mensaje):
    """Extrae datos de CUALQUIER mensaje - Versión ultra flexible"""
    if not mensaje:
        return None
    
    # EXCLUIR mensajes con "Desconectado" (por si acaso)
    if "Desconectado" in mensaje or "desconectado" in mensaje:
        return None
    
    # Intentar extraer código (siempre al inicio)
    codigo_match = re.match(r'^(\w+)', mensaje)
    if not codigo_match:
        return None
    
    codigo = codigo_match.group(1)
    
# Intentar extraer ubicación (buscar después del código) - MEJORADO
    ubicacion = "SIN UBICACIÓN"
    # Buscar patrones como "Conectado en CANO LAJAS hora: 19:32:06"
    # Se detiene antes de "hora:", "fecha:", "tiempo:" o números
    ubicacion_match = re.search(r'(?:Conectado en|en)\s+([A-Za-z0-9_\s]+?)(?=\s+hora:|\s+fecha:|\s+tiempo:|\s+\d{4}-|\s+\d{1,2}:|\s*$)', mensaje)
    if ubicacion_match:
        ubicacion = ubicacion_match.group(1).strip()
    
    # Intentar extraer hora (formato HH:MM:SS)
    hora = "SIN HORA"
    hora_match = re.search(r'(\d{1,2}:\d{2}:\d{2})', mensaje)
    if hora_match:
        hora = hora_match.group(1)
    
    # Intentar extraer fecha (formato YYYY-MM-DD)
    fecha = "SIN FECHA"
    fecha_match = re.search(r'(\d{4}-\d{1,2}-\d{1,2})', mensaje)
    if fecha_match:
        fecha = fecha_match.group(1)
    
    # Intentar extraer tiempo (cualquier formato)
    tiempo = "00:00:00"
    tiempo_match = re.search(r'Tiempo:\s*([\w:.]+)', mensaje)
    if tiempo_match:
        tiempo = tiempo_match.group(1)
    else:
        # Buscar cualquier patrón que parezca tiempo
        tiempo_match = re.search(r'(\d+[whdms]?\d*[:.]?\d*[:.]?\d*)', mensaje)
        if tiempo_match:
            tiempo = tiempo_match.group(1)
    
# Convertir tiempo a formato estándar si es necesario
    tiempo_convertido = convertir_tiempo_formato(tiempo)
    
    return {
        'codigo': codigo,
        'ubicacion': ubicacion,
        'hora': hora,
        'fecha': fecha,
        'tiempo_original': tiempo,
        'tiempo': tiempo_convertido,
        'mensaje_original': mensaje[:100]  # Guardar parte del mensaje original para debug
    }

def convertir_tiempo_formato(tiempo_str):
    """Convierte cualquier formato de tiempo a horas"""
    if not tiempo_str:
        return "00:00:00"
    
    # Si ya está en formato HH:MM:SS, retornar tal cual
    if re.match(r'^\d{1,2}:\d{2}:\d{2}$', tiempo_str):
        return tiempo_str
    
    # Procesar formatos como "4w2d00:00:00", "1d00:00:00", etc.
    try:
        # Intentar extraer semanas, días, horas, minutos, segundos
        total_horas = 0
        total_minutos = 0
        total_segundos = 0
        
        # Buscar semanas
        semanas_match = re.search(r'(\d+)w', tiempo_str)
        if semanas_match:
            total_horas += int(semanas_match.group(1)) * 7 * 24
        
        # Buscar días
        dias_match = re.search(r'(\d+)d', tiempo_str)
        if dias_match:
            total_horas += int(dias_match.group(1)) * 24
        
        # Buscar horas:minutos:segundos
        tiempo_match = re.search(r'(\d{1,2}):(\d{2}):(\d{2})', tiempo_str)
        if tiempo_match:
            total_horas += int(tiempo_match.group(1))
            total_minutos += int(tiempo_match.group(2))
            total_segundos += int(tiempo_match.group(3))
        
        # Si no encontramos formato específico, asumir que es horas
        if total_horas == 0 and total_minutos == 0 and total_segundos == 0:
            # Intentar extraer solo números
            numeros_match = re.findall(r'\d+', tiempo_str)
            if numeros_match:
                total_horas = int(numeros_match[0])
        
        # Para tiempos largos, asignar categorías
        if total_horas >= 24 * 30:  # 30 días o más
            return "720:00:00"  # 30 días en horas
        elif total_horas >= 24:     # 1 día o más
            return "24:00:00"
        elif total_horas == 1:
            return "01:00:00"
        elif total_horas == 2:
            return "02:00:00"
        elif total_horas == 3:
            return "03:00:00"
        else:
            return f"{total_horas:02d}:{total_minutos:02d}:{total_segundos:02d}"
            
    except:
        # Si falla la conversión, devolver 1 hora por defecto
        return "01:00:00"

def obtener_nombre_sitio(datos):
    """Obtiene el nombre del sitio más común de los mensajes procesados"""
    if not datos:
        return "SITIO DESCONOCIDO"
    
    ubicaciones = {}
    for item in datos:
        ubicacion = item['ubicacion']
        if ubicacion != "SIN UBICACIÓN":
            if ubicacion in ubicaciones:
                ubicaciones[ubicacion] += 1
            else:
                ubicaciones[ubicacion] = 1
    
    if ubicaciones:
        # Devolver la ubicación más común
        return max(ubicaciones, key=ubicaciones.get)
    else:
        return "SITIO DESCONOCIDO"

def calcular_ventas_y_comisiones(datos):
    """Calcula ventas, comisiones y totales"""
    ventas_por_tipo = {}
    total_ventas = 0
    total_valor = 0
    total_comision = 0
    
    for item in datos:
        tiempo = item['tiempo']
        
# Determinar el tipo de PIN basado en el tiempo convertido
        if tiempo == "01:00:00" or tiempo.startswith("01:"):
            tipo_pin = "1Hora"
            precio = PRECIOS_PINES["1Hora"]
            comision = COMISIONES_POR_PIN["1Hora"]
        elif tiempo == "24:00:00" or (tiempo.startswith("24:") and int(tiempo.split(':')[0]) == 24):
            tipo_pin = "1Dia"
            precio = PRECIOS_PINES["1Dia"]
            comision = COMISIONES_POR_PIN["1Dia"]
        elif tiempo == "360:00:00" or (tiempo.startswith("360:") or (24 * 15 <= int(tiempo.split(':')[0]) < 24 * 30)):
            tipo_pin = "15Dias"
            precio = PRECIOS_PINES["15Dias"]
            comision = COMISIONES_POR_PIN["15Dias"]
        elif tiempo == "720:00:00" or (tiempo.startswith("720:") or int(tiempo.split(':')[0]) >= 24 * 30):
            tipo_pin = "30Dias"
            precio = PRECIOS_PINES["30Dias"]
            comision = COMISIONES_POR_PIN["30Dias"]
        else:
            # Para otros tiempos, usar 1 hora por defecto
            tipo_pin = "1Hora"
            precio = PRECIOS_PINES["1Hora"]
            comision = COMISIONES_POR_PIN["1Hora"]
        
        # Actualizar contadores
        if tipo_pin in ventas_por_tipo:
            ventas_por_tipo[tipo_pin]['cantidad'] += 1
            ventas_por_tipo[tipo_pin]['valor_total'] += precio
            ventas_por_tipo[tipo_pin]['comision_total'] += comision
        else:
            ventas_por_tipo[tipo_pin] = {
                'cantidad': 1,
                'valor_total': precio,
                'comision_total': comision
            }
        
        total_ventas += 1
        total_valor += precio
        total_comision += comision
    
    # Calcular comisión por alcanzar metas
    comision_alcanza = calcular_comision_alcanza(total_valor)
    total_a_enviar = total_valor - total_comision - comision_alcanza
    
    return {
        'ventas_por_tipo': ventas_por_tipo,
        'total_ventas': total_ventas,
        'total_valor': total_valor,
        'total_comision': total_comision,
        'comision_alcanza': comision_alcanza,
        'total_a_enviar': total_a_enviar
    }

def crear_tabla_resumen(ventas_calculadas, fecha_inicio, fecha_fin, nombre_sitio):
    """Crea la tabla de resumen financiero con columnas ajustadas"""
    styles = getSampleStyleSheet()
    
    titulo_style = ParagraphStyle(
        'TituloStyle', 
        parent=styles['Heading1'],
        alignment=TA_CENTER,
        textColor=colors.darkblue,
        spaceAfter=15
    )
    
    subtitulo_style = ParagraphStyle(
        'SubtituloStyle',
        parent=styles['Heading2'],
        alignment=TA_CENTER,
        textColor=colors.darkred,
        spaceAfter=20
    )
    
    elementos = []
    
    # Título principal con nombre del sitio
    titulo = Paragraph(f"REPORTE FINANCIERO - {nombre_sitio}", titulo_style)
    elementos.append(titulo)
    
    # Subtítulo con período
    subtitulo = Paragraph(f"Período: {fecha_inicio} a {fecha_fin}", subtitulo_style)
    elementos.append(subtitulo)
    
    elementos.append(Spacer(1, 25))
    
    # Tabla de resumen financiero con columnas más anchas
    tabla_resumen = [['TIPO DE PIN', 'TOTAL PINES', 'VALOR', 'VALOR COMISION']]
    
# Tipos de PIN en el orden específico
    tipos_pin_orden = ["1Hora", "1Dia", "15Dias", "30Dias"]
    
    for tipo_pin in tipos_pin_orden:
        if tipo_pin in ventas_calculadas['ventas_por_tipo']:
            datos = ventas_calculadas['ventas_por_tipo'][tipo_pin]
            tabla_resumen.append([
                tipo_pin,
                str(datos['cantidad']),
                f"$ {datos['valor_total']:,}",
                f"$ {datos['comision_total']:,}"
            ])
        else:
            tabla_resumen.append([
                tipo_pin,
                "0",
                "-",
                "-"
            ])
    
    # Línea de totales
    tabla_resumen.append(['', '', '', ''])
    tabla_resumen.append([
        '',
        '',
        f"$ {ventas_calculadas['total_valor']:,}",
        f"$ {ventas_calculadas['total_comision']:,}"
    ])
    
    # Comisión por alcanzar metas
    tabla_resumen.append(['', '', 'COMISION ALCANZADA', f"$ {ventas_calculadas['comision_alcanza']:,}"])
    
    # Total a enviar
    tabla_resumen.append(['', '', 'TOTAL A ENVIAR', f"$ {ventas_calculadas['total_a_enviar']:,}"])
    
  # Crear la tabla con columnas más anchas
    tabla = Table(tabla_resumen, colWidths=[100, 75, 125, 130])
    estilo_tabla = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E86AB')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ALIGN', (0, 1), (0, -1), 'LEFT'),
        ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#CCCCCC')),
        ('FONTNAME', (0, -3), (-1, -1), 'Helvetica-Bold'),
        ('BACKGROUND', (0, -3), (-1, -1), colors.HexColor('#F8F9FA')),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#E8F5E8')),
        ('TEXTCOLOR', (0, -1), (-1, -1), colors.darkgreen),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ])
    tabla.setStyle(estilo_tabla)
    elementos.append(tabla)
    elementos.append(Spacer(1, 30))
    
    return elementos

def crear_detalle_registros(datos, fecha_inicio, fecha_fin, nombre_sitio):
    """Crea la tabla detallada de todos los registros"""
    styles = getSampleStyleSheet()
    
    elementos = []
    
    elementos.append(PageBreak())
    
    titulo_style = ParagraphStyle(
        'TituloDetalleStyle', 
        parent=styles['Heading1'],
        alignment=TA_CENTER,
        textColor=colors.darkred,
        spaceAfter=15
    )
    
    subtitulo_style = ParagraphStyle(
        'SubtituloDetalleStyle',
        parent=styles['Heading2'],
        alignment=TA_CENTER,
        textColor=colors.darkblue,
        spaceAfter=20
    )
    
    titulo_detalle = Paragraph(f"DETALLE DE REGISTROS - {nombre_sitio}", titulo_style)
    elementos.append(titulo_detalle)
    
    subtitulo = Paragraph(f"Período: {fecha_inicio} a {fecha_fin} - Total de registros: {len(datos)}", subtitulo_style)
    elementos.append(subtitulo)
    elementos.append(Spacer(1, 20))
    
# Tabla de datos detallada
    tabla_datos = [['CÓDIGO', 'UBICACIÓN', 'FECHA', 'HORA', 'TIEMPO ORIGINAL', 'TIEMPO CONVERTIDO', 'TIPO PIN', 'PRECIO']]
    
    for item in datos:
        tiempo = item['tiempo']
        
        if tiempo == "01:00:00" or tiempo.startswith("01:"):
            tipo_pin = "1Hora"
            precio = PRECIOS_PINES["1Hora"]
        elif tiempo == "24:00:00" or (tiempo.startswith("24:") and int(tiempo.split(':')[0]) == 24):
            tipo_pin = "1Dia"
            precio = PRECIOS_PINES["1Dia"]
        elif tiempo == "360:00:00" or (tiempo.startswith("360:") or (24 * 15 <= int(tiempo.split(':')[0]) < 24 * 30)):
            tipo_pin = "15Dias"
            precio = PRECIOS_PINES["15Dias"]
        elif tiempo == "720:00:00" or (tiempo.startswith("720:") or int(tiempo.split(':')[0]) >= 24 * 30):
            tipo_pin = "30Dias"
            precio = PRECIOS_PINES["30Dias"]
        else:
            tipo_pin = "1Hora"
            precio = PRECIOS_PINES["1Hora"]
        
        tabla_datos.append([
            item['codigo'],
            item['ubicacion'],
            item['fecha'],
            item['hora'],
            item['tiempo_original'],
            item['tiempo'],
            tipo_pin,
            f"$ {precio:,}"
        ])
    
    tabla = Table(tabla_datos, colWidths=[75, 65, 75, 55, 85, 85, 65, 60])
    estilo = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495E')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 7),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ECF0F1')),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 6),
        ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#BDC3C7')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8F9FA')]),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ])
    tabla.setStyle(estilo)
    
    elementos.append(tabla)
    
    return elementos

def crear_pdf(datos, fecha_inicio, fecha_fin):
    """Crea el PDF con resumen financiero y detalle de registros"""
# Obtener el nombre del sitio desde "Conectado en" del primer mensaje
    nombre_sitio = "SITIO_DESCONOCIDO"
    if datos:
        # Buscar el primer mensaje que tenga ubicación válida
        for item in datos:
            if item['ubicacion'] != "SIN UBICACIÓN":
                nombre_sitio = item['ubicacion']
                break
    
    # Crear nombre de archivo con el sitio y fechas
    nombre_archivo = f"reporte_{nombre_sitio}_{fecha_inicio}_a_{fecha_fin}.pdf"
    
    doc = SimpleDocTemplate(nombre_archivo, pagesize=letter)
    elementos = []
    
    ventas_calculadas = calcular_ventas_y_comisiones(datos)
    elementos.extend(crear_tabla_resumen(ventas_calculadas, fecha_inicio, fecha_fin, nombre_sitio))
    elementos.extend(crear_detalle_registros(datos, fecha_inicio, fecha_fin, nombre_sitio))
    
    doc.build(elementos)
    return nombre_archivo, ventas_calculadas, nombre_sitio

async def main():
    """Función principal"""
    print("[INICIO] Exportador de Mensajes de Telegram - TODOS los mensajes")
    print("-" * 60)
    
    fecha_inicio = input("Fecha inicio (YYYY-MM-DD): ").strip()
    fecha_fin = input("Fecha fin (YYYY-MM-DD): ").strip()
    
    try:
        datetime.strptime(fecha_inicio, '%Y-%m-%d')
        datetime.strptime(fecha_fin, '%Y-%m-%d')
    except ValueError:
        print("[ERROR] Formato de fecha incorrecto. Usa YYYY-MM-DD")
        return
    
    mensajes = await obtener_todos_los_mensajes(fecha_inicio, fecha_fin)
    
    if mensajes:
        archivo_pdf, ventas, nombre_sitio = crear_pdf(mensajes, fecha_inicio, fecha_fin)
        
        print(f"\n[OK] PDF creado exitosamente: {archivo_pdf}")
        print(f"[UBICACION] Sitio identificado: {nombre_sitio}")
        print(f"\n[DATOS] RESUMEN FINANCIERO:")
        print("=" * 60)
        for tipo_pin in ["1Hora", "1Dia", "15Dias", "30Dias"]:
            if tipo_pin in ventas['ventas_por_tipo']:
                datos = ventas['ventas_por_tipo'][tipo_pin]
                print(f"   {tipo_pin}: {datos['cantidad']} pines - ${datos['valor_total']:,} - Comisión: ${datos['comision_total']:,}")
            else:
                print(f"   {tipo_pin}: 0 pines - - - Comisión: -")
        print("-" * 60)
        print(f"   TOTAL VENTAS: ${ventas['total_valor']:,}")
        print(f"   TOTAL COMISIONES: ${ventas['total_comision']:,}")
        print(f"   COMISIÓN ALCANZA: ${ventas['comision_alcanza']:,}")
        print(f"   TOTAL A ENVIAR: ${ventas['total_a_enviar']:,}")
        print("=" * 60)
        print(f"   [DETALLE] DETALLE: {len(mensajes)} registros procesados")
        
    else:
        print("[ERROR] No se encontraron mensajes en el rango de fechas")

if __name__ == "__main__":
    asyncio.run(main())