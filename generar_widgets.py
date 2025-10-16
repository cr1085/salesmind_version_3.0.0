"""
🚀 GENERADOR DE WIDGETS PERSONALIZADOS
Crea widgets con ID de cliente integrado
"""

import os
import shutil

def generar_widget_cliente(
    cliente_id,
    nombre_cliente, 
    titulo_asistente=None,
    subtitulo=None,
    url_api=None
):
    """
    Genera un widget personalizado para un cliente específico
    """
    
    # Valores por defecto
    if not titulo_asistente:
        titulo_asistente = f"Asistente {nombre_cliente}"
    if not subtitulo:
        subtitulo = "Consultor Digital"
    if not url_api:
        url_api = "https://tu-servidor.com/chat-api"  # Cambiar por tu URL real
    
    # Crear HTML personalizado
    html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{nombre_cliente} - Asistente IA</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: white;
        }}
        .container {{
            max-width: 800px;
            margin: 0 auto;
            text-align: center;
            padding: 2rem;
        }}
        .integration-info {{
            background: rgba(255, 255, 255, 0.1);
            padding: 2rem;
            border-radius: 15px;
            backdrop-filter: blur(10px);
            margin: 2rem 0;
        }}
        .code-block {{
            background: rgba(0, 0, 0, 0.3);
            padding: 1rem;
            border-radius: 10px;
            font-family: 'Courier New', monospace;
            text-align: left;
            overflow-x: auto;
            margin: 1rem 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 {titulo_asistente}</h1>
        <h2>Widget Personalizado para {nombre_cliente}</h2>
        
        <div class="integration-info">
            <h3>✅ Configuración Lista</h3>
            <p><strong>ID Cliente:</strong> {cliente_id}</p>
            <p><strong>Título:</strong> {titulo_asistente}</p>
            <p><strong>Subtítulo:</strong> {subtitulo}</p>
            <p><strong>API URL:</strong> {url_api}</p>
            
            <h4>📋 Código de Integración:</h4>
            <div class="code-block">
&lt;script src="salesmind-widget.js" 
        data-client-id="{cliente_id}"
        data-title="{titulo_asistente}"
        data-subtitle="{subtitulo}"
        data-api-url="{url_api}"&gt;&lt;/script&gt;
            </div>
            
            <p><em>👆 Solo agrega este código a tu sitio web</em></p>
        </div>
        
        <p><strong>¡Prueba el widget aquí! →</strong></p>
        <p><em>Busca el botón azul en la esquina inferior derecha</em></p>
    </div>

    <!-- Widget integrado con configuración personalizada -->
    <script src="salesmind-widget.js" 
            data-client-id="{cliente_id}"
            data-title="{titulo_asistente}"
            data-subtitle="{subtitulo}"
            data-api-url="{url_api}"></script>
</body>
</html>"""
    
    # Crear nombre de archivo
    nombre_archivo = f"widget_{cliente_id.replace('-', '_')}.html"
    
    # Guardar archivo
    with open(nombre_archivo, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    # Copiar el widget JS (el mismo para todos)
    if os.path.exists('salesmind-widget.js'):
        shutil.copy('salesmind-widget.js', f'salesmind-widget-{cliente_id}.js')
    
    return {
        'archivo_html': nombre_archivo,
        'archivo_js': f'salesmind-widget-{cliente_id}.js',
        'cliente_id': cliente_id,
        'nombre_cliente': nombre_cliente,
        'titulo': titulo_asistente,
        'codigo_integracion': f'''<script src="salesmind-widget.js" 
        data-client-id="{cliente_id}"
        data-title="{titulo_asistente}"
        data-subtitle="{subtitulo}"
        data-api-url="{url_api}"></script>'''
    }

def generar_clientes_ejemplo():
    """Genera widgets para clientes de ejemplo"""
    
    clientes = [
        {
            'id': 'constructora-horizonte-2024',
            'nombre': 'Constructora Horizonte',
            'titulo': 'Asistente Inmobiliario',
            'subtitulo': 'Cotizaciones de Proyectos',
            'url': 'https://api.constructora-horizonte.com/chat'
        },
        {
            'id': 'cafe-del-sol-premium',
            'nombre': 'Café del Sol',
            'titulo': 'Asistente Café del Sol',
            'subtitulo': 'Menú y Reservas',
            'url': 'https://api.cafedelsol.com/chat'
        },
        {
            'id': 'grupo-manotas-corp',
            'nombre': 'Grupo Manotas',
            'titulo': 'Consultor Empresarial',
            'subtitulo': 'Soluciones de Negocio',
            'url': 'https://api.grupomanotas.com/chat'
        }
    ]
    
    resultados = []
    
    for cliente in clientes:
        resultado = generar_widget_cliente(
            cliente_id=cliente['id'],
            nombre_cliente=cliente['nombre'],
            titulo_asistente=cliente['titulo'],
            subtitulo=cliente['subtitulo'],
            url_api=cliente['url']
        )
        resultados.append(resultado)
        print(f"✅ Widget generado: {resultado['archivo_html']}")
    
    return resultados

if __name__ == "__main__":
    print("🚀 GENERADOR DE WIDGETS PERSONALIZADOS")
    print("=" * 50)
    
    # Generar widgets de ejemplo
    resultados = generar_clientes_ejemplo()
    
    print(f"\\n🎉 Se generaron {len(resultados)} widgets personalizados!")
    
    print("\\n📋 ARCHIVOS GENERADOS:")
    for resultado in resultados:
        print(f"\\n📁 {resultado['nombre_cliente']}:")
        print(f"   • HTML: {resultado['archivo_html']}")
        print(f"   • Widget: {resultado['archivo_js']}")
        print(f"   • ID: {resultado['cliente_id']}")
    
    print("\\n🎯 INSTRUCCIONES:")
    print("1. Cada cliente tiene su archivo HTML personalizado")
    print("2. Abre cualquier archivo .html para ver la demo")
    print("3. Entrega el código de integración a cada cliente")
    print("4. ¡El widget se configurará automáticamente!")
    
    # Generar uno personalizado
    print("\\n🛠️ EJEMPLO PERSONALIZADO:")
    custom = generar_widget_cliente(
        cliente_id="mi-empresa-especial-2024",
        nombre_cliente="Mi Empresa Especial",
        titulo_asistente="Mi Asistente Personal",
        subtitulo="Soporte Premium 24/7",
        url_api="https://mi-api.com/chat"
    )
    print(f"✅ Widget personalizado: {custom['archivo_html']}")
    print(f"\\n📋 Código para integrar:")
    print(custom['codigo_integracion'])