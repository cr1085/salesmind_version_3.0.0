# 🚀 GENERADOR DE PÁGINAS PARA CLIENTES
# Script para generar páginas personalizadas del asistente IA

import os
import uuid

def generar_pagina_cliente(nombre_cliente, id_cliente=None, url_api=None):
    """
    Genera una página personalizada para un cliente específico
    """
    # Configuración por defecto
    if not id_cliente:
        id_cliente = str(uuid.uuid4())
    
    if not url_api:
        url_api = "http://127.0.0.1:5000/chat-api"  # Cambiar por tu URL real
    
    # Leer plantilla
    with open('asistente_cliente.html', 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    # Reemplazar configuración
    contenido = contenido.replace(
        "CLIENT_ID: '78e5f512-0a21-407b-819a-b5f02a091aac'",
        f"CLIENT_ID: '{id_cliente}'"
    )
    
    contenido = contenido.replace(
        "API_URL: 'http://127.0.0.1:5000/chat-api'",
        f"API_URL: '{url_api}'"
    )
    
    contenido = contenido.replace(
        "CLIENT_NAME: 'Cliente Demo'",
        f"CLIENT_NAME: '{nombre_cliente}'"
    )
    
    contenido = contenido.replace(
        "<title>Asistente Comercial IA</title>",
        f"<title>Asistente IA - {nombre_cliente}</title>"
    )
    
    # Crear nombre de archivo seguro
    nombre_archivo = nombre_cliente.lower().replace(' ', '_').replace('&', 'y')
    nombre_archivo = f"asistente_{nombre_archivo}.html"
    
    # Guardar archivo
    with open(nombre_archivo, 'w', encoding='utf-8') as f:
        f.write(contenido)
    
    return {
        'archivo': nombre_archivo,
        'cliente': nombre_cliente,
        'id_cliente': id_cliente,
        'url_api': url_api
    }

def generar_multiples_clientes():
    """
    Genera páginas para múltiples clientes
    """
    clientes = [
        {"nombre": "Constructora Horizonte", "id": "constructora-horizonte-001"},
        {"nombre": "Café del Sol", "id": "cafe-del-sol-002"},  
        {"nombre": "Inmobiliaria Premium", "id": "inmobiliaria-premium-003"},
        {"nombre": "Grupo Empresarial ABC", "id": "grupo-abc-004"}
    ]
    
    resultados = []
    
    for cliente in clientes:
        resultado = generar_pagina_cliente(
            nombre_cliente=cliente["nombre"],
            id_cliente=cliente["id"],
            url_api="https://tu-servidor.com/chat-api"  # Cambiar por tu URL real
        )
        resultados.append(resultado)
        print(f"✅ Generado: {resultado['archivo']} para {resultado['cliente']}")
    
    return resultados

if __name__ == "__main__":
    print("🚀 GENERADOR DE PÁGINAS PERSONALIZADAS")
    print("=" * 50)
    
    # Opción 1: Cliente individual
    print("\n1. Generar página individual:")
    cliente = generar_pagina_cliente(
        nombre_cliente="Cliente Ejemplo",
        id_cliente="cliente-ejemplo-123",
        url_api="http://localhost:5000/chat-api"
    )
    print(f"   ✅ {cliente['archivo']} creado para {cliente['cliente']}")
    
    # Opción 2: Múltiples clientes
    print("\n2. Generar páginas múltiples:")
    resultados = generar_multiples_clientes()
    
    print(f"\n🎉 Se generaron {len(resultados)} páginas exitosamente!")
    print("\n📋 LISTA DE ARCHIVOS GENERADOS:")
    for resultado in resultados:
        print(f"   • {resultado['archivo']} → {resultado['cliente']} (ID: {resultado['id_cliente']})")
    
    print(f"\n📦 INSTRUCCIONES DE ENTREGA:")
    print(f"   1. Sube los archivos HTML a tu servidor web")
    print(f"   2. Cambia la URL_API en cada archivo por tu servidor real") 
    print(f"   3. Entrega la URL correspondiente a cada cliente")
    print(f"   4. Cada cliente tendrá su propio ID único integrado")