"""
Manejo centralizado de errores y notificaciones para la aplicación de asistente de reuniones.
Compatible con PyQt5, win10toast, plyer y fallback en QMessageBox.
"""
import logging
import traceback
from typing import Optional

from .notifications import NotificationManager

logger = logging.getLogger("meeting_assistant_error_manager")

class ErrorManager:
    notification_manager = NotificationManager()

    @staticmethod
    def handle_error(
        error: Exception,
        context: str = "",
        user_message: Optional[str] = None,
        notify: bool = True,
        log_traceback: bool = True,
    ):
        """
        Maneja el error: log, notifica al usuario y opcionalmente muestra traceback.
        :param error: Excepción capturada
        :param context: Contexto textual del error
        :param user_message: Mensaje amigable para el usuario
        :param notify: Si notificar al usuario
        :param log_traceback: Si loguear el traceback completo
        """
        msg = f"[MeetingAssistant][ERROR] {context}: {str(error)}"
        if log_traceback:
            logger.error(msg + "\n" + traceback.format_exc())
        else:
            logger.error(msg)
        if notify:
            ErrorManager.notification_manager.show_notification(
                title="Error en la aplicación",
                message=user_message or f"Ocurrió un error: {str(error)}"
            )

    @staticmethod
    def handle_warning(
        warning: Exception,
        context: str = "",
        user_message: Optional[str] = None,
        notify: bool = False,
    ):
        msg = f"[MeetingAssistant][WARNING] {context}: {str(warning)}"
        logger.warning(msg)
        if notify:
            ErrorManager.notification_manager.show_notification(
                title="Advertencia",
                message=user_message or str(warning)
            )

    @staticmethod
    def log_info(msg: str):
        logger.info(f"[MeetingAssistant][INFO] {msg}")
