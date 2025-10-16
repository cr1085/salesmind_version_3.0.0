# test_multilanguage_quotes.py
"""
Script de prueba para verificar funcionalidades multilenguaje y cotizaciones
"""

def test_language_detection():
    """Prueba la detección de idioma"""
    print("🧪 PROBANDO DETECCIÓN DE IDIOMA")
    print("=" * 50)
    
    try:
        from modules.assistant.core import detect_language, get_language_specific_prompt
        
        # Casos de prueba
        test_cases = [
            ("Hello, how much does a house cost?", "en"),
            ("Hola, ¿cuánto cuesta una casa?", "es"),
            ("Bonjour, combien coûte une maison?", "fr"),
            ("Guten Tag, wie viel kostet ein Haus?", "de"),
            ("Olá, quanto custa uma casa?", "pt"),
            ("Hi, what is the price of this property?", "en"),
            ("Buenos días, necesito una cotización", "es")
        ]
        
        for question, expected in test_cases:
            detected = detect_language(question)
            status = "✅" if detected == expected else "❌"
            print(f"{status} '{question}' -> Esperado: {expected}, Detectado: {detected}")
        
        print("\n🧪 PROBANDO GENERACIÓN DE PROMPTS")
        print("=" * 50)
        
        # Probar prompts en diferentes idiomas
        context = "Houses available from $100,000 to $500,000. Modern properties with 2-4 bedrooms."
        
        # Inglés
        prompt_en = get_language_specific_prompt("Hello, how much for a 3-bedroom house?", context)
        print("🇺🇸 PROMPT EN INGLÉS:")
        print(prompt_en[:200] + "...")
        print()
        
        # Español
        prompt_es = get_language_specific_prompt("Hola, ¿cuánto cuesta una casa de 3 habitaciones?", context)
        print("🇪🇸 PROMPT EN ESPAÑOL:")
        print(prompt_es[:200] + "...")
        print()
        
    except Exception as e:
        print(f"❌ Error en prueba de idioma: {e}")
        import traceback
        traceback.print_exc()

def test_quote_generation():
    """Prueba la generación de cotizaciones"""
    print("🧪 PROBANDO GENERACIÓN DE COTIZACIONES")
    print("=" * 50)
    
    try:
        from modules.quote_generator import QuoteGenerator, generate_quote_if_requested
        
        # Crear generador
        generator = QuoteGenerator()
        
        # Respuesta simulada de IA con precios
        ai_response = """
        Tenemos excelentes opciones para ti:
        
        🏠 Casa Modelo Aurora - $250,000 USD
        - 3 habitaciones, 2 baños
        - 120 m² de construcción
        - Garaje techado
        
        🏠 Casa Modelo Diamante - $180,000 USD  
        - 2 habitaciones, 2 baños
        - 95 m² de construcción
        - Jardín privado
        
        Incluye:
        ✅ Escrituras al día
        ✅ Servicios públicos instalados
        ✅ Asesoría legal gratuita
        
        ¡Aprovecha nuestros planes de financiación!
        """
        
        # Probar extracción de información
        quote_info = generator.extract_quote_info(ai_response, "Juan Pérez")
        
        print("📊 INFORMACIÓN EXTRAÍDA:")
        print(f"   Cliente: {quote_info['client_name']}")
        print(f"   Número: {quote_info['quote_number']}")
        print(f"   Items encontrados: {len(quote_info['items'])}")
        print(f"   Subtotal: ${quote_info['subtotal']:,.2f}")
        print(f"   Total: ${quote_info['total']:,.2f}")
        print()
        
        # Probar generación de PDF
        print("📄 GENERANDO PDF...")
        pdf_path = generator.generate_pdf_quote(ai_response, "Juan Pérez")
        print(f"   ✅ PDF generado: {pdf_path}")
        print()
        
        # Probar función integrada
        print("🔗 PROBANDO INTEGRACIÓN...")
        question = "Necesito una cotización para una casa"
        updated_response, pdf_url = generate_quote_if_requested(ai_response, question, "María García")
        
        if pdf_url:
            print(f"   ✅ URL de descarga: {pdf_url}")
            print(f"   ✅ Respuesta actualizada con enlace PDF")
        else:
            print("   ❌ No se generó URL de descarga")
        
    except Exception as e:
        print(f"❌ Error en prueba de cotización: {e}")
        import traceback
        traceback.print_exc()

def test_api_simulation():
    """Simula llamadas a la API"""
    print("🧪 SIMULANDO LLAMADAS API")
    print("=" * 50)
    
    try:
        import requests
        import json
        
        # Datos de prueba
        test_cases = [
            {
                "message": "Hello, how much does a house cost?",
                "clientId": "test-client-123",
                "expected_lang": "English"
            },
            {
                "message": "Hola, necesito una cotización para una casa",
                "clientId": "test-client-123", 
                "expected_lang": "Español"
            }
        ]
        
        for i, case in enumerate(test_cases):
            print(f"🧪 Caso {i+1}: {case['message']}")
            print(f"   Idioma esperado: {case['expected_lang']}")
            
            # Nota: En un entorno real, aquí haríamos la llamada POST
            # response = requests.post('http://127.0.0.1:5000/chat-api', json=case)
            print("   ⚠️  Llamada API requiere cliente válido en DB")
            print()
        
    except Exception as e:
        print(f"❌ Error en simulación API: {e}")

if __name__ == "__main__":
    print("🚀 INICIANDO PRUEBAS DE FUNCIONALIDADES")
    print("=" * 60)
    print()
    
    test_language_detection()
    print()
    test_quote_generation() 
    print()
    test_api_simulation()
    print()
    print("🎉 PRUEBAS COMPLETADAS")