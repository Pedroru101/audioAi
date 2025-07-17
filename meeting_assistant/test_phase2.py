# Crear archivo de prueba para la Fase 2
test_phase2 = '''# test_phase2.py - Prueba de funcionalidad de Configuración y Gestión

import os
import sys
import time
import json
from pathlib import Path
from datetime import datetime

# Añadir el directorio del proyecto al path
sys.path.insert(0, str(Path(__file__).parent))

# Importar los módulos de la Fase 2
from meeting_assistant.config.config_manager import ConfigManager
from meeting_assistant.utils.file_manager import FileManager
from meeting_assistant.utils.notifications import NotificationManager
from meeting_assistant.utils.error_manager import ErrorManager, ErrorContext

class Phase2Tester:
    """Clase para probar la funcionalidad de la Fase 2."""
    
    def __init__(self):
        print("🚀 Meeting Assistant Pro - Prueba Fase 2")
        print("=" * 50)
        
        # Inicializar componentes
        print("Inicializando componentes...")
        
        self.config_manager = ConfigManager()
        self.notification_manager = NotificationManager(self.config_manager)
        self.error_manager = ErrorManager(self.config_manager, self.notification_manager)
        self.file_manager = FileManager(self.config_manager)
        
        print("✅ Componentes inicializados")

    def test_config_manager(self):
        """Prueba el ConfigManager."""
        print("\\n📊 TEST 1: ConfigManager")
        print("-" * 40)
        
        results = {
            'load': False,
            'save': False,
            'validate': False,
            'update': False,
            'export': False
        }
        
        try:
            # 1. Cargar configuración
            print("1. Cargando configuración...")
            config = self.config_manager.get_config()
            print(f"   ✓ Configuración cargada. Claves: {len(config)}")
            results['load'] = True
            
            # 2. Obtener valor específico
            ui_mode = self.config_manager.get('ui_mode', 'default')
            print(f"   ✓ Modo UI actual: {ui_mode}")
            
            # 3. Actualizar valor
            print("\\n2. Actualizando configuración...")
            old_value = self.config_manager.get('test_value', 'no_existe')
            success = self.config_manager.set('test_value', 'prueba_fase2')
            if success:
                new_value = self.config_manager.get('test_value')
                print(f"   ✓ Valor actualizado: '{old_value}' -> '{new_value}'")
                results['update'] = True
            
            # 4. Guardar configuración
            print("\\n3. Guardando configuración...")
            if self.config_manager._save_config():
                print("   ✓ Configuración guardada exitosamente")
                results['save'] = True
            
            # 5. Validar configuración
            print("\\n4. Validando configuración...")
            is_valid = self.config_manager.is_valid()
            status = self.config_manager.get_status()
            print(f"   ✓ Configuración válida: {is_valid}")
            print(f"   ✓ LLM Provider: {status['llm_provider']}")
            print(f"   ✓ Transcription Provider: {status['transcription_provider']}")
            results['validate'] = True
            
            # 6. Exportar configuración
            print("\\n5. Exportando configuración...")
            export_path = "config_export_test.json"
            if self.config_manager.export_config(export_path, include_sensitive=False):
                print(f"   ✓ Configuración exportada a: {export_path}")
                results['export'] = True
                
                # Limpiar archivo de prueba
                try:
                    os.remove(export_path)
                except:
                    pass
            
        except Exception as e:
            print(f"\\n❌ Error en prueba de ConfigManager: {e}")
            import traceback
            traceback.print_exc()
        
        return results

    def test_file_manager(self):
        """Prueba el FileManager."""
        print("\\n📁 TEST 2: FileManager")
        print("-" * 40)
        
        results = {
            'create_folder': False,
            'save_files': False,
            'list_meetings': False,
            'storage_info': False,
            'export': False
        }
        
        meeting_path = None
        
        try:
            # 1. Crear carpeta de reunión
            print("1. Creando carpeta de reunión...")
            meeting_path = self.file_manager.create_meeting_folder("Reunión de Prueba Fase 2")
            print(f"   ✓ Carpeta creada: {meeting_path}")
            results['create_folder'] = True
            
            # 2. Guardar archivos de prueba
            print("\\n2. Guardando archivos de prueba...")
            
            # Texto
            text_saved = self.file_manager.save_text_file(
                meeting_path,
                "prueba.txt",
                "Este es un archivo de prueba para la Fase 2"
            )
            
            # JSON
            json_data = {
                "test": "fase2",
                "timestamp": datetime.now().isoformat(),
                "components": ["ConfigManager", "FileManager", "NotificationManager", "ErrorManager"]
            }
            json_saved = self.file_manager.save_json_file(
                meeting_path,
                "prueba.json",
                json_data
            )
            
            if text_saved and json_saved:
                print("   ✓ Archivos guardados correctamente")
                results['save_files'] = True
            
            # 3. Listar reuniones
            print("\\n3. Listando reuniones...")
            meetings = self.file_manager.list_meetings()
            print(f"   ✓ Total de reuniones: {len(meetings)}")
            if meetings:
                latest = meetings[0]
                print(f"   ✓ Última reunión: {latest.get('custom_name', 'Sin nombre')}")
                print(f"     - Fecha: {latest.get('created', 'Desconocida')}")
                print(f"     - Tamaño: {latest.get('size_mb', 0):.2f} MB")
            results['list_meetings'] = True
            
            # 4. Información de almacenamiento
            print("\\n4. Información de almacenamiento...")
            storage = self.file_manager.get_storage_info()
            print(f"   ✓ Espacio usado: {storage['total_size_mb']:.2f} MB")
            print(f"   ✓ Total de archivos: {storage['file_count']}")
            print(f"   ✓ Espacio libre: {storage['free_space_gb']:.2f} GB")
            results['storage_info'] = True
            
            # 5. Exportar reunión
            print("\\n5. Exportando reunión...")
            export_path = self.file_manager.export_meeting(
                meeting_path,
                export_format='zip',
                include_audio=False
            )
            if export_path:
                print(f"   ✓ Reunión exportada: {export_path}")
                results['export'] = True
                
                # Limpiar archivo exportado
                try:
                    os.remove(export_path)
                except:
                    pass
            
        except Exception as e:
            print(f"\\n❌ Error en prueba de FileManager: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            # Limpiar carpeta de prueba
            if meeting_path and os.path.exists(meeting_path):
                try:
                    import shutil
                    shutil.rmtree(meeting_path)
                    print("\\n   ✓ Carpeta de prueba limpiada")
                except:
                    pass
        
        return results

    def test_notification_manager(self):
        """Prueba el NotificationManager."""
        print("\\n💬 TEST 3: NotificationManager")
        print("-" * 40)
        
        results = {
            'info': False,
            'success': False,
            'warning': False,
            'error': False,
            'action': False
        }
        
        try:
            print("Mostrando notificaciones de prueba...")
            print("(Las notificaciones aparecerán en la esquina de tu pantalla)")
            
            # 1. Notificación de información
            print("\\n1. Notificación INFO...")
            self.notification_manager.show_info(
                "Esta es una notificación de información",
                "Prueba Info"
            )
            time.sleep(1)
            results['info'] = True
            
            # 2. Notificación de éxito
            print("2. Notificación ÉXITO...")
            self.notification_manager.show_success(
                "¡Operación completada exitosamente!",
                "Prueba Éxito"
            )
            time.sleep(1)
            results['success'] = True
            
            # 3. Notificación de advertencia
            print("3. Notificación ADVERTENCIA...")
            self.notification_manager.show_warning(
                "Esta es una advertencia de prueba",
                "Prueba Advertencia"
            )
            time.sleep(1)
            results['warning'] = True
            
            # 4. Notificación de error
            print("4. Notificación ERROR...")
            self.notification_manager.show_error(
                "Este es un error de prueba (no es real)",
                "Prueba Error"
            )
            time.sleep(1)
            results['error'] = True
            
            # 5. Notificación con acciones
            print("5. Notificación con ACCIONES...")
            
            def action_callback():
                print("   → Acción ejecutada desde notificación")
            
            self.notification_manager.show_action(
                "¿Deseas continuar con la prueba?",
                "Prueba Acción",
                actions=[
                    {'text': 'Sí', 'callback': action_callback},
                    {'text': 'No', 'callback': lambda: print("   → Cancelado")}
                ]
            )
            results['action'] = True
            
            print("\\n✅ Notificaciones enviadas. Espera a que se cierren...")
            time.sleep(5)
            
        except Exception as e:
            print(f"\\n❌ Error en prueba de NotificationManager: {e}")
            import traceback
            traceback.print_exc()
        
        return results

    def test_error_manager(self):
        """Prueba el ErrorManager."""
        print("\\n🚨 TEST 4: ErrorManager")
        print("-" * 40)
        
        results = {
            'logging': False,
            'context': False,
            'decorator': False,
            'summary': False,
            'export': False
        }
        
        try:
            # 1. Logging de diferentes niveles
            print("1. Probando logging de errores...")
            
            self.error_manager.log_info("Mensaje informativo de prueba")
            self.error_manager.log_warning("Advertencia de prueba")
            self.error_manager.log_error("Error de prueba (no es real)")
            
            print("   ✓ Mensajes registrados")
            results['logging'] = True
            
            # 2. Context manager
            print("\\n2. Probando context manager...")
            
            with ErrorContext(self.error_manager, "prueba_context", suppress=True):
                print("   → Ejecutando código en contexto seguro")
                # Simular un error controlado
                try:
                    raise ValueError("Error simulado en contexto")
                except ValueError:
                    pass
            
            print("   ✓ Context manager funcionando")
            results['context'] = True
            
            # 3. Decorador
            print("\\n3. Probando decorador...")
            
            @ErrorManager.handle_errors(default_return="Error manejado")
            def funcion_con_error():
                raise RuntimeError("Error simulado en función")
            
            resultado = funcion_con_error()
            print(f"   ✓ Función con error retornó: '{resultado}'")
            results['decorator'] = True
            
            # 4. Resumen de errores
            print("\\n4. Obteniendo resumen de errores...")
            summary = self.error_manager.get_error_summary()
            print(f"   ✓ Total de errores: {summary['total_errors']}")
            print(f"   ✓ Por nivel: {summary['by_level']}")
            results['summary'] = True
            
            # 5. Exportar reporte
            print("\\n5. Exportando reporte de errores...")
            report_path = "error_report_test.json"
            if self.error_manager.export_error_report(report_path):
                print(f"   ✓ Reporte exportado: {report_path}")
                results['export'] = True
                
                # Limpiar archivo
                try:
                    os.remove(report_path)
                except:
                    pass
            
        except Exception as e:
            print(f"\\n❌ Error en prueba de ErrorManager: {e}")
            import traceback
            traceback.print_exc()
        
        return results

    def run_all_tests(self):
        """Ejecuta todas las pruebas de la Fase 2."""
        print("\\n🔧 Ejecutando todas las pruebas de la Fase 2...")
        
        all_results = {}
        
        # Test 1: ConfigManager
        print("\\n" + "="*50)
        config_results = self.test_config_manager()
        all_results['ConfigManager'] = config_results
        
        # Test 2: FileManager
        print("\\n" + "="*50)
        file_results = self.test_file_manager()
        all_results['FileManager'] = file_results
        
        # Test 3: NotificationManager
        print("\\n" + "="*50)
        notification_results = self.test_notification_manager()
        all_results['NotificationManager'] = notification_results
        
        # Test 4: ErrorManager
        print("\\n" + "="*50)
        error_results = self.test_error_manager()
        all_results['ErrorManager'] = error_results
        
        # Resumen final
        print("\\n" + "="*50)
        print("📊 RESUMEN DE PRUEBAS FASE 2:")
        print("="*50)
        
        total_tests = 0
        passed_tests = 0
        
        for component, results in all_results.items():
            component_passed = sum(1 for v in results.values() if v)
            component_total = len(results)
            total_tests += component_total
            passed_tests += component_passed
            
            status = "✅" if component_passed == component_total else "⚠️"
            print(f"{status} {component}: {component_passed}/{component_total} pruebas pasadas")
            
            # Mostrar detalles si hay fallos
            if component_passed < component_total:
                for test, passed in results.items():
                    if not passed:
                        print(f"   ❌ {test}")
        
        print(f"\\nTotal general: {passed_tests}/{total_tests} pruebas pasadas")
        
        if passed_tests == total_tests:
            print("\\n🎉 ¡Todas las pruebas pasaron! La Fase 2 está completa.")
        elif passed_tests >= total_tests * 0.8:
            print("\\n✅ La mayoría de componentes funcionan correctamente.")
        else:
            print("\\n⚠️  Hay varios componentes con problemas. Revisa los errores.")
        
        # Limpiar
        print("\\nLimpiando notificaciones...")
        self.notification_manager.clear_all()

def main():
    """Función principal para ejecutar las pruebas."""
    tester = Phase2Tester()
    
    print("\\n¿Qué deseas probar?")
    print("1. Ejecutar todas las pruebas")
    print("2. Solo ConfigManager")
    print("3. Solo FileManager")
    print("4. Solo NotificationManager")
    print("5. Solo ErrorManager")
    print("6. Salir")
    
    choice = input("\\nSelecciona una opción (1-6): ").strip()
    
    if choice == '1':
        tester.run_all_tests()
    elif choice == '2':
        tester.test_config_manager()
    elif choice == '3':
        tester.test_file_manager()
    elif choice == '4':
        tester.test_notification_manager()
    elif choice == '5':
        tester.test_error_manager()
    elif choice == '6':
        print("\\n👋 ¡Hasta luego!")
    else:
        print("\\n❌ Opción no válida")
    
    # Asegurar que las notificaciones se cierren
    print("\\nCerrando componentes...")
    tester.notification_manager.stop()

if __name__ == "__main__":
    main()
'''

# Guardar el archivo
with open('test_phase2.py', 'w', encoding='utf-8') as f:
    f.write(test_phase2)

print("✅ test_phase2.py creado exitosamente")
print("\nEste archivo te permite probar:")
print("- ✓ ConfigManager: carga, guardado, validación, exportación")
print("- ✓ FileManager: creación de carpetas, gestión de archivos")
print("- ✓ NotificationManager: todos los tipos de notificaciones")
print("- ✓ ErrorManager: logging, decoradores, context managers")
print("- ✓ Verificación completa de la Fase 2")
print("\n🎯 Para ejecutar: python test_phase2.py")