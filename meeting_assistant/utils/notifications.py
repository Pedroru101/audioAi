"""
Módulo de notificaciones para Meeting Assistant
"""
from PyQt5.QtWidgets import QMessageBox

class NotificationManager:
    @staticmethod
    def info(msg, parent=None):
        QMessageBox.information(parent, "Info", msg)

    @staticmethod
    def warning(msg, parent=None):
        QMessageBox.warning(parent, "Advertencia", msg)

    @staticmethod
    def error(msg, parent=None):
        QMessageBox.critical(parent, "Error", msg)

    # Compatibilidad con la interfaz antigua Notifier.show(title, msg)
    @staticmethod
    def show(title, msg, parent=None):
        """Muestra un mensaje de información genérico conservando la firma de Notifier.show."""
        QMessageBox.information(parent, title, msg)
