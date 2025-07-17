# Crear el archivo recorder.py mejorado
improved_recorder = '''# audio/recorder.py (Versión mejorada)

import sounddevice as sd
import numpy as np
import wave
import threading
import os
import queue
from datetime import datetime
import soundfile as sf

class AudioRecorder:
    def __init__(self, config_manager, file_manager, notification_manager=None):
        self.config_manager = config_manager
        self.file_manager = file_manager
        self.notification_manager = notification_manager
        self.is_recording = False
        self.recording_thread = None
        self.output_path = None
        
        # Colas separadas para cada stream de audio
        self.input_queue = queue.Queue()
        self.output_queue = queue.Queue()
        
        # Streams de audio
        self.input_stream = None
        self.output_stream = None
        
        # Configuración de audio
        self.samplerate = 44100
        self.channels = 1  # Mono para eficiencia

    def list_audio_devices(self):
        """Lista todos los dispositivos de audio disponibles."""
        devices = sd.query_devices()
        input_devices = []
        output_devices = []
        
        for i, device in enumerate(devices):
            device_info = {
                'id': i,
                'name': device['name'],
                'channels': device['max_input_channels'] or device['max_output_channels']
            }
            
            if device['max_input_channels'] > 0:
                input_devices.append(device_info)
            if device['max_output_channels'] > 0:
                output_devices.append(device_info)
                
        return {
            'input_devices': input_devices,
            'output_devices': output_devices
        }

    def _get_device_id(self, device_name_str, device_type):
        """Extrae el ID numérico del dispositivo desde la cadena de configuración."""
        if not device_name_str or device_name_str.lower() == 'default':
            return None
        
        try:
            # Extrae el número del inicio de la cadena (ej. "2: Micrófono...")
            return int(device_name_str.split(':')[0])
        except (ValueError, IndexError):
            if self.notification_manager:
                self.notification_manager.show_warning(
                    f"No se pudo identificar el dispositivo de {device_type}. Usando predeterminado."
                )
            return None

    def _input_callback(self, indata, frames, time, status):
        """Callback para el stream de entrada (micrófono)."""
        if status:
            print(f"Estado del input: {status}")
        self.input_queue.put(indata.copy())

    def _output_callback(self, indata, frames, time, status):
        """Callback para el stream de salida (sistema/loopback)."""
        if status:
            print(f"Estado del output: {status}")
        self.output_queue.put(indata.copy())

    def _recording_worker(self, audio_queues, output_files):
        """Worker que procesa las colas de audio y guarda los datos."""
        writers = {}
        
        try:
            # Crear writers para cada archivo
            for name, filepath in output_files.items():
                writers[name] = sf.SoundFile(
                    filepath, mode='w', 
                    samplerate=self.samplerate,
                    channels=self.channels,
                    format='WAV'
                )
            
            # Procesar audio mientras se graba
            while self.is_recording:
                # Procesar cola de entrada
                if 'input' in audio_queues:
                    try:
                        data = audio_queues['input'].get(timeout=0.1)
                        writers['input'].write(data)
                    except queue.Empty:
                        pass
                
                # Procesar cola de salida
                if 'output' in audio_queues:
                    try:
                        data = audio_queues['output'].get(timeout=0.1)
                        writers['output'].write(data)
                    except queue.Empty:
                        pass
            
            # Procesar datos restantes en las colas
            for name, q in audio_queues.items():
                while not q.empty():
                    data = q.get()
                    writers[name].write(data)
                    
        finally:
            # Cerrar todos los writers
            for writer in writers.values():
                writer.close()

    def _merge_audio_files(self, input_file, output_file, merged_file):
        """Mezcla los archivos de audio de entrada y salida en uno solo."""
        try:
            # Leer ambos archivos
            data_input, sr1 = sf.read(input_file)
            data_output, sr2 = sf.read(output_file)
            
            # Asegurar que ambos tengan la misma longitud
            min_length = min(len(data_input), len(data_output))
            data_input = data_input[:min_length]
            data_output = data_output[:min_length]
            
            # Mezclar las señales (promedio simple)
            merged_data = (data_input + data_output) / 2
            
            # Guardar el archivo mezclado
            sf.write(merged_file, merged_data, self.samplerate)
            
            # Eliminar archivos temporales
            os.remove(input_file)
            os.remove(output_file)
            
            return True
        except Exception as e:
            print(f"Error al mezclar audio: {e}")
            return False

    def start_recording(self, record_input=True, record_output=True):
        """Inicia la grabación de audio."""
        if self.is_recording:
            return False
        
        self.is_recording = True
        config = self.config_manager.get_config()
        
        # Crear carpeta para la reunión
        self.output_path = self.file_manager.create_meeting_folder()
        
        # Configurar dispositivos
        input_device_id = self._get_device_id(
            config.get("audio_input_device"), "entrada"
        ) if record_input else None
        
        output_device_id = self._get_device_id(
            config.get("audio_output_device"), "salida"
        ) if record_output else None
        
        # Preparar archivos y colas
        audio_queues = {}
        output_files = {}
        
        try:
            # Iniciar stream de entrada si está habilitado
            if record_input and input_device_id is not None:
                self.input_stream = sd.InputStream(
                    device=input_device_id,
                    channels=self.channels,
                    samplerate=self.samplerate,
                    callback=self._input_callback
                )
                self.input_stream.start()
                audio_queues['input'] = self.input_queue
                output_files['input'] = os.path.join(self.output_path, "audio_input.wav")
            
            # Iniciar stream de salida si está habilitado
            if record_output and output_device_id is not None:
                # Para capturar salida, necesitamos usar el dispositivo como entrada
                self.output_stream = sd.InputStream(
                    device=output_device_id,
                    channels=self.channels,
                    samplerate=self.samplerate,
                    callback=self._output_callback
                )
                self.output_stream.start()
                audio_queues['output'] = self.output_queue
                output_files['output'] = os.path.join(self.output_path, "audio_output.wav")
            
            # Si no hay streams activos, cancelar
            if not audio_queues:
                raise Exception("No se pudo iniciar ningún stream de audio")
            
            # Iniciar worker de grabación
            self.recording_thread = threading.Thread(
                target=self._recording_worker,
                args=(audio_queues, output_files),
                daemon=True
            )
            self.recording_thread.start()
            
            # Notificar inicio exitoso
            if self.notification_manager:
                self.notification_manager.show_success("Grabación iniciada")
            
            return True
            
        except Exception as e:
            self.is_recording = False
            if self.notification_manager:
                self.notification_manager.show_error(f"Error al iniciar grabación: {str(e)}")
            return False

    def stop_recording(self):
        """Detiene la grabación y guarda los archivos."""
        if not self.is_recording:
            return None
        
        self.is_recording = False
        
        # Detener streams
        if self.input_stream:
            self.input_stream.stop()
            self.input_stream.close()
        
        if self.output_stream:
            self.output_stream.stop()
            self.output_stream.close()
        
        # Esperar a que el worker termine
        if self.recording_thread:
            self.recording_thread.join(timeout=5)
        
        # Verificar archivos generados
        input_file = os.path.join(self.output_path, "audio_input.wav")
        output_file = os.path.join(self.output_path, "audio_output.wav")
        final_file = os.path.join(self.output_path, "audio.wav")
        
        # Decidir qué hacer con los archivos
        if os.path.exists(input_file) and os.path.exists(output_file):
            # Mezclar ambos archivos
            self._merge_audio_files(input_file, output_file, final_file)
        elif os.path.exists(input_file):
            # Solo entrada
            os.rename(input_file, final_file)
        elif os.path.exists(output_file):
            # Solo salida
            os.rename(output_file, final_file)
        else:
            # No se grabó nada
            if self.notification_manager:
                self.notification_manager.show_error("No se grabó audio")
            return None
        
        # Limpiar colas
        while not self.input_queue.empty():
            self.input_queue.get()
        while not self.output_queue.empty():
            self.output_queue.get()
        
        # Notificar finalización
        if self.notification_manager:
            self.notification_manager.show_success(
                f"Grabación guardada en: {os.path.basename(self.output_path)}"
            )
        
        return self.output_path

    def get_recording_status(self):
        """Retorna el estado actual de la grabación."""
        return {
            'is_recording': self.is_recording,
            'output_path': self.output_path,
            'input_active': self.input_stream is not None if self.is_recording else False,
            'output_active': self.output_stream is not None if self.is_recording else False
        }
'''

# Guardar el archivo
with open('recorder_improved.py', 'w', encoding='utf-8') as f:
    f.write(improved_recorder)

print("✅ recorder.py mejorado creado exitosamente")
print("\nCaracterísticas añadidas:")
print("- ✓ Captura simultánea de entrada (micrófono) y salida (sistema)")
print("- ✓ Listado de dispositivos de audio disponibles")
print("- ✓ Procesamiento en tiempo real con colas")
print("- ✓ Mezcla automática de streams de audio")
print("- ✓ Integración con sistema de notificaciones")
print("- ✓ Mejor manejo de errores y estados")
print("- ✓ Método para obtener estado de grabación")