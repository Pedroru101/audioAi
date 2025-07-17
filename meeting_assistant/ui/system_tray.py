import pystray
from pystray import MenuItem as item
from PIL import Image
import os
from pynput import keyboard
from plyer import notification
from meeting_assistant.ui.history_ui import HistoryUI  # Integra con history_ui para acceso a reuniones
# Importa funciones de grabación de main_improved.py (ajusta según tu código)
from meeting_assistant.main_improved import start_recording, stop_recording  # Asume estas funciones existen

class SystemTray:
    def __init__(self):
        self.icon = None
        self.history_ui = HistoryUI()  # Para acceso a últimas reuniones

    def create_tray_icon(self):
        """Crea icono en tray con menú."""
        image = Image.open(os.path.join(os.path.dirname(__file__), '../../assets/icon.png'))  # Asume un icon.png en assets (crea si no existe)
        menu = (
            item('Iniciar Grabación', self.quick_start_recording),
            item('Últimas Reuniones', self.show_last_meetings),
            item('Minimizar', self.minimize_to_tray),
            item('Salir', self.quit_app)
        )
        self.icon = pystray.Icon("MeetingAssistantPro", image, "Meeting Assistant Pro", menu)
        self.icon.run()

    def quick_start_recording(self):
        """Inicio rápido de grabación."""
        start_recording()  # Llama a función de main
        notification.notify(title="Grabación Iniciada", message="Reunión en curso.")

    def show_last_meetings(self):
        """Acceso a últimas reuniones."""
        self.history_ui.show()  # Muestra UI de historial
        notification.notify(title="Historial", message="Abriendo últimas reuniones.")

    def minimize_to_tray(self):
        """Minimizar a tray (integra con main)."""
        # Lógica para ocultar ventana principal (ajusta en main)
        print("Minimizando a tray...")

    def quit_app(self):
        self.icon.stop()
        # Llama a exit de main

    def setup_hotkeys(self):
        """Hotkeys globales (ej: Ctrl+Alt+R para grabar)."""
        def on_activate():
            self.quick_start_recording()

        with keyboard.GlobalHotKeys({'<ctrl>+<alt>+r': on_activate}) as h:
            h.join()

# Ejemplo standalone
if __name__ == '__main__':
    tray = SystemTray()
    tray.create_tray_icon()