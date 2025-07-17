# Crear notification_manager.py
notification_manager_code = '''# utils/notifications.py
import tkinter as tk
from tkinter import ttk
import threading
import queue
import time
from typing import Optional, Callable, Dict, Any
from pathlib import Path
import winsound
import logging
from datetime import datetime
import json

class NotificationManager:
    """Gestor de notificaciones tipo messenger para Meeting Assistant Pro."""
    
    def __init__(self, config_manager=None):
        self.config_manager = config_manager
        self.logger = logging.getLogger(__name__)
        
        # Cola de notificaciones
        self.notification_queue = queue.Queue()
        
        # Estado
        self.is_running = False
        self.notification_thread = None
        self.active_notifications = []
        
        # Configuración por defecto
        self.config = {
            'enabled': True,
            'sound': True,
            'position': 'bottom-right',
            'duration': 3000,
            'max_notifications': 3,
            'animation_speed': 10,
            'opacity': 0.9
        }
        
        # Actualizar con configuración si está disponible
        if self.config_manager:
            self._load_config()
        
        # Iniciar el procesador de notificaciones
        self.start()

    def _load_config(self):
        """Carga la configuración desde el ConfigManager."""
        try:
            self.config['enabled'] = self.config_manager.get('notifications_enabled', True)
            self.config['sound'] = self.config_manager.get('notification_sound', True)
            self.config['position'] = self.config_manager.get('notification_position', 'bottom-right')
            self.config['duration'] = self.config_manager.get('notification_duration', 3000)
        except Exception as e:
            self.logger.error(f"Error cargando configuración de notificaciones: {e}")

    def start(self):
        """Inicia el procesador de notificaciones."""
        if not self.is_running:
            self.is_running = True
            self.notification_thread = threading.Thread(
                target=self._notification_processor,
                daemon=True
            )
            self.notification_thread.start()
            self.logger.info("NotificationManager iniciado")

    def stop(self):
        """Detiene el procesador de notificaciones."""
        self.is_running = False
        
        # Añadir notificación especial para despertar el thread
        self.notification_queue.put(None)
        
        if self.notification_thread:
            self.notification_thread.join(timeout=1)
        
        # Cerrar notificaciones activas
        for notification in self.active_notifications:
            try:
                notification.close()
            except:
                pass
        
        self.logger.info("NotificationManager detenido")

    def _notification_processor(self):
        """Procesa la cola de notificaciones."""
        while self.is_running:
            try:
                # Obtener notificación de la cola
                notification_data = self.notification_queue.get(timeout=0.1)
                
                if notification_data is None:
                    continue
                
                if self.config['enabled']:
                    self._show_notification(notification_data)
                    
            except queue.Empty:
                # Limpiar notificaciones expiradas
                self._cleanup_expired_notifications()
            except Exception as e:
                self.logger.error(f"Error en procesador de notificaciones: {e}")

    def _show_notification(self, notification_data: Dict[str, Any]):
        """Muestra una notificación en pantalla."""
        try:
            notification = NotificationWindow(
                title=notification_data.get('title', 'Meeting Assistant'),
                message=notification_data.get('message', ''),
                type=notification_data.get('type', 'info'),
                duration=notification_data.get('duration', self.config['duration']),
                position=self.config['position'],
                opacity=self.config['opacity'],
                callback=notification_data.get('callback'),
                actions=notification_data.get('actions', [])
            )
            
            # Calcular posición considerando notificaciones existentes
            position_offset = len([n for n in self.active_notifications if n.is_active()]) * 100
            notification.set_position_offset(position_offset)
            
            # Mostrar notificación
            notification.show()
            
            # Reproducir sonido si está habilitado
            if self.config['sound'] and notification_data.get('sound', True):
                self._play_notification_sound(notification_data.get('type', 'info'))
            
            # Añadir a lista de activas
            self.active_notifications.append(notification)
            
            # Limitar número de notificaciones visibles
            while len(self.active_notifications) > self.config['max_notifications']:
                oldest = self.active_notifications.pop(0)
                oldest.close()
                
        except Exception as e:
            self.logger.error(f"Error mostrando notificación: {e}")

    def _cleanup_expired_notifications(self):
        """Elimina notificaciones expiradas de la lista."""
        self.active_notifications = [
            n for n in self.active_notifications 
            if n.is_active()
        ]

    def _play_notification_sound(self, notification_type: str):
        """Reproduce un sonido de notificación."""
        try:
            # Mapeo de tipos a frecuencias de sonido
            sound_map = {
                'success': (1000, 100),  # Frecuencia alta, corta
                'error': (500, 200),     # Frecuencia baja, larga
                'warning': (750, 150),   # Frecuencia media
                'info': (800, 100)       # Por defecto
            }
            
            frequency, duration = sound_map.get(notification_type, (800, 100))
            
            # Reproducir sonido en Windows
            winsound.Beep(frequency, duration)
            
        except Exception as e:
            # Si falla el sonido, no es crítico
            self.logger.debug(f"No se pudo reproducir sonido: {e}")

    # Métodos públicos para mostrar notificaciones
    
    def show_info(self, message: str, title: str = "Información", 
                  duration: Optional[int] = None, callback: Optional[Callable] = None):
        """Muestra una notificación informativa."""
        self._queue_notification({
            'type': 'info',
            'title': title,
            'message': message,
            'duration': duration,
            'callback': callback
        })

    def show_success(self, message: str, title: str = "Éxito",
                    duration: Optional[int] = None, callback: Optional[Callable] = None):
        """Muestra una notificación de éxito."""
        self._queue_notification({
            'type': 'success',
            'title': title,
            'message': message,
            'duration': duration,
            'callback': callback
        })

    def show_warning(self, message: str, title: str = "Advertencia",
                    duration: Optional[int] = None, callback: Optional[Callable] = None):
        """Muestra una notificación de advertencia."""
        self._queue_notification({
            'type': 'warning',
            'title': title,
            'message': message,
            'duration': duration,
            'callback': callback
        })

    def show_error(self, message: str, title: str = "Error",
                  duration: Optional[int] = None, callback: Optional[Callable] = None):
        """Muestra una notificación de error."""
        self._queue_notification({
            'type': 'error',
            'title': title,
            'message': message,
            'duration': duration or 5000,  # Los errores duran más
            'callback': callback
        })

    def show_progress(self, message: str, title: str = "Procesando...",
                     progress: float = 0.0):
        """Muestra una notificación de progreso."""
        self._queue_notification({
            'type': 'progress',
            'title': title,
            'message': message,
            'progress': progress,
            'duration': None  # Sin auto-cierre
        })

    def show_action(self, message: str, title: str = "Acción requerida",
                   actions: list, duration: Optional[int] = None):
        """Muestra una notificación con botones de acción."""
        self._queue_notification({
            'type': 'action',
            'title': title,
            'message': message,
            'actions': actions,
            'duration': duration or 10000  # Más tiempo para acciones
        })

    def _queue_notification(self, notification_data: Dict[str, Any]):
        """Añade una notificación a la cola."""
        if self.config['enabled']:
            # Añadir timestamp
            notification_data['timestamp'] = datetime.now().isoformat()
            
            # Añadir a la cola
            self.notification_queue.put(notification_data)
            
            # Guardar en log de notificaciones si es importante
            if notification_data['type'] in ['error', 'warning']:
                self._log_notification(notification_data)

    def _log_notification(self, notification_data: Dict[str, Any]):
        """Guarda notificaciones importantes en un log."""
        try:
            log_path = Path.home() / ".meeting_assistant" / "notifications.log"
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps(notification_data, ensure_ascii=False) + '\\n')
                
        except Exception as e:
            self.logger.error(f"Error guardando log de notificación: {e}")

    def clear_all(self):
        """Cierra todas las notificaciones activas."""
        for notification in self.active_notifications:
            try:
                notification.close()
            except:
                pass
        
        self.active_notifications.clear()


class NotificationWindow:
    """Ventana individual de notificación."""
    
    def __init__(self, title: str, message: str, type: str = 'info',
                 duration: Optional[int] = 3000, position: str = 'bottom-right',
                 opacity: float = 0.9, callback: Optional[Callable] = None,
                 actions: list = None):
        self.title = title
        self.message = message
        self.type = type
        self.duration = duration
        self.position = position
        self.opacity = opacity
        self.callback = callback
        self.actions = actions or []
        
        self.window = None
        self.is_closing = False
        self.position_offset = 0
        
        # Colores por tipo
        self.colors = {
            'info': '#2196F3',
            'success': '#4CAF50',
            'warning': '#FF9800',
            'error': '#F44336',
            'progress': '#9C27B0',
            'action': '#607D8B'
        }

    def set_position_offset(self, offset: int):
        """Establece el desplazamiento de posición para apilar notificaciones."""
        self.position_offset = offset

    def show(self):
        """Muestra la notificación."""
        # Crear ventana en el thread principal de Tkinter
        self.window = tk.Toplevel()
        self.window.withdraw()  # Ocultar inicialmente
        
        # Configurar ventana
        self._setup_window()
        
        # Crear contenido
        self._create_content()
        
        # Posicionar ventana
        self._position_window()
        
        # Mostrar con animación
        self._animate_show()
        
        # Programar cierre automático si tiene duración
        if self.duration:
            self.window.after(self.duration, self.close)

    def _setup_window(self):
        """Configura las propiedades de la ventana."""
        self.window.overrideredirect(True)  # Sin bordes
        self.window.attributes('-topmost', True)  # Siempre encima
        self.window.attributes('-alpha', 0.0)  # Inicialmente transparente
        
        # Estilo según el sistema operativo
        try:
            self.window.attributes('-toolwindow', True)  # Windows
        except:
            pass

    def _create_content(self):
        """Crea el contenido de la notificación."""
        # Frame principal
        main_frame = tk.Frame(
            self.window,
            bg='white',
            relief=tk.RAISED,
            borderwidth=1
        )
        main_frame.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        
        # Barra de color según tipo
        color_bar = tk.Frame(
            main_frame,
            bg=self.colors.get(self.type, '#2196F3'),
            width=4
        )
        color_bar.pack(side=tk.LEFT, fill=tk.Y)
        
        # Contenido
        content_frame = tk.Frame(main_frame, bg='white', padx=15, pady=10)
        content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Título
        title_label = tk.Label(
            content_frame,
            text=self.title,
            bg='white',
            font=('Segoe UI', 10, 'bold'),
            anchor='w'
        )
        title_label.pack(fill=tk.X)
        
        # Mensaje
        message_label = tk.Label(
            content_frame,
            text=self.message,
            bg='white',
            font=('Segoe UI', 9),
            anchor='w',
            wraplength=250,
            justify='left'
        )
        message_label.pack(fill=tk.X, pady=(5, 0))
        
        # Barra de progreso si es necesario
        if self.type == 'progress':
            self.progress_bar = ttk.Progressbar(
                content_frame,
                length=200,
                mode='determinate'
            )
            self.progress_bar.pack(fill=tk.X, pady=(10, 0))
        
        # Botones de acción si hay
        if self.actions:
            action_frame = tk.Frame(content_frame, bg='white')
            action_frame.pack(fill=tk.X, pady=(10, 0))
            
            for action in self.actions:
                btn = tk.Button(
                    action_frame,
                    text=action['text'],
                    command=lambda a=action: self._handle_action(a),
                    bg='#f0f0f0',
                    relief=tk.FLAT,
                    padx=10,
                    pady=5
                )
                btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Botón de cerrar
        close_btn = tk.Button(
            main_frame,
            text='×',
            command=self.close,
            bg='white',
            fg='#666',
            relief=tk.FLAT,
            font=('Arial', 12),
            padx=5,
            pady=0
        )
        close_btn.place(relx=1.0, x=-20, y=5)

    def _position_window(self):
        """Posiciona la ventana según la configuración."""
        self.window.update_idletasks()
        
        # Obtener dimensiones
        window_width = self.window.winfo_width()
        window_height = self.window.winfo_height()
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        
        # Márgenes
        margin = 20
        
        # Calcular posición según configuración
        if 'right' in self.position:
            x = screen_width - window_width - margin
        else:
            x = margin
        
        if 'bottom' in self.position:
            y = screen_height - window_height - margin - self.position_offset
        else:
            y = margin + self.position_offset
        
        self.window.geometry(f"+{x}+{y}")

    def _animate_show(self):
        """Anima la aparición de la notificación."""
        self.window.deiconify()
        self._fade_in()

    def _fade_in(self, alpha=0.0):
        """Efecto de fade in."""
        if alpha < self.opacity:
            alpha += 0.05
            self.window.attributes('-alpha', alpha)
            self.window.after(10, lambda: self._fade_in(alpha))

    def _fade_out(self, alpha=None):
        """Efecto de fade out."""
        if alpha is None:
            alpha = self.opacity
        
        if alpha > 0:
            alpha -= 0.05
            self.window.attributes('-alpha', alpha)
            self.window.after(10, lambda: self._fade_out(alpha))
        else:
            self.window.destroy()

    def _handle_action(self, action: Dict[str, Any]):
        """Maneja el clic en un botón de acción."""
        if 'callback' in action and callable(action['callback']):
            action['callback']()
        
        # Cerrar notificación después de la acción
        self.close()

    def close(self):
        """Cierra la notificación con animación."""
        if not self.is_closing and self.window and self.window.winfo_exists():
            self.is_closing = True
            
            # Ejecutar callback si existe
            if self.callback:
                self.callback()
            
            # Animar cierre
            self._fade_out()

    def is_active(self) -> bool:
        """Verifica si la notificación está activa."""
        return self.window is not None and self.window.winfo_exists() and not self.is_closing

    def update_progress(self, value: float):
        """Actualiza el valor de la barra de progreso."""
        if hasattr(self, 'progress_bar'):
            self.progress_bar['value'] = value
'''

# Guardar el archivo
with open('notifications.py', 'w', encoding='utf-8') as f:
    f.write(notification_manager_code)

print("✅ notifications.py creado exitosamente")
print("\nCaracterísticas implementadas:")
print("- ✓ Notificaciones tipo messenger flotantes")
print("- ✓ Múltiples tipos (info, éxito, error, advertencia, progreso)")
print("- ✓ Animaciones de fade in/out")
print("- ✓ Apilamiento automático de notificaciones")
print("- ✓ Sonidos personalizados por tipo")
print("- ✓ Botones de acción interactivos")
print("- ✓ Log de notificaciones importantes")
print("- ✓ Configuración flexible de posición y duración")