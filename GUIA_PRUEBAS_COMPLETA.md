# 🎯 GUÍA COMPLETA DE PRUEBAS SALESMIND
# ==========================================

## 📋 PASO 1: PREPARACIÓN DEL ENTORNO

### 1.1 Abrir Terminal en la carpeta del proyecto
```bash
cd C:\xampp\htdocs\SalesMind-agente-web-INDEXADORANDANGENTE
```

### 1.2 Activar entorno virtual y verificar dependencias
```bash
# Activar entorno virtual
venv\Scripts\activate

# Verificar que ReportLab esté instalado (para PDFs)
pip list | findstr reportlab

# Si no está instalado:
pip install reportlab Pillow
```

### 1.3 Iniciar el servidor Flask
```bash
# Usar el ejecutable correcto del entorno virtual
C:/xampp/htdocs/SalesMind-agente-web-INDEXADORANDANGENTE/venv/Scripts/python.exe app.py
```

**✅ RESULTADO ESPERADO:**
```
-> Iniciando servidor Flask en modo desarrollo en http://127.0.0.1:5000
 * Running on http://127.0.0.1:5000
 * Debugger is active!
```

---

## 📋 PASO 2: VERIFICACIÓN COMPLETA DEL SISTEMA

### 2.1 Ejecutar verificación automática (OPCIONAL PERO RECOMENDADO)
```bash
# En una nueva terminal
C:/xampp/htdocs/SalesMind-agente-web-INDEXADORANDANGENTE/venv/Scripts/python.exe system_health_check.py
```

### 2.2 Auto-reparar cualquier problema detectado
```bash
C:/xampp/htdocs/SalesMind-agente-web-INDEXADORANDANGENTE/venv/Scripts/python.exe auto_fix_clients.py
```

**✅ RESULTADO ESPERADO:**
- Sistema reporta "EXCELENTE ESTADO"
- Todos los clientes tienen embeddings e índices FAISS
- Chat API funcional

---

## 📋 PASO 3: ACCEDER AL PANEL ADMINISTRATIVO

### 3.1 Abrir Panel de Administración
```
URL: http://127.0.0.1:5000/admin/indexer/
```

### 3.2 Verificar Dashboard
- ✅ Ver lista de clientes existentes
- ✅ Ver estadísticas del sistema  
- ✅ Estado de índices FAISS
- ✅ Documentos procesados

**✅ LO QUE DEBES VER:**
- Dashboard con métricas del sistema
- Lista de clientes (incluyendo "Cliente Demo")
- Estado "Activo" en índices FAISS
- Botones para agregar clientes

---

## 📋 PASO 4: CREAR NUEVO CLIENTE (PRUEBA DE INDEXADOR)

### 4.1 Click en "Agregar Cliente"
```
URL: http://127.0.0.1:5000/admin/indexer/add-client
```

### 4.2 Llenar formulario:
- **Nombre:** "Inmobiliaria Prueba"
- **Telegram ID:** (opcional, dejar vacío)
- **Documentos:** Subir 1-3 archivos PDF

### 4.3 Datos de prueba recomendados:
**Crear archivo PDF con este contenido:**
```
CATÁLOGO INMOBILIARIA PRUEBA

CASA EJECUTIVA ZONA NORTE
- Precio: $275,000 USD
- Área: 180 m²  
- Habitaciones: 3
- Baños: 2
- Características: Cocina moderna, jardín, garaje

APARTAMENTO CENTRO CIUDAD
- Precio: $125,000 USD
- Área: 85 m²
- Habitaciones: 2
- Baños: 1  
- Características: Amueblado, balcón, amenidades

LOTE COMERCIAL
- Precio: $95,000 USD
- Área: 500 m²
- Uso: Comercial
- Ubicación: Avenida principal
```

### 4.4 Click "Crear Cliente"

**✅ RESULTADO ESPERADO:**
- Cliente creado exitosamente
- Documentos procesados automáticamente
- Embeddings creados (verás en logs)
- Índice FAISS generado automáticamente
- Redirección al dashboard con nuevo cliente

---

## 📋 PASO 5: PROBAR AGENTE MULTILENGUAJE

### 5.1 Abrir Chat de Prueba
```
URL: http://127.0.0.1:5000/pagina_cliente_ejemplo.html
```

### 5.2 Probar en ESPAÑOL
**Preguntas de prueba:**
```
- ¿Cuánto cuesta una casa?
- Dame información sobre apartamentos
- Necesito una cotización de la casa ejecutiva
- ¿Qué propiedades tienes disponibles?
```

### 5.3 Probar en INGLÉS  
**Preguntas de prueba:**
```
- How much does a house cost?
- Give me information about apartments
- I need a quote for the executive house
- What properties do you have available?
```

### 5.4 Probar en FRANCÉS
**Preguntas de prueba:**
```
- Combien coûte une maison?
- Donnez-moi des informations sur les appartements
```

### 5.5 Probar en PORTUGUÉS
**Preguntas de prueba:**
```
- Quanto custa uma casa?
- Preciso de uma cotização
```

**✅ RESULTADO ESPERADO:**
- Respuestas en el MISMO idioma que preguntas
- Información específica de las propiedades
- Menciones de precios y características

---

## 📋 PASO 6: PROBAR SISTEMA DE COTIZACIONES PDF

### 6.1 Solicitar cotizaciones usando palabras clave:

**En ESPAÑOL:**
```
- "Dame una cotización de la casa ejecutiva"
- "¿Cuánto cuesta y puedes darme un presupuesto?"
- "Necesito una cotización oficial en PDF"
```

**En INGLÉS:**
```
- "Give me a quote for the house"
- "I need a price estimate in PDF"
- "Can you provide a quotation?"
```

### 6.2 Verificar generación de PDF

**✅ RESULTADO ESPERADO:**
- Respuesta del agente con información de precios
- Mensaje adicional: "📄 COTIZACIÓN OFICIAL GENERADA"
- Link de descarga: "🔗 [Descargar Cotización PDF]"
- Click en link descarga archivo PDF profesional

### 6.3 Verificar contenido del PDF:
- ✅ Encabezado "COTIZACIÓN OFICIAL"
- ✅ Información de la empresa (SalesMind)
- ✅ Datos del cliente
- ✅ Tabla de productos/servicios con precios
- ✅ Total calculado
- ✅ Términos y condiciones
- ✅ Validez de 30 días

---

## 📋 PASO 7: PROBAR MÚLTIPLES CLIENTES

### 7.1 Cambiar cliente en el chat
**Editar archivo:** `pagina_cliente_ejemplo.html`
```javascript
// Línea ~67 - Cambiar CLIENT_PUBLIC_ID
const CLIENT_PUBLIC_ID = "otro-client-id-aqui";
```

### 7.2 Crear segundo cliente de prueba
- Volver al panel admin
- Crear "Constructora Beta" con PDFs diferentes
- Probar que responde con información específica

### 7.3 Verificar aislamiento de datos
- Cliente A solo ve información de Cliente A
- Cliente B solo ve información de Cliente B
- Cotizaciones específicas por cliente

**✅ RESULTADO ESPERADO:**
- Cada cliente ve solo SUS datos
- Respuestas personalizadas por cliente
- Cotizaciones con información correcta

---

## 📋 PASO 8: PROBAR ESCALABILIDAD (CLIENTE REAL)

### 8.1 Subir documentos reales
- PDFs de propiedades reales
- Catálogos comerciales
- Brochures de proyectos

### 8.2 Verificar procesamiento automático
- Documentos se procesan sin intervención manual
- Embeddings se crean automáticamente  
- Índice FAISS se actualiza automáticamente
- Agente responde inmediatamente

### 8.3 Probar con más documentos
- Subir documentos adicionales a cliente existente
- Usar función "Subir Documentos" en panel admin
- Verificar que integra nueva información

**✅ RESULTADO ESPERADO:**
- Sistema procesa TODO automáticamente
- Sin necesidad de configuración manual
- Respuestas mejoradas con más información

---

## 🧪 COMANDOS DE VERIFICACIÓN Y DIAGNÓSTICO

### Verificar estado completo:
```bash
python system_health_check.py
```

### Reparar cualquier problema:
```bash  
python auto_fix_clients.py
```

### Probar API directamente:
```bash
python test_chat_api.py
```

### Ver logs del servidor:
- Observar terminal donde corre Flask
- Ver procesamiento en tiempo real
- Detectar errores si los hay

---

## ✅ CHECKLIST DE ÉXITO COMPLETO

### ✅ Indexador:
- [ ] Panel admin accesible
- [ ] Crear cliente funciona
- [ ] Subir PDFs funciona  
- [ ] Procesamiento automático
- [ ] Embeddings creados
- [ ] Índice FAISS generado

### ✅ Agente:
- [ ] Chat responde en español
- [ ] Chat responde en inglés  
- [ ] Chat responde en otros idiomas
- [ ] Información específica del cliente
- [ ] Respuestas coherentes y útiles

### ✅ Cotizaciones:
- [ ] Detecta solicitudes de cotización
- [ ] Genera PDF automáticamente
- [ ] PDF descargable
- [ ] Contenido profesional y completo
- [ ] Precios extraídos correctamente

### ✅ Escalabilidad:
- [ ] Múltiples clientes funcionan
- [ ] Datos aislados por cliente
- [ ] Procesamiento automático
- [ ] Sin configuración manual requerida
- [ ] Sistema estable bajo carga

---

## 🎉 RESULTADO FINAL ESPERADO

Al completar todas estas pruebas debes tener:

**🛡️ SISTEMA COMPLETAMENTE FUNCIONAL:**
- ✅ Indexador automático para cualquier cliente
- ✅ Agente multilenguaje inteligente  
- ✅ Cotizaciones PDF profesionales automáticas
- ✅ Escalabilidad sin intervención manual
- ✅ Panel administrativo completo

**🚀 LISTO PARA PRODUCCIÓN:**
- Crear cualquier cliente → Funciona automáticamente
- Subir cualquier PDF → Se procesa automáticamente  
- Hacer cualquier pregunta → Responde en su idioma
- Solicitar cotización → PDF generado automáticamente

**¡EL SISTEMA ESTÁ 100% BLINDADO Y LISTO!** 🎯