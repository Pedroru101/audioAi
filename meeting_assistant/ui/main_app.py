"""
Aplicación principal de Meeting Assistant Pro
Integra todas las interfaces y componentes
"""
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import sys
import os
import threading
import json
from datetime import datetime

# Importar componentes del proyecto
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ui.modern_ui import ModernUI, FloatingWidget
from ui.animated_components import FloatingNotification, LoadingSpinner
from ui.config_ui import ConfigUI
from ui.history_ui import HistoryUI

from audio.audio_capture import AudioCapture
from ai.transcriber import Transcriber
from ai.llm_processor import LLMProcessor
from ai.meeting_processor import MeetingProcessor
from utils.config_manager import ConfigManager
from utils.file_manager import FileManager

class MeetingAssistantApp:
    """Aplicación principal que coordina todos los componentes"""

    def __init__(self):
        # Inicializar configuración
        self.config_manager = ConfigManager()
        self.config = self.config_manager.get_config()

        # Inicializar componentes
        self.audio_capture = None
        self.transcriber = None
        self.llm_processor = None
        self.meeting_processor = None
        self.file_manager = FileManager(self.config.get('save_path', './recordings'))

        # Estado de la aplicación
        self.is_recording = False
        self.current_session = None
        self.ui_mode = self.config.get('ui_mode', 'modern')

        # Inicializar UI
        self.setup_ui()

    def setup_ui(self):
        """Configura la interfaz de usuario"""
        # Crear ventana principal
        self.main_ui = ModernUI(
            on_record=self.start_recording,
            on_stop=self.stop_recording,
            on_config=self.open_config,
            on_history=self.open_history
        )

        # Crear widget flotante opcional
        if self.config.get('enable_floating_widget', True):
            self.floating_widget = FloatingWidget(
                self.main_ui,
                on_record_toggle=self.toggle_recording
            )

        # Inicializar componentes de procesamiento
        self.initialize_processors()

    def initialize_processors(self):
        """Inicializa los procesadores de audio y AI"""
        try:
            # Audio capture
            self.audio_capture = AudioCapture(
                input_device=self.config.get('audio_input_device'),
                output_device=self.config.get('audio_output_device')
            )

            # Transcriber
            self.transcriber = Transcriber(
                model_size=self.config.get('whisper_model', 'base'),
                device=self.config.get('device', 'cpu')
            )

            # LLM Processor
            self.llm_processor = LLMProcessor(self.config)

            # Meeting Processor
            self.meeting_processor = MeetingProcessor(
                self.transcriber,
                self.llm_processor,
                self.config
            )

        except Exception as e:
            self.show_error(f"Error al inicializar componentes: {str(e)}")

    def start_recording(self):
        """Inicia la grabación de audio"""
        if self.is_recording:
            return

        try:
            # Crear nueva sesión
            self.current_session = {
                'id': datetime.now().strftime('%Y%m%d_%H%M%S'),
                'start_time': datetime.now(),
                'audio_file': None,
                'transcription': None,
                'summary': None,
                'action_items': None
            }

            # Iniciar captura de audio
            audio_file = self.file_manager.get_audio_path(self.current_session['id'])
            self.audio_capture.start_recording(audio_file)
            self.current_session['audio_file'] = audio_file

            self.is_recording = True

            # Mostrar notificación
            self.show_notification("Grabación iniciada", "success")

        except Exception as e:
            self.show_error(f"Error al iniciar grabación: {str(e)}")

    def stop_recording(self):
        """Detiene la grabación y procesa el audio"""
        if not self.is_recording:
            return

        try:
            # Detener grabación
            self.audio_capture.stop_recording()
            self.is_recording = False

            # Mostrar spinner de carga
            self.show_loading("Procesando grabación...")

            # Procesar en thread separado
            threading.Thread(
                target=self.process_recording,
                daemon=True
            ).start()

        except Exception as e:
            self.show_error(f"Error al detener grabación: {str(e)}")

    def process_recording(self):
        """Procesa la grabación completa"""
        try:
            # Procesar con MeetingProcessor
            results = self.meeting_processor.process_meeting(
                self.current_session['audio_file']
            )

            # Actualizar sesión
            self.current_session.update(results)

            # Guardar resultados
            self.file_manager.save_session(self.current_session)

            # Actualizar UI en el thread principal
            self.main_ui.after(0, self.update_results, results)

        except Exception as e:
            self.main_ui.after(0, self.show_error, f"Error al procesar: {str(e)}")
        finally:
            self.main_ui.after(0, self.hide_loading)

    def update_results(self, results):
        """Actualiza la UI con los resultados del procesamiento"""
        # Actualizar transcripción
        if results.get('transcription'):
            self.main_ui.set_transcription(results['transcription'])

        # Actualizar resumen
        if results.get('summary'):
            self.main_ui.set_summary(results['summary'])

        # Actualizar action items
        if results.get('action_items'):
            for action in results['action_items']:
                self.main_ui.add_action_item(action)

        # Mostrar notificación de éxito
        self.show_notification("Procesamiento completado", "success")

    def toggle_recording(self):
        """Alterna entre iniciar y detener grabación"""
        if self.is_recording:
            self.stop_recording()
        else:
            self.start_recording()

    def open_config(self):
        """Abre la ventana de configuración"""
        config_window = ctk.CTkToplevel(self.main_ui)
        ConfigUI(
            config_window,
            self.config_manager,
            on_close=self.on_config_close
        )

    def on_config_close(self):
        """Callback cuando se cierra la configuración"""
        # Recargar configuración
        self.config = self.config_manager.get_config()

        # Reinicializar procesadores si es necesario
        self.initialize_processors()

        self.show_notification("Configuración actualizada", "info")

    def open_history(self):
        """Abre la ventana de historial"""
        history_window = ctk.CTkToplevel(self.main_ui)
        history_window.title("Historial de Reuniones")
        history_window.geometry("800x600")

        # Crear frame para el historial
        history_frame = ctk.CTkFrame(history_window)
        history_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Título
        title = ctk.CTkLabel(
            history_frame,
            text="Historial de Reuniones",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(pady=(0, 20))

        # Lista de sesiones
        sessions = self.file_manager.list_sessions()

        if not sessions:
            empty_label = ctk.CTkLabel(
                history_frame,
                text="No hay reuniones grabadas",
                font=ctk.CTkFont(size=14),
                text_color=("gray60", "gray40")
            )
            empty_label.pack(pady=50)
        else:
            # Crear lista scrollable
            scrollable_frame = ctk.CTkScrollableFrame(history_frame)
            scrollable_frame.pack(fill="both", expand=True)

            for session in sessions:
                self.create_history_item(scrollable_frame, session)

    def create_history_item(self, parent, session):
        """Crea un item en el historial"""
        # Frame para el item
        item_frame = ctk.CTkFrame(parent)
        item_frame.pack(fill="x", padx=5, pady=5)

        # Información de la sesión
        info_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
        info_frame.pack(side="left", fill="x", expand=True, padx=10, pady=10)

        # Fecha y hora
        date_label = ctk.CTkLabel(
            info_frame,
            text=session.get('start_time', 'Fecha desconocida'),
            font=ctk.CTkFont(size=14, weight="bold")
        )
        date_label.pack(anchor="w")

        # Duración
        duration_label = ctk.CTkLabel(
            info_frame,
            text=f"Duración: {session.get('duration', 'N/A')}",
            font=ctk.CTkFont(size=12),
            text_color=("gray70", "gray30")
        )
        duration_label.pack(anchor="w")

        # Botones de acción
        action_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
        action_frame.pack(side="right", padx=10)

        # Botón ver
        view_btn = ctk.CTkButton(
            action_frame,
            text="Ver",
            width=80,
            command=lambda: self.view_session(session)
        )
        view_btn.pack(side="left", padx=2)

        # Botón exportar
        export_btn = ctk.CTkButton(
            action_frame,
            text="Exportar",
            width=80,
            fg_color="transparent",
            border_width=1,
            command=lambda: self.export_session(session)
        )
        export_btn.pack(side="left", padx=2)

    def view_session(self, session):
        """Muestra los detalles de una sesión"""
        # Cargar datos de la sesión
        session_data = self.file_manager.load_session(session['id'])

        if session_data:
            # Actualizar UI con los datos
            self.update_results(session_data)
            self.show_notification("Sesión cargada", "info")

    def export_session(self, session):
        """Exporta una sesión"""
        from tkinter import filedialog

        filename = filedialog.asksaveasfilename(
            title="Exportar sesión",
            defaultextension=".json",
            filetypes=[
                ("JSON files", "*.json"),
                ("Text files", "*.txt"),
                ("Markdown files", "*.md")
            ]
        )

        if filename:
            session_data = self.file_manager.load_session(session['id'])

            if filename.endswith('.json'):
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(session_data, f, indent=2, ensure_ascii=False)
            elif filename.endswith('.md'):
                self.export_as_markdown(session_data, filename)
            else:
                self.export_as_text(session_data, filename)

            self.show_notification("Sesión exportada", "success")

    def export_as_markdown(self, session_data, filename):
        """Exporta la sesión como Markdown"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"# Reunión - {session_data.get('start_time', 'Fecha desconocida')}\n\n")
            f.write(f"## Transcripción\n\n{session_data.get('transcription', 'N/A')}\n\n")
            f.write(f"## Resumen\n\n{session_data.get('summary', 'N/A')}\n\n")
            f.write(f"## Acciones\n\n")
            for action in session_data.get('action_items', []):
                f.write(f"- [ ] {action}\n")

    def export_as_text(self, session_data, filename):
        """Exporta la sesión como texto plano"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"REUNIÓN - {session_data.get('start_time', 'Fecha desconocida')}\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"TRANSCRIPCIÓN:\n{session_data.get('transcription', 'N/A')}\n\n")
            f.write(f"RESUMEN:\n{session_data.get('summary', 'N/A')}\n\n")
            f.write("ACCIONES:\n")
            for action in session_data.get('action_items', []):
                f.write(f"- {action}\n")

    def show_notification(self, message, notification_type="info"):
        """Muestra una notificación flotante"""
        FloatingNotification(
            self.main_ui,
            message,
            notification_type=notification_type
        )

    def show_error(self, message):
        """Muestra un mensaje de error"""
        messagebox.showerror("Error", message)

    def show_loading(self, message):
        """Muestra indicador de carga"""
        self.loading_window = ctk.CTkToplevel(self.main_ui)
        self.loading_window.title("")
        self.loading_window.geometry("300x150")
        self.loading_window.resizable(False, False)

        # Centrar ventana
        self.loading_window.update_idletasks()
        x = (self.loading_window.winfo_screenwidth() // 2) - 150
        y = (self.loading_window.winfo_screenheight() // 2) - 75
        self.loading_window.geometry(f"+{x}+{y}")

        # Contenido
        spinner = LoadingSpinner(self.loading_window, size=50)
        spinner.pack(pady=20)
        spinner.start()

        label = ctk.CTkLabel(
            self.loading_window,
            text=message,
            font=ctk.CTkFont(size=14)
        )
        label.pack()

    def hide_loading(self):
        """Oculta el indicador de carga"""
        if hasattr(self, 'loading_window'):
            self.loading_window.destroy()

    def run(self):
        """Ejecuta la aplicación"""
        self.main_ui.run()


def main():
    """Punto de entrada principal"""
    # Configurar apariencia
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    # Crear y ejecutar aplicación
    app = MeetingAssistantApp()
    app.run()


if __name__ == "__main__":
    main()
