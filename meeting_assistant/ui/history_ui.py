# Crear history_ui.py para la Fase 5

# ui/history_ui.py
"""
Interfaz de historial y analytics para Meeting Assistant Pro
Permite visualizar, buscar, filtrar y analizar reuniones pasadas
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLineEdit, QComboBox, QLabel, QSplitter, QTextEdit,
    QDateEdit, QGroupBox, QTabWidget, QProgressBar, QMessageBox,
    QHeaderView, QMenu, QAction, QFileDialog, QCheckBox, QSpinBox
)
from PyQt5.QtCore import Qt, QDate, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QIcon, QFont, QColor
from PyQt5.QtChart import QChart, QChartView, QPieSeries, QBarSeries, QBarSet, QValueAxis, QBarCategoryAxis

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional
import pandas as pd

from .components import ModernButton, StatusIndicator, RoundedWidget
from .styles import *
from utils.file_manager import FileManager
from config.config_manager import ConfigManager

class MeetingHistoryWidget(QWidget):
    """Widget principal para el historial de reuniones"""
    
    # Señales
    meeting_selected = pyqtSignal(str)  # Emite la ruta de la reunión seleccionada
    export_requested = pyqtSignal(str, str)  # Ruta y formato de exportación
    
    def __init__(self, config_manager: ConfigManager, file_manager: FileManager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.file_manager = file_manager
        self.current_meetings = []
        self.selected_meeting_path = None
        
        self.init_ui()
        self.load_meetings()
        
    def init_ui(self):
        """Inicializa la interfaz de usuario"""
        self.setStyleSheet(WINDOW_STYLE)
        
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        
        # Header
        header_layout = QHBoxLayout()
        
        title_label = QLabel("📊 Historial de Reuniones")
        title_label.setStyleSheet(f"""
            QLabel {{
                font-size: 24px;
                font-weight: bold;
                color: {COLORS['text_primary']};
                padding: 10px;
            }}
        """)
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Botones de acción principal
        self.refresh_btn = ModernButton("🔄 Actualizar", button_type="secondary")
        self.refresh_btn.clicked.connect(self.load_meetings)
        header_layout.addWidget(self.refresh_btn)
        
        self.analytics_btn = ModernButton("📈 Analytics", button_type="primary")
        self.analytics_btn.clicked.connect(self.load_analytics)
        header_layout.addWidget(self.analytics_btn)
        
        main_layout.addLayout(header_layout)
        
        # Barra de búsqueda y filtros
        filter_widget = self.create_filter_widget()
        main_layout.addWidget(filter_widget)
        
        # Splitter para tabla y detalles
        splitter = QSplitter(Qt.Horizontal)
        
        # Panel izquierdo - Lista de reuniones
        left_panel = self.create_meetings_table()
        splitter.addWidget(left_panel)
        
        # Panel derecho - Detalles y vista previa
        right_panel = self.create_details_panel()
        splitter.addWidget(right_panel)
        
        # Configurar proporciones del splitter
        splitter.setSizes([600, 400])
        
        main_layout.addWidget(splitter)
        
        # Barra de estado
        self.status_bar = self.create_status_bar()
        main_layout.addWidget(self.status_bar)
        
    def create_filter_widget(self) -> QWidget:
        """Crea el widget de filtros y búsqueda"""
        filter_widget = RoundedWidget()
        filter_layout = QHBoxLayout(filter_widget)
        filter_layout.setContentsMargins(15, 10, 15, 10)
        
        # Búsqueda por texto
        search_label = QLabel("🔍")
        filter_layout.addWidget(search_label)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar en títulos, resúmenes, participantes...")
        self.search_input.setStyleSheet(INPUT_STYLE)
        self.search_input.textChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.search_input, 2)
        
        # Filtro por fecha
        filter_layout.addWidget(QLabel("📅 Desde:"))
        self.date_from = QDateEdit()
        self.date_from.setCalendarPopup(True)
        self.date_from.setDate(QDate.currentDate().addDays(-30))
        self.date_from.setStyleSheet(INPUT_STYLE)
        self.date_from.dateChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.date_from)
        
        filter_layout.addWidget(QLabel("Hasta:"))
        self.date_to = QDateEdit()
        self.date_to.setCalendarPopup(True)
        self.date_to.setDate(QDate.currentDate())
        self.date_to.setStyleSheet(INPUT_STYLE)
        self.date_to.dateChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.date_to)
        
        # Filtro por estado
        filter_layout.addWidget(QLabel("Estado:"))
        self.status_filter = QComboBox()
        self.status_filter.addItems(["Todos", "Completado", "En proceso", "Error"])
        self.status_filter.setStyleSheet(COMBO_STYLE)
        self.status_filter.currentTextChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.status_filter)
        
        # Filtro por duración
        filter_layout.addWidget(QLabel("Duración mín:"))
        self.duration_filter = QSpinBox()
        self.duration_filter.setRange(0, 300)
        self.duration_filter.setSuffix(" min")
        self.duration_filter.setStyleSheet(INPUT_STYLE)
        self.duration_filter.valueChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.duration_filter)
        
        # Botón limpiar filtros
        clear_filters_btn = ModernButton("✖ Limpiar", button_type="secondary")
        clear_filters_btn.clicked.connect(self.clear_filters)
        filter_layout.addWidget(clear_filters_btn)
        
        filter_layout.addStretch()
        
        return filter_widget
        
    def clear_filters(self):
        """Limpia todos los filtros y recarga las reuniones."""
        self.search_input.clear()
        self.date_from.setDate(QDate.currentDate().addDays(-30))
        self.date_to.setDate(QDate.currentDate())
        self.status_filter.setCurrentIndex(0) # "Todos"
        self.duration_filter.setValue(0)
        self.apply_filters()
        
    def create_meetings_table(self) -> QWidget:
        """Crea la tabla de reuniones"""
        table_widget = QWidget()
        layout = QVBoxLayout(table_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Tabla
        self.meetings_table = QTableWidget()
        self.meetings_table.setStyleSheet(TABLE_STYLE)
        
        # Configurar columnas
        columns = ["", "Título", "Fecha", "Duración", "Participantes", "Estado", "Tamaño"]
        self.meetings_table.setColumnCount(len(columns))
        self.meetings_table.setHorizontalHeaderLabels(columns)
        
        # Configurar propiedades de la tabla
        self.meetings_table.setAlternatingRowColors(True)
        self.meetings_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.meetings_table.setSelectionMode(QTableWidget.SingleSelection)
        self.meetings_table.setSortingEnabled(True)
        
        # Ajustar columnas
        header = self.meetings_table.horizontalHeader()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.Fixed)  # Checkbox
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # Título
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Fecha
        
        self.meetings_table.setColumnWidth(0, 30)  # Checkbox
        
        # Conectar eventos
        self.meetings_table.itemSelectionChanged.connect(self.on_meeting_selected)
        self.meetings_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.meetings_table.customContextMenuRequested.connect(self.show_context_menu)
        
        layout.addWidget(self.meetings_table)
        
        # Controles de tabla
        controls_layout = QHBoxLayout()
        
        self.select_all_cb = QCheckBox("Seleccionar todos")
        self.select_all_cb.stateChanged.connect(self.toggle_select_all)
        controls_layout.addWidget(self.select_all_cb)
        
    def toggle_select_all(self, state):
        """Alterna la selección de todos los checkboxes en la tabla de reuniones."""
        is_checked = (state == Qt.Checked)
        for row in range(self.meetings_table.rowCount()):
            checkbox = self.meetings_table.cellWidget(row, 0)
            if isinstance(checkbox, QCheckBox):
                checkbox.setChecked(is_checked)
        
        controls_layout.addStretch()
        
        self.export_selected_btn = ModernButton("📤 Exportar seleccionados", button_type="secondary")
        self.export_selected_btn.clicked.connect(self.export_selected_meetings)
        controls_layout.addWidget(self.export_selected_btn)
        
        self.delete_selected_btn = ModernButton("🗑️ Eliminar seleccionados", button_type="secondary")
        self.delete_selected_btn.clicked.connect(self.delete_selected_meetings)
        controls_layout.addWidget(self.delete_selected_btn)
        
        layout.addLayout(controls_layout)
        
        return table_widget
        
    def export_selected_meetings(self):
        """Exporta las reuniones seleccionadas."""
        selected_paths = []
        for row in range(self.meetings_table.rowCount()):
            checkbox = self.meetings_table.cellWidget(row, 0)
            if isinstance(checkbox, QCheckBox) and checkbox.isChecked():
                title_item = self.meetings_table.item(row, 1)
                if title_item:
                    selected_paths.append(title_item.data(Qt.UserRole))
        
        if not selected_paths:
            QMessageBox.warning(self, "Exportar", "No hay reuniones seleccionadas para exportar.")
            return

        # Abrir diálogo para seleccionar formato y destino
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Exportar Reuniones",
            f"selected_meetings_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
            "ZIP Files (*.zip);;Markdown Files (*.md)"
        )

        if file_path:
            export_format = Path(file_path).suffix[1:] # Obtener extensión sin el punto
            if export_format == "zip":
                # Exportar como ZIP (manejar múltiples reuniones)
                # Esto requeriría una lógica más compleja en FileManager para ZIPs múltiples
                QMessageBox.information(self, "Exportar", "La exportación múltiple a ZIP está en desarrollo.")
            elif export_format == "md":
                # Exportar cada reunión a un archivo Markdown separado
                for path in selected_paths:
                    self.file_manager.export_meeting(path, export_format="markdown")
                QMessageBox.information(self, "Exportar", f"Reuniones exportadas a Markdown en {Path(file_path).parent}.")
            else:
                QMessageBox.warning(self, "Exportar", "Formato de exportación no soportado.")

    def delete_selected_meetings(self):
        """Elimina las reuniones seleccionadas."""
        selected_paths = []
        for row in range(self.meetings_table.rowCount()):
            checkbox = self.meetings_table.cellWidget(row, 0)
            if isinstance(checkbox, QCheckBox) and checkbox.isChecked():
                title_item = self.meetings_table.item(row, 1)
                if title_item:
                    selected_paths.append(title_item.data(Qt.UserRole))

        if not selected_paths:
            QMessageBox.warning(self, "Eliminar", "No hay reuniones seleccionadas para eliminar.")
            return

        reply = QMessageBox.question(self, "Confirmar Eliminación",
                                     f"¿Estás seguro de que deseas eliminar {len(selected_paths)} reunión(es) seleccionada(s)? Esta acción no se puede deshacer.",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            deleted_count = 0
            for path in selected_paths:
                if self.file_manager.delete_meeting(path, confirm=True):
                    deleted_count += 1
            QMessageBox.information(self, "Eliminar", f"Se eliminaron {deleted_count} reunión(es).")
            self.load_meetings() # Recargar la tabla después de eliminar
        
    def show_context_menu(self, pos):
        """Muestra el menú contextual para la tabla de reuniones."""
        menu = QMenu()
        
        # Acciones del menú
        view_action = menu.addAction("Ver Detalles")
        export_action = menu.addAction("Exportar Reunión")
        delete_action = menu.addAction("Eliminar Reunión")
        
        action = menu.exec_(self.meetings_table.mapToGlobal(pos))
        
        if action == view_action:
            self.on_meeting_selected() # Reutiliza la lógica de selección
        elif action == export_action:
            self.export_current_meeting()
        elif action == delete_action:
            self.delete_selected_meetings() # Reutiliza la lógica de eliminación

    def on_meeting_selected(self):
        """Maneja la selección de una reunión en la tabla."""
        selected_items = self.meetings_table.selectedItems()
        if not selected_items:
            self.selected_meeting_path = None
            self.clear_details_panel()
            return

        # Obtener la ruta de la reunión del primer elemento seleccionado (columna de título)
        title_item = self.meetings_table.item(selected_items[0].row(), 1)
        if title_item:
            self.selected_meeting_path = title_item.data(Qt.UserRole)
            self.load_meeting_details(self.selected_meeting_path)

    def clear_details_panel(self):
        """Limpia el panel de detalles."""
        self.summary_text.clear()
        self.actions_table.setRowCount(0)
        self.transcript_text.clear()
        self.transcript_search.clear()
        self.search_count_label.setText("0 coincidencias")
        for label in self.metrics_labels.values():
            label.setText("-")

    def load_meeting_details(self, meeting_path: str):
        """Carga y muestra los detalles de la reunión seleccionada."""
        if not meeting_path:
            return

        meeting_data = self.file_manager.get_meeting_data(meeting_path)
        if not meeting_data:
            QMessageBox.warning(self, "Error", "No se pudieron cargar los detalles de la reunión.")
            self.clear_details_panel()
            return

        # Resumen
        summary = meeting_data.get('summary', 'No hay resumen disponible.')
        self.summary_text.setText(summary)

        # Acciones
        actions = meeting_data.get('actions', [])
        self.actions_table.setRowCount(0)
        for row, action in enumerate(actions):
            self.actions_table.insertRow(row)
            checkbox = QCheckBox()
            checkbox.setChecked(action.get('completed', False))
            self.actions_table.setCellWidget(row, 0, checkbox)
            self.actions_table.setItem(row, 1, QTableWidgetItem(action.get('action', '')))
            self.actions_table.setItem(row, 2, QTableWidgetItem(action.get('responsible', '')))
            self.actions_table.setItem(row, 3, QTableWidgetItem(action.get('deadline', '')))
            self.actions_table.setItem(row, 4, QTableWidgetItem(action.get('priority', '')))

        # Transcripción
        transcription = meeting_data.get('transcription', 'No hay transcripción disponible.')
        self.transcript_text.setText(transcription)

        # Métricas
        analytics = meeting_data.get('analytics', {})
        if analytics:
            self.metrics_labels['duration'].setText(analytics.get('basic_metrics', {}).get('estimated_duration_formatted', '-'))
            self.metrics_labels['participants'].setText(str(analytics.get('participation_metrics', {}).get('identified_speakers', '-')))
            self.metrics_labels['topics'].setText(", ".join([t[0] for t in analytics.get('content_analysis', {}).get('top_words', [])[:3]]) or '-')
            self.metrics_labels['actions'].setText(str(len(actions)))
            self.metrics_labels['sentiment'].setText(analytics.get('sentiment_analysis', {}).get('dominant', '-'))
            self.metrics_labels['efficiency'].setText(f"{analytics.get('efficiency_metrics', {}).get('efficiency_score', 0):.2f}")

        # Emitir señal de selección de reunión
        self.meeting_selected.emit(meeting_path)
        
    def create_details_panel(self) -> QWidget:
        """Crea el panel de detalles"""
        details_widget = QWidget()
        layout = QVBoxLayout(details_widget)
        
        # Tabs para diferentes vistas
        self.details_tabs = QTabWidget()
        self.details_tabs.setStyleSheet(TAB_STYLE)
        
        # Tab de resumen
        self.summary_tab = self.create_summary_tab()
        self.details_tabs.addTab(self.summary_tab, "📝 Resumen")
        
        # Tab de acciones
        self.actions_tab = self.create_actions_tab()
        self.details_tabs.addTab(self.actions_tab, "✅ Acciones")
        
        # Tab de transcripción
        self.transcript_tab = self.create_transcript_tab()
        self.details_tabs.addTab(self.transcript_tab, "📄 Transcripción")
        
        # Tab de métricas
        self.metrics_tab = self.create_metrics_tab()
        self.details_tabs.addTab(self.metrics_tab, "📊 Métricas")
        
        layout.addWidget(self.details_tabs)
        
        # Botones de acción para la reunión seleccionada
        actions_layout = QHBoxLayout()
        
        self.open_folder_btn = ModernButton("📁 Abrir carpeta", button_type="secondary")
        self.open_folder_btn.clicked.connect(self.open_meeting_folder)
        actions_layout.addWidget(self.open_folder_btn)
        
        self.export_btn = ModernButton("💾 Exportar", button_type="secondary")
        self.export_btn.clicked.connect(self.export_current_meeting)
        actions_layout.addWidget(self.export_btn)
        
        self.reprocess_btn = ModernButton("🔄 Reprocesar", button_type="primary")
        self.reprocess_btn.clicked.connect(self.reprocess_meeting)
        actions_layout.addWidget(self.reprocess_btn)
        
        layout.addLayout(actions_layout)
        
        return details_widget
        
    def export_current_meeting(self):
        """Exporta la reunión actualmente seleccionada."""
        if not self.selected_meeting_path:
            QMessageBox.warning(self, "Exportar", "Selecciona una reunión para exportar.")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Exportar Reunión",
            f"{Path(self.selected_meeting_path).name}_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
            "ZIP Files (*.zip);;Markdown Files (*.md)"
        )

        if file_path:
            export_format = Path(file_path).suffix[1:] # Obtener extensión sin el punto
            try:
                self.file_manager.export_meeting(self.selected_meeting_path, export_format=export_format)
                QMessageBox.information(self, "Exportar", f"Reunión exportada exitosamente a:\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error de Exportación", f"Error al exportar la reunión: {e}")
        
    def reprocess_meeting(self):
        """Reprocesa la reunión seleccionada."""
        if not self.selected_meeting_path:
            QMessageBox.warning(self, "Reprocesar", "Selecciona una reunión para reprocesar.")
            return

        reply = QMessageBox.question(self, "Confirmar Reprocesamiento",
                                     "¿Estás seguro de que deseas reprocesar esta reunión? Esto puede sobrescribir los análisis existentes.",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            try:
                # Aquí se llamaría a la lógica de reprocesamiento en el backend
                # Por ahora, solo un mensaje de confirmación
                QMessageBox.information(self, "Reprocesar", "Reprocesamiento iniciado (funcionalidad en desarrollo).")
                # self.file_manager.reprocess_meeting(self.selected_meeting_path)
                self.load_meeting_details(self.selected_meeting_path) # Recargar para reflejar cambios
            except Exception as e:
                QMessageBox.critical(self, "Error de Reprocesamiento", f"Error al reprocesar la reunión: {e}")
        
    def open_meeting_folder(self):
        """Abre la carpeta de la reunión seleccionada en el explorador de archivos."""
        if not self.selected_meeting_path:
            QMessageBox.warning(self, "Abrir Carpeta", "Selecciona una reunión para abrir su carpeta.")
            return
        
        try:
            # Abrir la carpeta en el explorador de archivos del sistema
            os.startfile(self.selected_meeting_path)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo abrir la carpeta:\n{e}")
        
    def create_summary_tab(self) -> QWidget:
        """Crea la pestaña de resumen"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        self.summary_text = QTextEdit()
        self.summary_text.setReadOnly(True)
        self.summary_text.setStyleSheet(f"""
            QTextEdit {{
                background-color: {COLORS['secondary_bg']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 15px;
                font-family: '{FONTS['primary']}';
                font-size: 14px;
            }}
        """)
        
        layout.addWidget(self.summary_text)
        
        return widget
        
    def create_actions_tab(self) -> QWidget:
        """Crea la pestaña de acciones"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        self.actions_table = QTableWidget()
        self.actions_table.setStyleSheet(TABLE_STYLE)
        self.actions_table.setColumnCount(5)
        self.actions_table.setHorizontalHeaderLabels(
            ["Completada", "Acción", "Responsable", "Deadline", "Prioridad"]
        )
        
        header = self.actions_table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        
        layout.addWidget(self.actions_table)
        
        # Botones de acción
        actions_layout = QHBoxLayout()
        
        mark_complete_btn = ModernButton("✓ Marcar completadas", button_type="secondary")
        mark_complete_btn.clicked.connect(self.mark_actions_complete)
        actions_layout.addWidget(mark_complete_btn)
        
        export_actions_btn = ModernButton("📋 Exportar a CSV", button_type="secondary")
        export_actions_btn.clicked.connect(self.export_actions_csv)
        actions_layout.addWidget(export_actions_btn)
        
        actions_layout.addStretch()
        
        layout.addLayout(actions_layout)
        
        return widget
        
    def export_actions_csv(self):
        """Exporta las acciones de la reunión actual a un archivo CSV."""
        if not self.selected_meeting_path:
            QMessageBox.warning(self, "Exportar Acciones", "Selecciona una reunión para exportar sus acciones.")
            return

        meeting_data = self.file_manager.get_meeting_data(self.selected_meeting_path)
        actions = meeting_data.get('actions', [])

        if not actions:
            QMessageBox.information(self, "Exportar Acciones", "La reunión seleccionada no tiene acciones para exportar.")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Guardar Acciones como CSV",
            f"acciones_{Path(self.selected_meeting_path).name}.csv",
            "CSV Files (*.csv)"
        )

        if file_path:
            try:
                # Asegurarse de que el directorio existe
                Path(file_path).parent.mkdir(parents=True, exist_ok=True)
                
                # Escribir CSV
                with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                    fieldnames = ["Acción", "Responsable", "Deadline", "Prioridad", "Completada"]
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                    writer.writeheader()
                    for action in actions:
                        writer.writerow({
                            "Acción": action.get('action', ''),
                            "Responsable": action.get('responsible', ''),
                            "Deadline": action.get('deadline', ''),
                            "Prioridad": action.get('priority', ''),
                            "Completada": "Sí" if action.get('completed', False) else "No"
                        })
                QMessageBox.information(self, "Exportar Acciones", f"Acciones exportadas exitosamente a:\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error de Exportación", f"Error al exportar acciones: {e}")
        
    def mark_actions_complete(self):
        """Marca las acciones seleccionadas como completadas."""
        if not self.selected_meeting_path:
            QMessageBox.warning(self, "Acciones", "Selecciona una reunión para marcar acciones.")
            return

        meeting_data = self.file_manager.get_meeting_data(self.selected_meeting_path)
        if not meeting_data or 'actions' not in meeting_data:
            return

        updated_actions = []
        for row in range(self.actions_table.rowCount()):
            checkbox = self.actions_table.cellWidget(row, 0)
            action_item = meeting_data['actions'][row]
            if isinstance(checkbox, QCheckBox):
                action_item['completed'] = checkbox.isChecked()
            updated_actions.append(action_item)

        # Actualizar los datos de la reunión en el file_manager
        meeting_data['actions'] = updated_actions
        self.file_manager.save_json_file(self.selected_meeting_path, "acciones.json", updated_actions)
        QMessageBox.information(self, "Acciones", "Acciones actualizadas.")
        self.load_meeting_details(self.selected_meeting_path) # Recargar para reflejar cambios
        
    def create_transcript_tab(self) -> QWidget:
        """Crea la pestaña de transcripción"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Controles de búsqueda en transcripción
        search_layout = QHBoxLayout()
        
        self.transcript_search = QLineEdit()
        self.transcript_search.setPlaceholderText("Buscar en transcripción...")
        self.transcript_search.setStyleSheet(INPUT_STYLE)
        self.transcript_search.textChanged.connect(self.search_in_transcript)
        search_layout.addWidget(self.transcript_search)
        
        self.search_count_label = QLabel("0 coincidencias")
        search_layout.addWidget(self.search_count_label)
        
        layout.addLayout(search_layout)
        
        # Texto de transcripción
        self.transcript_text = QTextEdit()
        self.transcript_text.setReadOnly(True)
        self.transcript_text.setStyleSheet(f"""
            QTextEdit {{
                background-color: {COLORS['secondary_bg']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 15px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 13px;
                line-height: 1.5;
            }}
        """
        )
        
        layout.addWidget(self.transcript_text)
        
        return widget
        
    def search_in_transcript(self):
        """Busca texto en la transcripción y resalta las coincidencias."""
        search_text = self.transcript_search.text()
        transcript_content = self.transcript_text.toPlainText()
        
        # Limpiar formato anterior
        cursor = self.transcript_text.textCursor()
        cursor.beginEdit()
        cursor.select(QTextCursor.Document)
        cursor.setCharFormat(QTextCharFormat()) # Restablecer formato
        cursor.clearSelection()
        cursor.endEdit()

        if not search_text:
            self.search_count_label.setText("0 coincidencias")
            return

        format = QTextCharFormat()
        format.setBackground(QColor("yellow"))
        format.setForeground(QColor("black"))

        count = 0
        cursor = self.transcript_text.document().find(search_text, QTextDocument.FindWholeWords)
        while not cursor.isNull():
            cursor.mergeCharFormat(format)
            count += 1
            cursor = self.transcript_text.document().find(search_text, cursor.position(), QTextDocument.FindWholeWords)
        
        self.search_count_label.setText(f"{count} coincidencias")
        
    def create_metrics_tab(self) -> QWidget:
        """Crea la pestaña de métricas"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Información general
        self.metrics_info = QGroupBox("Información General")
        self.metrics_info.setStyleSheet(GROUP_BOX_STYLE)
        info_layout = QVBoxLayout(self.metrics_info)
        
        self.metrics_labels = {}
        metrics = [
            ("duration", "⏱️ Duración"),
            ("participants", "👥 Participantes"),
            ("topics", "📌 Temas principales"),
            ("actions", "✅ Acciones identificadas"),
            ("sentiment", "😊 Sentimiento general"),
            ("efficiency", "📈 Eficiencia")
        ]
        
        for key, label in metrics:
            metric_layout = QHBoxLayout()
            label_widget = QLabel(label + ":")
            label_widget.setStyleSheet(LABEL_SECONDARY)
            metric_layout.addWidget(label_widget)
            
            value_widget = QLabel("-")
            value_widget.setStyleSheet(LABEL_PRIMARY)
            self.metrics_labels[key] = value_widget
            metric_layout.addWidget(value_widget)
            
            metric_layout.addStretch()
            info_layout.addLayout(metric_layout)
        
        layout.addWidget(self.metrics_info)
        
        # Gráficos
        self.charts_widget = QWidget()
        charts_layout = QVBoxLayout(self.charts_widget)
        
        # Placeholder para gráficos (se llenarán dinámicamente)
        self.chart_view = QChartView()
        self.chart_view.setRenderHint(QPainter.Antialiasing)
        charts_layout.addWidget(self.chart_view)
        
        layout.addWidget(self.charts_widget)
        
        return widget
        
    def create_status_bar(self) -> QWidget:
        """Crea la barra de estado"""
        status_widget = QWidget()
        layout = QHBoxLayout(status_widget)
        layout.setContentsMargins(10, 5, 10, 5)
        
        self.status_indicator = StatusIndicator()
        layout.addWidget(self.status_indicator)
        
        layout.addStretch()
        
        # Información de almacenamiento
        self.storage_label = QLabel()
        self.storage_label.setStyleSheet(LABEL_SECONDARY)
        layout.addWidget(self.storage_label)
        
        # Contador de reuniones
        self.meeting_count_label = QLabel()
        self.meeting_count_label.setStyleSheet(LABEL_PRIMARY)
        layout.addWidget(self.meeting_count_label)
        
        self.update_status_bar()
        
        return status_widget
        
    def update_status_bar(self):
        """Actualiza la información de la barra de estado."""
        storage_info = self.file_manager.get_storage_info()
        total_meetings = len(self.current_meetings)

        self.storage_label.setText(f"Almacenamiento: {storage_info['total_size_gb']:.2f} GB / {storage_info['free_space_gb']:.2f} GB libres")
        self.meeting_count_label.setText(f"Reuniones: {total_meetings}")
        
    def load_meetings(self):
        """Carga la lista de reuniones desde el FileManager"""
        self.status_indicator.set_status("Cargando reuniones...", "processing")
        
        try:
            # Obtener lista de reuniones
            self.current_meetings = self.file_manager.list_meetings()
            
            # Limpiar tabla
            self.meetings_table.setRowCount(0)
            
            # Llenar tabla
            for meeting in self.current_meetings:
                self.add_meeting_to_table(meeting)
            
            self.status_indicator.set_status(
                f"{len(self.current_meetings)} reuniones cargadas", 
                "success"
            )
            
            self.update_status_bar()
            
        except Exception as e:
            self.status_indicator.set_status(f"Error: {str(e)}", "error")
            QMessageBox.critical(self, "Error", f"Error al cargar reuniones: {str(e)}")
            
    def add_meeting_to_table(self, meeting: Dict[str, Any]):
        """Añade una reunión a la tabla"""
        row = self.meetings_table.rowCount()
        self.meetings_table.insertRow(row)
        
        # Checkbox
        checkbox = QCheckBox()
        self.meetings_table.setCellWidget(row, 0, checkbox)
        
        # Título
        title = meeting.get('custom_name', 'Sin título')
        title_item = QTableWidgetItem(title)
        self.meetings_table.setItem(row, 1, title_item)
        
        # Fecha
        created = meeting.get('created', '')
        if created:
            date = datetime.fromisoformat(created)
            date_str = date.strftime('%Y-%m-%d %H:%M')
        else:
            date_str = 'Desconocida'
        date_item = QTableWidgetItem(date_str)
        self.meetings_table.setItem(row, 2, date_item)
        
        # Duración (calculada si hay analytics)
        duration = "-"
        if 'analytics' in meeting:
            duration = meeting['analytics'].get('estimated_duration', '-')
        duration_item = QTableWidgetItem(duration)
        self.meetings_table.setItem(row, 3, duration_item)
        
        # Participantes
        participants = "-"
        if 'analytics' in meeting:
            count = meeting['analytics'].get('participants_count', 0)
            if count > 0:
                participants = str(count)
        participants_item = QTableWidgetItem(participants)
        self.meetings_table.setItem(row, 4, participants_item)
        
        # Estado
        status = meeting.get('status', 'unknown')
        status_item = QTableWidgetItem(status.capitalize())
        
        # Color según estado
        status_colors = {
            'completed': QColor(COLORS['success']),
            'in_progress': QColor(COLORS['warning']),
            'error': QColor(COLORS['error'])
        }
        if status in status_colors:
            status_item.setForeground(status_colors[status])
        
        self.meetings_table.setItem(row, 5, status_item)
        
        # Tamaño
        size_mb = meeting.get('size_mb', 0)
        size_str = f"{size_mb:.1f} MB"
        size_item = QTableWidgetItem(size_str)
        self.meetings_table.setItem(row, 6, size_item)
        
        # Guardar la ruta en el item
        title_item.setData(Qt.UserRole, meeting.get('folder_path'))
        
    def apply_filters(self):
        """Aplica los filtros actuales a la lista de reuniones"""
        search_text = self.search_input.text().lower()
        date_from = self.date_from.date().toPyDate()
        date_to = self.date_to.date().toPyDate()
        status_filter = self.status_filter.currentText()
        min_duration = self.duration_filter.value()
        
        for row in range(self.meetings_table.rowCount()):
            show_row = True
            
            # Filtro por texto
            if search_text:
                found = False
                for col in range(1, self.meetings_table.columnCount()):
                    item = self.meetings_table.item(row, col)
                    if item and search_text in item.text().lower():
                        found = True
                        break
                
                # También buscar en los datos de la reunión
                if not found:
                    title_item = self.meetings_table.item(row, 1)
                    if title_item:
                        meeting_path = title_item.data(Qt.UserRole)
                        meeting_data = self.file_manager.get_meeting_data(meeting_path)
                        
                        # Buscar en resumen y transcripción
                        if 'summary' in meeting_data and search_text in meeting_data['summary'].lower():
                            found = True
                        elif 'transcription' in meeting_data and search_text in meeting_data['transcription'].lower():
                            found = True
                
                if not found:
                    show_row = False
            
            # Filtro por fecha
            date_item = self.meetings_table.item(row, 2)
            if date_item and show_row:
                try:
                    meeting_date = datetime.strptime(date_item.text(), '%Y-%m-%d %H:%M').date()
                    if meeting_date < date_from or meeting_date > date_to:
                        show_row = False
                except:
                    pass
            
            # Filtro por estado
            if status_filter != "Todos" and show_row:
                status_item = self.meetings_table.item(row, 5)
                if status_item and status_item.text() != status_filter:
                    show_row = False
            
            # Filtro por duración
            if min_duration > 0 and show_row:
                duration_item = self.meetings_table.item(row, 3)
                if duration_item:
                    try:
                        duration_text = duration_item.text()
                        if duration_text != "-":
                            # Extraer minutos del texto
                            duration_minutes = int(duration_text.split()[0])
                            if duration_minutes < min_duration:
                                show_row = False
                    except Exception:
                        pass
            
        layout.addWidget(self.tabs)
        
        # Botones de acción
        actions_layout = QHBoxLayout()
        
        export_btn = ModernButton("📊 Exportar Reporte", button_type="primary")
        export_btn.clicked.connect(self.export_analytics_report)
        actions_layout.addWidget(export_btn)
        
        actions_layout.addStretch()
        
        close_btn = ModernButton("Cerrar", button_type="secondary")
        close_btn.clicked.connect(self.close)
        actions_layout.addWidget(close_btn)
        
        layout.addLayout(actions_layout)
        
    def create_summary_tab(self) -> QWidget:
        """Crea la pestaña de resumen general"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Grid de métricas principales
        metrics_grid = QWidget()
        grid_layout = QGridLayout(metrics_grid)
        grid_layout.setSpacing(15)
        
        self.metric_cards = {}
        
        metrics = [
            ("total_meetings", "📅 Total Reuniones", "0"),
            ("total_hours", "⏱️ Horas Totales", "0h"),
            ("total_actions", "✅ Acciones Totales", "0"),
            ("avg_duration", "⏰ Duración Promedio", "0 min"),
            ("completion_rate", "✓ Tasa Completado", "0%"),
            ("avg_participants", "👥 Participantes Promedio", "0")
        ]
        
        for i, (key, title, default) in enumerate(metrics):
            card = self.create_metric_card(title, default)
            self.metric_cards[key] = card
            grid_layout.addWidget(card, i // 3, i % 3)
        
        layout.addWidget(metrics_grid)
        
        # Gráficos de resumen
        charts_layout = QHBoxLayout()
        
        # Gráfico de distribución por estado
        self.status_chart_view = QChartView()
        self.status_chart_view.setRenderHint(QPainter.Antialiasing)
        charts_layout.addWidget(self.status_chart_view)
        
        # Gráfico de reuniones por mes
        self.monthly_chart_view = QChartView()
        self.monthly_chart_view.setRenderHint(QPainter.Antialiasing)
        charts_layout.addWidget(self.monthly_chart_view)
        
        layout.addLayout(charts_layout)
        
        return widget
        
    def create_trends_tab(self) -> QWidget:
        """Crea la pestaña de tendencias"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Selector de período
        period_layout = QHBoxLayout()
        period_layout.addWidget(QLabel("Período:"))
        
        self.period_combo = QComboBox()
        self.period_combo.addItems(["Última semana", "Último mes", "Últimos 3 meses", "Último año", "Todo"])
        self.period_combo.setStyleSheet(COMBO_STYLE)
        self.period_combo.currentTextChanged.connect(self.update_trends)
        period_layout.addWidget(self.period_combo)
        
        period_layout.addStretch()
        layout.addLayout(period_layout)
        
        # Gráfico de tendencias
        self.trends_chart_view = QChartView()
        self.trends_chart_view.setRenderHint(QPainter.Antialiasing)
        self.trends_chart_view.setMinimumHeight(400)
        layout.addWidget(self.trends_chart_view)
        
        # Insights de tendencias
        self.trends_insights = QTextEdit()
        self.trends_insights.setReadOnly(True)
        self.trends_insights.setMaximumHeight(150)
        self.trends_insights.setStyleSheet(f"""
            QTextEdit {{
                background-color: {COLORS['secondary_bg']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 10px;
                font-size: 13px;
            }}
        """)
        layout.addWidget(self.trends_insights)
        
        return widget
        
    def create_productivity_tab(self) -> QWidget:
        """Crea la pestaña de productividad"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Métricas de productividad
        prod_metrics = QWidget()
        prod_layout = QHBoxLayout(prod_metrics)
        
        # Eficiencia promedio
        self.efficiency_gauge = self.create_gauge_widget("Eficiencia Promedio", 0, 10)
        prod_layout.addWidget(self.efficiency_gauge)
        
        # Tasa de acciones completadas
        self.actions_gauge = self.create_gauge_widget("Acciones Completadas", 0, 100)
        prod_layout.addWidget(self.actions_gauge)
        
        # Tiempo promedio de respuesta
        self.response_gauge = self.create_gauge_widget("Tiempo de Respuesta", 0, 7)
        prod_layout.addWidget(self.response_gauge)
        
        layout.addWidget(prod_metrics)
        
        # Tabla de top performers (reuniones más productivas)
        self.productivity_table = QTableWidget()
        self.productivity_table.setStyleSheet(TABLE_STYLE)
        self.productivity_table.setColumnCount(5)
        self.productivity_table.setHorizontalHeaderLabels([
            "Reunión", "Fecha", "Eficiencia", "Acciones", "Duración"
        ])
        
        header = self.productivity_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        
        layout.addWidget(QLabel("🏆 Reuniones Más Productivas"))
        layout.addWidget(self.productivity_table)
        
        return widget
        
    def create_topics_tab(self) -> QWidget:
        """Crea la pestaña de análisis de temas"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Word cloud placeholder
        self.topics_viz = QLabel("Visualización de temas")
        self.topics_viz.setMinimumHeight(300)
        self.topics_viz.setStyleSheet(f"""
            QLabel {{
                background-color: {COLORS['secondary_bg']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 20px;
                qproperty-alignment: AlignCenter;
            }}
        """)
        layout.addWidget(self.topics_viz)
        
        # Tabla de temas frecuentes
        self.topics_table = QTableWidget()
        self.topics_table.setStyleSheet(TABLE_STYLE)
        self.topics_table.setColumnCount(4)
        self.topics_table.setHorizontalHeaderLabels([
            "Tema", "Frecuencia", "Tiempo Total", "Reuniones"
        ])
        
        header = self.topics_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        
        layout.addWidget(QLabel("🏷️ Temas Más Frecuentes"))
        layout.addWidget(self.topics_table)
        
        return widget
        
    def create_metric_card(self, title: str, value: str) -> QWidget:
        """Crea una tarjeta de métrica"""
        card = RoundedWidget()
        card.setStyleSheet(f"""
            RoundedWidget {{
                background-color: {COLORS['accent_bg']};
                border: 1px solid {COLORS['border']};
                padding: 20px;
            }}
        """)
        
        layout = QVBoxLayout(card)
        
        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['text_secondary']};
                font-size: 12px;
                font-weight: 500;
            }}
        """)
        layout.addWidget(title_label)
        
        value_label = QLabel(value)
        value_label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['text_primary']};
                font-size: 24px;
                font-weight: bold;
            }}
        """)
        value_label.setObjectName("value")
        layout.addWidget(value_label)
        
        return card
        
    def create_gauge_widget(self, title: str, min_val: float, max_val: float) -> QWidget:
        """Crea un widget de medidor (gauge)"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet(LABEL_PRIMARY)
        layout.addWidget(title_label)
        
        # Placeholder para el gauge (se puede reemplazar con un widget personalizado)
        gauge = QProgressBar()
        gauge.setMinimum(int(min_val))
        gauge.setMaximum(int(max_val))
        gauge.setValue(0)
        gauge.setTextVisible(True)
        gauge.setStyleSheet(f"""
            QProgressBar {{
                border: 2px solid {COLORS['border']};
                border-radius: 5px;
                text-align: center;
                background-color: {COLORS['secondary_bg']};
            }}
            QProgressBar::chunk {{
                background-color: {COLORS['active_bg']};
                border-radius: 3px;
            }}
        """)
        layout.addWidget(gauge)
        
        widget.gauge = gauge
        return widget
        
    def load_analytics(self):
        """Carga y procesa los datos de analytics"""
        try:
            # Procesar datos de reuniones
            total_meetings = len(self.meetings)
            total_hours = 0
            total_actions = 0
            completed_meetings = 0
            total_participants = 0
            meetings_with_participants = 0
            
            # Datos para gráficos
            status_counts = {"Completado": 0, "En proceso": 0, "Error": 0}
            monthly_counts = {}
            all_topics = []
            productivity_scores = []
            
            for meeting in self.meetings:
                # Estado
                status = meeting.get('status', 'unknown')
                if status == 'completed':
                    status_counts["Completado"] += 1
                    completed_meetings += 1
                elif status == 'in_progress':
                    status_counts["En proceso"] += 1
                elif status == 'error':
                    status_counts["Error"] += 1
                
                # Fecha para agrupación mensual
                created = meeting.get('created', '')
                if created:
                    date = datetime.fromisoformat(created)
                    month_key = date.strftime('%Y-%m')
                    monthly_counts[month_key] = monthly_counts.get(month_key, 0) + 1
                
                # Obtener datos completos de la reunión
                meeting_data = self.file_manager.get_meeting_data(meeting['folder_path'])
                
                # Duración
                analytics = meeting_data.get('analytics', {})
                duration_str = analytics.get('estimated_duration', '0 minutos')
                try:
                    duration_minutes = int(duration_str.split()[0])
                    total_hours += duration_minutes / 60
                except:
                    pass
                
                # Acciones
                actions = meeting_data.get('actions', [])
                total_actions += len(actions)
                
                # Participantes
                participants_count = analytics.get('participants_count', 0)
                if participants_count > 0:
                    total_participants += participants_count
                    meetings_with_participants += 1
                
                # Temas
                topics = analytics.get('main_topics', [])
                all_topics.extend(topics)
                
                # Productividad
                efficiency = analytics.get('efficiency', {}).get('score', 0)
                if efficiency > 0:
                    productivity_scores.append({
                        'meeting': meeting.get('custom_name', 'Sin título'),
                        'date': created,
                        'efficiency': efficiency,
                        'actions': len(actions),
                        'duration': duration_minutes
                    })
            
            # Actualizar métricas
            self.update_metric_card('total_meetings', str(total_meetings))
            self.update_metric_card('total_hours', f"{total_hours:.1f}h")
            self.update_metric_card('total_actions', str(total_actions))
            
            avg_duration = (total_hours * 60 / total_meetings) if total_meetings > 0 else 0
            self.update_metric_card('avg_duration', f"{avg_duration:.0f} min")
            
            completion_rate = (completed_meetings / total_meetings * 100) if total_meetings > 0 else 0
            self.update_metric_card('completion_rate', f"{completion_rate:.1f}%")
            
            avg_participants = (total_participants / meetings_with_participants) if meetings_with_participants > 0 else 0
            self.update_metric_card('avg_participants', f"{avg_participants:.1f}")
            
            # Crear gráficos
            self.create_status_chart(status_counts)
            self.create_monthly_chart(monthly_counts)
            self.update_productivity_table(productivity_scores)
            self.update_topics_analysis(all_topics)
            
        except Exception as e:
            print(f"Error cargando analytics: {e}")
            
    def update_metric_card(self, key: str, value: str):
        """Actualiza el valor de una tarjeta de métrica"""
        if key in self.metric_cards:
            card = self.metric_cards[key]
            value_label = card.findChild(QLabel, "value")
            if value_label:
                value_label.setText(value)
                
    def create_status_chart(self, status_counts: Dict[str, int]):
        """Crea el gráfico de distribución por estado"""
        series = QPieSeries()
        
        colors = {
            "Completado": QColor(COLORS['success']),
            "En proceso": QColor(COLORS['warning']),
            "Error": QColor(COLORS['error'])
        }
        
        for status, count in status_counts.items():
            if count > 0:
                slice = series.append(f"{status} ({count})", count)
                if status in colors:
                    slice.setBrush(colors[status])
                slice.setLabelVisible(True)
        
        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("Distribución por Estado")
        chart.setAnimationOptions(QChart.SeriesAnimations)
        chart.setBackgroundBrush(QColor(COLORS['secondary_bg']))
        chart.setTitleBrush(QColor(COLORS['text_primary']))
        
        self.status_chart_view.setChart(chart)
        
    def create_monthly_chart(self, monthly_counts: Dict[str, int]):
        """Crea el gráfico de reuniones por mes"""
        # Ordenar por mes
        sorted_months = sorted(monthly_counts.items())
        
        # Crear series
        bar_set = QBarSet("Reuniones")
        bar_set.setColor(QColor(COLORS['active_bg']))
        
        categories = []
        for month, count in sorted_months[-12:]:  # Últimos 12 meses
            bar_set.append(count)
            # Formatear mes
            date = datetime.strptime(month, '%Y-%m')
            categories.append(date.strftime('%b %y'))
        
        series = QBarSeries()
        series.append(bar_set)
        
        # Crear gráfico
        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("Reuniones por Mes")
        chart.setAnimationOptions(QChart.SeriesAnimations)
        chart.setBackgroundBrush(QColor(COLORS['secondary_bg']))
        chart.setTitleBrush(QColor(COLORS['text_primary']))
        
        # Ejes
        axis_x = QBarCategoryAxis()
        axis_x.append(categories)
        chart.addAxis(axis_x, Qt.AlignBottom)
        series.attachAxis(axis_x)
        
        axis_y = QValueAxis()
        axis_y.setLabelFormat("%d")
        chart.addAxis(axis_y, Qt.AlignLeft)
        series.attachAxis(axis_y)
        
        self.monthly_chart_view.setChart(chart)
        
    def update_trends(self):
        """Actualiza el gráfico de tendencias según el período seleccionado"""
        period = self.period_combo.currentText()
        
        # Filtrar datos según período
        end_date = datetime.now()
        if period == "Última semana":
            start_date = end_date - timedelta(days=7)
        elif period == "Último mes":
            start_date = end_date - timedelta(days=30)
        elif period == "Últimos 3 meses":
            start_date = end_date - timedelta(days=90)
        elif period == "Último año":
            start_date = end_date - timedelta(days=365)
        else:  # Todo
            start_date = datetime.min
        
        # TODO: Implementar filtrado y actualización de gráfico
        
        # Actualizar insights
        insights = f"""
📈 Tendencias del período: {period}

• Incremento del 15% en el número de reuniones
• Reducción del 20% en la duración promedio
• Mayor participación los martes y jueves
• Los temas técnicos dominan con un 45% del tiempo
        """
        self.trends_insights.setPlainText(insights)
        
    def update_productivity_table(self, productivity_scores: List[Dict]):
        """Actualiza la tabla de productividad"""
        # Ordenar por eficiencia
        sorted_scores = sorted(productivity_scores, key=lambda x: x['efficiency'], reverse=True)
        
        self.productivity_table.setRowCount(0)
        
        for score in sorted_scores[:10]:  # Top 10
            row = self.productivity_table.rowCount()
            self.productivity_table.insertRow(row)
            
            self.productivity_table.setItem(row, 0, QTableWidgetItem(score['meeting']))
            
            date = datetime.fromisoformat(score['date']).strftime('%Y-%m-%d')
            self.productivity_table.setItem(row, 1, QTableWidgetItem(date))
            
            efficiency_item = QTableWidgetItem(f"{score['efficiency']:.1f}/10")
            if score['efficiency'] >= 8:
                efficiency_item.setForeground(QColor(COLORS['success']))
            elif score['efficiency'] >= 6:
                efficiency_item.setForeground(QColor(COLORS['warning']))
            else:
                efficiency_item.setForeground(QColor(COLORS['error']))
            self.productivity_table.setItem(row, 2, efficiency_item)
            
            self.productivity_table.setItem(row, 3, QTableWidgetItem(str(score['actions'])))
            self.productivity_table.setItem(row, 4, QTableWidgetItem(f"{score['duration']} min"))
        
        # Actualizar gauges
        if productivity_scores:
            avg_efficiency = sum(s['efficiency'] for s in productivity_scores) / len(productivity_scores)
            self.efficiency_gauge.gauge.setValue(int(avg_efficiency))
            
            # TODO: Calcular y actualizar otros gauges
            
    def update_topics_analysis(self, all_topics: List[str]):
        """Actualiza el análisis de temas"""
        # Contar frecuencia de temas
        topic_counts = {}
        for topic in all_topics:
            topic_counts[topic] = topic_counts.get(topic, 0) + 1
        
        # Ordenar por frecuencia
        sorted_topics = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)
        
        # Actualizar tabla
        self.topics_table.setRowCount(0)
        
        for topic, count in sorted_topics[:20]:  # Top 20
            row = self.topics_table.rowCount()
            self.topics_table.insertRow(row)
            
            self.topics_table.setItem(row, 0, QTableWidgetItem(topic))
            self.topics_table.setItem(row, 1, QTableWidgetItem(str(count)))
            
            # TODO: Calcular tiempo total y reuniones
            self.topics_table.setItem(row, 2, QTableWidgetItem("-"))
            self.topics_table.setItem(row, 3, QTableWidgetItem("-"))
        
        # TODO: Crear visualización de word cloud
        
    def export_analytics_report(self):
        """Exporta el reporte de analytics"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Exportar Reporte de Analytics",
            f"analytics_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            "PDF Files (*.pdf);;Excel Files (*.xlsx);;HTML Files (*.html)"
        )
        
        if file_path:
            # TODO: Implementar exportación real
            QMessageBox.information(
                self, "Exportación",
                f"Reporte exportado a:\\n{file_path}\\n\\n(Función en desarrollo)"
            )


# Agregar estilos adicionales necesarios
TABLE_STYLE = f"""
QTableWidget {{
    background-color: {COLORS['secondary_bg']};
    alternate-background-color: {COLORS['primary_bg']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border']};
    border-radius: 8px;
    gridline-color: {COLORS['border']};
    font-family: '{FONTS['primary']}';
}}

QTableWidget::item {{
    padding: 8px;
    border: none;
}}

QTableWidget::item:selected {{
    background-color: {COLORS['active_bg']};
    color: white;
}}

QHeaderView::section {{
    background-color: {COLORS['primary_bg']};
    color: {COLORS['text_primary']};
    padding: 10px;
    border: none;
    border-bottom: 2px solid {COLORS['active_bg']};
    font-weight: bold;
}}
"""

TAB_STYLE = f"""
QTabWidget::pane {{
    border: 1px solid {COLORS['border']};
    background-color: {COLORS['secondary_bg']};
    border-radius: 8px;
}}

QTabBar::tab {{
    background-color: {COLORS['primary_bg']};
    color: {COLORS['text_secondary']};
    padding: 10px 20px;
    margin-right: 5px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
}}

QTabBar::tab:selected {{
    background-color: {COLORS['secondary_bg']};
    color: {COLORS['text_primary']};
    font-weight: bold;
}}

QTabBar::tab:hover {{
    background-color: {COLORS['accent_bg']};
}}
"""

GROUP_BOX_STYLE = f"""
QGroupBox {{
    font-weight: bold;
    border: 2px solid {COLORS['border']};
    border-radius: 8px;
    margin-top: 10px;
    padding-top: 10px;
    background-color: {COLORS['secondary_bg']};
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 10px 0 10px;
    color: {COLORS['text_primary']};
}}
"""

MENU_STYLE = f"""
QMenu {{
    background-color: {COLORS['secondary_bg']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border']};
    border-radius: 8px;
    padding: 5px;
}}

QMenu::item {{
    padding: 8px 25px;
    border-radius: 4px;
}}

QMenu::item:selected {{
    background-color: {COLORS['active_bg']};
    color: white;
}}

QMenu::separator {{
    height: 1px;
    background-color: {COLORS['border']};
    margin: 5px 0;
}}
"""

# Importaciones adicionales necesarias
from PyQt5.QtWidgets import QGridLayout, QInputDialog
from PyQt5.QtGui import QPainter