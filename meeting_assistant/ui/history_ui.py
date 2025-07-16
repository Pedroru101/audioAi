"""
Historial de reuniones: muestra, filtra y exporta grabaciones
"""
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QHBoxLayout, QFileDialog, QMessageBox
from PyQt5.QtCore import Qt
from ..utils.file_manager import FileManager

class HistoryUI(QWidget):
    def __init__(self, on_export=None, on_open_folder=None, on_delete=None):
        super().__init__()
        self.setWindowTitle("Historial de reuniones")
        self.setMinimumSize(600, 400)
        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)
        self.table = QTableWidget()
        self.layout.addWidget(self.table)
        self.on_export = on_export
        self.on_open_folder = on_open_folder
        self.on_delete = on_delete
        self.load_history()

    def load_history(self):
        # Simula carga de historial
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Fecha", "Duración", "Acciones"])
        self.table.setRowCount(0)
        # Aquí deberías cargar datos reales usando FileManager
        # Ejemplo:
        # for i, meeting in enumerate(FileManager.list_meetings()):
        #     self.table.insertRow(i)
        #     self.table.setItem(i, 0, QTableWidgetItem(meeting['date']))
        #     self.table.setItem(i, 1, QTableWidgetItem(meeting['duration']))
        #     # Botones de acción...
        pass
