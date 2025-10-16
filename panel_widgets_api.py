"""
🚀 ENDPOINT PARA PANEL DE WIDGETS
Agrega este código a tu app.py o crea una ruta separada
"""

from flask import request, jsonify
import json
import os
from datetime import datetime

def crear_widget_cliente_api(cliente_id, nombre_cliente, titulo=None, subtitulo=None, servidor_api=None):
    """
    Versión API de crear_widget_cliente
    """
    # Valores por defecto
    if not titulo:
        titulo = f"Asistente {nombre_cliente}"
    if not subtitulo:
        subtitulo = "Consultor Digital"
    if not servidor_api:
        servidor_api = "http://127.0.0.1:5000/chat-api"
    
    try:
        # Leer plantilla
        with open('pagina_cliente_SIMPLE.html', 'r', encoding='utf-8') as f:
            contenido = f.read()
        
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
        
        # Nombre de archivo
        nombre_archivo = nombre_cliente.lower()
        nombre_archivo = nombre_archivo.replace(' ', '_').replace('&', 'y').replace('.', '')
        nombre_archivo = f"cliente_{nombre_archivo}_{cliente_id.split('-')[0]}.html"
        
        # Guardar archivo
        with open(nombre_archivo, 'w', encoding='utf-8') as f:
            f.write(contenido)
        
        return {
            'success': True,
            'archivo': nombre_archivo,
            'cliente': nombre_cliente,
            'id': cliente_id,
            'titulo': titulo,
            'subtitulo': subtitulo,
            'servidor': servidor_api,
            'url': f"http://localhost/{nombre_archivo}"
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def cargar_clientes_json():
    """Cargar clientes desde JSON"""
    try:
        with open('clientes.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def guardar_clientes_json(clientes):
    """Guardar clientes en JSON"""
    with open('clientes.json', 'w', encoding='utf-8') as f:
        json.dump(clientes, f, indent=2, ensure_ascii=False)

# Agrega esta ruta a tu app.py:
def setup_widget_routes(app):
    """
    Configura las rutas para el panel de widgets
    Llama esta función en tu app.py después de crear la app
    """
    
    @app.route('/generar-widgets', methods=['POST'])
    def generar_widgets():
        try:
            data = request.json
            accion = data.get('accion')
            
            if accion == 'listar':
                clientes = cargar_clientes_json()
                return jsonify({
                    'success': True,
                    'clientes': clientes
                })
            
            elif accion == 'generar_todos':
                clientes = cargar_clientes_json()
                resultados = []
                
                for cliente in clientes:
                    resultado = crear_widget_cliente_api(
                        cliente_id=cliente['id'],
                        nombre_cliente=cliente['nombre'],
                        titulo=cliente.get('titulo'),
                        subtitulo=cliente.get('subtitulo'),
                        servidor_api=cliente.get('servidor_api')
                    )
                    
                    if resultado['success']:
                        resultados.append(resultado)
                
                return jsonify({
                    'success': True,
                    'resultados': resultados
                })
            
            elif accion == 'agregar_cliente':
                nombre = data.get('nombre', '').strip()
                titulo = data.get('titulo', '').strip()
                subtitulo = data.get('subtitulo', '').strip()
                servidor_api = data.get('servidor_api', '').strip()
                
                if not nombre:
                    return jsonify({
                        'success': False,
                        'error': 'Nombre requerido'
                    })
                
                # Generar ID
                id_base = nombre.lower().replace(' ', '-').replace('&', 'y').replace('.', '')
                cliente_id = f"{id_base}-{datetime.now().strftime('%Y')}"
                
                # Crear widget
                resultado = crear_widget_cliente_api(
                    cliente_id=cliente_id,
                    nombre_cliente=nombre,
                    titulo=titulo if titulo else None,
                    subtitulo=subtitulo if subtitulo else None,
                    servidor_api=servidor_api if servidor_api else None
                )
                
                if resultado['success']:
                    # Agregar a JSON
                    clientes = cargar_clientes_json()
                    clientes.append({
                        "id": cliente_id,
                        "nombre": nombre,
                        "titulo": titulo if titulo else f"Asistente {nombre}",
                        "subtitulo": subtitulo if subtitulo else "Consultor Digital",
                        "servidor_api": servidor_api if servidor_api else None
                    })
                    guardar_clientes_json(clientes)
                
                return jsonify({
                    'success': resultado['success'],
                    'resultado': resultado if resultado['success'] else None,
                    'error': resultado.get('error')
                })
            
            else:
                return jsonify({
                    'success': False,
                    'error': 'Acción no válida'
                })
                
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            })

# INSTRUCCIONES PARA INTEGRAR:
# 1. En tu app.py, después de crear la app, agrega:
# from panel_widgets_api import setup_widget_routes
# setup_widget_routes(app)

# 2. O copia directamente la función setup_widget_routes y las funciones auxiliares a tu app.py