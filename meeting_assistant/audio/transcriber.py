# core/transcriber.py (Versión actualizada)

import os
import openai
import ollama
from ..utils.file_manager import FileManager

class Transcriber:
    def __init__(self, config_manager):
        self.config_manager = config_manager

    def process_meeting(self, meeting_folder_path):
        """
        Orquesta todo el proceso: transcripción, resumen y acciones.
        """
        config = self.config_manager.get_config()
        audio_path = os.path.join(meeting_folder_path, "audio.wav")

        # 1. Transcripción
        print("Iniciando transcripción...")
        try:
            transcription_text = self._transcribe_audio(audio_path, config)
            FileManager.save_text_file(meeting_folder_path, "transcripcion.txt", transcription_text)
            print("Transcripción completada y guardada.")
        except Exception as e:
            print(f"Error en la transcripción: {e}")
            return None, None

        # 2. Procesamiento con LLM (Resumen y Acciones)
        print("Generando resumen y propuestas de acción...")
        try:
            summary = self._get_llm_response(config.get("summary_prompt"), transcription_text, config)
            actions = self._get_llm_response(config.get("action_items_prompt"), transcription_text, config)
            
            FileManager.save_text_file(meeting_folder_path, "resumen.txt", summary)
            FileManager.save_text_file(meeting_folder_path, "acciones.txt", actions)
            print("Resumen y acciones generados y guardados.")
            
            return summary, actions
        except Exception as e:
            print(f"Error en el procesamiento con LLM: {e}")
            return None, None

    def _transcribe_audio(self, audio_path, config):
        """Transcribe el audio usando el proveedor configurado."""
        provider = config.get("transcription_provider", "local")
        
        if provider == "api":
            api_key = config.get("whisper_api_key")
            if not api_key:
                raise ValueError("La API Key de Whisper no está configurada.")
            
            client = openai.OpenAI(api_key=api_key)
            with open(audio_path, "rb") as audio_file:
                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file
                )
            return transcript.text
        else: # local
            # Usar la implementación local de Whisper
            # Esto asume que `openai-whisper` está instalado
            import whisper
            model = whisper.load_model("base") # Se puede hacer configurable
            result = model.transcribe(audio_path)
            return result["text"]

    def _get_llm_response(self, prompt_template, transcription, config):
        """Obtiene una respuesta del LLM configurado (local o API)."""
        provider = config.get("llm_provider", "local")
        full_prompt = f"{prompt_template}\n\n{transcription}"

        if provider == "local":
            return self._query_ollama(full_prompt, config)
        elif provider == "api":
            return self._query_api(full_prompt, config)
        else:
            raise ValueError(f"Proveedor de LLM desconocido: {provider}")

    def _query_ollama(self, prompt, config):
        """Envía una petición a un modelo local de Ollama."""
        host = config.get("ollama_host", "http://localhost")
        port = config.get("ollama_port", "11434")
        model_name = config.get("local_model_name")
        
        if not model_name:
            raise ValueError("No se ha seleccionado un modelo de Ollama.")

        client = ollama.Client(host=f"{host}:{port}")
        response = client.chat(
            model=model_name,
            messages=[{'role': 'user', 'content': prompt}]
        )
        return response['message']['content']

    def _query_api(self, prompt, config):
        """Envía una petición a una API remota (OpenAI, OpenRouter)."""
        api_provider = config.get("api_provider", "openai")
        api_key = config.get("api_key")
        model_name = config.get("api_model_name")

        if not api_key or not model_name:
            raise ValueError("La API Key o el nombre del modelo no están configurados.")

        if api_provider == "openrouter":
            base_url = "https://openrouter.ai/api/v1"
            headers = {
                "HTTP-Referer": config.get("openrouter_site_url", ""),
                "X-Title": config.get("openrouter_app_name", "")
            }
            client = openai.OpenAI(api_key=api_key, base_url=base_url, default_headers=headers)
        else: # openai
            client = openai.OpenAI(api_key=api_key)

        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content