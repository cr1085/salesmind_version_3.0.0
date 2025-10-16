# modules/assistant/core.py
import os
import traceback
from config import Config
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_community.llms import Ollama
# --- DETECCIÓN DE IDIOMA MEJORADA ---
def detect_language(text: str) -> str:
    """
    Detecta el idioma del texto usando múltiples métodos.
    Retorna: 'es', 'en', 'fr', 'de', 'pt'
    """
    text_lower = text.lower().strip()
    
    # Patrones más específicos para inglés
    english_patterns = [
        # Palabras muy específicas del inglés
        r'\b(hello|hi|hey|good morning|good afternoon)\b',
        r'\b(the|and|or|but|with|from|to|at|in|on|for)\b',
        r'\b(what|how|where|when|why|which|who)\b',
        r'\b(is|are|was|were|have|has|had|do|does|did)\b',
        r'\b(house|price|cost|available|model|information)\b',
        r'\b(can|could|would|should|will|may|might)\b',
        r'\b(this|that|these|those|here|there)\b'
    ]
    
    # Patrones específicos del español
    spanish_patterns = [
        r'\b(hola|buenos días|buenas tardes|buenas noches)\b',
        r'\b(qué|cómo|cuándo|dónde|por qué|cuál|quién)\b',
        r'\b(es|son|está|están|tiene|hay|puede|puedo)\b',
        r'\b(casa|precio|cuesta|modelo|información|disponible)\b',
        r'\b(el|la|los|las|un|una|de|del|en|con|por|para)\b',
        r'\b(este|esta|estos|estas|ese|esa|esos|esas)\b'
    ]
    
    import re
    
    # Contar coincidencias
    english_matches = sum(1 for pattern in english_patterns if re.search(pattern, text_lower))
    spanish_matches = sum(1 for pattern in spanish_patterns if re.search(pattern, text_lower))
    
    # Verificar palabras específicas muy claras
    if any(word in text_lower for word in ['hello', 'hi', 'good morning', 'thank you', 'please']):
        return 'en'
    elif any(word in text_lower for word in ['hola', 'gracias', 'por favor', 'buenos días']):
        return 'es'
    elif any(word in text_lower for word in ['bonjour', 'merci', 'comment', 'quel']):
        return 'fr'
    elif any(word in text_lower for word in ['guten tag', 'danke', 'wie', 'welche']):
        return 'de'
    elif any(word in text_lower for word in ['olá', 'obrigado', 'como', 'quanto']):
        return 'pt'
    
    # Decidir por coincidencias
    if english_matches > spanish_matches:
        return 'en'
    elif spanish_matches > 0:
        return 'es'
    
    # Por defecto español
    return 'es'

def get_language_specific_prompt(question: str, context: str) -> str:
    """Detecta el idioma y devuelve un prompt específico con capacidades de cotización"""
    
    detected_lang = detect_language(question)
    print(f"🌐 Idioma detectado: {detected_lang} para pregunta: '{question[:50]}...'")
    
    # Verificar si es una solicitud de cotización
    quote_keywords = {
        'es': ['cotizacion', 'cotización', 'presupuesto', 'precio', 'cuesta', 'cotizar', 'cuanto cuesta'],
        'en': ['quote', 'quotation', 'estimate', 'price', 'cost', 'how much', 'pricing'],
        'fr': ['devis', 'prix', 'coût', 'combien', 'tarif'],
        'de': ['angebot', 'preis', 'kosten', 'wie viel', 'preisliste'],
        'pt': ['cotação', 'orçamento', 'preço', 'quanto custa', 'valor']
    }
    
    is_quote_request = any(keyword in question.lower() for keyword in quote_keywords.get(detected_lang, []))
    
    if detected_lang == 'en':
        if is_quote_request:
            return f"""You are SalesMind, a professional sales consultant. Based on the context provided, generate a detailed QUOTE with prices, specifications, and terms. Your response must be COMPLETELY in English.

QUOTE INSTRUCTIONS:
- Include specific prices and models from the context
- Add payment terms and delivery information
- Be professional like a real estate sales advisor
- If specific prices aren't in context, provide realistic estimates based on similar properties

Context: {context}

Customer Request: {question}

Professional Quote in English:"""
        else:
            return f"""You are SalesMind, a professional sales assistant. Answer based on the provided context. Your response must be COMPLETELY in English. Act as a helpful sales consultant ready to provide quotes when asked.

Context: {context}

Question: {question}

Professional Answer in English:"""
    
    elif detected_lang == 'es':
        if is_quote_request:
            return f"""Eres SalesMind, un asesor de ventas profesional. Basándote en el contexto proporcionado, genera una COTIZACIÓN detallada con precios, especificaciones y términos. Tu respuesta debe estar COMPLETAMENTE en español.

INSTRUCCIONES DE COTIZACIÓN:
- Incluye precios específicos y modelos del contexto
- Agrega términos de pago e información de entrega  
- Sé profesional como un asesor inmobiliario real
- Si no hay precios específicos en el contexto, proporciona estimaciones realistas basadas en propiedades similares

Contexto: {context}

Solicitud del Cliente: {question}

Cotización Profesional en Español:"""
        else:
            return f"""Eres SalesMind, un asistente de ventas profesional. Responde basándote en el contexto proporcionado. Tu respuesta debe estar COMPLETAMENTE en español. Actúa como un asesor de ventas útil listo para proporcionar cotizaciones cuando se soliciten.

Contexto: {context}

Pregunta: {question}

Respuesta Profesional en Español:"""
    
    elif detected_lang == 'fr':
        return f"""Vous êtes SalesMind, un consultant en vente professionnel. Répondez en vous basant sur le contexte fourni. Votre réponse doit être COMPLÈTEMENT en français.

Contexte: {context}

Question: {question}

Réponse professionnelle en français:"""
    
    elif detected_lang == 'de':
        return f"""Sie sind SalesMind, ein professioneller Verkaufsberater. Antworten Sie basierend auf dem bereitgestellten Kontext. Ihre Antwort muss VOLLSTÄNDIG auf Deutsch sein.

Kontext: {context}

Frage: {question}

Professionelle Antwort auf Deutsch:"""
    
    elif detected_lang == 'pt':
        return f"""Você é SalesMind, um consultor de vendas profissional. Responda com base no contexto fornecido. Sua resposta deve estar COMPLETAMENTE em português.

Contexto: {context}

Pergunta: {question}

Resposta profissional em português:"""
    
    else:
        # Por defecto español
        return f"""Eres SalesMind, un asesor de ventas profesional. Responde basándote en el contexto proporcionado. Tu respuesta debe estar COMPLETAMENTE en español.

Contexto: {context}

Pregunta: {question}

Respuesta profesional:"""

# --- NUEVA LÓGICA MULTI-TENANT CON POSTGRESQL ---
def get_commercial_response(question: str, client_id: int) -> str:
    """
    Función RAG que usa PostgreSQL en lugar de archivos FAISS.
    
    Args:
        question: Pregunta del usuario
        client_id: ID del cliente en PostgreSQL
        
    Returns:
        Respuesta generada por la IA
    """
    try:
        from ..vector_manager import VectorManager
        from ..models import Client
        
        # 1. Verificar que el cliente existe (buscar por public_id)
        client = Client.query.filter_by(public_id=client_id).first()
        if not client:
            print(f"❌ Cliente no encontrado: {client_id}")
            return "Lo siento, no puedo acceder a tu base de conocimiento."
        
        print(f"🔍 Procesando consulta para cliente: {client.name}")
        
        # 2. Buscar chunks relevantes en PostgreSQL
        vector_manager = VectorManager()
        similar_chunks = vector_manager.search_similar_chunks(client.id, question, top_k=3)
        
        if not similar_chunks:
            print("⚠️ No se encontraron chunks relevantes")
            return "No tengo información sobre eso en mi base de conocimiento, pero un asesor experto puede ayudarte."
        
        # 3. Construir contexto desde PostgreSQL
        context_parts = []
        for i, chunk in enumerate(similar_chunks):
            context_parts.append(f"[Fragmento {i+1}]: {chunk['text']}")
        
        context = "\n\n".join(context_parts)
        print(f"📄 Contexto construido: {len(context)} caracteres desde {len(similar_chunks)} chunks")
        
        # 4. Configurar modelo de IA
        llm = None
        if Config.AI_PROVIDER == 'ollama':
            try:
                llm = Ollama(model="phi3:mini") 
                print("🤖 Usando Ollama")
            except Exception as e:
                print(f"❌ Error con Ollama: {e}")
                return "Error de conexión con el proveedor de IA local."
        
        if llm is None:
            llm = ChatGoogleGenerativeAI(
                model="gemini-1.5-flash-latest",
                google_api_key=Config.GOOGLE_API_KEY,
                temperature=0.2,
                convert_system_message_to_human=True
            )
            print("🤖 Usando Google Gemini")
        
        # 5. Generar respuesta usando prompt específico por idioma
        prompt_text = get_language_specific_prompt(question, context)
        
        # Usar el modelo directamente en lugar de RetrievalQA
        if hasattr(llm, 'predict'):
            result = llm.predict(prompt_text)
        else:
            # Para modelos de chat
            result = llm.invoke(prompt_text)
            if hasattr(result, 'content'):
                result = result.content
        
        # 6. Verificar si necesita generar cotización con SISTEMA V2 (SIN REFRESH)
        try:
            from ..quote_system_v2 import generate_quote_v2_if_requested
            result, quote_result = generate_quote_v2_if_requested(result, question, client.name)
            if quote_result:
                print(f"✅ Cotización V2 generada: {quote_result['quote_number']} (SIN REFRESH)")
            else:
                print(f"✅ Respuesta generada exitosamente (sin cotización)")
        except ImportError:
            print("⚠️ Módulo de cotizaciones V2 no disponible - usando fallback")
            try:
                from ..quote_generator import generate_quote_if_requested
                result, pdf_url = generate_quote_if_requested(result, question, client.name)
                print(f"✅ Fallback: cotización generada. PDF: {pdf_url is not None}")
            except Exception as e2:
                print(f"⚠️ Error en fallback: {e2}")
        except Exception as e:
            print(f"⚠️ Error generando cotización V2: {e}")
        
        return result

    except Exception as e:
        print("💥 ERROR EN LA CADENA RAG POSTGRESQL")
        print(f"   Cliente ID: {client_id}")
        print(f"   Pregunta: {question[:100]}...")
        print(f"   Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return "Ocurrió un error al procesar tu solicitud. Por favor, contacta a un asesor."


# --- FUNCIÓN DE COMPATIBILIDAD PARA CÓDIGO LEGACY ---
def get_commercial_response_legacy(question: str, client_index_path: str) -> str:
    """
    FUNCIÓN LEGACY: Mantiene compatibilidad con código existente.
    Intenta mapear client_index_path a client_id y usar PostgreSQL.
    
    Args:
        question: Pregunta del usuario
        client_index_path: Path del cliente (se intentará mapear a ID)
        
    Returns:
        Respuesta generada
    """
    try:
        from ..models import Client
        
        # Intentar encontrar cliente por index_path
        client = Client.query.filter_by(index_path=client_index_path).first()
        
        if not client:
            # Intentar buscar por coincidencia en el nombre del path
            import os
            path_name = os.path.basename(client_index_path)
            # Buscar cliente cuyo nombre coincida aproximadamente
            all_clients = Client.query.all()
            for c in all_clients:
                client_slug = c.name.lower().replace(' ', '_').replace('á', 'a').replace('é', 'e')
                if client_slug in path_name.lower() or path_name.lower() in client_slug:
                    client = c
                    break
        
        if client:
            print(f"🔄 Redirigiendo legacy path '{client_index_path}' -> Cliente ID {client.id}")
            return get_commercial_response(question, client.id)
        else:
            print(f"❌ No se pudo mapear path legacy '{client_index_path}' a cliente PostgreSQL")
            return "Lo siento, no puedo acceder a la base de conocimiento solicitada."
    
    except Exception as e:
        print(f"❌ Error en función legacy: {e}")
        return "Error al procesar la consulta con el sistema legacy."