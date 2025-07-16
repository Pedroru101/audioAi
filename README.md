# Meeting Assistant

![Versión](https://img.shields.io/badge/versión-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![Plataforma](https://img.shields.io/badge/plataforma-Windows-lightgrey)

Asistente de reuniones que captura audio, transcribe y genera resúmenes con IA. Incluye interfaz flotante y modo clásico.

## 🌟 Características

- 🎙️ Grabación de audio bidireccional
- ✍ Transcripción en tiempo real
- 📝 Generación de resúmenes con IA
- 🎨 Interfaz moderna con temas oscuros
- 🪟 Modos flotante y clásico
- ⚙️ Configuración personalizable

## 🏗️ Estructura del Proyecto

```
meeting_assistant/
│
├── audio/                  # Módulo de procesamiento de audio
│   ├── recorder.py         # Grabación de audio desde micrófono/sistema
│   ├── transcriber.py      # Transcripción de audio a texto
│   └── utils.py            # Utilidades de audio
│
├── config/                 # Configuración de la aplicación
│   ├── config_manager.py   # Gestor de configuración
│   └── settings.py         # Configuración por defecto
│
├── ui/                     # Interfaz de usuario
│   ├── classic_ui.py       # Interfaz de ventana clásica
│   ├── components/         # Componentes UI reutilizables
│   ├── config_ui.py        # Panel de configuración
│   ├── floating_ui.py      # Interfaz flotante
│   ├── history_ui.py       # Historial de reuniones
│   └── styles.py           # Estilos y temas
│
├── utils/                  # Utilidades generales
│   ├── file_manager.py     # Gestión de archivos
│   └── notifications.py    # Notificaciones del sistema
│
└── main.py                # Punto de entrada principal
```

## 🛠️ Instalación

1. Clona el repositorio
2. Instala dependencias:
   ```bash
   pip install -r requirements.txt
   ```
3. Ejecuta:
   ```bash
   python -m meeting_assistant.main
   ```

## 📝 Requisitos

- Python 3.8+
- Windows 10/11
- Micrófono (opcional para grabación de voz)

## 📄 Licencia

MIT License - ver [LICENSE](LICENSE) para más detalles.
