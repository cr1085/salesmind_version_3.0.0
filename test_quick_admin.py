# test_quick_admin.py
"""
Prueba rápida de que todas las páginas de la interfaz administrativa cargan correctamente
"""
import requests
import time

def test_admin_pages():
    """Prueba todas las páginas principales de la interfaz admin"""
    
    base_url = "http://127.0.0.1:5000/admin/indexer"
    
    pages = {
        "Dashboard": "/",
        "Clientes": "/clients", 
        "Agregar Cliente": "/add-client",
        "Logs": "/logs",
        "Estado Sistema": "/system-status"
    }
    
    print("🚀 Probando interfaz administrativa del indexador...")
    print(f"📍 Base URL: {base_url}")
    print("-" * 50)
    
    all_good = True
    
    for name, path in pages.items():
        url = base_url + path
        try:
            print(f"🧪 Probando {name}...")
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                print(f"   ✅ {name}: OK (200)")
                
                # Verificar contenido básico
                if name == "Estado Sistema":
                    # Para JSON endpoint
                    try:
                        data = response.json()
                        print(f"   📊 BD Conectada: {data.get('database_connected', 'N/A')}")
                    except:
                        print("   ⚠️ Respuesta no es JSON válido")
                else:
                    # Para páginas HTML
                    if "SalesMind" in response.text:
                        print(f"   ✅ Contenido verificado")
                    else:
                        print(f"   ⚠️ Contenido no verificado")
                        
            else:
                print(f"   ❌ {name}: ERROR {response.status_code}")
                all_good = False
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ {name}: Error de conexión - {e}")
            all_good = False
        except Exception as e:
            print(f"   ❌ {name}: Error - {e}")
            all_good = False
            
        time.sleep(0.5)  # Pequeña pausa entre requests
    
    print("-" * 50)
    if all_good:
        print("🎉 ¡Todas las páginas funcionan correctamente!")
        print("\n📋 URLs disponibles para ingenieros:")
        for name, path in pages.items():
            print(f"   {name}: {base_url}{path}")
        print("\n🔗 Acceso principal: http://127.0.0.1:5000/admin/indexer/")
    else:
        print("❌ Algunas páginas tienen problemas")
    
    return all_good

if __name__ == "__main__":
    test_admin_pages()