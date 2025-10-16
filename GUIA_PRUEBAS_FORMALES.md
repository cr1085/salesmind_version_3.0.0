# 🧪 GUÍA DE PRUEBAS FORMALES - SalesMind v2.0.0
## Procedimiento de Testing Completo para Funcionalidades Comerciales

---

## 📋 **PRERREQUISITOS**

### **1. Instalar Nuevas Dependencias:**
```bash
pip install reportlab==4.0.4 Pillow==10.0.1
```

### **2. Verificar Estado del Sistema:**
```bash
# Verificar que el servidor no esté corriendo
# Cerrar cualquier instancia de python app.py

# Verificar base de datos PostgreSQL activa
# Asegurarse de que la BD 'salesmind' esté accesible
```

---

## 🔧 **PASO 1: PREPARACIÓN DEL ENTORNO**

### **1.1 Ejecutar Migración de Base de Datos:**
```bash
python migrate_to_v2.py
```
**Resultado esperado:** 
```
🚀 Iniciando migración de SalesMind a versión 2.0.0...
✅ Tablas creadas exitosamente:
   - products (Catálogo de productos/servicios)
   - quotes (Cotizaciones automáticas)
   - quote_items (Elementos de cotización)
   - orders (Órdenes/pedidos)
   - order_items (Elementos de orden)
   - invoices (Facturas automáticas)
   - inventory_movements (Movimientos de inventario)
   - leads (Gestión CRM)
   - lead_interactions (Historial de interacciones)

🎉 ¡Migración completada exitosamente!
```

### **1.2 Registrar Rutas Comerciales:**
Agregar al final de `app.py`:
```python
# Registrar módulo comercial
try:
    from modules.commercial.routes import register_commercial_routes
    register_commercial_routes(app)
    print("✅ Módulo comercial registrado exitosamente")
except ImportError as e:
    print(f"⚠️ Error cargando módulo comercial: {e}")
```

---

## 🚀 **PASO 2: INICIAR SISTEMA**

### **2.1 Ejecutar Servidor:**
```bash
python app.py
```

**Verificar salida esperada:**
```
✅ Módulo comercial registrado exitosamente
✅ Conexión a PostgreSQL establecida
✅ Modelos de base de datos sincronizados
 * Running on http://127.0.0.1:5000
```

### **2.2 Verificar Endpoints Básicos:**
Abrir navegador y verificar:
- ✅ `http://localhost:5000/` - Página principal funcional
- ✅ `http://localhost:5000/admin/indexer/` - Dashboard administrativo
- ✅ Sin errores en consola

---

## 🧪 **PASO 3: PRUEBAS FUNCIONALES COMERCIALES**

### **3.1 Test de API - Crear Producto (Postman/curl):**
```bash
curl -X POST http://localhost:5000/commercial/inventory/product/add \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": 1,
    "product_data": {
      "name": "Apartamento 2 Habitaciones",
      "description": "Apartamento moderno de 2 habitaciones con balcón",
      "category": "Vivienda",
      "sku": "APT-2H-001",
      "base_price": 150000000,
      "stock_quantity": 5,
      "min_stock_alert": 2
    }
  }'
```

**Resultado esperado:**
```json
{
  "success": true,
  "product_id": 1,
  "public_id": "uuid-generado",
  "message": "Producto Apartamento 2 Habitaciones agregado exitosamente"
}
```

### **3.2 Test de Cotización Automática:**
```bash
curl -X POST http://localhost:5000/commercial/quote/generate \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": 1,
    "customer_query": "Quiero 2 apartamentos de 2 habitaciones",
    "customer_info": {
      "name": "Juan Pérez",
      "email": "juan@email.com",
      "phone": "3001234567"
    }
  }'
```

**Resultado esperado:**
```json
{
  "success": true,
  "quote_id": 1,
  "quote_number": "COT-20251013-XXXXX",
  "total_amount": 300000000.0,
  "products": [...],
  "valid_until": "2025-11-12T..."
}
```

### **3.3 Test de Dashboard Comercial:**
Acceder a: `http://localhost:5000/commercial/dashboard/1`

**Verificar que se muestren:**
- ✅ Estadísticas del pipeline de ventas
- ✅ Resumen de órdenes
- ✅ Estado del inventario
- ✅ Alertas (sin errores de carga)

---

## 📊 **PASO 4: PRUEBAS DE INTEGRACIÓN CON IA**

### **4.1 Test de Procesamiento Inteligente de Mensajes:**
```bash
curl -X POST http://localhost:5000/commercial/ai/process-customer-message \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": 1,
    "message": "¿Cuánto cuesta un apartamento de 2 habitaciones?",
    "customer_info": {
      "name": "María García",
      "email": "maria@email.com"
    }
  }'
```

**Resultado esperado:**
```json
{
  "success": true,
  "action": "quote_generated",
  "quote": {
    "quote_id": 2,
    "total_amount": 150000000.0
  },
  "message": "He generado una cotización automática por $150,000,000. ¿Te interesa proceder con la orden?"
}
```

### **4.2 Test de Chat Existente con Nueva Funcionalidad:**
- Ir al chat normal: `http://localhost:5000/` 
- Hacer consulta: "Quiero comprar apartamentos"
- **Verificar:** Que el sistema detecte intención comercial y ofrezca cotización

---

## 🔄 **PASO 5: FLUJO COMPLETO DE VENTA**

### **5.1 Crear Lead:**
```bash
curl -X POST http://localhost:5000/commercial/crm/lead/create \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": 1,
    "lead_data": {
      "name": "Carlos Ruiz",
      "email": "carlos@empresa.com",
      "phone": "3009876543",
      "company": "Empresa Test",
      "source": "website",
      "estimated_value": 200000000
    }
  }'
```

### **5.2 Generar Cotización para Lead:**
```bash
curl -X POST http://localhost:5000/commercial/quote/generate \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": 1,
    "customer_query": "Necesito 1 apartamento de 2 habitaciones",
    "customer_info": {
      "name": "Carlos Ruiz",
      "email": "carlos@empresa.com"
    }
  }'
```

### **5.3 Aceptar Cotización y Crear Orden:**
```bash
# Primero actualizar cotización a "accepted"
curl -X PUT http://localhost:5000/commercial/quote/1/status \
  -H "Content-Type: application/json" \
  -d '{"status": "accepted"}'

# Luego crear orden
curl -X POST http://localhost:5000/commercial/order/create-from-quote \
  -H "Content-Type: application/json" \
  -d '{
    "quote_id": 1,
    "additional_info": {
      "shipping_address": "Calle 123 #45-67, Bogotá"
    }
  }'
```

### **5.4 Generar Factura:**
```bash
curl -X POST http://localhost:5000/commercial/invoice/generate \
  -H "Content-Type: application/json" \
  -d '{
    "order_id": 1,
    "tax_info": {
      "company_name": "Mi Constructora SAS",
      "company_tax_id": "900123456-1",
      "company_address": "Av. Principal #123-45"
    }
  }'
```

**Verificar:** Que se genere archivo PDF en `instance/invoices/`

---

## 📈 **PASO 6: VERIFICACIÓN DE REPORTES**

### **6.1 Estadísticas de Pipeline CRM:**
```bash
curl -X GET http://localhost:5000/commercial/crm/pipeline/1
```

### **6.2 Reporte de Inventario:**
```bash
curl -X GET http://localhost:5000/commercial/inventory/report/1
```

### **6.3 Estadísticas de Órdenes:**
```bash
curl -X GET http://localhost:5000/commercial/orders/statistics/1?days=30
```

---

## ✅ **CRITERIOS DE ÉXITO**

### **Funcionalidad Básica:**
- [ ] Migración de BD ejecutada sin errores
- [ ] Servidor inicia sin errores
- [ ] Endpoints comerciales responden correctamente
- [ ] Dashboard comercial carga sin errores

### **Funcionalidades Comerciales:**
- [ ] Productos se crean correctamente
- [ ] Cotizaciones automáticas funcionan
- [ ] Órdenes se procesan correctamente
- [ ] Facturas PDF se generan
- [ ] Inventario se actualiza automáticamente

### **Integración IA:**
- [ ] Procesamiento de mensajes con intención comercial
- [ ] Análisis automático de consultas de productos
- [ ] Creación automática de leads
- [ ] Chat existente mantiene funcionalidad

### **CRM y Reportes:**
- [ ] Leads se crean y actualizan
- [ ] Pipeline de ventas funcional
- [ ] Estadísticas se generan correctamente
- [ ] Reportes de inventario precisos

---

## 🚨 **SOLUCIÓN DE PROBLEMAS**

### **Error: ImportError modules.commercial**
```bash
# Verificar que todos los archivos están creados
ls -la modules/commercial/
```

### **Error: reportlab not found**
```bash
pip install reportlab==4.0.4 Pillow==10.0.1
```

### **Error: Tabla no existe**
```bash
# Re-ejecutar migración
python migrate_to_v2.py
```

### **Error: 404 en endpoints comerciales**
- Verificar que las rutas se registraron en `app.py`
- Reiniciar servidor después de cambios

---

## 📝 **CHECKLIST FINAL DE PRUEBAS**

```
PREPARACIÓN:
□ Dependencias instaladas
□ Migración ejecutada exitosamente
□ Rutas comerciales registradas
□ Servidor inicia sin errores

FUNCIONALIDADES CORE:
□ Crear producto → ✅ Success
□ Generar cotización → ✅ Success  
□ Crear orden → ✅ Success
□ Generar factura PDF → ✅ Success
□ Crear lead CRM → ✅ Success

INTEGRACIÓN:
□ Dashboard comercial carga → ✅ Success
□ Procesamiento IA funciona → ✅ Success
□ Chat mantiene funcionalidad → ✅ Success
□ Reportes se generan → ✅ Success

FLUJO COMPLETO:
□ Consulta → Cotización → Orden → Factura → ✅ Success
□ Inventario se actualiza correctamente → ✅ Success
□ CRM pipeline funcional → ✅ Success
```

---

**🎯 RESULTADO ESPERADO:**  
SalesMind v2.0.0 funcionando como plataforma comercial completa, procesando transacciones de extremo a extremo de forma automatizada.