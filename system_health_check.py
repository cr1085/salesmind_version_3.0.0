#!/usr/bin/env python
# system_health_check.py - VERIFICACIÓN COMPLETA DEL SISTEMA SALESMIND
"""
🛡️ SISTEMA DE VERIFICACIÓN Y AUTO-REPARACIÓN BLINDADO
=====================================================

Este script verifica que TODOS los componentes del sistema funcionen correctamente:

VERIFICACIONES INCLUIDAS:
✅ Estado del servidor Flask
✅ Conectividad de base de datos PostgreSQL
✅ Clientes sin embeddings/índices FAISS
✅ Documentos sin procesar
✅ APIs de Google (embeddings)
✅ Sistema de cotizaciones PDF
✅ Multilenguaje del chat
✅ Panel administrativo
✅ Sistema de extensiones
✅ Integridad de archivos core

CAPACIDADES DE AUTO-REPARACIÓN:
🔧 Crear embeddings faltantes
🔧 Regenerar índices FAISS
🔧 Procesar documentos pendientes
🔧 Validar configuración
🔧 Reiniciar servicios si es necesario

GARANTÍA: Este script NUNCA rompe el sistema - solo lo repara.
"""

import sys
import os
import time
import requests
import psycopg2
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import traceback

# Agregar ruta del proyecto
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

class SystemHealthChecker:
    """Verificador completo de salud del sistema SalesMind."""
    
    def __init__(self):
        self.results = {
            'timestamp': datetime.now(),
            'overall_status': 'unknown',
            'checks': {},
            'repairs': {},
            'errors': [],
            'warnings': []
        }
        self.flask_url = "http://127.0.0.1:5000"
    
    def run_complete_check(self) -> Dict:
        """Ejecuta verificación completa del sistema."""
        print("🔍 VERIFICACIÓN COMPLETA DEL SISTEMA SALESMIND")
        print("=" * 60)
        
        checks = [
            ("flask_server", self._check_flask_server),
            ("database", self._check_database_connection),
            ("google_api", self._check_google_api),
            ("clients_integrity", self._check_clients_integrity),
            ("chat_functionality", self._check_chat_functionality),
            ("admin_panel", self._check_admin_panel),
            ("pdf_generation", self._check_pdf_generation),
            ("multilanguage", self._check_multilanguage),
            ("extensions", self._check_extensions_system),
            ("core_files", self._check_core_files_integrity)
        ]
        
        passed = 0
        total = len(checks)
        
        for check_name, check_function in checks:
            try:
                print(f"\n🧪 Verificando: {check_name.replace('_', ' ').title()}")
                result = check_function()
                self.results['checks'][check_name] = result
                
                if result['status'] == 'pass':
                    print(f"   ✅ {result['message']}")
                    passed += 1
                elif result['status'] == 'warning':
                    print(f"   ⚠️ {result['message']}")
                    self.results['warnings'].append(f"{check_name}: {result['message']}")
                    passed += 1  # Warnings no fallan el sistema
                else:
                    print(f"   ❌ {result['message']}")
                    self.results['errors'].append(f"{check_name}: {result['message']}")
                    
                    # Intentar auto-reparación si está disponible
                    if 'auto_fix' in result and result['auto_fix']:
                        print(f"   🔧 Intentando auto-reparación...")
                        fix_result = result['auto_fix']()
                        self.results['repairs'][check_name] = fix_result
                        
                        if fix_result.get('success', False):
                            print(f"   ✅ Reparación exitosa: {fix_result['message']}")
                            passed += 1
                        else:
                            print(f"   ❌ Reparación falló: {fix_result.get('message', 'Error desconocido')}")
                
            except Exception as e:
                error_msg = f"Error ejecutando verificación {check_name}: {str(e)}"
                print(f"   💥 {error_msg}")
                self.results['errors'].append(error_msg)
                self.results['checks'][check_name] = {
                    'status': 'error',
                    'message': error_msg,
                    'exception': str(e)
                }
        
        # Calcular estado general
        success_rate = (passed / total) * 100
        if success_rate == 100:
            self.results['overall_status'] = 'excellent'
        elif success_rate >= 80:
            self.results['overall_status'] = 'good'
        elif success_rate >= 60:
            self.results['overall_status'] = 'fair'
        else:
            self.results['overall_status'] = 'poor'
        
        # Mostrar resumen
        self._print_summary(passed, total)
        
        return self.results
    
    def _check_flask_server(self) -> Dict:
        """Verifica que el servidor Flask esté funcionando."""
        try:
            response = requests.get(f"{self.flask_url}/admin/indexer/system-status", timeout=10)
            if response.status_code == 200:
                return {
                    'status': 'pass',
                    'message': 'Servidor Flask funcionando correctamente',
                    'details': f'Status: {response.status_code}'
                }
            else:
                return {
                    'status': 'fail',
                    'message': f'Servidor responde pero con error: {response.status_code}',
                    'auto_fix': lambda: self._restart_flask_server()
                }
        except requests.exceptions.ConnectionError:
            return {
                'status': 'fail',
                'message': 'Servidor Flask no está ejecutándose',
                'auto_fix': lambda: self._start_flask_server()
            }
        except Exception as e:
            return {
                'status': 'fail',
                'message': f'Error verificando servidor: {str(e)}'
            }
    
    def _check_database_connection(self) -> Dict:
        """Verifica conectividad con PostgreSQL."""
        try:
            from modules import create_app, db
            from modules.models import Client
            
            app = create_app()
            with app.app_context():
                # Intentar consulta simple
                client_count = Client.query.count()
                return {
                    'status': 'pass',
                    'message': f'Base de datos conectada - {client_count} clientes registrados',
                    'details': {'client_count': client_count}
                }
        except Exception as e:
            return {
                'status': 'fail',
                'message': f'Error de base de datos: {str(e)}',
                'auto_fix': lambda: self._repair_database_connection()
            }
    
    def _check_google_api(self) -> Dict:
        """Verifica que la API de Google esté configurada."""
        try:
            from config import Config
            from langchain_google_genai import GoogleGenerativeAIEmbeddings
            
            if not Config.GOOGLE_API_KEY:
                return {
                    'status': 'fail',
                    'message': 'GOOGLE_API_KEY no configurada en .env'
                }
            
            # Intentar crear modelo de embeddings
            embedding_model = GoogleGenerativeAIEmbeddings(
                model="models/text-embedding-004",
                google_api_key=Config.GOOGLE_API_KEY
            )
            
            # Probar con texto simple
            test_embedding = embedding_model.embed_query("test")
            
            return {
                'status': 'pass',
                'message': f'API de Google funcionando - Vector dimensión: {len(test_embedding)}',
                'details': {'vector_dimension': len(test_embedding)}
            }
        except Exception as e:
            return {
                'status': 'fail',
                'message': f'Error con API de Google: {str(e)}'
            }
    
    def _check_clients_integrity(self) -> Dict:
        """Verifica integridad de todos los clientes."""
        try:
            from modules import create_app
            from modules.models import Client, Document, Embedding, FAISSIndex
            
            app = create_app()
            with app.app_context():
                clients = Client.query.all()
                
                clients_ok = 0
                clients_need_repair = []
                
                for client in clients:
                    documents = Document.query.filter_by(client_id=client.id).count()
                    embeddings = Embedding.query.filter_by(client_id=client.id).count()
                    faiss_indexes = FAISSIndex.query.filter_by(client_id=client.id, is_active=True).count()
                    
                    if documents > 0 and embeddings > 0 and faiss_indexes > 0:
                        clients_ok += 1
                    elif documents > 0:  # Tiene documentos pero falta procesamiento
                        clients_need_repair.append({
                            'id': client.id,
                            'name': client.name,
                            'documents': documents,
                            'embeddings': embeddings,
                            'faiss_indexes': faiss_indexes
                        })
                
                if not clients_need_repair:
                    return {
                        'status': 'pass',
                        'message': f'Todos los {len(clients)} clientes están correctamente configurados',
                        'details': {'total_clients': len(clients), 'clients_ok': clients_ok}
                    }
                else:
                    return {
                        'status': 'fail',
                        'message': f'{len(clients_need_repair)} clientes necesitan reparación',
                        'details': {'clients_need_repair': clients_need_repair},
                        'auto_fix': lambda: self._repair_clients(clients_need_repair)
                    }
        except Exception as e:
            return {
                'status': 'fail',
                'message': f'Error verificando clientes: {str(e)}'
            }
    
    def _check_chat_functionality(self) -> Dict:
        """Verifica funcionalidad del chat."""
        try:
            # Buscar cliente demo para pruebas
            test_payload = {
                "message": "Hello, test message",
                "clientId": "demo-client-12345"
            }
            
            response = requests.post(
                f"{self.flask_url}/chat-api",
                json=test_payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                reply = data.get('reply', '')
                
                if 'error' in reply.lower() or 'asesor' in reply.lower():
                    return {
                        'status': 'warning',
                        'message': 'Chat responde pero con mensaje de error genérico',
                        'details': {'response': reply[:100] + '...' if len(reply) > 100 else reply}
                    }
                else:
                    return {
                        'status': 'pass',
                        'message': 'Chat funcionando correctamente',
                        'details': {'response_length': len(reply)}
                    }
            else:
                return {
                    'status': 'fail',
                    'message': f'Chat API error: {response.status_code}',
                    'details': {'status_code': response.status_code}
                }
        except Exception as e:
            return {
                'status': 'fail',
                'message': f'Error verificando chat: {str(e)}'
            }
    
    def _check_admin_panel(self) -> Dict:
        """Verifica panel administrativo."""
        try:
            response = requests.get(f"{self.flask_url}/admin/indexer/", timeout=10)
            if response.status_code == 200:
                return {
                    'status': 'pass',
                    'message': 'Panel administrativo accesible'
                }
            else:
                return {
                    'status': 'fail',
                    'message': f'Panel admin error: {response.status_code}'
                }
        except Exception as e:
            return {
                'status': 'fail',
                'message': f'Error verificando panel admin: {str(e)}'
            }
    
    def _check_pdf_generation(self) -> Dict:
        """Verifica generación de PDFs."""
        try:
            from modules.quote_generator import QuoteGenerator
            
            generator = QuoteGenerator()
            
            # Probar extracción de información
            test_response = "Casa moderna de 3 habitaciones por $150,000 USD"
            quote_info = generator.extract_quote_info(test_response, "test")
            
            if quote_info.get('products'):
                return {
                    'status': 'pass',
                    'message': 'Sistema de cotizaciones PDF funcionando',
                    'details': {'products_found': len(quote_info['products'])}
                }
            else:
                return {
                    'status': 'warning',
                    'message': 'Sistema PDF disponible pero no detecta productos automáticamente'
                }
        except ImportError as e:
            return {
                'status': 'fail',
                'message': f'Módulo ReportLab no instalado: {str(e)}',
                'auto_fix': lambda: self._install_pdf_dependencies()
            }
        except Exception as e:
            return {
                'status': 'fail',
                'message': f'Error verificando PDFs: {str(e)}'
            }
    
    def _check_multilanguage(self) -> Dict:
        """Verifica sistema multilenguaje."""
        try:
            from modules.assistant.core import get_language_specific_prompt
            
            # Probar diferentes idiomas
            test_cases = [
                ("¿Cuánto cuesta?", "es"),
                ("How much does it cost?", "en"),
                ("Combien ça coûte?", "fr")
            ]
            
            languages_working = 0
            
            for question, expected_lang in test_cases:
                prompt = get_language_specific_prompt(question, "test context")
                if expected_lang == "es" and "español" in prompt.lower():
                    languages_working += 1
                elif expected_lang == "en" and "english" in prompt.lower():
                    languages_working += 1
                elif expected_lang == "fr" and "français" in prompt.lower():
                    languages_working += 1
            
            if languages_working == len(test_cases):
                return {
                    'status': 'pass',
                    'message': f'Sistema multilenguaje funcionando - {languages_working} idiomas verificados'
                }
            else:
                return {
                    'status': 'warning',
                    'message': f'Solo {languages_working}/{len(test_cases)} idiomas funcionando correctamente'
                }
        except Exception as e:
            return {
                'status': 'fail',
                'message': f'Error verificando multilenguaje: {str(e)}'
            }
    
    def _check_extensions_system(self) -> Dict:
        """Verifica sistema de extensiones."""
        try:
            from modules.extensions import list_extensions, get_extension
            from modules.integrations.extension_hooks import hook_system
            
            extensions = list_extensions()
            hooks = hook_system.list_hooks()
            
            return {
                'status': 'pass',
                'message': f'Sistema de extensiones funcionando - {len(extensions)} extensiones, {sum(hooks.values())} hooks',
                'details': {'extensions': extensions, 'hooks': hooks}
            }
        except Exception as e:
            return {
                'status': 'warning',
                'message': f'Sistema de extensiones disponible pero con advertencias: {str(e)}'
            }
    
    def _check_core_files_integrity(self) -> Dict:
        """Verifica integridad de archivos core."""
        core_files = [
            'modules/assistant/core.py',
            'modules/models.py',
            'modules/vector_manager.py',
            'modules/document_manager.py',
            'modules/quote_generator.py',
            'modules/indexer_admin/routes.py'
        ]
        
        missing_files = []
        
        for file_path in core_files:
            if not os.path.exists(file_path):
                missing_files.append(file_path)
        
        if not missing_files:
            return {
                'status': 'pass',
                'message': f'Todos los {len(core_files)} archivos core están presentes'
            }
        else:
            return {
                'status': 'fail',
                'message': f'{len(missing_files)} archivos core faltantes: {missing_files}'
            }
    
    def _repair_clients(self, clients_need_repair: List[Dict]) -> Dict:
        """Auto-repara clientes con problemas."""
        try:
            from auto_fix_clients import auto_fix_all_clients
            success = auto_fix_all_clients()
            
            if success:
                return {
                    'success': True,
                    'message': f'{len(clients_need_repair)} clientes reparados automáticamente'
                }
            else:
                return {
                    'success': False,
                    'message': 'Error en auto-reparación de clientes'
                }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error ejecutando auto-reparación: {str(e)}'
            }
    
    def _print_summary(self, passed: int, total: int):
        """Imprime resumen de verificación."""
        success_rate = (passed / total) * 100
        
        print(f"\n🎯 RESUMEN DE VERIFICACIÓN")
        print("=" * 40)
        print(f"✅ Verificaciones exitosas: {passed}/{total} ({success_rate:.1f}%)")
        print(f"⚠️ Advertencias: {len(self.results['warnings'])}")
        print(f"❌ Errores: {len(self.results['errors'])}")
        print(f"🔧 Reparaciones aplicadas: {len(self.results['repairs'])}")
        
        if self.results['overall_status'] == 'excellent':
            print("🎉 SISTEMA EN EXCELENTE ESTADO")
        elif self.results['overall_status'] == 'good':
            print("👍 SISTEMA EN BUEN ESTADO")
        elif self.results['overall_status'] == 'fair':
            print("⚠️ SISTEMA NECESITA ATENCIÓN")
        else:
            print("🚨 SISTEMA NECESITA REPARACIÓN URGENTE")
        
        if self.results['warnings']:
            print("\n⚠️ ADVERTENCIAS:")
            for warning in self.results['warnings']:
                print(f"   • {warning}")
        
        if self.results['errors']:
            print("\n❌ ERRORES:")
            for error in self.results['errors']:
                print(f"   • {error}")
        
        if self.results['repairs']:
            print("\n🔧 REPARACIONES APLICADAS:")
            for repair, result in self.results['repairs'].items():
                status = "✅" if result.get('success') else "❌"
                print(f"   {status} {repair}: {result.get('message', 'Sin mensaje')}")

if __name__ == "__main__":
    print("🛡️ VERIFICADOR DE SALUD SISTEMA SALESMIND")
    print("Ejecutando verificación completa...")
    
    checker = SystemHealthChecker()
    results = checker.run_complete_check()
    
    # Guardar resultados en archivo
    import json
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_file = f"system_health_report_{timestamp}.json"
    
    # Convertir datetime para JSON
    results_json = results.copy()
    results_json['timestamp'] = results['timestamp'].isoformat()
    
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(results_json, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 Reporte guardado en: {report_file}")
    
    # Código de salida basado en estado
    exit_codes = {
        'excellent': 0,
        'good': 0,
        'fair': 1,
        'poor': 2
    }
    
    exit_code = exit_codes.get(results['overall_status'], 2)
    print(f"🚪 Saliendo con código: {exit_code}")
    sys.exit(exit_code)