"""
Componentes animados inspirados en Kivy para Meeting Assistant Pro
Incluye efectos de transición, ripple effects y animaciones suaves
"""
import customtkinter as ctk
import tkinter as tk
from PIL import Image, ImageDraw, ImageFilter
import math
import threading
import time

class RippleButton(ctk.CTkButton):
    """Botón con efecto ripple al hacer clic"""

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.ripple_active = False
        self.ripple_radius = 0
        self.ripple_alpha = 255
        self.bind("<Button-1>", self.on_click)

    def on_click(self, event):
        """Inicia el efecto ripple"""
        if not self.ripple_active:
            self.ripple_active = True
            self.ripple_x = event.x
            self.ripple_y = event.y
            threading.Thread(target=self.animate_ripple, daemon=True).start()

    def animate_ripple(self):
        """Anima el efecto ripple"""
        max_radius = max(self.winfo_width(), self.winfo_height())
        steps = 20

        for i in range(steps):
            self.ripple_radius = (i / steps) * max_radius
            self.ripple_alpha = 255 - (i / steps) * 255
            self.update()
            time.sleep(0.02)

        self.ripple_active = False
        self.ripple_radius = 0
        self.ripple_alpha = 255


class PulseButton(ctk.CTkButton):
    """Botón con efecto de pulso continuo"""

    def __init__(self, master, pulse_color="#4CAF50", **kwargs):
        super().__init__(master, **kwargs)
        self.pulse_color = pulse_color
        self.is_pulsing = False
        self.pulse_scale = 1.0

    def start_pulse(self):
        """Inicia la animación de pulso"""
        self.is_pulsing = True
        threading.Thread(target=self._pulse_animation, daemon=True).start()

    def stop_pulse(self):
        """Detiene la animación de pulso"""
        self.is_pulsing = False

    def _pulse_animation(self):
        """Ejecuta la animación de pulso"""
        while self.is_pulsing:
            # Expandir
            for i in range(20):
                if not self.is_pulsing:
                    break
                self.pulse_scale = 1.0 + (i / 20) * 0.1
                self.update()
                time.sleep(0.02)

            # Contraer
            for i in range(20):
                if not self.is_pulsing:
                    break
                self.pulse_scale = 1.1 - (i / 20) * 0.1
                self.update()
                time.sleep(0.02)


class AnimatedProgressBar(ctk.CTkProgressBar):
    """Barra de progreso con animación suave"""

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.target_value = 0
        self.current_value = 0
        self.animation_speed = 0.02

    def set_value_animated(self, value, duration=0.5):
        """Establece el valor con animación"""
        self.target_value = value
        steps = int(duration / self.animation_speed)
        increment = (value - self.current_value) / steps

        def animate():
            for _ in range(steps):
                self.current_value += increment
                self.set(self.current_value)
                self.update()
                time.sleep(self.animation_speed)

        threading.Thread(target=animate, daemon=True).start()


class WaveformVisualizer(ctk.CTkCanvas):
    """Visualizador de forma de onda animado"""

    def __init__(self, master, width=400, height=100, **kwargs):
        super().__init__(master, width=width, height=height, **kwargs)
        self.configure(bg="#1a1a1a", highlightthickness=0)

        self.bars = []
        self.bar_count = 60
        self.is_active = False
        self.amplitude_data = [0] * self.bar_count

        self._create_bars()

    def _create_bars(self):
        """Crea las barras del visualizador"""
        bar_width = self.winfo_reqwidth() / self.bar_count
        spacing = 2

        for i in range(self.bar_count):
            x = i * bar_width + spacing
            bar = self.create_rectangle(
                x, self.winfo_reqheight(),
                x + bar_width - spacing, self.winfo_reqheight(),
                fill="#4CAF50",
                outline=""
            )
            self.bars.append(bar)

    def start_animation(self):
        """Inicia la animación del visualizador"""
        self.is_active = True
        threading.Thread(target=self._animate, daemon=True).start()

    def stop_animation(self):
        """Detiene la animación"""
        self.is_active = False

    def _animate(self):
        """Ejecuta la animación"""
        import random

        while self.is_active:
            # Simular datos de audio
            for i in range(self.bar_count):
                # Suavizar transiciones
                target = random.uniform(0.1, 1.0)
                self.amplitude_data[i] += (target - self.amplitude_data[i]) * 0.3

                # Actualizar altura de la barra
                height = self.amplitude_data[i] * self.winfo_height() * 0.8
                x1, y1, x2, y2 = self.coords(self.bars[i])
                self.coords(
                    self.bars[i],
                    x1, self.winfo_height() - height,
                    x2, self.winfo_height()
                )

            self.update()
            time.sleep(0.05)

        # Reset al detener
        for i, bar in enumerate(self.bars):
            x1, y1, x2, y2 = self.coords(bar)
            self.coords(bar, x1, self.winfo_height(), x2, self.winfo_height())
            self.amplitude_data[i] = 0


class CircularProgress(ctk.CTkCanvas):
    """Indicador de progreso circular animado"""

    def __init__(self, master, size=100, **kwargs):
        super().__init__(master, width=size, height=size, **kwargs)
        self.configure(bg="#1a1a1a", highlightthickness=0)

        self.size = size
        self.center = size // 2
        self.radius = (size - 20) // 2
        self.progress = 0
        self.is_animating = False

        self._draw_background()

    def _draw_background(self):
        """Dibuja el círculo de fondo"""
        self.create_oval(
            10, 10, self.size - 10, self.size - 10,
            outline="#333333",
            width=8
        )

    def set_progress(self, value, animate=True):
        """Establece el progreso (0-100)"""
        if animate:
            threading.Thread(
                target=self._animate_progress,
                args=(value,),
                daemon=True
            ).start()
        else:
            self.progress = value
            self._draw_progress()

    def _animate_progress(self, target_value):
        """Anima el progreso hacia el valor objetivo"""
        steps = 30
        increment = (target_value - self.progress) / steps

        for _ in range(steps):
            self.progress += increment
            self._draw_progress()
            time.sleep(0.02)

    def _draw_progress(self):
        """Dibuja el arco de progreso"""
        # Limpiar arco anterior
        self.delete("progress")

        # Calcular ángulo
        angle = (self.progress / 100) * 360

        # Dibujar arco
        self.create_arc(
            10, 10, self.size - 10, self.size - 10,
            start=90,
            extent=-angle,
            outline="#4CAF50",
            width=8,
            style="arc",
            tags="progress"
        )

        # Texto de porcentaje
        self.delete("text")
        self.create_text(
            self.center, self.center,
            text=f"{int(self.progress)}%",
            fill="white",
            font=("Arial", 16, "bold"),
            tags="text"
        )


class AnimatedCard(ctk.CTkFrame):
    """Tarjeta con animación de entrada"""

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(corner_radius=15)

        # Estado inicial (oculto)
        self.place(relx=1.5, rely=0)

    def slide_in(self, target_x=0.5, duration=0.5):
        """Anima la entrada de la tarjeta"""
        steps = 30
        current_x = 1.5
        increment = (target_x - current_x) / steps
        delay = duration / steps

        def animate():
            nonlocal current_x
            for _ in range(steps):
                current_x += increment
                self.place(relx=current_x, rely=0.5, anchor="center")
                self.update()
                time.sleep(delay)

        threading.Thread(target=animate, daemon=True).start()

    def slide_out(self, duration=0.5):
        """Anima la salida de la tarjeta"""
        self.slide_in(target_x=-0.5, duration=duration)


class FloatingNotification(ctk.CTkFrame):
    """Notificación flotante con animación"""

    def __init__(self, master, message, notification_type="info", duration=3000):
        super().__init__(master)

        self.duration = duration

        # Colores según tipo
        colors = {
            "info": "#2196F3",
            "success": "#4CAF50",
            "warning": "#FF9800",
            "error": "#f44336"
        }

        self.configure(
            corner_radius=10,
            fg_color=colors.get(notification_type, "#2196F3")
        )

        # Contenido
        self.label = ctk.CTkLabel(
            self,
            text=message,
            font=ctk.CTkFont(size=14),
            text_color="white"
        )
        self.label.pack(padx=20, pady=10)

        # Posición inicial (fuera de la pantalla)
        self.place(relx=0.5, y=-100, anchor="n")

        # Iniciar animación
        self.slide_in()

    def slide_in(self):
        """Anima la entrada de la notificación"""
        target_y = 20
        steps = 20
        current_y = -100
        increment = (target_y - current_y) / steps

        def animate():
            nonlocal current_y
            for _ in range(steps):
                current_y += increment
                self.place(relx=0.5, y=current_y, anchor="n")
                self.update()
                time.sleep(0.01)

            # Programar salida
            self.after(self.duration, self.slide_out)

        threading.Thread(target=animate, daemon=True).start()

    def slide_out(self):
        """Anima la salida de la notificación"""
        steps = 20
        current_y = 20
        target_y = -100
        increment = (target_y - current_y) / steps

        def animate():
            nonlocal current_y
            for _ in range(steps):
                current_y += increment
                self.place(relx=0.5, y=current_y, anchor="n")
                self.update()
                time.sleep(0.01)

            # Destruir al finalizar
            self.destroy()

        threading.Thread(target=animate, daemon=True).start()


class AnimatedSwitch(ctk.CTkSwitch):
    """Switch con animación personalizada"""

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(
            button_color="#4CAF50",
            button_hover_color="#45a049",
            progress_color="#81C784"
        )


class LoadingSpinner(ctk.CTkCanvas):
    """Spinner de carga animado"""

    def __init__(self, master, size=50, **kwargs):
        super().__init__(master, width=size, height=size, **kwargs)
        self.configure(bg="#1a1a1a", highlightthickness=0)

        self.size = size
        self.center = size // 2
        self.is_spinning = False
        self.angle = 0

    def start(self):
        """Inicia la animación del spinner"""
        self.is_spinning = True
        self._animate()

    def stop(self):
        """Detiene la animación"""
        self.is_spinning = False

    def _animate(self):
        """Ejecuta la animación de rotación"""
        if self.is_spinning:
            self.delete("spinner")

            # Dibujar arco
            self.create_arc(
                5, 5, self.size - 5, self.size - 5,
                start=self.angle,
                extent=90,
                outline="#4CAF50",
                width=4,
                style="arc",
                tags="spinner"
            )

            # Incrementar ángulo
            self.angle = (self.angle + 10) % 360

            # Continuar animación
            self.after(20, self._animate)


if __name__ == "__main__":
    # Demo de componentes
    root = ctk.CTk()
    root.geometry("800x600")
    root.title("Componentes Animados Demo")

    # Ejemplos de uso
    pulse_btn = PulseButton(root, text="Pulse Button")
    pulse_btn.pack(pady=10)
    pulse_btn.start_pulse()

    waveform = WaveformVisualizer(root)
    waveform.pack(pady=10)
    waveform.start_animation()

    progress = CircularProgress(root)
    progress.pack(pady=10)
    progress.set_progress(75)

    spinner = LoadingSpinner(root)
    spinner.pack(pady=10)
    spinner.start()

    root.mainloop()
