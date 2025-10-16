#!/usr/bin/env python
# fix_refresh_issue.py - CORREGIR PROBLEMA DE REFRESH SIN DAÑAR CÓDIGO CORE
"""
🔧 CORRECCIÓN AUTOMÁTICA DEL PROBLEMA DE REFRESH
================================================

Este script aplica las correcciones mínimas necesarias para evitar
que la página se refresque al generar cotizaciones.

CORRECCIONES APLICADAS:
✅ Agregar preventDefault en evento Enter
✅ Mejorar manejo de enlaces de descarga  
✅ Agregar logging para debug

NO MODIFICA LÓGICA CORE - Solo corrige comportamiento del frontend.
"""

import os
import sys

def fix_refresh_issue():
    """Aplica correcciones al problema de refresh automáticamente."""
    
    print("🔧 CORRECTOR AUTOMÁTICO DE PROBLEMA DE REFRESH")
    print("=" * 60)
    
    original_file = "pagina_cliente_ejemplo.html"
    backup_file = "pagina_cliente_ejemplo_BACKUP.html"
    
    # 1. Crear backup del original
    print(f"\n📋 PASO 1: Creando backup")
    if os.path.exists(original_file):
        if not os.path.exists(backup_file):
            with open(original_file, 'r', encoding='utf-8') as f:
                content = f.read()
            with open(backup_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Backup creado: {backup_file}")
        else:
            print(f"✅ Backup ya existe: {backup_file}")
    else:
        print(f"❌ Archivo original no encontrado: {original_file}")
        return False
    
    # 2. Leer contenido original
    print(f"\n📖 PASO 2: Leyendo archivo original")
    with open(original_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 3. Aplicar correcciones
    print(f"\n🔧 PASO 3: Aplicando correcciones")
    
    # Corrección 1: Agregar preventDefault en keypress
    old_keypress = """chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') sendMessage();
        });"""
    
    new_keypress = """chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault(); // ✅ PREVENIR REFRESH
                sendMessage();
            }
        });"""
    
    if old_keypress in content:
        content = content.replace(old_keypress, new_keypress)
        print("   ✅ Agregado preventDefault en evento Enter")
    else:
        print("   ⚠️ Patrón de keypress no encontrado exactamente")
    
    # Corrección 2: Mejorar enlaces de descarga
    old_link_conversion = """const htmlText = text.replace(/\\[([^\\]]+)\\]\\(([^)]+)\\)/g, '<a href="$2" download style="color: #FFD700; text-decoration: underline;">$1</a>');"""
    
    new_link_conversion = """const htmlText = text.replace(/\\[([^\\]]+)\\]\\(([^)]+)\\)/g, '<a href="$2" download style="color: #FFD700; text-decoration: underline;" target="_blank" onclick="event.preventDefault(); event.stopPropagation(); window.open(this.href, \\'_blank\\');">$1</a>');"""
    
    if old_link_conversion in content:
        content = content.replace(old_link_conversion, new_link_conversion)
        print("   ✅ Mejorado manejo de enlaces de descarga")
    else:
        print("   ⚠️ Patrón de enlaces no encontrado exactamente")
    
    # Corrección 3: Agregar logging básico
    old_send_function = """const sendMessage = async () => {
            const messageText = chatInput.value.trim();
            if (messageText === '') return;
            appendMessage(messageText, 'user-message');
            chatInput.value = '';
            chatInput.disabled = true;
            sendButton.disabled = true;"""
    
    new_send_function = """const sendMessage = async () => {
            const messageText = chatInput.value.trim();
            if (messageText === '') return;
            console.log('📤 Enviando mensaje:', messageText); // ✅ LOGGING
            appendMessage(messageText, 'user-message');
            chatInput.value = '';
            chatInput.disabled = true;
            sendButton.disabled = true;"""
    
    if old_send_function in content:
        content = content.replace(old_send_function, new_send_function)
        print("   ✅ Agregado logging básico")
    else:
        print("   ⚠️ Función sendMessage no encontrada exactamente")
    
    # 4. Escribir archivo corregido
    print(f"\n💾 PASO 4: Guardando correcciones")
    with open(original_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Archivo corregido guardado: {original_file}")
    
    # 5. Resumen de cambios
    print(f"\n📊 RESUMEN DE CORRECCIONES APLICADAS:")
    print(f"   ✅ preventDefault agregado en evento Enter")
    print(f"   ✅ Enlaces de descarga mejorados")  
    print(f"   ✅ Logging básico agregado")
    print(f"   ✅ Backup creado en: {backup_file}")
    
    print(f"\n🧪 CÓMO PROBAR:")
    print(f"   1. Actualiza la página en el navegador")
    print(f"   2. Solicita cotización: '¿Puedes enviarme una cotización oficial?'")
    print(f"   3. Presiona Enter - NO debería refrescar")
    print(f"   4. Haz click en enlace PDF - NO debería refrescar")
    
    print(f"\n🔄 PARA REVERTIR:")
    print(f"   cp {backup_file} {original_file}")
    
    return True

def restore_backup():
    """Restaura el backup original."""
    
    original_file = "pagina_cliente_ejemplo.html"
    backup_file = "pagina_cliente_ejemplo_BACKUP.html"
    
    if os.path.exists(backup_file):
        with open(backup_file, 'r', encoding='utf-8') as f:
            content = f.read()
        with open(original_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Backup restaurado: {backup_file} -> {original_file}")
        return True
    else:
        print(f"❌ Backup no encontrado: {backup_file}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "restore":
        restore_backup()
    else:
        fix_refresh_issue()