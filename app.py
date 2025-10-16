# app.py
import nest_asyncio
nest_asyncio.apply()

import os
from dotenv import load_dotenv
from waitress import serve  # <-- 1. Importar serve desde waitress

# Cargar .env
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path=dotenv_path)

from modules import create_app

app = create_app()

# 🚀 ENDPOINT PARA PANEL DE WIDGETS (Agregado sin afectar sistema original)
from flask import request, jsonify
import json
from datetime import datetime

def crear_widget_cliente_api(cliente_id, nombre_cliente, titulo=None, subtitulo=None, servidor_api=None):
    if not titulo:
        titulo = f"Asistente {nombre_cliente}"
    if not subtitulo:
        subtitulo = "Consultor Digital"
    if not servidor_api:
        servidor_api = "http://127.0.0.1:5000/chat-api"
    
    try:
        with open('pagina_cliente_SIMPLE.html', 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        contenido = contenido.replace("CLIENT_ID: '78e5f512-0a21-407b-819a-b5f02a091aac'", f"CLIENT_ID: '{cliente_id}'")
        contenido = contenido.replace("API_URL: 'http://127.0.0.1:5000/chat-api'", f"API_URL: '{servidor_api}'")
        contenido = contenido.replace("<title>SalesMind - Asistente IA</title>", f"<title>{titulo} - {nombre_cliente}</title>")
        contenido = contenido.replace('<h1>🤖 SalesMind</h1>', f'<h1>🤖 {titulo}</h1>')
        contenido = contenido.replace('<div class="subtitle">Asistente Inteligente de Ventas</div>', f'<div class="subtitle">{subtitulo}</div>')
        
        nombre_archivo = nombre_cliente.lower().replace(' ', '_').replace('&', 'y').replace('.', '')
        nombre_archivo = f"cliente_{nombre_archivo}_{cliente_id.split('-')[0]}.html"
        
        with open(nombre_archivo, 'w', encoding='utf-8') as f:
            f.write(contenido)
        
        return {
            'success': True, 'archivo': nombre_archivo, 'cliente': nombre_cliente, 
            'id': cliente_id, 'titulo': titulo, 'url': f"http://localhost/{nombre_archivo}"
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

@app.route('/generar-widgets', methods=['POST'])
def generar_widgets():
    try:
        data = request.json
        accion = data.get('accion')
        
        if accion == 'listar':
            try:
                with open('clientes.json', 'r', encoding='utf-8') as f:
                    clientes = json.load(f)
            except FileNotFoundError:
                clientes = []
            return jsonify({'success': True, 'clientes': clientes})
        
        elif accion == 'generar_todos':
            try:
                with open('clientes.json', 'r', encoding='utf-8') as f:
                    clientes = json.load(f)
            except FileNotFoundError:
                clientes = []
            
            resultados = []
            for cliente in clientes:
                resultado = crear_widget_cliente_api(
                    cliente_id=cliente['id'], nombre_cliente=cliente['nombre'],
                    titulo=cliente.get('titulo'), subtitulo=cliente.get('subtitulo'),
                    servidor_api=cliente.get('servidor_api')
                )
                if resultado['success']:
                    resultados.append(resultado)
            
            return jsonify({'success': True, 'resultados': resultados})
        
        elif accion == 'agregar_cliente':
            nombre = data.get('nombre', '').strip()
            if not nombre:
                return jsonify({'success': False, 'error': 'Nombre requerido'})
            
            titulo = data.get('titulo', '').strip()
            subtitulo = data.get('subtitulo', '').strip()
            servidor_api = data.get('servidor_api', '').strip()
            
            id_base = nombre.lower().replace(' ', '-').replace('&', 'y').replace('.', '')
            cliente_id = f"{id_base}-{datetime.now().strftime('%Y')}"
            
            resultado = crear_widget_cliente_api(
                cliente_id=cliente_id, nombre_cliente=nombre,
                titulo=titulo if titulo else None, subtitulo=subtitulo if subtitulo else None,
                servidor_api=servidor_api if servidor_api else None
            )
            
            if resultado['success']:
                try:
                    with open('clientes.json', 'r', encoding='utf-8') as f:
                        clientes = json.load(f)
                except FileNotFoundError:
                    clientes = []
                
                clientes.append({
                    "id": cliente_id, "nombre": nombre,
                    "titulo": titulo if titulo else f"Asistente {nombre}",
                    "subtitulo": subtitulo if subtitulo else "Consultor Digital",
                    "servidor_api": servidor_api if servidor_api else None
                })
                
                with open('clientes.json', 'w', encoding='utf-8') as f:
                    json.dump(clientes, f, indent=2, ensure_ascii=False)
            
            return jsonify({'success': resultado['success'], 'resultado': resultado if resultado['success'] else None, 'error': resultado.get('error')})
        
        else:
            return jsonify({'success': False, 'error': 'Acción no válida'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# Sistema funcional original - Sin módulo comercial por ahora

if __name__ == '__main__':
    # Iniciando servidor Flask en modo desarrollo para pruebas
    print("-> Iniciando servidor Flask en modo desarrollo en http://127.0.0.1:5000")
    app.run(host='127.0.0.1', port=5000, debug=True, threaded=True)