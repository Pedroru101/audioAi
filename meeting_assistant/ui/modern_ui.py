"""
Interfaz moderna para Meeting Assistant Pro
Combina CustomTkinter con animaciones y efectos inspirados en Kivy
"""
import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
import threading
import time
from datetime import datetime
import json
from PIL import Image, ImageTk
import os
import logging

# Configuración de tema
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Configuración de logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class ModernUI(ctk.CTk):
    def __init__(self, on_record=None, on_stop=None, on_config=None, on_history=None):
        super().__init__()
        logging.debug("Inicializando ModernUI")  # Log de diagnóstico

        self.on_record = on_record
        self.on_stop = on_stop
        self.on_config = on_config
        self.on_history = on_history

        self.is_recording = False
        self.recording_time = 0
        self.timer_thread = None

        # Estado de fuentes activas (por defecto: micrófono activo, sistema inactivo)
        self.mic_active = True
        self.sys_active = False

        # Configuración de ventana
        self.title("Meeting Assistant Pro")
        self.geometry("1000x700")
        self.minsize(800, 600)
        logging.debug("Configuración de ventana completada")  # Log de diagnóstico

        # Variables de estado
        self.current_transcription = tk.StringVar()
        self.current_summary = tk.StringVar()
        self.status_text = tk.StringVar(value="Listo para grabar")

        self.setup_ui()
        self.center_window()

    def center_window(self):
        """Centra la ventana en la pantalla"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def setup_ui(self):
        """Configura la interfaz principal"""
        # Frame principal con grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.create_sidebar()

        # Área de contenido principal
        self.create_main_content()

        # Floating action button (FAB) style
        self.create_fab()

    def create_sidebar(self):
        """Crea el sidebar con navegación"""
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(6, weight=1)

        # Logo/Título
        self.logo_label = ctk.CTkLabel(
            self.sidebar, 
            text="MIA Pro", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Subtítulo
        self.subtitle = ctk.CTkLabel(
            self.sidebar,
            text="Meeting Intelligence Assistant",
            font=ctk.CTkFont(size=10),
            text_color=("gray70", "gray30")
        )
        self.subtitle.grid(row=1, column=0, padx=20, pady=(0, 20))

        # Botones de navegación
        self.nav_buttons = []

        # Dashboard
        self.btn_dashboard = self.create_nav_button(
            "🏠 Dashboard", 
            row=2,
            command=self.show_dashboard
        )

        # Historial
        self.btn_history = self.create_nav_button(
            "📋 Historial",
            row=3,
            command=self.on_history
        )

        # Analytics
        self.btn_analytics = self.create_nav_button(
            "📊 Analytics",
            row=4,
            command=self.show_analytics
        )

        # Configuración
        self.btn_config = self.create_nav_button(
            "⚙️ Configuración",
            row=5,
            command=self.on_config
        )

        # Espacio flexible
        self.sidebar_spacer = ctk.CTkFrame(self.sidebar, height=20)
        self.sidebar_spacer.grid(row=6, column=0, sticky="nsew")

        # Info de versión
        self.version_label = ctk.CTkLabel(
            self.sidebar,
            text="v1.0.0",
            font=ctk.CTkFont(size=10),
            text_color=("gray60", "gray40")
        )
        self.version_label.grid(row=7, column=0, pady=(0, 10))

    def create_nav_button(self, text, row, command=None):
        """Crea un botón de navegación estilizado"""
        btn = ctk.CTkButton(
            self.sidebar,
            text=text,
            font=ctk.CTkFont(size=14),
            height=40,
            corner_radius=8,
            fg_color="transparent",
            text_color=("gray10", "gray90"),
            hover_color=("gray70", "gray30"),
            anchor="w",
            command=command
        )
        btn.grid(row=row, column=0, padx=10, pady=5, sticky="ew")
        self.nav_buttons.append(btn)
        return btn

    def create_main_content(self):
        """Crea el área de contenido principal"""
        self.main_frame = ctk.CTkFrame(self, corner_radius=0)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(2, weight=1)

        # Header con estado
        self.create_header()

        # Área de grabación
        self.create_recording_area()

        # Área de resultados
        self.create_results_area()

    def create_header(self):
        """Crea el header con información de estado"""
        self.header_frame = ctk.CTkFrame(self.main_frame)
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        self.header_frame.grid_columnconfigure(1, weight=1)

        # Título de la sección
        self.section_title = ctk.CTkLabel(
            self.header_frame,
            text="Panel de Control",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.section_title.grid(row=0, column=0, sticky="w")

        # Estado
        self.status_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.status_frame.grid(row=0, column=1, sticky="e")

        self.status_indicator = ctk.CTkLabel(
            self.status_frame,
            text="●",
            font=ctk.CTkFont(size=16),
            text_color="#4CAF50"
        )
        self.status_indicator.grid(row=0, column=0, padx=(0, 5))

        self.status_label = ctk.CTkLabel(
            self.status_frame,
            textvariable=self.status_text,
            font=ctk.CTkFont(size=14)
        )
        self.status_label.grid(row=0, column=1)

    def create_recording_area(self):
        """Crea el área de control de grabación"""
        self.recording_frame = ctk.CTkFrame(self.main_frame)
        self.recording_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=10)
        self.recording_frame.grid_columnconfigure(1, weight=1)

        # Controles de grabación
        self.controls_frame = ctk.CTkFrame(self.recording_frame)
        self.controls_frame.grid(row=0, column=0, sticky="w", padx=10, pady=10)

        # Botón de grabación principal con indicadores de fuente
        self.record_button = CTkRecordButton(
            self.controls_frame,
            text="🎤 Iniciar Grabación",
            font=ctk.CTkFont(size=16, weight="bold"),
            width=200,
            height=50,
            corner_radius=25,
            fg_color="#4CAF50",
            hover_color="#45a049"
        )
        self.record_button.grid(row=0, column=0, padx=5)

        # Eventos de ratón personalizados
        self._single_click_after_id = None
        self.record_button.bind('<Button-1>', self._on_record_click)
        self.record_button.bind('<Double-Button-1>', self._on_record_double_click)
        self.record_button.bind('<Button-3>', self._on_record_right_click)

        # Estado de fuentes activas (por defecto: micrófono activo, sistema inactivo)
        self.mic_active = True
        self.sys_active = False

        # Timer
        self.timer_label = ctk.CTkLabel(
            self.controls_frame,
            text="00:00:00",
            font=ctk.CTkFont(size=20, family="Consolas")
        )
        self.timer_label.grid(row=0, column=1, padx=20)

        # Visualizador de audio (simulado)
        self.audio_viz_frame = ctk.CTkFrame(self.recording_frame, height=60)
        self.audio_viz_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 10))
        self.audio_viz_frame.grid_columnconfigure(0, weight=1)

        self.create_audio_visualizer()

    def create_audio_visualizer(self):
        """Crea un visualizador de audio simple"""
        self.viz_canvas = ctk.CTkCanvas(
            self.audio_viz_frame,
            height=50,
            bg="#212121",
            highlightthickness=0
        )
        self.viz_canvas.grid(row=0, column=0, sticky="ew", padx=5, pady=5)

        # Dibuja líneas de visualización inicial
        self.viz_bars = []
        bar_count = 50
        bar_width = 4
        spacing = 2

        for i in range(bar_count):
            x = i * (bar_width + spacing) + 10
            bar = self.viz_canvas.create_rectangle(
                x, 45, x + bar_width, 45,
                fill="#4CAF50",
                outline=""
            )
            self.viz_bars.append(bar)

    def animate_audio_visualizer(self):
        """Anima el visualizador de audio durante la grabación"""
        import random
        if self.is_recording:
            for i, bar in enumerate(self.viz_bars):
                height = random.randint(5, 40)
                self.viz_canvas.coords(
                    bar,
                    i * 6 + 10, 45 - height,
                    i * 6 + 14, 45
                )
            self.after(100, self.animate_audio_visualizer)
        else:
            # Reset bars
            for i, bar in enumerate(self.viz_bars):
                self.viz_canvas.coords(
                    bar,
                    i * 6 + 10, 45,
                    i * 6 + 14, 45
                )

    def create_results_area(self):
        """Crea el área de resultados con tabs"""
        self.results_frame = ctk.CTkFrame(self.main_frame)
        self.results_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=(0, 20))
        self.results_frame.grid_columnconfigure(0, weight=1)
        self.results_frame.grid_rowconfigure(1, weight=1)

        # Tabview para resultados
        self.tabview = ctk.CTkTabview(self.results_frame)
        self.tabview.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # Tab de Transcripción
        self.tab_transcription = self.tabview.add("📝 Transcripción")
        self.transcription_text = ctk.CTkTextbox(
            self.tab_transcription,
            font=ctk.CTkFont(size=14),
            wrap="word"
        )
        self.transcription_text.pack(fill="both", expand=True, padx=10, pady=10)

        # Tab de Resumen
        self.tab_summary = self.tabview.add("📋 Resumen")
        self.summary_text = ctk.CTkTextbox(
            self.tab_summary,
            font=ctk.CTkFont(size=14),
            wrap="word"
        )
        self.summary_text.pack(fill="both", expand=True, padx=10, pady=10)

        # Tab de Acciones
        self.tab_actions = self.tabview.add("✅ Acciones")
        self.actions_frame = ctk.CTkScrollableFrame(self.tab_actions)
        self.actions_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Tab de Analytics
        self.tab_analytics = self.tabview.add("📊 Analytics")
        self.analytics_label = ctk.CTkLabel(
            self.tab_analytics,
            text="Analytics en tiempo real aparecerán aquí",
            font=ctk.CTkFont(size=14),
            text_color=("gray60", "gray40")
        )
        self.analytics_label.pack(pady=50)

    def create_fab(self):
        """Crea un Floating Action Button para acciones rápidas"""
        self.fab_frame = ctk.CTkFrame(
            self,
            width=60,
            height=60,
            corner_radius=30,
            fg_color="#2196F3"
        )
        self.fab_frame.place(relx=0.95, rely=0.95, anchor="se")

        self.fab_button = ctk.CTkButton(
            self.fab_frame,
            text="➕",
            font=ctk.CTkFont(size=24),
            width=60,
            height=60,
            corner_radius=30,
            fg_color="transparent",
            hover_color="#1976D2",
            command=self.show_quick_actions
        )
        self.fab_button.pack()

    def _on_record_click(self, event):
        """Gestión de click izquierdo con debounce para distinguir single vs double click"""
        if self._single_click_after_id:
            self.after_cancel(self._single_click_after_id)
            self._single_click_after_id = None
        # Espera 200 ms para ver si es doble click
        self._single_click_after_id = self.after(200, lambda: self._handle_single_click())

    def _handle_single_click(self):
        self._single_click_after_id = None
        if not self.is_recording:
            self.start_recording()
        elif hasattr(self, 'is_paused') and self.is_paused:
            self.resume_recording()
        # Si ya está grabando y no está en pausa, no hace nada

    def _on_record_double_click(self, event):
        """Doble click izquierdo: pausar grabación"""
        if self._single_click_after_id:
            self.after_cancel(self._single_click_after_id)
            self._single_click_after_id = None
        if self.is_recording and (not hasattr(self, 'is_paused') or not self.is_paused):
            self.pause_recording()

    def _on_record_right_click(self, event):
        """Click derecho: mostrar menú para terminar grabación"""
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="Terminar grabación", command=self.stop_recording)
        menu.tk_popup(event.x_root, event.y_root)

    def start_recording(self):
        """Inicia la grabación"""
        self.is_recording = True
        self.is_paused = False
        self.recording_time = 0

        # Actualizar UI
        self.record_button.set_recording(True)
        self.status_text.set("Grabando...")
        self.status_indicator.configure(text_color="#f44336")

        # Iniciar timer
        self.timer_thread = threading.Thread(target=self.update_timer, daemon=True)
        self.timer_thread.start()

        # Iniciar animación de audio
        self.animate_audio_visualizer()

        # Callback
        if self.on_record:
            self.on_record()

    def pause_recording(self):
        """Pausa la grabación"""
        if not self.is_recording or (hasattr(self, 'is_paused') and self.is_paused):
            return
        self.is_paused = True
        self.record_button.configure(text="⏸️ Pausada", fg_color="#FF9800", hover_color="#FFA726")
        self.status_text.set("Grabación pausada")
        self.status_indicator.configure(text_color="#FFA726")
        # Aquí podrías pausar el timer real y la animación si lo deseas

    def resume_recording(self):
        """Reanuda la grabación pausada"""
        if not self.is_recording or not (hasattr(self, 'is_paused') and self.is_paused):
            return
        self.is_paused = False
        self.record_button.set_recording(True)
        self.status_text.set("Grabando...")
        self.status_indicator.configure(text_color="#f44336")
        # Aquí podrías reanudar el timer real y la animación si lo deseas

    def stop_recording(self):
        """Detiene la grabación"""
        self.is_recording = False

        # Actualizar UI
        self.record_button.set_recording(False)
        self.status_text.set("Procesando...")
        self.status_indicator.configure(text_color="#FF9800")

        # Callback
        if self.on_stop:
            self.on_stop()

        # Simular procesamiento
        self.after(2000, self.finish_processing)

    def finish_processing(self):
        """Finaliza el procesamiento"""
        self.status_text.set("Listo para grabar")
        self.status_indicator.configure(text_color="#4CAF50")

    def update_timer(self):
        """Actualiza el timer durante la grabación"""
        while self.is_recording:
            hours = self.recording_time // 3600
            minutes = (self.recording_time % 3600) // 60
            seconds = self.recording_time % 60

            time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            self.timer_label.configure(text=time_str)

            time.sleep(1)
            self.recording_time += 1

        # Reset timer
        self.timer_label.configure(text="00:00:00")

    def show_quick_actions(self):
        """Muestra menú de acciones rápidas"""
        menu = tk.Menu(self, tearoff=0, bg="#2c2c2c", fg="white")
        menu.add_command(label="📁 Importar Audio", command=self.import_audio)
        menu.add_command(label="📤 Exportar Resultados", command=self.export_results)
        menu.add_separator()
        menu.add_command(label="🔄 Sincronizar", command=self.sync_data)

        # Posición del menú
        x = self.fab_frame.winfo_rootx()
        y = self.fab_frame.winfo_rooty() - 100
        menu.post(x - 150, y)

    def show_dashboard(self):
        """Muestra el dashboard principal"""
        self.section_title.configure(text="Panel de Control")
        # Aquí puedes cambiar el contenido del área principal

    def show_analytics(self):
        """Muestra la sección de analytics"""
        self.section_title.configure(text="Analytics")
        # Implementar vista de analytics

    def import_audio(self):
        """Importa un archivo de audio"""
        from tkinter import filedialog
        filename = filedialog.askopenfilename(
            title="Seleccionar archivo de audio",
            filetypes=[("Audio files", "*.mp3 *.wav *.m4a *.flac")]
        )
        if filename:
            # Procesar archivo
            pass

    def export_results(self):
        """Exporta los resultados"""
        from tkinter import filedialog
        filename = filedialog.asksaveasfilename(
            title="Guardar resultados",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("Text files", "*.txt")]
        )
        if filename:
            # Guardar resultados
            pass

    def sync_data(self):
        """Sincroniza datos (placeholder)"""
        self.status_text.set("Sincronizando...")
        self.after(1500, lambda: self.status_text.set("Sincronización completa"))

    def set_transcription(self, text):
        """Actualiza la transcripción"""
        self.transcription_text.delete("1.0", "end")
        self.transcription_text.insert("1.0", text)
        self.tabview.set("📝 Transcripción")

    def set_summary(self, text):
        """Actualiza el resumen"""
        self.summary_text.delete("1.0", "end")
        self.summary_text.insert("1.0", text)

    def add_action_item(self, action):
        """Añade un item de acción"""
        action_frame = ctk.CTkFrame(self.actions_frame)
        action_frame.pack(fill="x", padx=5, pady=5)

        checkbox = ctk.CTkCheckBox(
            action_frame,
            text=action,
            font=ctk.CTkFont(size=14)
        )
        checkbox.pack(side="left", padx=10, pady=5)

    def set_audio_sources(self, mic: bool, sys: bool):
        """Actualiza el estado visual de las fuentes de audio en el botón de grabación."""
        self.mic_active = mic
        self.sys_active = sys
        if hasattr(self, 'record_button'):
            self.record_button.set_audio_sources(mic, sys)

    def run(self):
        """Inicia la aplicación"""
        self.mainloop()


# Clase para ventana flotante minimalista
class FloatingWidget(ctk.CTkToplevel):
    """Widget flotante para control rápido"""

    def __init__(self, parent, on_record_toggle=None):
        super().__init__(parent)

        self.on_record_toggle = on_record_toggle
        self.is_recording = False

        # Configuración de ventana
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.geometry("80x80+100+100")
        self.configure(fg_color="transparent")

        # Frame circular
        self.circle_frame = ctk.CTkFrame(
            self,
            width=80,
            height=80,
            corner_radius=40,
            fg_color="#4CAF50"
        )
        self.circle_frame.pack()

        # Botón
        self.record_btn = ctk.CTkButton(
            self.circle_frame,
            text="🎤",
            font=ctk.CTkFont(size=28),
            width=80,
            height=80,
            corner_radius=40,
            fg_color="transparent",
            hover_color="#45a049",
            command=self.toggle_recording
        )
        self.record_btn.pack()

        # Hacer draggable
        self.bind("<Button-1>", self.start_move)
        self.bind("<ButtonRelease-1>", self.stop_move)
        self.bind("<B1-Motion>", self.on_motion)

        self._drag_data = {"x": 0, "y": 0}

    def start_move(self, event):
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

    def stop_move(self, event):
        self._drag_data["x"] = 0
        self._drag_data["y"] = 0

    def on_motion(self, event):
        x = self.winfo_x() + event.x - self._drag_data["x"]
        y = self.winfo_y() + event.y - self._drag_data["y"]
        self.geometry(f"+{x}+{y}")

    def toggle_recording(self):
        self.is_recording = not self.is_recording

        if self.is_recording:
            self.circle_frame.configure(fg_color="#f44336")
            self.record_btn.configure(
                text="⏹",
                hover_color="#d32f2f"
            )
        else:
            self.circle_frame.configure(fg_color="#4CAF50")
            self.record_btn.configure(
                text="🎤",
                hover_color="#45a049"
            )

        if self.on_record_toggle:
            self.on_record_toggle()


# ---
# Botón de grabación con indicadores de fuente para CustomTkinter
# ---

class CTkRecordButton(ctk.CTkButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_recording = False
        self.mic_active = True
        self.sys_active = False
        self.update_style()

    def set_audio_sources(self, mic: bool, sys: bool):
        self.mic_active = mic
        self.sys_active = sys
        self.update_style()

    def set_recording(self, recording: bool):
        self.is_recording = recording
        self.update_style()

    def update_style(self):
        # Decide text and color based on state
        if self.is_recording:
            if self.mic_active and self.sys_active:
                text = "⏹ 🎤+💻"
            elif self.mic_active:
                text = "⏹ 🎤"
            elif self.sys_active:
                text = "⏹ 💻"
            else:
                text = "⏹"
            self.configure(text=text, fg_color="#f44336", hover_color="#d32f2f")
        else:
            if self.mic_active and self.sys_active:
                text = "🎤+💻 Iniciar Grabación"
            elif self.mic_active:
                text = "🎤 Iniciar Grabación"
            elif self.sys_active:
                text = "💻 Iniciar Grabación"
            else:
                text = "⛔ Sin fuentes"
            self.configure(text=text, fg_color="#4CAF50", hover_color="#45a049")

if __name__ == "__main__":
    # Test
    app = ModernUI()
    app.run()
