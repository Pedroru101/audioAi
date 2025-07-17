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
from utils.error_manager import ErrorManager
from utils.auto_updater import AutoUpdater  # Asume tu versión existente; fusioné con la mía abajo
from ui.floating_ui import FloatingUI
from ui.classic_ui import ClassicUI
from ui.modern_ui import ModernUI
from ui.config_ui import ConfigUI
from ui.history_ui import MeetingHistoryWidget
from audio.recorder import AudioRecorder
from audio.transcriber import AudioTranscriber
from ai.llm_processor import LLMProcessor

# Nuevos imports para Fase 9 (agrega deps: plyer, pynput, requests)
import requests
import shutil
import zipfile
import platform
import ctypes
from plyer import notification
from pynput import keyboard
import tkinter as tk

# Versión de la aplicación
APP_VERSION = "1.0.0"

class MeetingAssistantApp:
    """Aplicación principal de Meeting Assistant Pro"""

    def __init__(self):
        # Inicializar error manager
        self.error_manager = ErrorManager()
        self.error_manager.log_info(f"Iniciando Meeting Assistant Pro v{APP_VERSION}")

        # Configuración
        self.settings = QSettings('MeetingAssistantPro', 'MIA')
        self.config_manager = ConfigManager()
        self.file_manager = FileManager(self.config_manager)

        # Componentes principales
        self.audio_recorder = AudioRecorder(self.config_manager, self.file_manager)
        self.transcriber = AudioTranscriber(self.config_manager)
        self.llm_processor = LLMProcessor(self.config_manager)

        # Auto-updater (fusionado con tu versión existente)
        self.updater = AutoUpdater(self.config_manager, self.file_manager)
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

    @ErrorManager.handle_errors()
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

        # Setup adicionales de Fase 9
        self.setup_startup()  # Inicio con sistema
        self.setup_hotkeys()  # Hotkeys globales

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
        """Configura el icono de la bandeja del sistema (extendido para Fase 9)"""
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

        # Crear menú (extendido con opciones rápidas)
        tray_menu = QMenu()

        # Acciones del menú
        show_action = QAction("Mostrar", self.tray_icon)
        show_action.triggered.connect(self.show_main_window)
        tray_menu.addAction(show_action)

        tray_menu.addSeparator()

        record_action = QAction("Nueva Grabación", self.tray_icon)
        record_action.triggered.connect(lambda: self.start_recording())
        tray_menu.addAction(record_action)

        history_action = QAction("Historial", self.tray_icon)
        history_action.triggered.connect(lambda checked: self.open_history_window())
        tray_menu.addAction(history_action)

        tray_menu.addSeparator()

        config_action = QAction("Configuración", self.tray_icon)
        config_action.triggered.connect(self.open_config_dialog)
        tray_menu.addAction(config_action)

        update_action = QAction("Buscar Actualizaciones", self.tray_icon)
        update_action.triggered.connect(lambda: self.updater.check_for_updates(silent=False))
        tray_menu.addAction(update_action)

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
        # Crear UI flotante
        # Iniciar ventana tkinter para FloatingUI
        self.tk_root = tk.Tk()
        # Integrar bucle de eventos tkinter en el bucle de Qt
        self.tk_timer = QTimer()
        self.tk_timer.timeout.connect(self.tk_root.update)
        self.tk_timer.start(50)
        self.floating_ui = FloatingUI(self.tk_root, self.start_recording, self.open_config_dialog, self.quit_application)

        # Crear UI principal según preferencia
        if self.preferred_ui == 'classic':
            self.main_ui = ClassicUI(self)
        elif self.preferred_ui == 'modern':
            self.main_ui = ModernUI(self)
        else:
            # Por defecto usar la flotante como principal
            self.main_ui = self.floating_ui

        # Mostrar UI principal
        self.main_ui.show()

    def show_main_window(self):
        """Muestra la ventana principal"""
        if self.main_ui:
            # Si es UI flotante (tkinter), solo mostrarla
            if isinstance(self.main_ui, FloatingUI):
                self.main_ui.show()
            else:
                # Qt UIs
                self.main_ui.show()
                self.main_ui.raise_()
                self.main_ui.activateWindow()

    @ErrorManager.handle_errors()
    def start_recording(self):
        """Inicia una nueva grabación"""
        if self.is_recording:
            self.error_manager.log_warning("Ya hay una grabación en curso")
            return

        try:
            # Crear nueva reunión
            self.current_meeting_id = self.file_manager.create_meeting_folder()

            # Leer flags de configuración
            config = self.config_manager.get_config()
            record_mic = config.get("record_microphone", True)
            record_sys = config.get("record_system_audio", True)
            # Actualizar UI de fuentes de audio antes de iniciar grabación
            if self.main_ui and hasattr(self.main_ui, 'set_audio_sources'):
                self.main_ui.set_audio_sources(record_mic, record_sys)

            # Iniciar grabación respetando flags
            self.audio_recorder.start_recording(record_input=record_mic, record_output=record_sys)
            self.is_recording = True

            # Actualizar UI
            if self.floating_ui:
                self.floating_ui.update_recording_state(True)
            if self.main_ui and self.main_ui != self.floating_ui:
                self.main_ui.update_recording_state(True)

            self.error_manager.log_info(f"Grabación iniciada: {self.current_meeting_id}")

            # Notificación nativa (Fase 9)
            notification.notify(title="Grabación Iniciada", message="Reunión en curso.")

        except Exception as e:
            self.error_manager.log_error(f"Error al iniciar grabación: {str(e)}")
            raise

    @ErrorManager.handle_errors()
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

            # Notificación nativa (Fase 9)
            notification.notify(title="Grabación Detenida", message="Procesando reunión.")

        except Exception as e:
            self.error_manager.log_error(f"Error al detener grabación: {str(e)}")
            raise

    @ErrorManager.handle_errors()
    def process_recording(self, audio_file: str, meeting_id: str):
        """Procesa la grabación"""
        try:
            # Transcribir
            self.update_status("Transcribiendo audio...")
            transcription = self.transcriber.transcribe(audio_file)

            # Guardar transcripción
            self.file_manager.save_text_file(meeting_id, "transcripcion.txt", transcription)

            # Generar y guardar resumen
            config = self.config_manager.get_config()
            if config.get("generate_summary", True):
                self.update_status("Generando resumen...")
                summary = self.llm_processor.generate_summary(transcription)
                self.file_manager.save_text_file(meeting_id, "resumen.md", summary)

            # Generar y guardar propuestas de acción
            if config.get("generate_actions", True):
                self.update_status("Generando propuestas de acción...")
                actions = self.llm_processor.generate_actions(transcription)
                if not actions.strip():
                    actions = "No se encontraron acciones en la transcripción."
                self.file_manager.save_text_file(meeting_id, "acciones.txt", actions)

            self.update_status("Procesamiento completado")

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
            # Crear diálogo de configuración en tkinter
            dialog_root = tk.Toplevel(self.tk_root)
            self.config_dialog = ConfigUI(dialog_root, self.config_manager, on_close=self._on_config_close)
        else:
            # Traer ventana existente al frente
            self.config_dialog.root.deiconify()
            self.config_dialog.root.lift()

    def _on_config_close(self):
        """Callback al cerrar diálogo de configuración."""
        self.config_dialog = None

    @ErrorManager.handle_errors()
    def open_history_window(self, show_window=True):
        """Abre la ventana de historial
        
        Args:
            show_window: Si es True, muestra la ventana después de crearla
        """
        if not self.history_window or not self.history_window.isVisible():
            self.history_window = MeetingHistoryWidget(
                self.config_manager,
                self.file_manager
            )

        if show_window:
            self.history_window.show()
            self.history_window.raise_()
        
        return self.history_window

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

    # Nuevas funciones de Fase 9 fusionadas

    def minimize_to_tray(self):
        """Minimizar a tray (oculta ventana principal)"""
        if self.main_ui:
            self.main_ui.hide()
        if self.floating_ui and self.floating_ui != self.main_ui:
            self.floating_ui.hide()
        notification.notify(title="Minimizado", message="Meeting Assistant Pro está en la bandeja.")

    def setup_startup(self):
        """Inicio con el sistema (Fase 9)"""
        if self.start_with_windows and platform.system() == 'Windows':
            app_path = sys.executable
            ctypes.windll.shell32.ShellExecuteW(None, "runas", "schtasks", f'/create /tn "MeetingAssistantPro" /tr "{app_path}" /sc onlogon', '', 1)
        # Agrega lógica para Mac/Linux si es necesario

    def setup_hotkeys(self):
        """Hotkeys globales (Fase 9, ej: Ctrl+Alt+R para grabar)"""
        def on_activate():
            self.start_recording()

        listener = keyboard.GlobalHotKeys({'<ctrl>+<alt>+r': on_activate})
        listener.start()  # Inicia el listener en background

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

    

    # Crear ventana principal
    meeting_assistant = MeetingAssistantApp()
    meeting_assistant.show_main_window()  # Asegurar que la ventana principal se muestre

    # Ejecutar
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()