# config/settings.py
import os

DEFAULT_CONFIG = {
    "ui_mode": "floating",
    # ... (otras configuraciones sin cambios)
    "audio_input_device": "default",
    "audio_output_device": "default",
    "save_path": os.path.join(os.path.expanduser("~"), "MeetingAssistant_Recordings"),

    # --- Configuración del LLM ---
    "llm_provider": "local",
    
    # --- Novedad: Configuración de API más detallada ---
    "api_provider": "openai",  # "openai" u "openrouter"
    "api_key": "",
    "api_model_name": "gpt-4o",
    
    # Campos específicos para OpenRouter
    "openrouter_site_url": "http://localhost:3000", # O el nombre de tu app
    "openrouter_app_name": "Meeting Assistant",

    # ... (resto de configuraciones sin cambios)
    "ollama_host": "http://localhost",
    "ollama_port": "11434",
    "local_model_name": "llama3",
    "summary_prompt": """...""",
    "action_items_prompt": """...""",
    "transcription_provider": "local",
    "whisper_api_key": ""
}