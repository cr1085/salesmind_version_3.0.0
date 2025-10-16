"""
Pruebas manuales paso a paso para SalesMind v2.0.0
Guía de testing con resultados esperados
"""

import requests
import json

def test_commercial_endpoints():
    """Prueba los endpoints comerciales uno por uno"""
    base_url = "http://127.0.0.1:5000"
    
    print("🧪 INICIANDO PRUEBAS COMERCIALES DE SALESMIND v2.0.0")
    print("=" * 60)
    
    # Test 1: Agregar producto
    print("\n1️⃣ AGREGANDO PRODUCTO AL INVENTARIO...")
    
    product_data = {
        "client_id": 1,
        "product_data": {
            "name": "Apartamento 2 Habitaciones Deluxe",
            "description": "Apartamento moderno con balcón y vista panorámica",
            "category": "Vivienda",
            "sku": "APT-2H-DLX-001", 
            "base_price": 200000000,
            "stock_quantity": 8,
            "min_stock_alert": 2,
            "discount_percentage": 10.0
        }
    }
    
    try:
        response = requests.post(
            f"{base_url}/commercial/inventory/product/add",
            json=product_data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print(f"   ✅ Producto creado exitosamente: ID {result.get('product_id')}")
                product_id = result.get('product_id')
            else:
                print(f"   ❌ Error: {result.get('error')}")
                return False
        else:
            print(f"   ❌ Error HTTP: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Excepción: {e}")
        return False
    
    # Test 2: Generar cotización
    print("\n2️⃣ GENERANDO COTIZACIÓN AUTOMÁTICA...")
    
    quote_data = {
        "client_id": 1,
        "customer_query": "Quiero 2 apartamentos de 2 habitaciones deluxe",
        "customer_info": {
            "name": "Ana María López",
            "email": "ana@ejemplo.com",
            "phone": "3101234567"
        }
    }
    
    try:
        response = requests.post(
            f"{base_url}/commercial/quote/generate",
            json=quote_data,
            timeout=30  # Más tiempo para IA
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                quote_id = result.get('quote_id')
                total = result.get('total_amount', 0)
                print(f"   ✅ Cotización generada: {result.get('quote_number')} por ${total:,.0f}")
            else:
                print(f"   ❌ Error: {result.get('error')}")
                # Continuar con pruebas manuales si IA no funciona
                quote_id = None
        else:
            print(f"   ❌ Error HTTP: {response.status_code}")
            quote_id = None
            
    except Exception as e:
        print(f"   ❌ Excepción: {e}")
        quote_id = None
    
    # Test 3: Crear lead en CRM
    print("\n3️⃣ CREANDO LEAD EN CRM...")
    
    lead_data = {
        "client_id": 1,
        "lead_data": {
            "name": "Roberto González",
            "email": "roberto@empresa.com", 
            "phone": "3207654321",
            "company": "González & Asociados",
            "source": "website",
            "estimated_value": 350000000,
            "notes": "Interesado en múltiples unidades"
        }
    }
    
    try:
        response = requests.post(
            f"{base_url}/commercial/crm/lead/create",
            json=lead_data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print(f"   ✅ Lead creado exitosamente: ID {result.get('lead_id')}")
            else:
                print(f"   ❌ Error: {result.get('error')}")
        else:
            print(f"   ❌ Error HTTP: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Excepción: {e}")
    
    # Test 4: Reporte de inventario
    print("\n4️⃣ GENERANDO REPORTE DE INVENTARIO...")
    
    try:
        response = requests.get(f"{base_url}/commercial/inventory/report/1", timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                report = result.get('report', {})
                summary = report.get('summary', {})
                total_products = summary.get('total_products', 0)
                total_value = summary.get('total_stock_value', 0)
                print(f"   ✅ Reporte generado: {total_products} productos, valor ${total_value:,.0f}")
            else:
                print(f"   ❌ Error: {result.get('error')}")
        else:
            print(f"   ❌ Error HTTP: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Excepción: {e}")
    
    # Test 5: Pipeline de CRM
    print("\n5️⃣ VERIFICANDO PIPELINE DE CRM...")
    
    try:
        response = requests.get(f"{base_url}/commercial/crm/pipeline/1", timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                pipeline = result.get('pipeline', {})
                summary = pipeline.get('summary', {})
                total_leads = summary.get('total_leads', 0)
                active_leads = summary.get('active_leads', 0)
                print(f"   ✅ Pipeline verificado: {total_leads} leads totales, {active_leads} activos")
            else:
                print(f"   ❌ Error: {result.get('error')}")
        else:
            print(f"   ❌ Error HTTP: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Excepción: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 PRUEBAS BÁSICAS COMPLETADAS")
    print("\nPróximos pasos de testing manual:")
    print("1. Abrir http://localhost:5000/admin/indexer/ - Verificar dashboard")
    print("2. Probar chat normal en http://localhost:5000/ - Consultar precios")
    print("3. Verificar logs en consola del servidor")
    print("4. Revisar base de datos para confirmar registros")
    
    return True

if __name__ == "__main__":
    test_commercial_endpoints()