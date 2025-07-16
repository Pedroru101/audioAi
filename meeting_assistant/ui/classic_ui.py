"""
Interfaz clásica moderna y minimalista
Inspiración Windows 11/Fluent Design con sidebar y área principal limpia
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QStackedWidget, QScrollArea
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QIcon
from .styles import *
from .components import SidebarButton, StatusIndicator, RoundedWidget

class ClassicUI(QWidget):
    def __init__(self, on_record=None, on_stop=None, on_config=None, on_history=None):
        super().__init__()
        self.on_record = on_record
        self.on_stop = on_stop
        self.on_config = on_config
        self.on_history = on_history

        self.setWindowTitle("Meeting Assistant - Clásico")
        self.setMinimumSize(700, 420)
        self.setStyleSheet(WINDOW_STYLE)
        apply_window_shadow(self)
        self.setup_ui()

    def setup_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Sidebar
        sidebar = QFrame()
        sidebar.setFixedWidth(70)
        sidebar.setStyleSheet(SIDEBAR_STYLE)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 20, 0, 20)
        sidebar_layout.setSpacing(12)

        btn_history = SidebarButton("Historial", icon="🕓")
        btn_history.clicked.connect(self.on_history)
        btn_config = SidebarButton("Config", icon="⚙️")
        btn_config.clicked.connect(self.on_config)
        btn_export = SidebarButton("Exportar", icon="⬇️")
        # btn_export.clicked.connect(self.on_export)  # Implementar si es necesario

        sidebar_layout.addWidget(btn_history)
        sidebar_layout.addWidget(btn_config)
        sidebar_layout.addWidget(btn_export)
        sidebar_layout.addStretch()

        # Área principal
        content = QFrame()
        content.setStyleSheet(CONTENT_AREA)
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(24, 24, 24, 24)
        content_layout.setSpacing(18)

        # Título y descripción
        lbl_title = QLabel("Meeting Assistant")
        lbl_title.setStyleSheet(LABEL_TITLE)
        content_layout.addWidget(lbl_title)
        lbl_desc = QLabel("Tu asistente todo-en-uno: graba, transcribe y resume tus reuniones virtuales, generando propuestas de acción inteligentes.")
        lbl_desc.setWordWrap(True)
        lbl_desc.setStyleSheet(LABEL_SECONDARY)
        content_layout.addWidget(lbl_desc)

        # Botones principales
        btns_layout = QHBoxLayout()
        self.btn_record = QPushButton("🎤 Grabar")
        self.btn_record.setStyleSheet(BUTTON_PRIMARY)
        self.btn_record.setFixedHeight(44)
        self.btn_record.clicked.connect(self.on_record)

        self.btn_stop = QPushButton("⏹ Detener")
        self.btn_stop.setStyleSheet(BUTTON_SECONDARY)
        self.btn_stop.setFixedHeight(44)
        self.btn_stop.clicked.connect(self.on_stop)

        btns_layout.addWidget(self.btn_record)
        btns_layout.addWidget(self.btn_stop)
        content_layout.addLayout(btns_layout)

        # Estado
        self.status = StatusIndicator()
        content_layout.addWidget(self.status)

        # Transcripción y resumen
        self.transcription_label = QLabel("Transcripción:")
        self.transcription_label.setStyleSheet(LABEL_SECONDARY)
        self.transcription_text = QLabel("")
        self.transcription_text.setWordWrap(True)
        self.transcription_text.setStyleSheet(LABEL_PRIMARY)

        self.summary_label = QLabel("Resumen:")
        self.summary_label.setStyleSheet(LABEL_SECONDARY)
        self.summary_text = QLabel("")
        self.summary_text.setWordWrap(True)
        self.summary_text.setStyleSheet(LABEL_PRIMARY)

        # Scroll area para textos largos
        scroll = QScrollArea()
        scroll.setStyleSheet(SCROLL_AREA)
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(10)
        scroll_layout.addWidget(self.transcription_label)
        scroll_layout.addWidget(self.transcription_text)
        scroll_layout.addWidget(self.summary_label)
        scroll_layout.addWidget(self.summary_text)
        scroll.setWidget(scroll_content)
        content_layout.addWidget(scroll, stretch=1)

        main_layout.addWidget(sidebar)
        main_layout.addWidget(content, stretch=1)

        self.setLayout(main_layout)

    def set_status(self, text, color="#fff"):
        # Mapea color a tipo de estado
        if color == "#f00":
            self.status.set_status(text, "recording")
        elif color == "#ff0":
            self.status.set_status(text, "processing")
        elif color == "#0f0":
            self.status.set_status(text, "success")
        else:
            self.status.set_status(text, "normal")

    def set_transcription(self, text):
        self.transcription_text.setText(text)

    def set_summary(self, text):
        self.summary_text.setText(text)

    def run(self):
        self.show()

    def close(self):
        super().close()
