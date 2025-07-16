# main.py (Versión actualizada)

import tkinter as tk
from tkinter import messagebox
import threading

from .config.config_manager import ConfigManager
from .ui.floating_ui import FloatingUI
from .ui.classic_ui import ClassicUI
from .ui.config_ui import ConfigUI
from .audio.recorder import AudioRecorder
from .audio.transcriber import Transcriber
from .utils.file_manager import FileManager
from .utils.notifications import NotificationManager

class MeetingAssistantApp:
    def __init__(self, root):
        self.root = root
        self.root.withdraw()  # Ocultar la ventana principal inicial

        self.config_manager = ConfigManager()
        self.file_manager = FileManager
        self.notifier = NotificationManager
        
        # Inyectar dependencias en los módulos principales
        self.recorder = AudioRecorder(self.config_manager, self.file_manager)
        self.transcriber = Transcriber(self.config_manager)

        self.config_window = None
        self.ui = None
        self.load_ui()

    def load_ui(self):
        config = self.config_manager.get_config()
        ui_mode = config.get("ui_mode", "floating")

        if self.ui:
            self.ui.destroy()

        if ui_mode == "classic":
            self.ui = ClassicUI(
                self.root,
                on_record_toggle=self.toggle_recording,
                on_config=self.open_config_window
            )
        else: # floating
            self.ui = FloatingUI(
                self.root,
                on_record_toggle=self.toggle_recording,
                on_config=self.open_config_window,
                on_exit=self.exit_app
            )

    def toggle_recording(self):
        if self.recorder.is_recording:
            self.notifier.show("Deteniendo", "Grabación detenida. Procesando reunión...")
            meeting_folder = self.recorder.stop_recording()
            if self.ui:
                self.ui.set_recording_status(False)
            
            if meeting_folder:
                self._start_processing(meeting_folder)
        else:
            self.recorder.start_recording()
            if self.ui:
                self.ui.set_recording_status(True)
            self.notifier.show("Grabando", "La grabación de la reunión ha comenzado.")

    def _start_processing(self, meeting_folder):
        """Inicia el procesamiento en un hilo separado para no bloquear la UI."""
        processing_thread = threading.Thread(
            target=self._process_in_background,
            args=(meeting_folder,),
            daemon=True
        )
        processing_thread.start()

    def _process_in_background(self, meeting_folder):
        """Función que se ejecuta en el hilo para procesar el audio."""
        summary, actions = self.transcriber.process_meeting(meeting_folder)
        
        # Volver al hilo principal para mostrar la notificación
        self.root.after(0, self._on_processing_complete, summary, actions)

    def _on_processing_complete(self, summary, actions):
        """Se ejecuta cuando el procesamiento ha terminado."""
        if summary and actions:
            self.notifier.show("Éxito", "El resumen de la reunión está listo.")
            # Aquí se podría abrir una ventana con los resultados
        else:
            self.notifier.show("Error", "Hubo un problema al procesar la reunión.")

    def open_config_window(self):
        if self.config_window and self.config_window.winfo_exists():
            self.config_window.lift()
            return

        self.config_window = tk.Toplevel(self.root)
        ConfigUI(self.config_window, self.config_manager, on_close=self.on_config_closed)

    def on_config_closed(self):
        self.config_window = None
        # Podríamos necesitar recargar la UI si se cambió el modo
        # self.load_ui() # Descomentar si se quiere cambio de UI instantáneo

    def exit_app(self):
        if self.recorder.is_recording:
            if messagebox.askyesno("Salir", "La grabación está en curso. ¿Seguro que quieres salir? Se perderá la grabación."):
                self.root.quit()
        else:
            self.root.quit()

if __name__ == "__main__":
    root = tk.Tk()
    app = MeetingAssistantApp(root)
    root.mainloop()