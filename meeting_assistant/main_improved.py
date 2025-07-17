"""
Meeting Assistant Pro - Aplicación Principal
Version: 1.0.0
"""

import sys
import os
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction
from PyQt5.QtCore import Qt, QSettings, QTimer
from PyQt5.QtGui import QIcon

# Importar módulos del proyecto
from config.config_manager import ConfigManager
from config.settings import *
from utils.file_manager import FileManager
from utils.error_handler import get_error_manager, error_handler
from utils.auto_updater import AutoUpdater
from ui.floating_ui import FloatingUI
from ui.classic_ui import ClassicUI
from ui.modern_ui import ModernUI
from ui.config_ui import ConfigDialog
from ui.history_ui import MeetingHistoryWidget
from audio.recorder import AudioRecorder
from audio.transcriber import AudioTranscriber
from ai.llm_processor import LLMProcessor

# Versión de la aplicación
APP_VERSION = "1.0.0"

class MeetingAssistantApp:
    """Aplicación principal de Meeting Assistant Pro"""

    def __init__(self):
        # Inicializar error manager
        self.error_manager = get_error_manager()
        self.error_manager.log_info(f"Iniciando Meeting Assistant Pro v{APP_VERSION}")

        # Configuración
        self.settings = QSettings('MeetingAssistantPro', 'MIA')
        self.config_manager = ConfigManager()
        self.file_manager = FileManager(self.config_manager)

        # Componentes principales
        self.audio_recorder = AudioRecorder(self.config_manager)
        self.transcriber = AudioTranscriber(self.config_manager)
        self.llm_processor = LLMProcessor(self.config_manager)

        # Auto-updater
        self.updater = AutoUpdater(APP_VERSION)
        self.updater.schedule_update_check(interval_hours=24)

        # Interfaces
        self.floating_ui = None
        self.main_ui = None
        self.config_dialog = None
        self.history_window = None

        # System tray
        self.tray_icon = None

        # Estado
        self.is_recording = False
        self.current_meeting_id = None

        # Inicializar
        self.setup_application()

    @error_handler
    def setup_application(self):
        """Configura la aplicación"""
        # Crear directorios necesarios
        self.create_directories()

        # Cargar configuración
        self.load_settings()

        # Configurar system tray
        self.setup_system_tray()

        # Inicializar UI según preferencias
        self.initialize_ui()

        # Verificar actualizaciones al inicio
        QTimer.singleShot(5000, lambda: self.updater.check_for_updates(silent=True))

        self.error_manager.log_info("Aplicación iniciada correctamente")

    def create_directories(self):
        """Crea los directorios necesarios"""
        directories = [
            'data/meetings',
            'data/logs',
            'data/temp',
            'data/backups',
            'config',
            'assets'
        ]

        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)

    def load_settings(self):
        """Carga la configuración guardada"""
        # UI preferida
        self.preferred_ui = self.settings.value('preferred_ui', 'floating')

        # Inicio con Windows
        self.start_with_windows = self.settings.value('start_with_windows', False, type=bool)

        # Minimizar a bandeja
        self.minimize_to_tray = self.settings.value('minimize_to_tray', True, type=bool)

        # Tema
        self.theme = self.settings.value('theme', 'dark')

    def save_settings(self):
        """Guarda la configuración"""
        self.settings.setValue('preferred_ui', self.preferred_ui)
        self.settings.setValue('start_with_windows', self.start_with_windows)
        self.settings.setValue('minimize_to_tray', self.minimize_to_tray)
        self.settings.setValue('theme', self.theme)

    def setup_system_tray(self):
        """Configura el icono de la bandeja del sistema"""
        if not QSystemTrayIcon.isSystemTrayAvailable():
            return

        # Crear icono
        icon_path = Path('assets/icon.png')
        if not icon_path.exists():
            # Usar icono por defecto si no existe
            self.tray_icon = QSystemTrayIcon(QApplication.style().standardIcon(
                QApplication.style().SP_ComputerIcon
            ))
        else:
            self.tray_icon = QSystemTrayIcon(QIcon(str(icon_path)))

        # Crear menú
        tray_menu = QMenu()

        # Acciones del menú
        show_action = QAction("Mostrar", self.tray_icon)
        show_action.triggered.connect(self.show_main_window)
        tray_menu.addAction(show_action)

        tray_menu.addSeparator()

        record_action = QAction("Nueva Grabación", self.tray_icon)
        record_action.triggered.connect(self.start_recording)
        tray_menu.addAction(record_action)

        history_action = QAction("Historial", self.tray_icon)
        history_action.triggered.connect(self.open_history_window)
        tray_menu.addAction(history_action)

        tray_menu.addSeparator()

        config_action = QAction("Configuración", self.tray_icon)
        config_action.triggered.connect(self.open_config_dialog)
        tray_menu.addAction(config_action)

        tray_menu.addSeparator()

        exit_action = QAction("Salir", self.tray_icon)
        exit_action.triggered.connect(self.quit_application)
        tray_menu.addAction(exit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.setToolTip("Meeting Assistant Pro")

        # Doble clic para mostrar
        self.tray_icon.activated.connect(self.tray_icon_activated)

        # Mostrar
        self.tray_icon.show()

    def tray_icon_activated(self, reason):
        """Maneja la activación del icono de bandeja"""
        if reason == QSystemTrayIcon.DoubleClick:
            self.show_main_window()

    def initialize_ui(self):
        """Inicializa la interfaz de usuario"""
        # Siempre crear la UI flotante
        self.floating_ui = FloatingUI(self)

        # Crear UI principal según preferencia
        if self.preferred_ui == 'classic':
            self.main_ui = ClassicUI(self)
        elif self.preferred_ui == 'modern':
            self.main_ui = ModernUI(self)
        else:
            # Por defecto usar la flotante como principal
            self.main_ui = self.floating_ui

        # Mostrar UI
        if self.preferred_ui == 'floating':
            self.floating_ui.show()
        else:
            self.main_ui.show()

    def show_main_window(self):
        """Muestra la ventana principal"""
        if self.main_ui:
            self.main_ui.show()
            self.main_ui.raise_()
            self.main_ui.activateWindow()

    @error_handler
    def start_recording(self):
        """Inicia una nueva grabación"""
        if self.is_recording:
            self.error_manager.log_warning("Ya hay una grabación en curso")
            return

        try:
            # Crear nueva reunión
            self.current_meeting_id = self.file_manager.create_meeting_folder()

            # Iniciar grabación
            self.audio_recorder.start_recording()
            self.is_recording = True

            # Actualizar UI
            if self.floating_ui:
                self.floating_ui.update_recording_state(True)
            if self.main_ui and self.main_ui != self.floating_ui:
                self.main_ui.update_recording_state(True)

            self.error_manager.log_info(f"Grabación iniciada: {self.current_meeting_id}")

        except Exception as e:
            self.error_manager.log_error(f"Error al iniciar grabación: {str(e)}")
            raise

    @error_handler
    def stop_recording(self):
        """Detiene la grabación actual"""
        if not self.is_recording:
            return

        try:
            # Detener grabación
            audio_file = self.audio_recorder.stop_recording()
            self.is_recording = False

            # Actualizar UI
            if self.floating_ui:
                self.floating_ui.update_recording_state(False)
            if self.main_ui and self.main_ui != self.floating_ui:
                self.main_ui.update_recording_state(False)

            # Procesar audio
            if audio_file and self.current_meeting_id:
                self.process_recording(audio_file, self.current_meeting_id)

            self.error_manager.log_info(f"Grabación detenida: {self.current_meeting_id}")

        except Exception as e:
            self.error_manager.log_error(f"Error al detener grabación: {str(e)}")
            raise

    @error_handler
    def process_recording(self, audio_file: str, meeting_id: str):
        """Procesa la grabación"""
        try:
            # Transcribir
            self.update_status("Transcribiendo audio...")
            transcription = self.transcriber.transcribe(audio_file)

            # Procesar con LLM
            self.update_status("Analizando contenido...")
            analysis = self.llm_processor.process_transcription(transcription)

            # Guardar resultados
            self.update_status("Guardando resultados...")
            self.file_manager.save_meeting_data(meeting_id, {
                'audio_file': audio_file,
                'transcription': transcription,
                'analysis': analysis
            })

            self.update_status("Procesamiento completado")

            # Notificar finalización
            if self.tray_icon:
                self.tray_icon.showMessage(
                    "Meeting Assistant Pro",
                    "Reunión procesada exitosamente",
                    QSystemTrayIcon.Information,
                    3000
                )

        except Exception as e:
            self.error_manager.log_error(f"Error procesando grabación: {str(e)}")
            self.update_status(f"Error: {str(e)}")
            raise

    def update_status(self, message: str):
        """Actualiza el estado en todas las UIs"""
        if self.floating_ui:
            self.floating_ui.update_status(message)
        if self.main_ui and self.main_ui != self.floating_ui:
            self.main_ui.update_status(message)

    def open_config_dialog(self):
        """Abre el diálogo de configuración"""
        if not self.config_dialog:
            self.config_dialog = ConfigDialog(self.config_manager, parent=self.main_ui)

        self.config_dialog.show()
        self.config_dialog.raise_()

    def open_history_window(self):
        """Abre la ventana de historial"""
        if not self.history_window or not self.history_window.isVisible():
            self.history_window = MeetingHistoryWidget(
                self.config_manager,
                self.file_manager
            )

        self.history_window.show()
        self.history_window.raise_()

    def switch_ui(self, ui_type: str):
        """Cambia el tipo de interfaz"""
        self.preferred_ui = ui_type
        self.save_settings()

        # Cerrar UI actual
        if self.main_ui:
            self.main_ui.close()

        # Crear nueva UI
        if ui_type == 'classic':
            self.main_ui = ClassicUI(self)
        elif ui_type == 'modern':
            self.main_ui = ModernUI(self)
        else:
            self.main_ui = self.floating_ui

        self.main_ui.show()

    def quit_application(self):
        """Cierra la aplicación"""
        # Detener grabación si está activa
        if self.is_recording:
            self.stop_recording()

        # Guardar configuración
        self.save_settings()

        # Limpiar
        if self.tray_icon:
            self.tray_icon.hide()

        # Log de cierre
        self.error_manager.log_info("Aplicación cerrada por el usuario")

        # Salir
        QApplication.quit()


def main():
    """Función principal"""
    # Configurar para DPI alto
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    # Crear aplicación
    app = QApplication(sys.argv)
    app.setApplicationName("Meeting Assistant Pro")
    app.setApplicationDisplayName("Meeting Assistant Pro")
    app.setOrganizationName("MIA Development Team")

    # Verificar instancia única
    if app.isRunning():
        print("La aplicación ya está en ejecución")
        sys.exit(1)

    # Crear ventana principal
    meeting_assistant = MeetingAssistantApp()

    # Ejecutar
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
