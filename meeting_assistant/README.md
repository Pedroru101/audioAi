# Meeting Assistant Pro (MIA) 🎙️

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)

## 📋 Descripción

Meeting Assistant Pro es una aplicación de escritorio avanzada para la grabación, transcripción y análisis inteligente de reuniones. Utiliza tecnología de IA para generar resúmenes ejecutivos, extraer puntos clave y crear tareas accionables automáticamente.

## ✨ Características Principales

### 🎯 Funcionalidades Core
- **Grabación de Audio**: Captura de audio de alta calidad con detección automática de silencio
- **Transcripción Automática**: Conversión de voz a texto con alta precisión
- **Análisis con IA**: Procesamiento inteligente usando modelos de lenguaje avanzados
- **Resúmenes Ejecutivos**: Generación automática de resúmenes concisos
- **Extracción de Acciones**: Identificación de tareas y responsables
- **Gestión de Reuniones**: Organización y búsqueda eficiente de reuniones pasadas

### 🎨 Interfaces de Usuario
- **UI Flotante**: Interfaz minimalista para grabación rápida
- **UI Clásica**: Interfaz tradicional con todas las funciones
- **UI Moderna**: Diseño contemporáneo con animaciones fluidas
- **Historial Completo**: Vista detallada de todas las reuniones con analytics

### 📊 Analytics y Reportes
- Métricas de productividad
- Análisis de tendencias
- Visualización de datos
- Exportación en múltiples formatos

## 🚀 Instalación

### Requisitos Previos
- Python 3.8 o superior
- Windows 10/11, macOS 10.14+, o Linux (Ubuntu 20.04+)
- Micrófono funcional

### Instalación Rápida

1. **Clonar el repositorio**
   ```bash
   git clone https://github.com/yourusername/meeting-assistant-pro.git
   cd meeting-assistant-pro
   ```

2. **Crear entorno virtual**
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```

3. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements_ui.txt
   ```

4. **Ejecutar la aplicación**
   ```bash
   python main.py
   ```

### Instalación con Ejecutable (Windows)

Descarga el instalador desde [Releases](https://github.com/yourusername/meeting-assistant-pro/releases) y ejecuta `MeetingAssistantPro_Setup_1.0.0.exe`

## 📖 Uso

### Primera Ejecución

1. Al iniciar por primera vez, se abrirá el asistente de configuración
2. Configura tu clave API para el servicio de transcripción
3. Selecciona tu interfaz preferida
4. Ajusta las preferencias de audio

### Grabación de Reuniones

1. **Iniciar Grabación**: Clic en el botón de grabación o usa el atajo `Ctrl+R`
2. **Durante la Reunión**: El indicador mostrará el estado de grabación
3. **Finalizar**: Clic en detener o usa `Ctrl+S`
4. **Procesamiento**: La aplicación transcribirá y analizará automáticamente

### Gestión de Reuniones

- **Ver Historial**: Accede a todas tus reuniones desde el menú principal
- **Buscar**: Usa la barra de búsqueda para encontrar reuniones específicas
- **Exportar**: Exporta reuniones individuales o múltiples en varios formatos
- **Analytics**: Visualiza estadísticas y tendencias en el panel de analytics

## ⚙️ Configuración

### Archivo de Configuración

La configuración se almacena en `config/settings.json`:

```json
{
  "audio": {
    "sample_rate": 16000,
    "channels": 1,
    "chunk_size": 1024
  },
  "transcription": {
    "service": "whisper",
    "model": "base",
    "language": "es"
  },
  "ui": {
    "theme": "dark",
    "start_minimized": false,
    "always_on_top": true
  }
}
```

### Variables de Entorno

```bash
# API Keys
OPENAI_API_KEY=tu_clave_api
ANTHROPIC_API_KEY=tu_clave_api

# Configuración de desarrollo
MIA_DEBUG=true
MIA_LOG_LEVEL=DEBUG
```

## 🛠️ Desarrollo

### Estructura del Proyecto

```
meeting_assistant/
├── ai/                    # Módulos de IA
├── audio/                 # Grabación y transcripción
├── config/                # Configuración
├── ui/                    # Interfaces de usuario
├── utils/                 # Utilidades
├── data/                  # Datos de la aplicación
└── main.py               # Punto de entrada
```

### Construir desde Código

```bash
# Construir ejecutable
python build.py

# Construir con debug
python build.py --debug

# Limpiar archivos de construcción
python build.py --clean
```

### Ejecutar Tests

```bash
# Todos los tests
pytest

# Tests específicos
pytest tests/test_audio.py

# Con cobertura
pytest --cov=meeting_assistant
```

## 🤝 Contribuir

1. Fork el proyecto
2. Crea tu rama de características (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

### Guía de Estilo

- Seguir PEP 8 para Python
- Documentar todas las funciones públicas
- Incluir tests para nuevas características
- Actualizar la documentación según sea necesario

## 📝 Licencia

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

## 🙏 Agradecimientos

- OpenAI Whisper por la tecnología de transcripción
- PyQt5 por el framework de UI
- Todos los contribuidores del proyecto

## 📞 Soporte

- **Issues**: [GitHub Issues](https://github.com/yourusername/meeting-assistant-pro/issues)
- **Discusiones**: [GitHub Discussions](https://github.com/yourusername/meeting-assistant-pro/discussions)
- **Email**: support@meetingassistantpro.com

## 🗺️ Roadmap

### Version 1.1
- [ ] Soporte para múltiples idiomas simultáneos
- [ ] Integración con calendarios (Google, Outlook)
- [ ] Grabación de pantalla sincronizada

### Version 1.2
- [ ] Colaboración en tiempo real
- [ ] API REST para integraciones
- [ ] Aplicación móvil complementaria

### Version 2.0
- [ ] Análisis de sentimientos
- [ ] Detección automática de participantes
- [ ] Generación de presentaciones automáticas

---

Desarrollado con ❤️ por el equipo de MIA Development
