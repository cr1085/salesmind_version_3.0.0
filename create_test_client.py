# create_test_client.py
"""
Script para crear un cliente de prueba en la base de datos
"""

def create_test_client():
    """Crea un cliente de prueba si no existe"""
    
    try:
        from modules import create_app, db
        from modules.models import Client
        import uuid
        
        # Crear aplicación
        app = create_app()
        
        with app.app_context():
            # Verificar si ya existe el cliente de prueba
            test_client = Client.query.filter_by(name='Cliente Demo').first()
            
            if test_client:
                print(f"✅ Cliente de prueba ya existe:")
                print(f"   Nombre: {test_client.name}")
                print(f"   ID Público: {test_client.public_id}")
                return test_client.public_id
            
            # Crear nuevo cliente
            new_client = Client(
                name='Cliente Demo',
                public_id='demo-client-12345',  # ID fijo para pruebas
                telegram_chat_id=None
            )
            
            db.session.add(new_client)
            db.session.commit()
            
            print(f"✅ Cliente de prueba creado:")
            print(f"   Nombre: {new_client.name}")
            print(f"   ID Público: {new_client.public_id}")
            print(f"   ID en DB: {new_client.id}")
            
            return new_client.public_id
            
    except Exception as e:
        print(f"❌ Error creando cliente: {e}")
        import traceback
        traceback.print_exc()
        return None

def add_sample_documents():
    """Agrega documentos de ejemplo para pruebas"""
    
    try:
        from modules import create_app, db
        from modules.models import Client, Document
        import hashlib
        
        app = create_app()
        
        with app.app_context():
            # Buscar cliente demo
            client = Client.query.filter_by(public_id='demo-client-12345').first()
            if not client:
                print("❌ Cliente demo no encontrado")
                return
            
            # Texto de ejemplo sobre propiedades
            sample_text = """
            CATÁLOGO DE PROPIEDADES INMOBILIARIAS
            
            🏠 CASA MODELO AURORA
            Precio: $250,000 USD
            Características:
            - 3 habitaciones principales
            - 2 baños completos
            - Sala, comedor y cocina integral
            - Garaje techado para 2 vehículos
            - Jardín privado de 50 m²
            - Área de construcción: 120 m²
            - Área del lote: 200 m²
            
            🏠 CASA MODELO DIAMANTE  
            Precio: $180,000 USD
            Características:
            - 2 habitaciones principales
            - 2 baños completos
            - Sala comedor integrada
            - Cocina tipo americano
            - Jardín frontal y trasero
            - Área de construcción: 95 m²
            - Área del lote: 150 m²
            
            🏠 CASA MODELO ESMERALDA
            Precio: $320,000 USD  
            Características:
            - 4 habitaciones (1 principal con baño privado)
            - 3 baños completos
            - Sala, comedor, cocina y estudio
            - Garaje doble techado
            - Piscina y zona social
            - Área de construcción: 180 m²
            - Área del lote: 300 m²
            
            SERVICIOS INCLUIDOS:
            ✅ Escrituras al día
            ✅ Servicios públicos instalados (agua, luz, gas, internet)
            ✅ Asesoría legal gratuita durante todo el proceso
            ✅ Financiación hasta 20 años
            ✅ Entrega inmediata
            
            UBICACIÓN: Urbanización Los Pinos
            - A 10 minutos del centro comercial
            - Cerca de colegios y universidades
            - Transporte público disponible
            - Zona residencial segura
            
            CONTACTO:
            📧 ventas@inmobiliariademo.com
            📱 +1 (555) 123-4567
            🌐 www.inmobiliariademo.com
            """
            
            # Crear hash del contenido
            content_hash = hashlib.sha256(sample_text.encode()).hexdigest()
            
            # Verificar si ya existe
            existing_doc = Document.query.filter_by(
                client_id=client.id, 
                content_hash=content_hash
            ).first()
            
            if existing_doc:
                print("✅ Documentos de ejemplo ya existen")
                return
            
            # Crear documento
            sample_doc = Document(
                client_id=client.id,
                filename='catalogo_propiedades.txt',
                file_type='txt',
                file_size=len(sample_text.encode()),
                file_content=sample_text.encode(),
                extracted_text=sample_text,
                is_processed=True,
                content_hash=content_hash
            )
            
            db.session.add(sample_doc)
            db.session.commit()
            
            print(f"✅ Documento de ejemplo creado:")
            print(f"   Archivo: {sample_doc.filename}")
            print(f"   Tamaño: {sample_doc.file_size} bytes")
            print(f"   Cliente: {client.name}")
            
    except Exception as e:
        print(f"❌ Error agregando documentos: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 CONFIGURANDO CLIENTE DE PRUEBA")
    print("=" * 50)
    
    client_id = create_test_client()
    if client_id:
        print()
        add_sample_documents()
        print()
        print("🎉 CONFIGURACIÓN COMPLETADA")
        print(f"🔗 Usar ID de cliente: {client_id}")
        print("📝 Ya puedes probar el chat multilenguaje y cotizaciones")
    else:
        print("❌ Error en la configuración")