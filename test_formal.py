"""
Script de pruebas automáticas para SalesMind v2.0.0
Verifica todas las funcionalidades comerciales
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://127.0.0.1:5000"

class SalesMindTester:
    def __init__(self):
        self.client_id = 1
        self.session = requests.Session()
        self.results = []
    
    def log_test(self, test_name, success, details=""):
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"    {details}")
        self.results.append({
            'test': test_name,
            'success': success,
            'details': details,
            'timestamp': datetime.now()
        })
    
    def test_server_health(self):
        """Test 1: Verificar que el servidor esté funcionando"""
        try:
            response = self.session.get(f"{BASE_URL}/")
            success = response.status_code == 200
            self.log_test("Servidor Principal", success, f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("Servidor Principal", False, str(e))
            return False
    
    def test_admin_dashboard(self):
        """Test 2: Verificar dashboard administrativo"""
        try:
            response = self.session.get(f"{BASE_URL}/admin/indexer/")
            success = response.status_code == 200
            self.log_test("Dashboard Administrativo", success, f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("Dashboard Administrativo", False, str(e))
            return False
    
    def test_add_product(self):
        """Test 3: Agregar producto al inventario"""
        try:
            product_data = {
                "client_id": self.client_id,
                "product_data": {
                    "name": "Apartamento 2 Habitaciones Premium",
                    "description": "Apartamento moderno de 2 habitaciones con balcón y vista panorámica",
                    "category": "Vivienda",
                    "sku": "APT-2H-PREM-001",
                    "base_price": 180000000,
                    "stock_quantity": 10,
                    "min_stock_alert": 3,
                    "discount_percentage": 5.0,
                    "tax_rate": 19.0
                }
            }
            
            response = self.session.post(
                f"{BASE_URL}/commercial/inventory/product/add",
                json=product_data,
                headers={'Content-Type': 'application/json'}
            )
            
            data = response.json()
            success = data.get('success', False)
            details = f"Product ID: {data.get('product_id', 'N/A')}" if success else data.get('error', 'Unknown error')
            
            self.log_test("Agregar Producto", success, details)
            
            if success:
                self.product_id = data.get('product_id')
            
            return success
            
        except Exception as e:
            self.log_test("Agregar Producto", False, str(e))
            return False
    
    def test_generate_quote(self):
        """Test 4: Generar cotización automática"""
        try:
            quote_data = {
                "client_id": self.client_id,
                "customer_query": "Necesito 2 apartamentos de 2 habitaciones premium para mi familia",
                "customer_info": {
                    "name": "María García Test",
                    "email": "maria.test@email.com",
                    "phone": "3001234567"
                }
            }
            
            response = self.session.post(
                f"{BASE_URL}/commercial/quote/generate",
                json=quote_data,
                headers={'Content-Type': 'application/json'}
            )
            
            data = response.json()
            success = data.get('success', False)
            
            if success:
                details = f"Quote: {data.get('quote_number', 'N/A')}, Total: ${data.get('total_amount', 0):,.0f}"
                self.quote_id = data.get('quote_id')
            else:
                details = data.get('error', 'Unknown error')
            
            self.log_test("Generar Cotización", success, details)
            return success
            
        except Exception as e:
            self.log_test("Generar Cotización", False, str(e))
            return False
    
    def test_accept_quote_create_order(self):
        """Test 5: Aceptar cotización y crear orden"""
        if not hasattr(self, 'quote_id'):
            self.log_test("Crear Orden", False, "No hay cotización disponible")
            return False
        
        try:
            # Primero actualizar cotización a "accepted"
            response = self.session.put(
                f"{BASE_URL}/commercial/quote/{self.quote_id}/status",
                json={"status": "accepted"},
                headers={'Content-Type': 'application/json'}
            )
            
            if not response.json().get('success'):
                self.log_test("Crear Orden", False, "Error actualizando cotización")
                return False
            
            # Crear orden desde cotización
            order_data = {
                "quote_id": self.quote_id,
                "additional_info": {
                    "shipping_address": "Calle 123 #45-67, Bogotá, Colombia",
                    "free_shipping": False
                }
            }
            
            response = self.session.post(
                f"{BASE_URL}/commercial/order/create-from-quote",
                json=order_data,
                headers={'Content-Type': 'application/json'}
            )
            
            data = response.json()
            success = data.get('success', False)
            
            if success:
                details = f"Order: {data.get('order_number', 'N/A')}, Total: ${data.get('total_amount', 0):,.0f}"
                self.order_id = data.get('order_id')
            else:
                details = data.get('error', 'Unknown error')
            
            self.log_test("Crear Orden", success, details)
            return success
            
        except Exception as e:
            self.log_test("Crear Orden", False, str(e))
            return False
    
    def test_update_order_status(self):
        """Test 6: Actualizar estado de orden"""
        if not hasattr(self, 'order_id'):
            self.log_test("Actualizar Orden", False, "No hay orden disponible")
            return False
        
        try:
            response = self.session.put(
                f"{BASE_URL}/commercial/order/{self.order_id}/status",
                json={
                    "status": "confirmed", 
                    "notes": "Orden confirmada por sistema de pruebas"
                },
                headers={'Content-Type': 'application/json'}
            )
            
            data = response.json()
            success = data.get('success', False)
            details = data.get('message', '') if success else data.get('error', 'Unknown error')
            
            self.log_test("Actualizar Orden", success, details)
            return success
            
        except Exception as e:
            self.log_test("Actualizar Orden", False, str(e))
            return False
    
    def test_generate_invoice(self):
        """Test 7: Generar factura automática"""
        if not hasattr(self, 'order_id'):
            self.log_test("Generar Factura", False, "No hay orden disponible")
            return False
        
        try:
            invoice_data = {
                "order_id": self.order_id,
                "tax_info": {
                    "company_name": "Constructora Test SAS",
                    "company_tax_id": "900123456-1",
                    "company_address": "Av. Principal #123-45, Bogotá",
                    "company_phone": "601-2345678"
                }
            }
            
            response = self.session.post(
                f"{BASE_URL}/commercial/invoice/generate",
                json=invoice_data,
                headers={'Content-Type': 'application/json'}
            )
            
            data = response.json()
            success = data.get('success', False)
            
            if success:
                details = f"Invoice: {data.get('invoice_number', 'N/A')}, PDF: {data.get('pdf_path', 'N/A')}"
                self.invoice_id = data.get('invoice_id')
            else:
                details = data.get('error', 'Unknown error')
            
            self.log_test("Generar Factura", success, details)
            return success
            
        except Exception as e:
            self.log_test("Generar Factura", False, str(e))
            return False
    
    def test_create_lead(self):
        """Test 8: Crear lead en CRM"""
        try:
            lead_data = {
                "client_id": self.client_id,
                "lead_data": {
                    "name": "Carlos Ruiz Test",
                    "email": "carlos.test@empresa.com",
                    "phone": "3009876543",
                    "company": "Empresa Test SAS",
                    "source": "website",
                    "estimated_value": 250000000,
                    "notes": "Lead generado por sistema de pruebas automatizado"
                }
            }
            
            response = self.session.post(
                f"{BASE_URL}/commercial/crm/lead/create",
                json=lead_data,
                headers={'Content-Type': 'application/json'}
            )
            
            data = response.json()
            success = data.get('success', False)
            
            if success:
                details = f"Lead ID: {data.get('lead_id', 'N/A')}"
                self.lead_id = data.get('lead_id')
            else:
                details = data.get('error', 'Unknown error')
            
            self.log_test("Crear Lead CRM", success, details)
            return success
            
        except Exception as e:
            self.log_test("Crear Lead CRM", False, str(e))
            return False
    
    def test_inventory_report(self):
        """Test 9: Generar reporte de inventario"""
        try:
            response = self.session.get(f"{BASE_URL}/commercial/inventory/report/{self.client_id}")
            
            data = response.json()
            success = data.get('success', False)
            
            if success:
                report = data.get('report', {})
                summary = report.get('summary', {})
                details = f"Productos: {summary.get('total_products', 0)}, Valor: ${summary.get('total_stock_value', 0):,.0f}"
            else:
                details = data.get('error', 'Unknown error')
            
            self.log_test("Reporte Inventario", success, details)
            return success
            
        except Exception as e:
            self.log_test("Reporte Inventario", False, str(e))
            return False
    
    def test_crm_pipeline(self):
        """Test 10: Verificar pipeline de CRM"""
        try:
            response = self.session.get(f"{BASE_URL}/commercial/crm/pipeline/{self.client_id}")
            
            data = response.json()
            success = data.get('success', False)
            
            if success:
                pipeline = data.get('pipeline', {})
                summary = pipeline.get('summary', {})
                details = f"Total leads: {summary.get('total_leads', 0)}, Activos: {summary.get('active_leads', 0)}"
            else:
                details = data.get('error', 'Unknown error')
            
            self.log_test("Pipeline CRM", success, details)
            return success
            
        except Exception as e:
            self.log_test("Pipeline CRM", False, str(e))
            return False
    
    def run_all_tests(self):
        """Ejecuta todas las pruebas en orden"""
        print("🚀 Iniciando pruebas formales de SalesMind v2.0.0...")
        print("=" * 60)
        
        tests = [
            self.test_server_health,
            self.test_admin_dashboard,
            self.test_add_product,
            self.test_generate_quote,
            self.test_accept_quote_create_order,
            self.test_update_order_status,
            self.test_generate_invoice,
            self.test_create_lead,
            self.test_inventory_report,
            self.test_crm_pipeline
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            try:
                if test():
                    passed += 1
                time.sleep(1)  # Pausa entre pruebas
            except Exception as e:
                print(f"❌ Error ejecutando {test.__name__}: {e}")
        
        print("\n" + "=" * 60)
        print(f"📊 RESUMEN DE PRUEBAS:")
        print(f"   Total: {total}")
        print(f"   Pasaron: {passed}")
        print(f"   Fallaron: {total - passed}")
        print(f"   Éxito: {passed/total*100:.1f}%")
        
        if passed == total:
            print("\n🎉 ¡TODAS LAS PRUEBAS PASARON! SalesMind v2.0.0 está funcionando correctamente.")
        else:
            print(f"\n⚠️  {total - passed} pruebas fallaron. Revisar implementación.")
        
        return passed == total

if __name__ == "__main__":
    tester = SalesMindTester()
    success = tester.run_all_tests()
    exit(0 if success else 1)