"""
Script de migración para SalesMind versión 2.0.0
Agrega funcionalidades comerciales completas
"""

from modules.models import db
from modules.commercial_models import (
    Product, Quote, QuoteItem, Order, OrderItem, 
    Invoice, InventoryMovement, Lead, LeadInteraction
)

def upgrade_database():
    """
    Ejecuta la migración de base de datos para agregar tablas comerciales
    """
    try:
        print("🚀 Iniciando migración de SalesMind a versión 2.0.0...")
        
        # Crear todas las nuevas tablas
        db.create_all()
        
        print("✅ Tablas creadas exitosamente:")
        print("   - products (Catálogo de productos/servicios)")
        print("   - quotes (Cotizaciones automáticas)")
        print("   - quote_items (Elementos de cotización)")
        print("   - orders (Órdenes/pedidos)")
        print("   - order_items (Elementos de orden)")
        print("   - invoices (Facturas automáticas)")
        print("   - inventory_movements (Movimientos de inventario)")
        print("   - leads (Gestión CRM)")
        print("   - lead_interactions (Historial de interacciones)")
        
        print("\n🎉 ¡Migración completada exitosamente!")
        print("\n📋 SalesMind ahora incluye:")
        print("   ✅ Sistema de cotizaciones automáticas")
        print("   ✅ Procesamiento completo de pedidos")
        print("   ✅ Gestión de inventarios en tiempo real")
        print("   ✅ Generación automática de facturas")
        print("   ✅ CRM completo con pipeline de ventas")
        
        return True
        
    except Exception as e:
        print(f"❌ Error durante la migración: {e}")
        return False

if __name__ == '__main__':
    from app import app
    
    with app.app_context():
        upgrade_database()