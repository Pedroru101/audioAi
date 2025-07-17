"""
Sistema de estilos centralizado para Meeting Assistant
Paleta de colores oscuros con acentos azulados - Inspiración Windows 11/Fluent Design
"""

# Paleta de colores
COLORS = {
    'primary_bg': '#0b0c10',           # Fondo principal oscuro espacial
    'secondary_bg': '#13151a',        # Fondo secundario
    'accent_bg': '#1f2128',           # Fondo de acentos
    'hover_bg': '#404040',            # Hover states
    'active_bg': '#00e8ff',           # Cian neon activo
    'active_hover': '#00c2d6',        # Cian hover
    'text_primary': '#ffffff',        # Texto principal
    'text_secondary': '#cccccc',      # Texto secundario
    'text_muted': '#999999',          # Texto deshabilitado
    'border': '#404040',              # Bordes
    'success': '#107c10',             # Verde éxito
    'warning': '#ff8c00',             # Naranja advertencia
    'error': '#d13438',               # Rojo error
    'recording': '#ff4444',           # Rojo grabación
}

# Tipografía
FONTS = {
    'primary': 'Segoe UI',
    'secondary': 'Segoe UI Semibold',
    'mono': 'Consolas',
}

# Estilos base para ventanas
WINDOW_STYLE = f"""
    QWidget {{
        background-color: {COLORS['primary_bg']};
        color: {COLORS['text_primary']};
        font-family: '{FONTS['primary']}';
        font-size: 12px;
    }}
"""

# Estilo para botones principales
BUTTON_PRIMARY = f"""
    QPushButton {{
        background-color: {COLORS['active_bg']};
        color: {COLORS['text_primary']};
        border: none;
        border-radius: 8px;
        padding: 12px 24px;
        font-family: '{FONTS['secondary']}';
        font-size: 13px;
        font-weight: 600;
    }}
    QPushButton:hover {{
        background-color: {COLORS['active_hover']};
    }}
    QPushButton:pressed {{
        background-color: #005a9e;
    }}
    QPushButton:disabled {{
        background-color: {COLORS['accent_bg']};
        color: {COLORS['text_muted']};
    }}
"""

# Estilo para botones secundarios
BUTTON_SECONDARY = f"""
    QPushButton {{
        background-color: {COLORS['secondary_bg']};
        color: {COLORS['text_primary']};
        border: 1px solid {COLORS['border']};
        border-radius: 8px;
        padding: 10px 20px;
        font-family: '{FONTS['primary']}';
        font-size: 12px;
    }}
    QPushButton:hover {{
        background-color: {COLORS['hover_bg']};
        border-color: {COLORS['active_bg']};
    }}
    QPushButton:pressed {{
        background-color: {COLORS['accent_bg']};
    }}
"""

# Estilo para botón de grabación
RECORD_BUTTON = f"""
    QPushButton {{
        background-color: {COLORS['recording']};
        color: {COLORS['text_primary']};
        border: none;
        border-radius: 25px;
        font-family: '{FONTS['secondary']}';
        font-size: 14px;
        font-weight: 600;
        min-width: 50px;
        min-height: 50px;
    }}
    QPushButton:hover {{
        background-color: #ff6666;
        transform: scale(1.05);
    }}
    QPushButton:pressed {{
        background-color: #cc3333;
    }}
"""

# Estilo para botón de grabación cuando está activo
RECORD_BUTTON_ACTIVE = f"""
    QPushButton {{
        background-color: {COLORS['success']};
        color: {COLORS['text_primary']};
        border: none;
        border-radius: 25px;
        font-family: '{FONTS['secondary']}';
        font-size: 14px;
        font-weight: 600;
        min-width: 50px;
        min-height: 50px;
    }}
    QPushButton:hover {{
        background-color: #13a313;
    }}
    QPushButton:pressed {{
        background-color: #0e7a0e;
    }}
"""

# Estilo para labels
LABEL_PRIMARY = f"""
    QLabel {{
        color: {COLORS['text_primary']};
        font-family: '{FONTS['primary']}';
        font-size: 12px;
    }}
"""

LABEL_SECONDARY = f"""
    QLabel {{
        color: {COLORS['text_secondary']};
        font-family: '{FONTS['primary']}';
        font-size: 11px;
    }}
"""

LABEL_TITLE = f"""
    QLabel {{
        color: {COLORS['text_primary']};
        font-family: '{FONTS['secondary']}';
        font-size: 18px;
        font-weight: 600;
    }}
"""

# Estilo para sidebar
SIDEBAR_STYLE = f"""
    QWidget {{
        background-color: {COLORS['secondary_bg']};
        border-right: 1px solid {COLORS['border']};
    }}
"""

# Estilo para botones del sidebar
SIDEBAR_BUTTON = f"""
    QPushButton {{
        background-color: transparent;
        color: {COLORS['text_secondary']};
        border: none;
        border-radius: 6px;
        padding: 12px;
        text-align: left;
        font-family: '{FONTS['primary']}';
        font-size: 12px;
        margin: 2px;
    }}
    QPushButton:hover {{
        background-color: {COLORS['hover_bg']};
        color: {COLORS['text_primary']};
    }}
    QPushButton:pressed {{
        background-color: {COLORS['accent_bg']};
    }}
"""

# Estilo para área de contenido
CONTENT_AREA = f"""
    QWidget {{
        background-color: {COLORS['primary_bg']};
        border-radius: 8px;
        padding: 16px;
    }}
"""

# Estilo para scroll areas
SCROLL_AREA = f"""
    QScrollArea {{
        background-color: {COLORS['primary_bg']};
        border: none;
        border-radius: 8px;
    }}
    QScrollBar:vertical {{
        background-color: {COLORS['secondary_bg']};
        width: 12px;
        border-radius: 6px;
    }}
    QScrollBar::handle:vertical {{
        background-color: {COLORS['accent_bg']};
        border-radius: 6px;
        min-height: 20px;
    }}
    QScrollBar::handle:vertical:hover {{
        background-color: {COLORS['hover_bg']};
    }}
"""

# Estilo para tooltips
TOOLTIP_STYLE = f"""
    QToolTip {{
        background-color: {COLORS['accent_bg']};
        color: {COLORS['text_primary']};
        border: 1px solid {COLORS['border']};
        border-radius: 4px;
        padding: 8px;
        font-family: '{FONTS['primary']}';
        font-size: 11px;
    }}
"""

# Estilo para campos de entrada de texto
INPUT_STYLE = f"""
    QLineEdit,
    QTextEdit,
    QComboBox,
    QSpinBox,
    QDateEdit {{
        background-color: {COLORS['secondary_bg']};
        color: {COLORS['text_primary']};
        border: 1px solid {COLORS['border']};
        border-radius: 5px;
        padding: 8px;
        font-family: '{FONTS['primary']}';
        font-size: 13px;
    }}
    QLineEdit:focus,
    QTextEdit:focus,
    QComboBox:focus,
    QSpinBox:focus,
    QDateEdit:focus {{
        border: 1px solid {COLORS['active_bg']};
    }}
"""

# Estilo para QComboBox
COMBO_STYLE = f"""
    QComboBox {{
        background-color: {COLORS['secondary_bg']};
        color: {COLORS['text_primary']};
        border: 1px solid {COLORS['border']};
        border-radius: 5px;
        padding: 5px;
        font-family: '{FONTS['primary']}';
        font-size: 12px;
    }}
    QComboBox::drop-down {{
        border: 0px;
    }}
    QComboBox::down-arrow {{
        image: url(assets/icons/arrow_down.png); /* Asegúrate de tener este icono */
        width: 10px;
        height: 10px;
    }}
    QComboBox:on {{
        border: 1px solid {COLORS['active_bg']};
    }}
    QComboBox QAbstractItemView {{
        background-color: {COLORS['secondary_bg']};
        color: {COLORS['text_primary']};
        selection-background-color: {COLORS['active_bg']};
        selection-color: white;
        border: 1px solid {COLORS['border']};
    }}
"""

# Función para aplicar sombra a ventanas
def apply_window_shadow(widget):
    """Aplica sombra elegante a una ventana"""
    from PyQt5.QtWidgets import QGraphicsDropShadowEffect
    from PyQt5.QtCore import Qt
    from PyQt5.QtGui import QColor
    
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(20)
    shadow.setXOffset(0)
    shadow.setYOffset(4)
    shadow.setColor(QColor(0, 0, 0, 80))
    widget.setGraphicsEffect(shadow)

# Función para crear animaciones suaves
def create_fade_animation(widget, duration=200):
    """Crea animación de fade para widgets"""
    from PyQt5.QtCore import QPropertyAnimation, QEasingCurve
    from PyQt5.QtWidgets import QGraphicsOpacityEffect
    
    effect = QGraphicsOpacityEffect()
    widget.setGraphicsEffect(effect)
    
    animation = QPropertyAnimation(effect, b"opacity")
    animation.setDuration(duration)
    animation.setStartValue(0)
    animation.setEndValue(1)
    animation.setEasingCurve(QEasingCurve.OutCubic)
    
    return animation