#!/usr/bin/env python
# test_quote_flow.py - PROBAR FLUJO DE COTIZACIÓN COMPLETO SIN MODIFICAR CÓDIGO
"""
🧪 PRUEBA COMPLETA DEL FLUJO DE COTIZACIÓN
============================================

Simula el flujo exacto que usa pagina_cliente_ejemplo.html
para identificar dónde se pierde la información de precios.
"""

import sys
import os
import requests
import json

def test_complete_quote_flow():
    """Prueba el flujo completo de cotización como lo hace el frontend."""
    
    print("🧪 PRUEBA COMPLETA DEL FLUJO DE COTIZACIÓN")
    print("=" * 60)
    
    # URL del endpoint del chat (como lo usa pagina_cliente_ejemplo.html)
    chat_url = "http://localhost:5000/chat-api"
    
    # Datos exactos que envía el frontend
    test_data = {
        "clientId": "demo-client-12345", 
        "message": "¿Puedes enviarme una cotización oficial?"
    }
    
    print("📤 PASO 1: Enviando solicitud al endpoint /chat")
    print(f"   URL: {chat_url}")
    print(f"   Datos: {test_data}")
    
    try:
        response = requests.post(chat_url, json=test_data)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            print("✅ Respuesta exitosa recibida")
            
            print(f"\n📝 PASO 2: Analizando respuesta")
            print(f"   Tipo de respuesta: {type(response_data)}")
            
            if isinstance(response_data, dict):
                # Respuesta estructurada
                for key, value in response_data.items():
                    if key == 'response' and len(str(value)) > 300:
                        print(f"   {key}: {str(value)[:300]}...")
                    else:
                        print(f"   {key}: {value}")
            else:
                # Respuesta de texto
                response_text = str(response_data)
                if len(response_text) > 500:
                    print(f"   Respuesta: {response_text[:500]}...")
                else:
                    print(f"   Respuesta: {response_text}")
            
            # Verificar si hay información de cotización
            response_str = str(response_data).lower()
            
            print(f"\n🔍 PASO 3: Análisis de contenido")
            
            # Verificar precios
            has_prices = any(indicator in response_str for indicator in ['$', 'precio', 'price', 'usd'])
            print(f"   ¿Contiene precios?: {'✅' if has_prices else '❌'} {has_prices}")
            
            # Verificar PDF
            has_pdf = any(pdf_indicator in response_str for pdf_indicator in ['pdf', 'cotización', 'descargar'])
            print(f"   ¿Menciona PDF?: {'✅' if has_pdf else '❌'} {has_pdf}")
            
            # Verificar enlaces de descarga
            has_download = 'download' in response_str or '/download-quote/' in response_str
            print(f"   ¿Enlace de descarga?: {'✅' if has_download else '❌'} {has_download}")
            
            # Buscar precios específicos
            import re
            prices_found = re.findall(r'\$[\d,]+', str(response_data))
            print(f"   Precios encontrados: {prices_found}")
            
        else:
            print(f"❌ Error en respuesta: {response.status_code}")
            print(f"   Contenido: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ No se pudo conectar al servidor")
        print("   ⚠️ Asegúrate de que Flask esté ejecutándose en puerto 5000")
        return
        
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return

if __name__ == "__main__":
    test_complete_quote_flow()