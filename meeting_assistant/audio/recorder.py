# core/recorder.py (Versión actualizada)

import sounddevice as sd
import numpy as np
import wave
import threading
import os
from datetime import datetime

class AudioRecorder:
    def __init__(self, config_manager, file_manager):
        self.config_manager = config_manager
        self.file_manager = file_manager
        self.is_recording = False
        self.frames = []
        self.thread = None
        self.stream = None
        self.output_path = None

    def _get_device_id(self, device_name_str, device_type):
        """Extrae el ID numérico del dispositivo desde la cadena de configuración."""
        if not device_name_str or device_name_str.lower() == 'default':
            return None # Usar el dispositivo por defecto del sistema
        try:
            # Extrae el número del inicio de la cadena (ej. "2: Micrófono...")
            return int(device_name_str.split(':')[0])
        except (ValueError, IndexError):
            print(f"Advertencia: No se pudo parsear el ID del dispositivo de {device_type}: '{device_name_str}'. Usando el predeterminado.")
            return None

    def _recording_loop(self):
        """Bucle que se ejecuta en un hilo para capturar el audio."""
        config = self.config_manager.get_config()
        
        # Obtener IDs de dispositivos desde la configuración
        input_device_id = self._get_device_id(config.get("audio_input_device"), "entrada")
        
        # Para el loopback, el dispositivo de "salida" de la app es la "entrada" de la grabación
        output_device_id = self._get_device_id(config.get("audio_output_device"), "salida")

        # TODO: Implementar la grabación simultánea de entrada y salida.
        # Por ahora, priorizamos el micrófono si está configurado.
        # Una solución avanzada requeriría mezclar dos streams.
        device_id = input_device_id if input_device_id is not None else output_device_id
        if device_id is None:
            print("Usando dispositivo de entrada por defecto.")

        samplerate = 44100
        channels = 1 # Mono es suficiente y más eficiente

        def callback(indata, frames, time, status):
            if status:
                print(status)
            self.frames.append(indata.copy())

        try:
            with sd.InputStream(samplerate=samplerate, device=device_id, channels=channels, callback=callback):
                print("Grabación iniciada...")
                while self.is_recording:
                    sd.sleep(100)
        except Exception as e:
            print(f"Error al iniciar la grabación: {e}")
            # Aquí podrías notificar al usuario a través de la UI
            self.is_recording = False # Detener el intento de grabación

    def start_recording(self):
        if self.is_recording:
            return
        
        self.is_recording = True
        self.frames = []
        
        # Crear la carpeta para la reunión actual
        self.output_path = self.file_manager.create_meeting_folder()
        
        self.thread = threading.Thread(target=self._recording_loop, daemon=True)
        self.thread.start()
        print("Hilo de grabación iniciado.")

    def stop_recording(self):
        if not self.is_recording:
            return None
        
        self.is_recording = False
        if self.thread:
            self.thread.join() # Esperar a que el hilo termine limpiamente
        
        print("Grabación detenida. Guardando archivo...")
        
        if not self.frames:
            print("No se grabaron datos de audio.")
            return None

        # Guardar el archivo de audio
        audio_file_path = os.path.join(self.output_path, "audio.wav")
        
        try:
            recording = np.concatenate(self.frames, axis=0)
            with wave.open(audio_file_path, 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2) # 2 bytes = 16 bits
                wf.setframerate(44100)
                wf.writeframes((recording * 32767).astype(np.int16).tobytes())
            
            print(f"Archivo de audio guardado en: {audio_file_path}")
            return self.output_path # Devolvemos la carpeta de la reunión
        except Exception as e:
            print(f"Error al guardar el archivo de audio: {e}")
            return None