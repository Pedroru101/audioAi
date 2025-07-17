# audio/transcriber.py (Versión mejorada)

import whisper
import os
import threading
from faster_whisper import WhisperModel

class AudioTranscriber:
    def __init__(self, config_manager, notification_manager=None):
        self.config_manager = config_manager
        self.notification_manager = notification_manager
        self.model = None
        self.is_model_loaded = False
        self.current_model_size = None
        self.current_compute_type = None

    def _load_model(self):
        """Carga el modelo de Whisper según la configuración."""
        config = self.config_manager.get_config()
        model_size = config.get("whisper_model", "base")
        use_faster_whisper = config.get("use_faster_whisper", True)
        compute_type = config.get("compute_type", "int8") # float16, int8
        
        # Si el modelo ya está cargado y la configuración no ha cambiado, no hacer nada
        if self.is_model_loaded and self.current_model_size == model_size and self.current_compute_type == compute_type:
            return

        try:
            if self.notification_manager:
                self.notification_manager.show_info(f"Cargando modelo Whisper ({model_size})...")
            
            if use_faster_whisper:
                self.model = WhisperModel(model_size, device="cpu", compute_type=compute_type)
            else:
                self.model = whisper.load_model(model_size)
            
            self.is_model_loaded = True
            self.current_model_size = model_size
            self.current_compute_type = compute_type
            
            if self.notification_manager:
                self.notification_manager.show_success("Modelo Whisper cargado exitosamente.")
                
        except Exception as e:
            self.is_model_loaded = False
            if self.notification_manager:
                self.notification_manager.show_error(f"Error al cargar modelo Whisper: {e}")
            raise

    def transcribe_audio(self, audio_path, language="es"):
        """Transcribe un archivo de audio."""
        if not self.is_model_loaded:
            self._load_model()
        
        if not self.is_model_loaded:
            return "Error: Modelo de transcripción no cargado."

        try:
            if isinstance(self.model, WhisperModel):
                # Usar faster-whisper
                segments, info = self.model.transcribe(audio_path, language=language, beam_size=5)
                transcription = " ".join([segment.text for segment in segments])
            else:
                # Usar whisper original
                result = self.model.transcribe(audio_path, language=language)
                transcription = result["text"]
            
            return transcription
            
        except Exception as e:
            if self.notification_manager:
                self.notification_manager.show_error(f"Error durante la transcripción: {e}")
            return f"Error de transcripción: {e}"

    def transcribe_in_background(self, audio_path, callback, language="es"):
        """Transcribe en un hilo separado y llama a un callback con el resultado."""
        def task():
            transcription = self.transcribe_audio(audio_path, language)
            callback(transcription)

        thread = threading.Thread(target=task, daemon=True)
        thread.start()
