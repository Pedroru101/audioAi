import tkinter as tk

class FloatingUI:
    def __init__(self, root, on_record_toggle, on_config, on_exit):
        self.root = root
        self.on_record_toggle = on_record_toggle
        self.on_config = on_config
        self.on_exit = on_exit
        self.is_recording = False
        self._offset = {'x': 0, 'y': 0}
        self._dragging = False

        # --- Configuración de la ventana flotante ---
        # Elimina la barra de título y los bordes
        self.root.overrideredirect(True)
        # Mantiene la ventana siempre encima de las demás
        self.root.wm_attributes("-topmost", 1)
        # Establece una posición inicial
        self.root.geometry("+100+100")
        # Hace que el color de fondo de la ventana sea transparente
        self.root.wm_attributes("-transparentcolor", "white")
        self.root.config(bg='white')

        # --- Creación del botón circular (usando un Canvas) ---
        self.canvas = tk.Canvas(self.root, width=60, height=60, bg='white', highlightthickness=0)
        self.canvas.pack()

        # Dibuja el círculo que será nuestro botón
        self.circle = self.canvas.create_oval(5, 5, 55, 55, fill="#4CAF50", outline="") # Verde inicial (listo para grabar)
        
        # --- Vinculación de eventos ---
        # Clic izquierdo para grabar/detener
        self.canvas.tag_bind(self.circle, '<ButtonRelease-1>', self.toggle_recording_visuals)
        
        # Clic derecho para abrir configuración (opcional, pero útil)
        self.canvas.tag_bind(self.circle, '<Button-3>', self.open_settings_menu)

        # Eventos para arrastrar la ventana
        self.canvas.bind('<ButtonPress-1>', self.start_move)
        self.canvas.bind('<ButtonRelease-1>', self.stop_move)
        self.canvas.bind('<B1-Motion>', self.on_motion)

    def start_move(self, event):
        """Registra la posición inicial del clic para mover la ventana."""
        self._dragging = False
        self._offset['x'] = event.x
        self._offset['y'] = event.y

    def stop_move(self, event):
        """Resetea la posición al soltar el clic."""
        self._offset['x'] = 0
        self._offset['y'] = 0

    def on_motion(self, event):
        """Mueve la ventana según el movimiento del ratón."""
        self._dragging = True
        new_x = self.root.winfo_x() + event.x - self._offset['x']
        new_y = self.root.winfo_y() + event.y - self._offset['y']
        self.root.geometry(f"+{new_x}+{new_y}")

    def toggle_recording_visuals(self, event=None):
        """Cambia el estado y el color del botón."""
        # Ignorar toggle si fue arrastre
        if getattr(self, '_dragging', False):
            return
        self.is_recording = not self.is_recording
        self.update_visual_state()
        # Llama a la función de lógica de grabación real
        if self.on_record_toggle:
            self.on_record_toggle()

    def update_visual_state(self):
        """Actualiza el color del botón según el estado de grabación."""
        if self.is_recording:
            # Rojo: grabando
            self.canvas.itemconfig(self.circle, fill="#F44336") 
        else:
            # Verde: listo para grabar
            self.canvas.itemconfig(self.circle, fill="#4CAF50")

    def open_settings_menu(self, event):
        """Muestra un menú contextual al hacer clic derecho."""
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="Configuración", command=self.on_config)
        menu.add_separator()
        menu.add_command(label="Salir", command=self.on_exit)
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def show_notification(self, message):
        """(Placeholder) Muestra una notificación simple."""
        # Aquí se integraría con notifications.py
        print(f"NOTIFICACIÓN: {message}")
        # Podrías crear una pequeña ventana emergente temporal aquí

    def show(self):
        """Muestra la ventana flotante."""
        self.root.deiconify()

    def hide(self):
        """Oculta la ventana flotante."""
        self.root.withdraw()

    def update_recording_state(self, is_recording):
        """Actualiza el estado de grabación desde la lógica."""
        self.is_recording = is_recording
        self.update_visual_state()

    def update_status(self, message):
        """Actualiza el estado mostrando notificación."""
        self.show_notification(message)