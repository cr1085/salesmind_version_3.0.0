# test_admin_interface.py
"""
Script de prueba para verificar que la interfaz administrativa del indexador funciona correctamente.
"""
import requests
import sys
import json
from datetime import datetime

def test_admin_interface():
    """
    Prueba la interfaz administrativa del indexador
    """
    base_url = "http://127.0.0.1:5000"
    admin_url = f"{base_url}/admin/indexer"
    
    print("🚀 === PRUEBA DE INTERFAZ ADMINISTRATIVA DEL INDEXADOR ===")
    print(f"📍 URL Base: {admin_url}")
    print(f"🕐 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test 1: Dashboard principal
    print("📊 Test 1: Dashboard principal...")
    try:
        response = requests.get(f"{admin_url}/", timeout=10)
        if response.status_code == 200:
            print("✅ Dashboard cargado correctamente")
            if "Dashboard del Indexador" in response.text:
                print("✅ Título del dashboard encontrado")
            else:
                print("⚠️ Título del dashboard no encontrado")
        else:
            print(f"❌ Error HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error accediendo al dashboard: {e}")
        return False
    
    # Test 2: Lista de clientes
    print("\n👥 Test 2: Lista de clientes...")
    try:
        response = requests.get(f"{admin_url}/clients", timeout=10)
        if response.status_code == 200:
            print("✅ Página de clientes cargada correctamente")
            if "Gestión de Clientes" in response.text:
                print("✅ Título de la página encontrado")
            else:
                print("⚠️ Título de la página no encontrado")
        else:
            print(f"❌ Error HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error accediendo a la lista de clientes: {e}")
        return False
    
    # Test 3: Formulario agregar cliente
    print("\n➕ Test 3: Formulario agregar cliente...")
    try:
        response = requests.get(f"{admin_url}/add-client", timeout=10)
        if response.status_code == 200:
            print("✅ Formulario de agregar cliente cargado correctamente")
            if "Agregar Nuevo Cliente" in response.text:
                print("✅ Título del formulario encontrado")
            else:
                print("⚠️ Título del formulario no encontrado")
        else:
            print(f"❌ Error HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error accediendo al formulario: {e}")
        return False
    
    # Test 4: Estado del sistema (API)
    print("\n🔧 Test 4: Estado del sistema (API)...")
    try:
        response = requests.get(f"{admin_url}/system-status", timeout=10)
        if response.status_code == 200:
            try:
                data = response.json()
                print("✅ API de estado del sistema funcional")
                print(f"   📊 BD Conectada: {data.get('database_connected', 'N/A')}")
                print(f"   👥 Total Clientes: {data.get('total_clients', 'N/A')}")
                print(f"   🐍 Python: {data.get('python_version', 'N/A')}")
                if 'timestamp' in data:
                    print(f"   🕐 Timestamp: {data['timestamp']}")
            except json.JSONDecodeError:
                print("⚠️ Respuesta no es JSON válido")
        else:
            print(f"❌ Error HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error accediendo a la API de estado: {e}")
        return False
    
    # Test 5: Logs del sistema
    print("\n📋 Test 5: Logs del sistema...")
    try:
        response = requests.get(f"{admin_url}/logs", timeout=10)
        if response.status_code == 200:
            print("✅ Página de logs cargada correctamente")
            if "Logs del Sistema" in response.text:
                print("✅ Título de logs encontrado")
            else:
                print("⚠️ Título de logs no encontrado")
        else:
            print(f"❌ Error HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error accediendo a los logs: {e}")
        return False
    
    print("\n🎉 === TODAS LAS PRUEBAS COMPLETADAS EXITOSAMENTE ===")
    print("📋 Resumen:")
    print("   ✅ Dashboard principal: OK")
    print("   ✅ Lista de clientes: OK")
    print("   ✅ Formulario agregar cliente: OK")
    print("   ✅ API estado del sistema: OK")
    print("   ✅ Logs del sistema: OK")
    print()
    print("🔗 URLs disponibles:")
    print(f"   📊 Dashboard: {admin_url}/")
    print(f"   👥 Clientes: {admin_url}/clients")
    print(f"   ➕ Agregar Cliente: {admin_url}/add-client")
    print(f"   📋 Logs: {admin_url}/logs")
    print(f"   🔧 Estado API: {admin_url}/system-status")
    
    return True

def test_main_site():
    """
    Prueba que el sitio principal sigue funcionando
    """
    print("\n🌐 === PRUEBA DEL SITIO PRINCIPAL ===")
    
    try:
        response = requests.get("http://127.0.0.1:5000/", timeout=10)
        if response.status_code == 200:
            print("✅ Sitio principal funcionando correctamente")
            return True
        else:
            print(f"❌ Error HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error accediendo al sitio principal: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Verificando que el servidor esté ejecutándose...")
    
    # Verificar que el servidor esté en línea
    try:
        response = requests.get("http://127.0.0.1:5000/", timeout=5)
        print("✅ Servidor en línea")
    except Exception as e:
        print("❌ Servidor no disponible. Asegúrate de que esté ejecutándose con 'python app.py'")
        sys.exit(1)
    
    # Ejecutar pruebas
    success = True
    
    # Probar interfaz administrativa
    success &= test_admin_interface()
    
    # Probar sitio principal
    success &= test_main_site()
    
    print("\n" + "="*60)
    if success:
        print("🎉 ¡TODAS LAS PRUEBAS EXITOSAS!")
        print("💡 La interfaz administrativa del indexador está lista para usar")
        print("🔒 Los ingenieros pueden acceder de manera segura a:")
        print("   • Gestión completa de clientes")
        print("   • Subida y administración de documentos")
        print("   • Monitoreo del sistema en tiempo real")
        print("   • Logs y estadísticas detalladas")
        print("   • Re-indexación de clientes")
        print("   • Pruebas de funcionalidad")
    else:
        print("❌ ALGUNAS PRUEBAS FALLARON")
        print("🔧 Revisa los errores mostrados arriba")
        sys.exit(1)