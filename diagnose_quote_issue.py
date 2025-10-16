#!/usr/bin/env python
# diagnose_quote_issue.py - DIAGNOSTICAR PROBLEMA DE COTIZACIÓN SIN TOCAR CÓDIGO CORE
"""
🔍 DIAGNÓSTICO DE PROBLEMA DE COTIZACIÓN
========================================

Este script analiza por qué la cotización no usa datos reales del cliente.
NO MODIFICA CÓDIGO EXISTENTE - Solo diagnostica.

VERIFICACIONES:
✅ Cliente activo y sus datos
✅ Documentos y contenido 
✅ Embeddings disponibles
✅ Índice FAISS funcional
✅ Búsqueda RAG
✅ Contexto recuperado
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

def diagnose_quote_system():
    """Diagnostica sistema de cotizaciones sin tocar código core."""
    
    print("🔍 DIAGNÓSTICO DE SISTEMA DE COTIZACIONES")
    print("=" * 60)
    
    from modules import create_app, db
    from modules.models import Client, Document, Embedding, FAISSIndex
    from modules.vector_manager import VectorManager
    
    app = create_app()
    with app.app_context():
        
        # 1. Verificar cliente demo
        print("\n📊 PASO 1: Verificando cliente actual")
        client = Client.query.filter_by(public_id='demo-client-12345').first()
        
        if not client:
            print("❌ Cliente demo no encontrado - revisar pagina_cliente_ejemplo.html")
            return
            
        print(f"✅ Cliente: {client.name} (ID: {client.id})")
        
        # 2. Verificar documentos
        print("\n📄 PASO 2: Verificando documentos")
        documents = Document.query.filter_by(client_id=client.id).all()
        
        if not documents:
            print("❌ No hay documentos para este cliente")
            return
            
        for doc in documents:
            print(f"✅ Documento: {doc.filename}")
            print(f"   - Tamaño texto: {len(doc.extracted_text or '')} caracteres")
            print(f"   - Procesado: {doc.is_processed}")
            
            # Mostrar muestra del contenido
            if doc.extracted_text:
                sample = doc.extracted_text[:300] + "..." if len(doc.extracted_text) > 300 else doc.extracted_text
                print(f"   - Contenido muestra: {sample}")
        
        # 3. Verificar embeddings
        print(f"\n🧮 PASO 3: Verificando embeddings")
        embeddings = Embedding.query.filter_by(client_id=client.id).all()
        print(f"✅ Total embeddings: {len(embeddings)}")
        
        for i, emb in enumerate(embeddings):
            chunk_sample = emb.text_chunk[:100] + "..." if len(emb.text_chunk) > 100 else emb.text_chunk
            print(f"   Chunk {i+1}: {chunk_sample}")
        
        # 4. Verificar índice FAISS
        print(f"\n🔧 PASO 4: Verificando índice FAISS")
        faiss_indexes = FAISSIndex.query.filter_by(client_id=client.id, is_active=True).all()
        
        for idx in faiss_indexes:
            print(f"✅ Índice: {idx.index_name}")
            print(f"   - Vectores: {idx.total_vectors}")
            print(f"   - Dimensión: {idx.vector_dimension}")
        
        # 5. Probar búsqueda RAG
        print(f"\n🔍 PASO 5: Probando búsqueda RAG")
        vector_manager = VectorManager()
        
        test_queries = [
            "casa precio",
            "apartamento costo", 
            "cotización propiedad",
            "price house"
        ]
        
        for query in test_queries:
            try:
                results = vector_manager.search_similar_chunks(client.id, query, top_k=2)
                print(f"\n🔍 Búsqueda: '{query}'")
                print(f"   Resultados: {len(results)}")
                
                for i, result in enumerate(results):
                    chunk_text = result.get('text', '')[:200] + "..." if len(result.get('text', '')) > 200 else result.get('text', '')
                    score = result.get('similarity_score', 0)
                    print(f"   Resultado {i+1} (score: {score:.4f}): {chunk_text}")
                    
            except Exception as e:
                print(f"❌ Error en búsqueda '{query}': {e}")
        
        # 6. Probar extracción de información para cotización
        print(f"\n💰 PASO 6: Probando extracción de cotización")
        
        try:
            from modules.quote_generator import QuoteGenerator
            
            # Simular respuesta con datos reales del cliente
            sample_contexts = []
            for emb in embeddings:
                sample_contexts.append(emb.text_chunk)
            
            combined_context = "\n".join(sample_contexts)
            
            generator = QuoteGenerator()
            quote_info = generator.extract_quote_info(combined_context, "¿Puedes enviarme una cotización oficial?")
            
            print("📊 Información extraída para cotización:")
            print(f"   - Productos encontrados: {len(quote_info.get('products', []))}")
            print(f"   - Precio total: ${quote_info.get('total_price', 0):,.2f}")
            
            for i, product in enumerate(quote_info.get('products', [])):
                print(f"   Producto {i+1}:")
                print(f"     - Nombre: {product.get('name', 'N/A')}")
                print(f"     - Precio: ${product.get('price', 0):,.2f}")
                print(f"     - Descripción: {product.get('description', 'N/A')[:100]}...")
                
        except Exception as e:
            print(f"❌ Error probando cotización: {e}")
        
        # 7. Diagnóstico final
        print(f"\n🎯 DIAGNÓSTICO FINAL")
        print("=" * 40)
        
        issues_found = []
        
        if not documents:
            issues_found.append("Sin documentos")
        elif not any(doc.extracted_text for doc in documents):
            issues_found.append("Documentos sin texto extraído")
            
        if not embeddings:
            issues_found.append("Sin embeddings")
            
        if not faiss_indexes:
            issues_found.append("Sin índices FAISS")
            
        # Verificar si hay precios en los documentos
        all_text = " ".join([doc.extracted_text or "" for doc in documents])
        has_prices = any(keyword in all_text.lower() for keyword in ["$", "precio", "price", "costo", "cost"])
        
        if not has_prices:
            issues_found.append("Documentos no contienen precios")
            
        if not issues_found:
            print("✅ SISTEMA TÉCNICAMENTE CORRECTO")
            print("🔍 POSIBLES CAUSAS DEL PROBLEMA:")
            print("   1. Cliente incorrecto en pagina_cliente_ejemplo.html")
            print("   2. Documentos no tienen información de precios")
            print("   3. Texto extraído no es el esperado")
            print("   4. Búsqueda RAG no encuentra contexto relevante")
        else:
            print("❌ PROBLEMAS ENCONTRADOS:")
            for issue in issues_found:
                print(f"   • {issue}")

if __name__ == "__main__":
    diagnose_quote_system()