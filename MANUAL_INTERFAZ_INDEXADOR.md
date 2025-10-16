# 🛠️ **INTERFAZ ADMINISTRATIVA DEL INDEXADOR SALESMIND**
## Manual para Ingenieros - Versión 1.0.0

---

## 📋 **ACCESO RÁPIDO**

### **URLs de la Interfaz Administrativa:**
- 🏠 **Dashboard Principal:** http://127.0.0.1:5000/admin/indexer/
- 👥 **Gestión de Clientes:** http://127.0.0.1:5000/admin/indexer/clients
- ➕ **Agregar Cliente:** http://127.0.0.1:5000/admin/indexer/add-client
- 📊 **Logs del Sistema:** http://127.0.0.1:5000/admin/indexer/logs
- 🔧 **Estado API:** http://127.0.0.1:5000/admin/indexer/system-status

### **Inicio Rápido:**
```bash
# 1. Navegar al directorio del proyecto
cd C:\xampp\htdocs\SalesMind-agente-web-INDEXADORANDANGENTE

# 2. Activar entorno virtual (si aplica)
venv\Scripts\activate

# 3. Iniciar servidor
python app.py

# 4. Abrir navegador en: http://127.0.0.1:5000/admin/indexer/
```

---

## 🎯 **FUNCIONALIDADES PRINCIPALES**

### **1. Dashboard de Monitoreo**
- **Vista general del sistema** con estadísticas en tiempo real
- **Estado de la base de datos** PostgreSQL
- **Número total de clientes** activos
- **Estado del indexador** y servicios
- **Acciones rápidas** para tareas comunes
- **Auto-actualización** cada 60 segundos

### **2. Gestión Completa de Clientes**
- **Lista visual de todos los clientes** con estadísticas
- **Información detallada** por cliente:
  - Documentos indexados
  - Vectores generados
  - Tamaño total de datos
  - Conversaciones realizadas
- **Acciones disponibles** por cliente:
  - ✅ **Probar funcionamiento** (test automático)
  - 🔄 **Re-indexar documentos** (regenerar vectores)
  - 📁 **Subir documentos adicionales**
  - 👁️ **Ver detalles completos**

### **3. Agregar Nuevos Clientes**
- **Formulario intuitivo** con validación en tiempo real
- **Subida de documentos** durante la creación
- **Proceso automatizado** de indexación
- **Feedback visual** del progreso
- **Generación automática** de IDs públicos únicos

### **4. Monitoreo y Logs**
- **Conversaciones recientes** de todos los clientes
- **Logs de consultas** con tiempos de respuesta
- **Estadísticas de rendimiento** en tiempo real
- **Exportación de datos** a CSV
- **Detalle de cada conversación** con metadatos

### **5. Estado del Sistema**
- **Monitoreo de recursos** (CPU, memoria, disco)
- **Estado de la base de datos** PostgreSQL
- **Información de versiones** Python y dependencias
- **API de estado** para integración externa

---

## 🔧 **OPERACIONES COMUNES**

### **Agregar un Nuevo Cliente Empresa:**
1. Ir a **"Agregar Cliente"** en el menú lateral
2. Llenar el **nombre de la empresa** (requerido)
3. Agregar **ID de Telegram** (opcional)
4. **Subir documentos PDFs** iniciales (opcional)
5. Hacer clic en **"Crear Cliente"**
6. Esperar a que termine el **proceso de indexación**
7. **Copiar el ID público** generado para el widget web

### **Re-indexar un Cliente (Si hay problemas):**
1. Ir a **"Clientes"** en el menú lateral
2. Localizar el cliente con problemas
3. Hacer clic en **"Re-indexar"**
4. **Confirmar la acción** (puede tomar varios minutos)
5. Esperar a que termine el proceso
6. **Verificar las estadísticas** actualizadas

### **Agregar Documentos a Cliente Existente:**
1. En la **lista de clientes**, hacer clic en **"Subir"**
2. **Seleccionar archivos** PDF, TXT, DOC, DOCX
3. Hacer clic en **"Subir Documentos"**
4. Esperar el **procesamiento automático**
5. Verificar que las **estadísticas se actualicen**

### **Probar que un Cliente Funciona:**
1. En la **lista de clientes**, hacer clic en **"Probar"**
2. El sistema **enviará una pregunta automática**
3. Revisar la **respuesta generada**
4. Verificar que **no hay errores** en la comunicación

---

## 🚨 **SOLUCIÓN DE PROBLEMAS**

### **Cliente no Responde Correctamente:**
1. **Verificar en Dashboard** que la BD esté conectada
2. **Re-indexar el cliente** desde la lista
3. **Revisar los logs** para errores específicos
4. **Probar la API** con el botón "Probar"

### **Error al Subir Documentos:**
1. **Verificar formato** de archivos (PDF, TXT, DOC, DOCX)
2. **Comprobar tamaño** de archivos (máx. 50MB por archivo)
3. **Revisar espacio en disco** disponible
4. **Verificar conexión** a PostgreSQL

### **Sistema Lento o No Responde:**
1. **Verificar recursos del sistema** en Dashboard
2. **Revisar logs** para errores de memoria
3. **Reiniciar el servidor** si es necesario:
   ```bash
   # Detener con Ctrl+C, luego:
   python app.py
   ```
4. **Verificar estado de PostgreSQL**

### **Base de Datos Desconectada:**
1. **Verificar que PostgreSQL esté ejecutándose**
2. **Revisar credenciales** en archivo `.env`
3. **Comprobar conectividad** de red
4. **Re-inicializar BD** si es necesario:
   ```bash
   flask init-db
   ```

---

## 🔒 **CONSIDERACIONES DE SEGURIDAD**

### **Acceso Controlado:**
- La interfaz está **disponible solo localmente** (127.0.0.1)
- Cada cliente tiene **datos completamente aislados**
- Los **IDs públicos son UUIDs** no predecibles
- **No hay exposición** de IDs internos de base de datos

### **Datos Sensibles:**
- **Todos los documentos** se almacenan en PostgreSQL
- **Los vectores están encriptados** en la base de datos
- **No se logea contenido** sensible de documentos
- **Cada empresa** solo accede a sus propios datos

### **Mejores Prácticas:**
- **Cambiar contraseñas** de BD regularmente
- **Hacer backups** de PostgreSQL frecuentemente
- **Monitorear accesos** a través de los logs
- **Mantener actualizadas** las dependencias Python

---

## 📊 **MÉTRICAS Y MONITOREO**

### **Estadísticas Disponibles:**
- **Por Cliente:**
  - Número total de documentos
  - Cantidad de vectores (embeddings)
  - Tamaño total de datos en MB
  - Total de conversaciones realizadas
  
- **Del Sistema:**
  - Tiempo promedio de respuesta
  - Uso de CPU, memoria y disco
  - Estado de conexión a PostgreSQL
  - Versión de Python y dependencias

### **Alertas Automáticas:**
- **Indicador de estado** en tiempo real (esquina superior derecha)
- **Cambio de color** si hay problemas de conectividad
- **Mensajes de error** claros en caso de fallos

---

## 🛡️ **COMANDOS DE LÍNEA (Backup)**

### **Si la Interfaz Web No Está Disponible:**
```bash
# Listar todos los clientes
flask --app app.py list-clients

# Agregar cliente por comando
flask --app app.py add-client "Nombre Empresa" "telegram_id" "ruta/pdfs"

# Eliminar cliente (CUIDADO!)
flask --app app.py remove-client "Nombre Empresa"

# Verificar estado de BD
flask --app app.py init-db
```

---

## 📞 **SOPORTE Y CONTACTO**

### **Si Necesitas Ayuda:**
1. **Revisar este manual** primero
2. **Consultar los logs** del sistema en la interfaz
3. **Verificar estado** de todos los componentes
4. **Documentar el problema** con capturas de pantalla
5. **Contactar al equipo técnico** con toda la información

### **Información de Sistema:**
- **Versión:** SalesMind 1.0.0
- **Base de Datos:** PostgreSQL 12+
- **Python:** 3.11+
- **Framework:** Flask + Waitress
- **IA:** Google Gemini + Embeddings

---

**✅ ¡La interfaz está lista para usar de manera segura por el equipo de ingenieros!**

**🔗 Acceso directo:** http://127.0.0.1:5000/admin/indexer/