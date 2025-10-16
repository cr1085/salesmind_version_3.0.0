from modules import create_app, db

# Creamos una instancia de la aplicación para tener el contexto correcto
app = create_app()

# Usamos el contexto de la aplicación para interactuar con la base de datos
with app.app_context():
    print("🚀 === INICIALIZANDO POSTGRESQL PARA SALESMIND ===")
    print("📊 Creando todas las tablas necesarias...")
    
    # Este comando lee todos los modelos y crea las tablas correspondientes
    db.create_all()
    
    print("\n✅ ¡Tablas creadas con éxito!")
    
    # Mostrar información de las tablas creadas
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    
    print(f"\n📋 Tablas creadas en PostgreSQL:")
    for table in sorted(tables):
        print(f"   📄 {table}")
    
    print(f"\n🎯 Total: {len(tables)} tablas")
    print("\n🔧 Para añadir un cliente, usa:")
    print("   flask add-client \"Nombre Cliente\" \"telegram_chat_id\" \"ruta/pdfs\"")
    
    print("\n🎉 ¡Sistema PostgreSQL listo para usar!")