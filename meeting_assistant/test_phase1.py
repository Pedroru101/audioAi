# Crear archivo de prueba para la Fase 1
test_phase1 = '''# test_phase1.py - Prueba de funcionalidad Core Audio y Transcripción

import os
import sys
import time
from pathlib import Path

# Añadir el directorio del proyecto al path
sys.path.insert(0, str(Path(__file__).parent))

# Importar los módulos necesarios
from meeting_assistant.audio.recorder import AudioRecorder
from meeting_assistant.audio.transcriber import Transcriber
from meeting_assistant.config.config_manager import ConfigManager
from meeting_assistant.config.settings import DEFAULT_CONFIG
from meeting_assistant.utils.file_manager import FileManager
from meeting_assistant.utils.notifications import NotificationManager

class Phase1Tester:
    """Clase para probar la funcionalidad de la Fase 1."""
    
    def __init__(self):
        print("🚀 Meeting Assistant Pro - Prueba Fase 1")
        print("=" * 50)
        
        # Inicializar componentes
        self.config_manager = ConfigManager()
        self.file_manager = FileManager(self.config_manager)
        self.notification_manager = NotificationManager()
        
        self.recorder = AudioRecorder(
            self.config_manager, 
            self.file_manager,
            self.notification_manager
        )
        
        self.transcriber = Transcriber(
            self.config_manager,
            self.file_manager,
            self.notification_manager
        )

    def test_list_devices(self):
        """Prueba el listado de dispositivos de audio."""
        print("\\n📊 TEST 1: Listando dispositivos de audio...")
        
        try:
            devices = self.recorder.list_audio_devices()
            
            print("\\n🎤 Dispositivos de entrada:")
            for device in devices['input_devices']:
                print(f"  - ID: {device['id']}, Nombre: {device['name']}")
            
            print("\\n🔊 Dispositivos de salida:")
            for device in devices['output_devices']:
                print(f"  - ID: {device['id']}, Nombre: {device['name']}")
                
            print("\\n✅ Test de dispositivos completado")
            return True
            
        except Exception as e:
            print(f"\\n❌ Error en test de dispositivos: {e}")
            return False

    def test_short_recording(self, duration=5):
        """Prueba una grabación corta."""
        print(f"\\n🎙️ TEST 2: Grabación de {duration} segundos...")
        
        try:
            # Iniciar grabación
            print("Iniciando grabación...")
            success = self.recorder.start_recording(
                record_input=True, 
                record_output=False  # Solo micrófono para la prueba
            )
            
            if not success:
                print("❌ No se pudo iniciar la grabación")
                return None
            
            # Grabar por X segundos
            for i in range(duration, 0, -1):
                print(f"  Grabando... {i} segundos restantes", end='\\r')
                time.sleep(1)
            
            # Detener grabación
            print("\\nDeteniendo grabación...")
            output_path = self.recorder.stop_recording()
            
            if output_path:
                print(f"\\n✅ Grabación guardada en: {output_path}")
                
                # Verificar archivo
                audio_file = os.path.join(output_path, "audio.wav")
                if os.path.exists(audio_file):
                    file_size = os.path.getsize(audio_file) / 1024  # KB
                    print(f"   Tamaño del archivo: {file_size:.2f} KB")
                
                return output_path
            else:
                print("\\n❌ Error al guardar la grabación")
                return None
                
        except Exception as e:
            print(f"\\n❌ Error en grabación: {e}")
            return None

    def test_transcription(self, audio_path):
        """Prueba la transcripción de un archivo de audio."""
        print("\\n📝 TEST 3: Transcripción de audio...")
        
        if not audio_path:
            print("❌ No hay archivo de audio para transcribir")
            return False
        
        try:
            # Configurar para usar transcripción local
            config = self.config_manager.get_config()
            config['transcription_provider'] = 'local'
            config['whisper_model_size'] = 'tiny'  # Modelo más rápido para pruebas
            
            # Transcribir
            print("Cargando modelo de transcripción...")
            self.transcriber.load_whisper_model('tiny')
            
            print("Transcribiendo audio...")
            result = self.transcriber._transcribe_audio(
                os.path.join(audio_path, "audio.wav"),
                config
            )
            
            if result and result.get('text'):
                print("\\n✅ Transcripción completada:")
                print("-" * 40)
                print(result['text'][:200] + "..." if len(result['text']) > 200 else result['text'])
                print("-" * 40)
                
                # Guardar transcripción
                self.file_manager.save_text_file(
                    audio_path,
                    "transcripcion_test.txt",
                    result['text']
                )
                
                return True
            else:
                print("\\n❌ No se pudo transcribir el audio")
                return False
                
        except Exception as e:
            print(f"\\n❌ Error en transcripción: {e}")
            import traceback
            traceback.print_exc()
            return False

    def test_llm_processing(self, audio_path):
        """Prueba el procesamiento con LLM."""
        print("\\n🧠 TEST 4: Procesamiento con LLM...")
        
        if not audio_path:
            print("❌ No hay archivo de audio para procesar")
            return False
        
        try:
            # Configurar el LLM (ajustar según tu configuración)
            config = self.config_manager.get_config()
            
            # Verificar si hay API key configurada
            if config.get('llm_provider') == 'api' and not config.get('api_key'):
                print("⚠️  No hay API key configurada. Cambiando a modo local...")
                config['llm_provider'] = 'local'
                
                # Verificar si Ollama está disponible
                try:
                    import ollama
                    # Intentar listar modelos
                    ollama.list()
                    print("✅ Usando Ollama local")
                except:
                    print("❌ Ollama no está disponible. Saltando prueba de LLM.")
                    return False
            
            # Procesar reunión completa
            print("Procesando reunión con IA...")
            meeting_data, error = self.transcriber.process_meeting(audio_path)
            
            if meeting_data and not error:
                print("\\n✅ Procesamiento completado:")
                
                if meeting_data.get('summary'):
                    print("\\n📋 Resumen generado:")
                    print("-" * 40)
                    print(meeting_data['summary'][:300] + "..." 
                          if len(meeting_data['summary']) > 300 
                          else meeting_data['summary'])
                    print("-" * 40)
                
                if meeting_data.get('actions'):
                    print(f"\\n✅ {len(meeting_data['actions'])} acciones identificadas")
                
                if meeting_data.get('tags'):
                    print(f"\\n🏷️  Tags: {', '.join(meeting_data['tags'])}")
                
                return True
            else:
                print(f"\\n❌ Error en procesamiento: {error}")
                return False
                
        except Exception as e:
            print(f"\\n❌ Error en procesamiento LLM: {e}")
            import traceback
            traceback.print_exc()
            return False

    def run_all_tests(self):
        """Ejecuta todas las pruebas de la Fase 1."""
        print("\\n🔧 Ejecutando todas las pruebas de la Fase 1...")
        
        results = {
            'devices': False,
            'recording': False,
            'transcription': False,
            'llm_processing': False
        }
        
        # Test 1: Dispositivos
        results['devices'] = self.test_list_devices()
        
        # Test 2: Grabación
        audio_path = self.test_short_recording(duration=5)
        results['recording'] = audio_path is not None
        
        # Test 3: Transcripción (solo si hay grabación)
        if audio_path:
            results['transcription'] = self.test_transcription(audio_path)
        
        # Test 4: Procesamiento LLM (opcional)
        if audio_path:
            try:
                results['llm_processing'] = self.test_llm_processing(audio_path)
            except:
                print("\\n⚠️  Procesamiento LLM no disponible")
        
        # Resumen de resultados
        print("\\n" + "=" * 50)
        print("📊 RESUMEN DE PRUEBAS FASE 1:")
        print("=" * 50)
        
        for test, passed in results.items():
            status = "✅ PASÓ" if passed else "❌ FALLÓ"
            print(f"{test.ljust(20)}: {status}")
        
        total_passed = sum(1 for v in results.values() if v)
        print(f"\\nTotal: {total_passed}/{len(results)} pruebas pasadas")
        
        if total_passed == len(results):
            print("\\n🎉 ¡Todas las pruebas pasaron! La Fase 1 está completa.")
        elif total_passed >= 3:
            print("\\n✅ La funcionalidad core está operativa. Algunos componentes opcionales fallaron.")
        else:
            print("\\n⚠️  Hay problemas con la funcionalidad core. Revisa los errores.")

def main():
    """Función principal para ejecutar las pruebas."""
    tester = Phase1Tester()
    
    print("\\n¿Qué deseas probar?")
    print("1. Ejecutar todas las pruebas")
    print("2. Solo listar dispositivos")
    print("3. Solo probar grabación")
    print("4. Solo probar transcripción (necesitas un archivo)")
    print("5. Salir")
    
    choice = input("\\nSelecciona una opción (1-5): ").strip()
    
    if choice == '1':
        tester.run_all_tests()
    elif choice == '2':
        tester.test_list_devices()
    elif choice == '3':
        audio_path = tester.test_short_recording()
        if audio_path:
            print(f"\\n💡 Puedes encontrar la grabación en: {audio_path}")
    elif choice == '4':
        # Buscar la última grabación
        meetings_dir = Path("data/meetings")
        if meetings_dir.exists():
            recent_meetings = sorted(meetings_dir.iterdir(), key=os.path.getmtime, reverse=True)
            if recent_meetings:
                last_meeting = recent_meetings[0]
                print(f"\\nUsando la última grabación: {last_meeting.name}")
                tester.test_transcription(str(last_meeting))
            else:
                print("\\n❌ No hay grabaciones disponibles")
        else:
            print("\\n❌ No existe el directorio de reuniones")
    elif choice == '5':
        print("\\n👋 ¡Hasta luego!")
    else:
        print("\\n❌ Opción no válida")

if __name__ == "__main__":
    main()
'''

# Guardar el archivo
with open('test_phase1.py', 'w', encoding='utf-8') as f:
    f.write(test_phase1)

print("✅ test_phase1.py creado exitosamente")
print("\nEste archivo te permite probar:")
print("- ✓ Listado de dispositivos de audio")
print("- ✓ Grabación de audio de prueba (5 segundos)")
print("- ✓ Transcripción con Whisper")
print("- ✓ Procesamiento con LLM")
print("- ✓ Verificación completa de la Fase 1")
print("\n🎯 Para ejecutar: python test_phase1.py")