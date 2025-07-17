# Crear el archivo settings.py mejorado
improved_settings = '''# config/settings.py (Versión mejorada)
import os
from pathlib import Path

# Paths base
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
MEETINGS_DIR = DATA_DIR / "meetings"
LOGS_DIR = DATA_DIR / "logs"

# Asegurar que los directorios existan
for directory in [DATA_DIR, MEETINGS_DIR, LOGS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Configuración por defecto
DEFAULT_CONFIG = {
    # === INTERFAZ DE USUARIO ===
    "ui_mode": "floating",  # "floating" o "classic"
    "theme": "dark",  # "dark" o "light"
    "window_opacity": 0.95,
    "always_on_top": True,
    "start_minimized": False,
    "language": "es",  # "es", "en"
    
    # === AUDIO ===
    "audio_input_device": "default",
    "audio_output_device": "default",
    "audio_quality": "high",  # "low", "medium", "high"
    "audio_format": "wav",
    "sample_rate": 44100,
    "channels": 1,  # 1 = mono, 2 = stereo
    "record_system_audio": True,
    "record_microphone": True,
    
    # === PATHS ===
    "save_path": os.path.join(os.path.expanduser("~"), "MeetingAssistant_Recordings"),
    "temp_path": os.path.join(os.path.expanduser("~"), ".meeting_assistant", "temp"),
    
    # === TRANSCRIPCIÓN ===
    "transcription_provider": "local",  # "local" o "api"
    "whisper_model_size": "base",  # "tiny", "base", "small", "medium", "large"
    "whisper_language": None,  # None = auto-detectar, o código ISO (es, en, etc)
    "whisper_api_key": "",
    "transcription_api_provider": "openai",  # "openai", "assemblyai", "deepgram"
    
    # === MODELO DE LENGUAJE (LLM) ===
    "llm_provider": "local",  # "local" o "api"
    
    # Configuración para API
    "api_provider": "openai",  # "openai" o "openrouter"
    "api_key": "",
    "api_model_name": "gpt-4o",
    "api_temperature": 0.7,
    "api_max_tokens": 2000,
    
    # Configuración para OpenRouter
    "openrouter_site_url": "http://localhost:3000",
    "openrouter_app_name": "Meeting Assistant Pro",
    
    # Configuración para Ollama (local)
    "ollama_host": "http://localhost",
    "ollama_port": "11434",
    "local_model_name": "llama3",
    "local_temperature": 0.7,
    "local_max_tokens": 2000,
    
    # === PROCESAMIENTO ===
    "auto_process": True,  # Procesar automáticamente al terminar grabación
    "generate_summary": True,
    "generate_actions": True,
    "generate_insights": True,
    "generate_analytics": True,
    "export_formats": ["md", "json", "txt"],  # Formatos de exportación
    
    # === NOTIFICACIONES ===
    "notifications_enabled": True,
    "notification_sound": True,
    "notification_position": "bottom-right",  # "top-right", "top-left", "bottom-right", "bottom-left"
    "notification_duration": 3000,  # milisegundos
    
    # === SEGURIDAD Y PRIVACIDAD ===
    "encryption_enabled": False,
    "auto_delete_recordings": False,
    "retention_days": 30,  # Días antes de eliminar automáticamente
    "require_confirmation": True,  # Confirmar antes de procesar
    
    # === ATAJOS DE TECLADO ===
    "hotkeys": {
        "start_stop_recording": "Ctrl+Shift+R",
        "pause_resume": "Ctrl+Shift+P",
        "save_meeting": "Ctrl+Shift+S",
        "open_settings": "Ctrl+Shift+O",
        "minimize_restore": "Ctrl+Shift+M"
    },
    
    # === CONTEXTO DE REUNIÓN ===
    "meeting_context": {
        "title": "",
        "participants": [],
        "objective": "",
        "tags": []
    },
    
    # === PROMPTS DEL SISTEMA ===
    "summary_prompt": """Analiza la siguiente transcripción y genera un resumen ejecutivo conciso.

INSTRUCCIONES:
- Máximo 200 palabras
- Incluye los puntos clave discutidos
- Menciona decisiones importantes
- Usa un tono profesional y objetivo
- Estructura en párrafos cortos

TRANSCRIPCIÓN:
""",

    "action_items_prompt": """Analiza la transcripción e identifica TODAS las acciones y tareas mencionadas.

FORMATO REQUERIDO:
| Acción | Responsable | Deadline | Prioridad |
|--------|-------------|----------|-----------|
| [Descripción clara] | [Nombre o "No asignado"] | [Fecha o "Por definir"] | [Alta/Media/Baja] |

INSTRUCCIONES:
- Incluye solo acciones concretas y realizables
- Si no hay responsable claro, indica "No asignado"
- Si no hay fecha, indica "Por definir"
- Evalúa la prioridad según el contexto

TRANSCRIPCIÓN:
""",

    "advanced_analysis_prompt": """Eres MIA, un asistente experto en análisis de reuniones.

Tu tarea es analizar la transcripción y proporcionar un análisis completo y estructurado.

FORMATO DE SALIDA REQUERIDO:

## RESUMEN
[Resumen ejecutivo de máximo 200 palabras con los puntos clave]

## ACCIONES
| Acción | Responsable | Deadline | Prioridad |
|--------|-------------|----------|-----------|
| [Acción 1] | [Nombre] | [Fecha] | [Alta/Media/Baja] |

## INSIGHTS
### Riesgos Identificados
- [Riesgo 1 con breve explicación]
- [Riesgo 2 con breve explicación]

### Oportunidades
- [Oportunidad 1 con potencial impacto]
- [Oportunidad 2 con potencial impacto]

### Recomendaciones
- [Recomendación 1 accionable]
- [Recomendación 2 accionable]

## ANALYTICS
- Duración estimada: [X minutos]
- Participantes detectados: [número y nombres si es posible]
- Tono general: [Positivo/Neutral/Negativo/Mixto]
- Nivel de consenso: [Alto/Medio/Bajo]
- Temas controversiales: [Sí/No - breve descripción si aplica]

## TEMAS PRINCIPALES
1. [Tema principal 1]
2. [Tema principal 2]
3. [Tema principal 3]
4. [Tema principal 4]
5. [Tema principal 5]

## PRÓXIMOS PASOS SUGERIDOS
1. [Paso 1 con timeline]
2. [Paso 2 con timeline]
3. [Paso 3 con timeline]

## TAGS
#tag1 #tag2 #tag3 #tag4 #tag5

---JSON_START---
{
  "summary": "resumen aquí",
  "actions": [
    {
      "action": "descripción clara de la acción",
      "responsible": "nombre del responsable",
      "deadline": "fecha límite",
      "priority": "Alta/Media/Baja"
    }
  ],
  "insights": {
    "risks": ["riesgo 1", "riesgo 2"],
    "opportunities": ["oportunidad 1", "oportunidad 2"],
    "recommendations": ["recomendación 1", "recomendación 2"]
  },
  "analytics": {
    "estimated_duration": "X minutos",
    "participants_count": 0,
    "participants_names": ["nombre1", "nombre2"],
    "general_tone": "Positivo/Neutral/Negativo/Mixto",
    "consensus_level": "Alto/Medio/Bajo",
    "controversial_topics": false,
    "key_decisions": ["decisión 1", "decisión 2"]
  },
  "main_topics": ["tema1", "tema2", "tema3", "tema4", "tema5"],
  "next_steps": [
    {"step": "descripción", "timeline": "cuando"},
    {"step": "descripción", "timeline": "cuando"}
  ],
  "tags": ["tag1", "tag2", "tag3", "tag4", "tag5"],
  "meeting_type": "Brainstorming/Planning/Review/Decision/Informative/Other"
}
---JSON_END---

IMPORTANTE:
- Sé preciso y objetivo
- Si no hay información suficiente para un campo, usa "(No especificado)" o valores por defecto
- No inventes información que no esté en la transcripción
- Prioriza la claridad y utilidad práctica

TRANSCRIPCIÓN:
""",

    # === TEMPLATES DE EXPORTACIÓN ===
    "export_templates": {
        "email_subject": "Resumen de Reunión: {title} - {date}",
        "email_body": """Estimado equipo,

Adjunto el resumen de la reunión "{title}" realizada el {date}.

**Resumen Ejecutivo:**
{summary}

**Acciones Acordadas:**
{actions}

**Próximos Pasos:**
{next_steps}

Saludos,
Meeting Assistant Pro
""",
        "slack_format": """*Reunión:* {title}
*Fecha:* {date}
*Duración:* {duration}

*Resumen:*
{summary}

*Acciones:*
{actions}

*Tags:* {tags}
"""
    },
    
    # === INTEGRACIONES ===
    "integrations": {
        "email": {
            "enabled": False,
            "smtp_server": "",
            "smtp_port": 587,
            "smtp_user": "",
            "smtp_password": "",
            "default_recipients": []
        },
        "slack": {
            "enabled": False,
            "webhook_url": "",
            "default_channel": "#general"
        },
        "calendar": {
            "enabled": False,
            "provider": "google",  # "google", "outlook", "ical"
            "sync_enabled": False
        }
    },
    
    # === CARACTERÍSTICAS EXPERIMENTALES ===
    "experimental_features": {
        "speaker_diarization": False,  # Identificación de hablantes
        "emotion_detection": False,  # Detección de emociones
        "auto_chapters": False,  # División automática en capítulos
        "video_recording": False,  # Grabación de video (futuro)
        "real_time_transcription": False,  # Transcripción en tiempo real
        "multi_language_meeting": False  # Soporte para reuniones multiidioma
    },
    
    # === MÉTRICAS Y ESTADÍSTICAS ===
    "metrics": {
        "track_usage": True,
        "track_performance": True,
        "anonymous_analytics": False,
        "export_metrics": True
    }
}

# Validadores de configuración
CONFIG_VALIDATORS = {
    "audio_quality": ["low", "medium", "high"],
    "ui_mode": ["floating", "classic"],
    "theme": ["dark", "light"],
    "language": ["es", "en"],
    "transcription_provider": ["local", "api"],
    "llm_provider": ["local", "api"],
    "api_provider": ["openai", "openrouter"],
    "whisper_model_size": ["tiny", "base", "small", "medium", "large"],
    "notification_position": ["top-right", "top-left", "bottom-right", "bottom-left"]
}

# Modelos disponibles por proveedor
AVAILABLE_MODELS = {
    "openai": [
        "gpt-4o",
        "gpt-4-turbo",
        "gpt-4",
        "gpt-3.5-turbo",
        "gpt-3.5-turbo-16k"
    ],
    "openrouter": [
        "openai/gpt-4",
        "anthropic/claude-3-opus",
        "anthropic/claude-3-sonnet",
        "google/gemini-pro",
        "meta-llama/llama-3-70b",
        "mistralai/mixtral-8x7b"
    ],
    "ollama": [
        "llama3",
        "llama2",
        "mistral",
        "mixtral",
        "codellama",
        "vicuna",
        "orca-mini"
    ]
}

# Idiomas soportados para Whisper
WHISPER_LANGUAGES = {
    "es": "Spanish",
    "en": "English", 
    "fr": "French",
    "de": "German",
    "it": "Italian",
    "pt": "Portuguese",
    "ru": "Russian",
    "ja": "Japanese",
    "ko": "Korean",
    "zh": "Chinese"
}

# Configuración de logging
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        },
        "detailed": {
            "format": "%(asctime)s [%(levelname)s] %(name)s:%(lineno)d: %(message)s"
        }
    },
    "handlers": {
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": str(LOGS_DIR / "meeting_assistant.log"),
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
            "formatter": "detailed"
        },
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard"
        }
    },
    "root": {
        "level": "INFO",
        "handlers": ["file", "console"]
    }
}
'''

# Guardar el archivo
with open('settings_improved.py', 'w', encoding='utf-8') as f:
    f.write(improved_settings)

print("✅ settings.py mejorado creado exitosamente")
print("\nCaracterísticas añadidas:")
print("- ✓ Configuración completa y estructurada")
print("- ✓ Prompts avanzados para análisis integral")
print("- ✓ Soporte para múltiples proveedores de API")
print("- ✓ Configuración de integraciones (Email, Slack, Calendar)")
print("- ✓ Atajos de teclado personalizables")
print("- ✓ Templates de exportación")
print("- ✓ Características experimentales")
print("- ✓ Validadores de configuración")
print("- ✓ Configuración de logging")