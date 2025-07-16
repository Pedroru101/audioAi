"""
Componentes UI reutilizables para Meeting Assistant
"""
from PyQt5.QtWidgets import (QPushButton, QLabel, QWidget, QVBoxLayout, 
                            QHBoxLayout, QFrame, QGraphicsOpacityEffect)
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtSignal
from PyQt5.QtGui import QFont, QPainter, QPainterPath, QColor
from .styles import *

class ModernButton(QPushButton):
    """Botón moderno con animaciones"""
    
    def __init__(self, text="", icon=None, button_type="primary", parent=None):
        super().__init__(text, parent)
        self.button_type = button_type
        self.setup_style()
        
    def setup_style(self):
        if self.button_type == "primary":
            self.setStyleSheet(BUTTON_PRIMARY)
        elif self.button_type == "secondary":
            self.setStyleSheet(BUTTON_SECONDARY)
        elif self.button_type == "record":
            self.setStyleSheet(RECORD_BUTTON)
        elif self.button_type == "record_active":
            self.setStyleSheet(RECORD_BUTTON_ACTIVE)
        elif self.button_type == "sidebar":
            self.setStyleSheet(SIDEBAR_BUTTON)

class RecordButton(QPushButton):
    """Botón especializado para grabación con estados visuales"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_recording = False
        self.setFixedSize(50, 50)
        self._scale_anim = QPropertyAnimation(self, b"size")
        self._scale_anim.setDuration(350)
        self._scale_anim.setEasingCurve(QEasingCurve.OutBack)
        self._scale_anim.setStartValue(self.size())
        self._scale_anim.setEndValue(self.size())

    def animate_scale_in(self):
        self._scale_anim.stop()
        self._scale_anim.setStartValue(self.size()*2)
        self._scale_anim.setEndValue(self.size())
        self._scale_anim.start()
        self.setup_style()
        
    def setup_style(self):
        self.setStyleSheet(RECORD_BUTTON)
        self.setText("🎤")
        
    def set_recording(self, recording):
        self.is_recording = recording
        if recording:
            self.setStyleSheet(RECORD_BUTTON_ACTIVE)
            self.setText("⏹")
        else:
            self.setStyleSheet(RECORD_BUTTON)
            self.setText("🎤")

class TimeDisplay(QLabel):
    """Display de tiempo de grabación"""
    
    def __init__(self, parent=None):
        super().__init__("00:00", parent)
        self.setStyleSheet(LABEL_SECONDARY)
        self.setAlignment(Qt.AlignCenter)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)
        self.seconds = 0
        
    def start_timer(self):
        self.seconds = 0
        self.timer.start(1000)
        
    def stop_timer(self):
        self.timer.stop()
        self.seconds = 0
        self.setText("00:00")
        
    def update_time(self):
        self.seconds += 1
        minutes = self.seconds // 60
        seconds = self.seconds % 60
        self.setText(f"{minutes:02d}:{seconds:02d}")

class StatusIndicator(QLabel):
    """Indicador de estado con colores"""
    
    def __init__(self, parent=None):
        super().__init__("Listo", parent)
        self.setStyleSheet(LABEL_PRIMARY)
        
    def set_status(self, text, status_type="normal"):
        self.setText(text)
        colors = {
            "normal": COLORS['text_primary'],
            "recording": COLORS['recording'],
            "processing": COLORS['warning'],
            "success": COLORS['success'],
            "error": COLORS['error']
        }
        color = colors.get(status_type, COLORS['text_primary'])
        self.setStyleSheet(f"QLabel {{ color: {color}; font-family: '{FONTS['primary']}'; font-size: 12px; }}")

class RoundedWidget(QWidget):
    """Widget con esquinas redondeadas"""
    
    def __init__(self, radius=12, parent=None):
        super().__init__(parent)
        self.radius = radius
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        path = QPainterPath()
        path.addRoundedRect(self.rect(), self.radius, self.radius)
        
        painter.fillPath(path, QColor(COLORS['primary_bg']))
        painter.setPen(QColor(COLORS['border']))
        painter.drawPath(path)

class SidebarButton(QPushButton):
    """Botón especializado para sidebar"""
    
    def __init__(self, text, icon=None, parent=None):
        super().__init__(parent)
        self.setText(f"  {icon}  {text}" if icon else f"  {text}")
        self.setStyleSheet(SIDEBAR_BUTTON)
        self.setFixedHeight(40)

class FloatingTooltip(QLabel):
    """Tooltip flotante personalizado"""
    
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet(f"""
            QLabel {{
                background-color: {COLORS['accent_bg']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                padding: 8px 12px;
                font-family: '{FONTS['primary']}';
                font-size: 11px;
            }}
        """)
        self.setWindowFlags(Qt.ToolTip)
        
    def show_at(self, pos):
        self.move(pos)
        self.show()
        
        # Auto-hide después de 3 segundos
        QTimer.singleShot(3000, self.hide)