# 🚀 SalesMind Widget - Guía de Integración

## ✨ Qué es SalesMind Widget

Un asistente de IA que se integra en **cualquier sitio web** con una sola línea de código. Tus visitantes pueden chatear y solicitar cotizaciones sin salir de tu página.

---

## 🎯 Integración Súper Fácil

### Paso 1: Descarga los archivos
- `salesmind-widget.js` - El script del widget
- `demo_integracion.html` - Ejemplo de cómo se ve

### Paso 2: Sube el archivo a tu servidor
Coloca `salesmind-widget.js` en tu servidor web (donde tienes tu sitio).

### Paso 3: Agrega UNA línea a tu HTML
Antes del `</body>` de tu página, agrega:

```html
<script src="salesmind-widget.js" 
        data-client-id="TU_ID_UNICO"
        data-title="Tu Asistente"
        data-api-url="https://tu-servidor.com/chat-api"></script>
```

### ¡Ya está! 🎉
El widget aparecerá como un botón azul flotante en tu página.

---

## ⚙️ Configuración Personalizada

### Parámetros disponibles:

| Parámetro | Descripción | Ejemplo |
|-----------|-------------|---------|
| `data-client-id` | ID único de tu empresa | `"mi-empresa-123"` |
| `data-title` | Nombre del asistente | `"Asistente Virtual"` |
| `data-subtitle` | Subtítulo | `"Soporte 24/7"` |
| `data-api-url` | URL de tu servidor | `"https://api.miempresa.com/chat"` |

### Ejemplo completo:
```html
<script src="salesmind-widget.js" 
        data-client-id="constructora-abc-2024"
        data-title="Asistente Constructora ABC"
        data-subtitle="Cotizaciones inmediatas"
        data-api-url="https://api.constructora-abc.com/chat"></script>
```

---

## 🎨 Características del Widget

### ✅ Funciona en cualquier sitio:
- WordPress
- Shopify  
- Wix
- HTML estático
- React, Vue, Angular
- Cualquier CMS

### ✅ Completamente responsivo:
- Se adapta a móviles
- No afecta el diseño de tu sitio
- Carga rápido

### ✅ Funciones incluidas:
- Chat en tiempo real
- Descarga de cotizaciones PDF
- Notificaciones elegantes
- Indicadores de estado
- Contador de mensajes

---

## 🛠️ Instalación en Plataformas Populares

### WordPress:
1. Ve a **Apariencia → Editor de temas**
2. Abre `footer.php` 
3. Antes de `</body>` agrega el script
4. Guarda

### Shopify:
1. Ve a **Temas → Acciones → Editar código**
2. Abre `theme.liquid`
3. Antes de `</body>` agrega el script  
4. Guarda

### HTML Estático:
1. Abre tu archivo `index.html`
2. Antes de `</body>` agrega el script
3. Sube a tu servidor

---

## 🔧 Configuración del Servidor

El widget necesita un endpoint que responda a:

```
POST /chat-api
Content-Type: application/json

{
  "message": "Mensaje del usuario",
  "clientId": "tu-id-cliente"
}
```

Respuesta esperada:
```json
{
  "reply": "Respuesta del asistente con posibles [enlaces](url) para descargas"
}
```

---

## 📱 Vista Previa

### En Desktop:
- Botón flotante en esquina inferior derecha
- Ventana de chat de 350px × 500px
- Diseño profesional con gradientes

### En Mobile:
- Botón adaptativo
- Ventana optimizada para móviles
- Scroll suave en conversaciones

---

## 🎉 Beneficios para tu Negocio

### ✨ Para tus Visitantes:
- Respuestas inmediatas 24/7
- Cotizaciones al instante
- Sin necesidad de formularios largos
- Experiencia conversacional natural

### 📈 Para tu Empresa:
- Captura más leads
- Automatiza atención al cliente
- Genera cotizaciones automáticamente  
- Mejora conversión de visitantes

---

## 🆘 Soporte

Si necesitas ayuda con la integración:

1. **Revisa** `demo_integracion.html` para ver un ejemplo funcionando
2. **Verifica** que tu servidor responda correctamente al endpoint
3. **Comprueba** la consola del navegador para errores
4. **Contacta** soporte técnico si persisten problemas

---

## 🚀 ¡Listo para Empezar!

1. ✅ Descarga los archivos
2. ✅ Sube `salesmind-widget.js` a tu servidor  
3. ✅ Agrega la línea de código
4. ✅ Configura tu endpoint API
5. ✅ ¡Disfruta de tu nuevo asistente IA!

**¡Tu sitio web ahora tiene inteligencia artificial integrada!** 🤖✨