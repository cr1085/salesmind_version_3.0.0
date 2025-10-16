#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 GENERADOR AUTOMÁTICO DE WIDGETS PARA CLIENTES
Comando: python generar_widget.py

Genera páginas personalizadas con widgets integrados
"""

import os
import sys
import json
from datetime import datetime

def crear_widget_cliente(cliente_id, nombre_cliente, titulo=None, subtitulo=None, servidor_api=None):
    """
    Crea una página HTML con widget personalizado para un cliente
    """
    # Valores por defecto
    if not titulo:
        titulo = f"Asistente {nombre_cliente}"
    if not subtitulo:
        subtitulo = "Consultor Digital"
    if not servidor_api:
        servidor_api = "http://127.0.0.1:5000/chat-api"
    
    # Leer la plantilla base
    try:
        with open('pagina_cliente_SIMPLE.html', 'r', encoding='utf-8') as f:
            contenido = f.read()
    except FileNotFoundError:
        print("❌ Error: No se encuentra pagina_cliente_SIMPLE.html")
        return None
    
    # Reemplazar configuraciones
    contenido = contenido.replace(
        "CLIENT_ID: '78e5f512-0a21-407b-819a-b5f02a091aac'",
        f"CLIENT_ID: '{cliente_id}'"
    )
    
    contenido = contenido.replace(
        "API_URL: 'http://127.0.0.1:5000/chat-api'",
        f"API_URL: '{servidor_api}'"
    )
    
    contenido = contenido.replace(
        "<title>SalesMind - Asistente IA</title>",
        f"<title>{titulo} - {nombre_cliente}</title>"
    )
    
    contenido = contenido.replace(
        '<h1>🤖 SalesMind</h1>',
        f'<h1>🤖 {titulo}</h1>'
    )
    
    contenido = contenido.replace(
        '<div class="subtitle">Asistente Inteligente de Ventas</div>',
        f'<div class="subtitle">{subtitulo}</div>'
    )
    
    # Crear nombre de archivo seguro
    nombre_archivo = nombre_cliente.lower()
    nombre_archivo = nombre_archivo.replace(' ', '_').replace('&', 'y').replace('.', '')
    nombre_archivo = f"cliente_{nombre_archivo}_{cliente_id.split('-')[0]}.html"
    
    # Guardar archivo
    with open(nombre_archivo, 'w', encoding='utf-8') as f:
        f.write(contenido)
    
    return {
        'archivo': nombre_archivo,
        'cliente': nombre_cliente,
        'id': cliente_id,
        'titulo': titulo,
        'subtitulo': subtitulo,
        'servidor': servidor_api,
        'url_acceso': f"http://localhost/{nombre_archivo}"
    }

def cargar_clientes_desde_json():
    """
    Carga clientes desde un archivo JSON
    """
    try:
        with open('clientes.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        # Crear archivo de ejemplo
        clientes_ejemplo = [
            {
                "id": "constructora-horizonte-2024",
                "nombre": "Constructora Horizonte",
                "titulo": "Asistente Inmobiliario",
                "subtitulo": "Cotizaciones de Proyectos"
            },
            {
                "id": "cafe-del-sol-001", 
                "nombre": "Café del Sol",
                "titulo": "Asistente Café del Sol",
                "subtitulo": "Menú y Reservas"
            },
            {
                "id": "grupo-manotas-corp",
                "nombre": "Grupo Manotas", 
                "titulo": "Consultor Empresarial",
                "subtitulo": "Soluciones Corporativas"
            }
        ]
        
        with open('clientes.json', 'w', encoding='utf-8') as f:
            json.dump(clientes_ejemplo, f, indent=2, ensure_ascii=False)
        
        print("📁 Archivo 'clientes.json' creado con ejemplos")
        return clientes_ejemplo

def generar_todos_los_widgets():
    """
    Genera widgets para todos los clientes en clientes.json
    """
    clientes = cargar_clientes_desde_json()
    resultados = []
    
    print(f"🚀 Generando widgets para {len(clientes)} clientes...")
    print("-" * 50)
    
    for cliente in clientes:
        resultado = crear_widget_cliente(
            cliente_id=cliente['id'],
            nombre_cliente=cliente['nombre'],
            titulo=cliente.get('titulo'),
            subtitulo=cliente.get('subtitulo'),
            servidor_api=cliente.get('servidor_api')
        )
        
        if resultado:
            resultados.append(resultado)
            print(f"✅ {resultado['cliente']} → {resultado['archivo']}")
        else:
            print(f"❌ Error generando widget para {cliente['nombre']}")
    
    return resultados

def agregar_cliente_interactivo():
    """
    Agrega un nuevo cliente de forma interactiva
    """
    print("\n🆕 AGREGAR NUEVO CLIENTE")
    print("-" * 30)
    
    nombre = input("📝 Nombre del cliente: ").strip()
    if not nombre:
        print("❌ Nombre requerido")
        return None
    
    # Generar ID automático
    id_base = nombre.lower().replace(' ', '-').replace('&', 'y').replace('.', '')
    cliente_id = f"{id_base}-{datetime.now().strftime('%Y')}"
    
    titulo = input(f"🤖 Título del asistente [{nombre} Asistente]: ").strip()
    if not titulo:
        titulo = f"{nombre} Asistente"
    
    subtitulo = input("💬 Subtítulo [Consultor Digital]: ").strip()
    if not subtitulo:
        subtitulo = "Consultor Digital"
    
    # Crear widget
    resultado = crear_widget_cliente(
        cliente_id=cliente_id,
        nombre_cliente=nombre,
        titulo=titulo,
        subtitulo=subtitulo
    )
    
    if resultado:
        # Agregar al JSON
        clientes = cargar_clientes_desde_json()
        clientes.append({
            "id": cliente_id,
            "nombre": nombre,
            "titulo": titulo,
            "subtitulo": subtitulo
        })
        
        with open('clientes.json', 'w', encoding='utf-8') as f:
            json.dump(clientes, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Cliente agregado exitosamente!")
        print(f"📄 Archivo: {resultado['archivo']}")
        print(f"🌐 URL: {resultado['url_acceso']}")
        
    return resultado

def mostrar_ayuda():
    """
    Muestra la ayuda del comando
    """
    print("""
🚀 GENERADOR DE WIDGETS PARA CLIENTES

COMANDOS DISPONIBLES:
  python generar_widget.py todos      - Genera widgets para todos los clientes
  python generar_widget.py nuevo      - Agrega un nuevo cliente interactivo
  python generar_widget.py listar     - Lista todos los clientes
  python generar_widget.py ayuda      - Muestra esta ayuda

ARCHIVOS:
  clientes.json          - Base de datos de clientes
  pagina_cliente_SIMPLE.html - Plantilla base (NO MODIFICAR)
  cliente_*.html         - Páginas generadas para cada cliente

EJEMPLO DE USO:
  1. python generar_widget.py nuevo
  2. python generar_widget.py todos
  3. Abrir cliente_*.html en navegador
    """)

def listar_clientes():
    """
    Lista todos los clientes registrados
    """
    clientes = cargar_clientes_desde_json()
    
    print(f"\n📋 CLIENTES REGISTRADOS ({len(clientes)})")
    print("-" * 50)
    
    for i, cliente in enumerate(clientes, 1):
        print(f"{i}. {cliente['nombre']}")
        print(f"   ID: {cliente['id']}")
        print(f"   Título: {cliente.get('titulo', 'N/A')}")
        print(f"   Archivo: cliente_{cliente['nombre'].lower().replace(' ', '_')}_{cliente['id'].split('-')[0]}.html")
        print()

def main():
    """
    Función principal del script
    """
    if len(sys.argv) < 2:
        mostrar_ayuda()
        return
    
    comando = sys.argv[1].lower()
    
    if comando == 'todos':
        resultados = generar_todos_los_widgets()
        print(f"\n🎉 ¡{len(resultados)} widgets generados exitosamente!")
        
    elif comando == 'nuevo':
        agregar_cliente_interactivo()
        
    elif comando == 'listar':
        listar_clientes()
        
    elif comando == 'ayuda' or comando == 'help':
        mostrar_ayuda()
        
    else:
        print(f"❌ Comando desconocido: {comando}")
        mostrar_ayuda()

if __name__ == "__main__":
    print("🤖 GENERADOR DE WIDGETS SALESMIND")
    print("=" * 40)
    main()