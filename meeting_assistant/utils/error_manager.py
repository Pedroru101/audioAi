# utils/error_manager.py
import logging
import logging.handlers  # Import necesario para RotatingFileHandler
import traceback
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, Callable
import json
import threading
from functools import wraps

class ErrorManager:
    """Gestor centralizado de errores para Meeting Assistant Pro."""
    
    def __init__(self, config_manager=None, notification_manager=None):
        self.config_manager = config_manager
        self.notification_manager = notification_manager
        self.logger = logging.getLogger(__name__)
        
        # Configuración de logging
        self._setup_logging()
        
        # Historial de errores para la sesión
        self.error_history = []
        self.error_count = {
            'critical': 0,
            'error': 0,
            'warning': 0,
            'info': 0
        }
        
        # Callbacks para tipos de error específicos
        self.error_handlers = {}
        
        # Lock para thread safety
        self.lock = threading.Lock()
        
        # Configurar el manejador de excepciones no capturadas
        sys.excepthook = self._handle_uncaught_exception

    def _setup_logging(self):
        """Configura el sistema de logging de forma segura."""
        try:
            # Configuración básica como fallback
            logging.basicConfig(
                level=logging.INFO,
                format='%(levelname)s - %(name)s - %(message)s'
            )
            
            # Configuración avanzada si es posible
            if self.config_manager:
                log_dir = Path(self.config_manager.get('save_path', '~')) / 'logs'
                log_dir.mkdir(parents=True, exist_ok=True)
                
                log_file = log_dir / f"meeting_assistant_{datetime.now().strftime('%Y%m%d')}.log"
                
                # Configurar handler de archivo con rotación
                file_handler = logging.handlers.RotatingFileHandler(
                    log_file,
                    maxBytes=10*1024*1024,  # 10MB
                    backupCount=5,
                    encoding='utf-8'
                )
                file_handler.setFormatter(logging.Formatter(
                    '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
                ))
                
                # Configurar logger root
                root_logger = logging.getLogger()
                root_logger.setLevel(logging.INFO)
                root_logger.addHandler(file_handler)
                
        except Exception as e:
            print(f"Error configurando logging: {e}")
            # Fallback a configuración básica
            logging.basicConfig(level=logging.INFO)
        
        # Configuración de logging
        # try:
        #     # Obtener configuración si está disponible
        #     if self.config_manager:
        #         log_dir = Path(self.config_manager.get('save_path', '~')) / 'logs'
        #     else:
        #         log_dir = Path.home() / '.meeting_assistant' / 'logs'
        #     
        #     log_dir.mkdir(parents=True, exist_ok=True)
        #     
        #     # Archivo de log principal
        #     log_file = log_dir / f"meeting_assistant_{datetime.now().strftime('%Y%m%d')}.log"
        #     
        #     # Configurar handler de archivo
        #     file_handler = logging.handlers.RotatingFileHandler(
        #         log_file,
        #         maxBytes=10*1024*1024,  # 10MB
        #         backupCount=5,
        #         encoding='utf-8'
        #     )
        #     
        #     # Formato detallado para archivo
        #     file_formatter = logging.Formatter(
        #         '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        #     )
        #     file_handler.setFormatter(file_formatter)
        #     
        #     # Configurar handler de consola
        #     console_handler = logging.StreamHandler()
        #     console_formatter = logging.Formatter(
        #         '%(levelname)s - %(name)s - %(message)s'
        #     )
        #     console_handler.setFormatter(console_formatter)
        #     
        #     # Configurar logger root
        #     root_logger = logging.getLogger()
        #     root_logger.setLevel(logging.INFO)
        #     root_logger.addHandler(file_handler)
        #     root_logger.addHandler(console_handler)
        #     
        # except Exception as e:
        #     print(f"Error configurando logging: {e}")

    def _handle_uncaught_exception(self, exc_type, exc_value, exc_traceback):
        """Maneja excepciones no capturadas."""
        if issubclass(exc_type, KeyboardInterrupt):
            # No registrar interrupciones de teclado
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        
        # Registrar el error crítico
        self.log_critical(
            "Excepción no capturada",
            exc_info=(exc_type, exc_value, exc_traceback)
        )

    def log_critical(self, message: str, exc_info=None, extra_data: Dict[str, Any] = None):
        """Registra un error crítico."""
        self._log_error('critical', message, exc_info, extra_data)
        
        # Notificar al usuario
        if self.notification_manager:
            self.notification_manager.show_error(
                f"Error crítico: {message}",
                "Error Crítico",
                duration=10000
            )

    def log_error(self, message: str, exc_info=None, extra_data: Dict[str, Any] = None):
        """Registra un error."""
        self._log_error('error', message, exc_info, extra_data)
        
        # Notificar según configuración
        if self.notification_manager and self._should_notify('error'):
            self.notification_manager.show_error(message)

    def log_warning(self, message: str, exc_info=None, extra_data: Dict[str, Any] = None):
        """Registra una advertencia."""
        self._log_error('warning', message, exc_info, extra_data)
        
        # Notificar según configuración
        if self.notification_manager and self._should_notify('warning'):
            self.notification_manager.show_warning(message)

    def log_info(self, message: str, extra_data: Dict[str, Any] = None):
        """Registra información."""
        self._log_error('info', message, None, extra_data)

    def _log_error(self, level: str, message: str, exc_info=None, extra_data: Dict[str, Any] = None):
        """Método interno para registrar errores."""
        with self.lock:
            # Crear entrada de error
            error_entry = {
                'timestamp': datetime.now().isoformat(),
                'level': level,
                'message': message,
                'extra_data': extra_data or {}
            }
            
            # Añadir información de excepción si está disponible
            if exc_info:
                if isinstance(exc_info, tuple):
                    error_entry['exception'] = {
                        'type': exc_info[0].__name__,
                        'value': str(exc_info[1]),
                        'traceback': ''.join(traceback.format_tb(exc_info[2]))
                    }
                else:
                    error_entry['exception'] = {
                        'type': type(exc_info).__name__,
                        'value': str(exc_info),
                        'traceback': traceback.format_exc()
                    }
            
            # Añadir al historial
            self.error_history.append(error_entry)
            self.error_count[level] += 1
            
            # Limitar tamaño del historial
            if len(self.error_history) > 1000:
                self.error_history = self.error_history[-500:]
            
            # Log usando el logger
            log_message = f"{message}"
            if extra_data:
                log_message += f" | Data: {json.dumps(extra_data, ensure_ascii=False)}"
            
            if level == 'critical':
                self.logger.critical(log_message, exc_info=exc_info)
            elif level == 'error':
                self.logger.error(log_message, exc_info=exc_info)
            elif level == 'warning':
                self.logger.warning(log_message, exc_info=exc_info)
            else:
                self.logger.info(log_message)
            
            # Ejecutar handlers personalizados
            self._execute_handlers(level, error_entry)
            
            # Guardar en archivo de errores si es crítico o error
            if level in ['critical', 'error']:
                self._save_error_to_file(error_entry)

    def _should_notify(self, level: str) -> bool:
        """Determina si se debe mostrar una notificación para este nivel."""
        if not self.config_manager:
            return level in ['error', 'critical']
        
        # Obtener configuración de notificaciones por nivel
        notify_config = self.config_manager.get('error_notifications', {
            'critical': True,
            'error': True,
            'warning': False,
            'info': False
        })
        
        return notify_config.get(level, False)

    def _execute_handlers(self, level: str, error_entry: Dict[str, Any]):
        """Ejecuta handlers personalizados para el error."""
        # Handler general
        if 'all' in self.error_handlers:
            try:
                self.error_handlers['all'](error_entry)
            except Exception as e:
                self.logger.error(f"Error en handler general: {e}")
        
        # Handler específico del nivel
        if level in self.error_handlers:
            try:
                self.error_handlers[level](error_entry)
            except Exception as e:
                self.logger.error(f"Error en handler {level}: {e}")

    def _save_error_to_file(self, error_entry: Dict[str, Any]):
        """Guarda errores importantes en un archivo separado."""
        try:
            if self.config_manager:
                error_dir = Path(self.config_manager.get('save_path', '~')) / 'logs' / 'errors'
            else:
                error_dir = Path.home() / '.meeting_assistant' / 'logs' / 'errors'
            
            error_dir.mkdir(parents=True, exist_ok=True)
            
            # Archivo de errores del día
            error_file = error_dir / f"errors_{datetime.now().strftime('%Y%m%d')}.json"
            
            # Cargar errores existentes
            if error_file.exists():
                with open(error_file, 'r', encoding='utf-8') as f:
                    errors = json.load(f)
            else:
                errors = []
            
            # Añadir nuevo error
            errors.append(error_entry)
            
            # Guardar
            with open(error_file, 'w', encoding='utf-8') as f:
                json.dump(errors, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            self.logger.error(f"No se pudo guardar error en archivo: {e}")

    def register_handler(self, level: str, handler: Callable):
        """Registra un handler personalizado para un nivel de error."""
        self.error_handlers[level] = handler

    def get_error_summary(self) -> Dict[str, Any]:
        """Obtiene un resumen de los errores de la sesión."""
        with self.lock:
            return {
                'total_errors': sum(self.error_count.values()),
                'by_level': self.error_count.copy(),
                'recent_errors': self.error_history[-10:],
                'session_start': self.error_history[0]['timestamp'] if self.error_history else None
            }

    def get_recent_errors(self, count: int = 50, level: Optional[str] = None) -> list:
        """Obtiene los errores más recientes."""
        with self.lock:
            if level:
                filtered = [e for e in self.error_history if e['level'] == level]
                return filtered[-count:]
            else:
                return self.error_history[-count:]

    def clear_history(self):
        """Limpia el historial de errores de la sesión."""
        with self.lock:
            self.error_history.clear()
            self.error_count = {
                'critical': 0,
                'error': 0,
                'warning': 0,
                'info': 0
            }

    def export_error_report(self, filepath: str) -> bool:
        """Exporta un reporte de errores."""
        try:
            report = {
                'generated': datetime.now().isoformat(),
                'summary': self.get_error_summary(),
                'errors': self.error_history
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Reporte de errores exportado: {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error exportando reporte: {e}")
            return False

    # Decoradores para manejo automático de errores
    
    @staticmethod
    def handle_errors(default_return=None, notify=True, level='error'):
        """Decorador para manejo automático de errores en funciones."""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    # Buscar ErrorManager en self si existe
                    error_manager = None
                    if args and hasattr(args[0], 'error_manager'):
                        error_manager = args[0].error_manager
                    
                    # Registrar el error
                    if error_manager:
                        error_manager._log_error(
                            level,
                            f"Error en {func.__name__}: {str(e)}",
                            exc_info=sys.exc_info(),
                            extra_data={'function': func.__name__, 'args': str(args), 'kwargs': str(kwargs)}
                        )
                    else:
                        logging.getLogger(__name__).error(
                            f"Error en {func.__name__}: {str(e)}",
                            exc_info=True
                        )
                    
                    return default_return
            
            return wrapper
        return decorator

    @staticmethod
    def retry_on_error(max_attempts=3, delay=1.0, backoff=2.0):
        """Decorador para reintentar operaciones en caso de error."""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                attempts = 0
                current_delay = delay
                
                while attempts < max_attempts:
                    try:
                        return func(*args, **kwargs)
                    except Exception as e:
                        attempts += 1
                        
                        if attempts >= max_attempts:
                            raise
                        
                        # Log del intento
                        logging.getLogger(__name__).warning(
                            f"Error en {func.__name__}, intento {attempts}/{max_attempts}: {str(e)}"
                        )
                        
                        # Esperar antes de reintentar
                        import time
                        time.sleep(current_delay)
                        current_delay *= backoff
                
            return wrapper
        return decorator


class ErrorContext:
    """Context manager para manejo de errores en bloques de código."""
    
    def __init__(self, error_manager: ErrorManager, context_name: str,
                 suppress=False, default_return=None):
        self.error_manager = error_manager
        self.context_name = context_name
        self.suppress = suppress
        self.default_return = default_return
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            # Registrar el error
            self.error_manager.log_error(
                f"Error en contexto '{self.context_name}': {exc_val}",
                exc_info=(exc_type, exc_val, exc_tb),
                extra_data={'context': self.context_name}
            )
            
            # Suprimir la excepción si se solicita
            return self.suppress


# Funciones de utilidad

def safe_execute(func: Callable, default_return=None, error_message: str = None):
    """Ejecuta una función de forma segura, capturando excepciones."""
    try:
        return func()
    except Exception as e:
        if error_message:
            logging.getLogger(__name__).error(f"{error_message}: {e}")
        else:
            logging.getLogger(__name__).error(f"Error ejecutando {func.__name__}: {e}")
        return default_return

def format_exception(exc_info=None) -> str:
    """Formatea una excepción para mostrar al usuario."""
    if exc_info:
        if isinstance(exc_info, tuple):
            return f"{exc_info[0].__name__}: {exc_info[1]}"
        else:
            return f"{type(exc_info).__name__}: {str(exc_info)}"
    else:
        return "Error desconocido"
