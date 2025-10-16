# Guía completa para programadores y entrega al cliente

## 1. Alta y configuración de cliente

1. Solicitar al cliente:
   - Nombre de la empresa
   - ID de chat de Telegram (si quiere notificaciones)
   - Carpeta con los PDFs relevantes

2. Crear carpeta de PDFs en el proyecto y colocar los archivos.

3. Dar de alta al cliente ejecutando:
   ```powershell
   C:/xampp/htdocs/SalesMind-agente-web/venv/Scripts/python.exe alta_cliente.py
   ```
   - Ingresar los datos solicitados.
   - Guardar el `public_id` generado para el cliente.

4. Verificar que el bot de Telegram esté correctamente configurado y agregado al grupo/canal del cliente.

---

## 2. Generar archivo de integración para el cliente

1. Copiar el archivo base de chat (ejemplo: `chat_cliente.html` o `chat_constructora.html`).
2. Cambiar:
   - `CLIENT_PUBLIC_ID` por el `public_id` del cliente.
   - `API_HOST` por la URL pública del VPS (ejemplo: `https://tuservidor.com/chat-api`).
3. Personalizar el diseño si el cliente lo solicita.

---

## 3. Entrega al cliente

1. Enviar el archivo HTML personalizado por correo o enlace de descarga.
2. Instrucciones para el cliente:
   - Subir el archivo HTML a su web.
   - (Opcional) Integrar el chat en su página principal copiando el código.
   - Crear grupo/canal en Telegram y agregar el bot.
   - Enviar el ID del grupo/canal para recibir notificaciones.

---

## 4. Prueba y soporte

1. Probar el chat web y Telegram con preguntas reales.
2. Verificar que las respuestas sean correctas y las notificaciones lleguen.
3. Ofrecer soporte técnico para ajustes o dudas.

---

## 5. Ejemplo de correo de entrega al cliente

---

Estimado cliente,

Adjuntamos el archivo de chat inteligente para su web. Siga estos pasos:
1. Suba el archivo a su sitio web.
2. Si desea integrar el chat en otra página, copie el código donde lo necesite.
3. Para recibir notificaciones en Telegram, agregue el bot a su grupo/canal y envíenos el ID.

¡Listo! Su agente de ventas está activo y responderá usando sus documentos.

Cualquier duda, estamos a disposición.

---

## 6. Checklist para el equipo

- [ ] PDFs recibidos y en carpeta correcta
- [ ] Cliente dado de alta y `public_id` guardado
- [ ] Bot de Telegram configurado y agregado
- [ ] Archivo HTML personalizado y entregado
- [ ] Pruebas realizadas
- [ ] Cliente informado y soporte disponible

---

Esta guía asegura que el proceso sea rápido, profesional y escalable para muchos clientes.
