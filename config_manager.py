# config/config_manager.py
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
import shutil
from datetime import datetime
import logging

from .settings import DEFAULT_CONFIG, CONFIG_VALIDATORS, AVAILABLE_MODELS

class ConfigManager:
    """Gestor centralizado de configuración para Meeting Assistant Pro."""
    
    def __init__(self, config_path: Optional[str] = None):
        self.logger = logging.getLogger(__name__)
        
        # Determinar la ruta del archivo de configuración
        if config_path:
            self.config_path = Path(config_path)
        else:
            # Usar la carpeta de datos del proyecto
            self.config_path = Path(__file__).parent.parent / "data" / "config.json"
        
        # Asegurar que existe el directorio
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Cargar configuración
        self.config = self._load_config()
        
        # Validar configuración al cargar
        self._validate_config()
        
        # Guardar configuración actualizada (por si se añadieron valores por defecto)
        self._save_config()
        
        self.logger.info(f"ConfigManager inicializado. Archivo: {self.config_path}")

    def _load_config(self) -> Dict[str, Any]:
        """Carga la configuración desde el archivo o crea una nueva."""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                
                # Fusionar con configuración por defecto (para nuevas opciones)
                merged_config = DEFAULT_CONFIG.copy()
                self._deep_update(merged_config, loaded_config)
                
                self.logger.info("Configuración cargada exitosamente")
                return merged_config
                
            except json.JSONDecodeError as e:
                self.logger.error(f"Error al parsear config.json: {e}")
                # Hacer backup del archivo corrupto
                backup_path = self.config_path.with_suffix('.json.backup')
                shutil.copy2(self.config_path, backup_path)
                self.logger.warning(f"Backup creado en: {backup_path}")
                
                # Retornar configuración por defecto
                return DEFAULT_CONFIG.copy()
            except Exception as e:
                self.logger.error(f"Error al cargar configuración: {e}")
                return DEFAULT_CONFIG.copy()
        else:
            self.logger.info("No se encontró archivo de configuración. Creando nuevo...")
            return DEFAULT_CONFIG.copy()

    def _deep_update(self, base_dict: Dict, update_dict: Dict) -> None:
        """Actualiza recursivamente un diccionario anidado."""
        for key, value in update_dict.items():
            if key in base_dict and isinstance(base_dict[key], dict) and isinstance(value, dict):
                self._deep_update(base_dict[key], value)
            else:
                base_dict[key] = value

    def _save_config(self) -> bool:
        """Guarda la configuración actual en el archivo."""
        try:
            # Crear backup antes de guardar
            if self.config_path.exists():
                backup_path = self.config_path.with_suffix(f'.json.{datetime.now().strftime("%Y%m%d_%H%M%S")}')
                shutil.copy2(self.config_path, backup_path)
                
                # Mantener solo los últimos 5 backups
                self._cleanup_old_backups()
            
            # Guardar configuración
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            
            self.logger.info("Configuración guardada exitosamente")
            return True
            
        except Exception as e:
            self.logger.error(f"Error al guardar configuración: {e}")
            return False

    def _cleanup_old_backups(self, keep_count: int = 5):
        """Elimina backups antiguos, manteniendo solo los más recientes."""
        backup_pattern = f"{self.config_path.stem}.json.*"
        backups = sorted(self.config_path.parent.glob(backup_pattern), 
                        key=os.path.getmtime, reverse=True)
        
        for backup in backups[keep_count:]:
            try:
                backup.unlink()
                self.logger.debug(f"Backup antiguo eliminado: {backup}")
            except Exception as e:
                self.logger.warning(f"No se pudo eliminar backup: {backup}, {e}")

    def _validate_config(self) -> None:
        """Valida la configuración actual."""
        # Validar valores según CONFIG_VALIDATORS
        for key, valid_values in CONFIG_VALIDATORS.items():
            if key in self.config and self.config[key] not in valid_values:
                self.logger.warning(
                    f"Valor inválido para '{key}': '{self.config[key]}'. "
                    f"Valores válidos: {valid_values}. Usando valor por defecto."
                )
                self.config[key] = DEFAULT_CONFIG.get(key)
        
        # Validar rutas
        self._validate_paths()
        
        # Validar modelos según el proveedor
        self._validate_models()
        
        # Validar API keys si es necesario
        self._validate_api_keys()

    def _validate_paths(self) -> None:
        """Valida y crea las rutas necesarias."""
        paths_to_check = ['save_path', 'temp_path']
        
        for path_key in paths_to_check:
            if path_key in self.config:
                path = Path(self.config[path_key])
                try:
                    path.mkdir(parents=True, exist_ok=True)
                    self.config[path_key] = str(path.absolute())
                except Exception as e:
                    self.logger.error(f"No se pudo crear el directorio {path_key}: {e}")
                    # Usar ruta por defecto
                    default_path = Path.home() / ".meeting_assistant" / path_key
                    default_path.mkdir(parents=True, exist_ok=True)
                    self.config[path_key] = str(default_path)

    def _validate_models(self) -> None:
        """Valida que los modelos configurados estén disponibles."""
        # Validar modelo de API
        if self.config.get('llm_provider') == 'api':
            provider = self.config.get('api_provider', 'openai')
            model = self.config.get('api_model_name')
            
            if provider in AVAILABLE_MODELS:
                if model not in AVAILABLE_MODELS[provider]:
                    self.logger.warning(
                        f"Modelo '{model}' no reconocido para {provider}. "
                        f"Modelos disponibles: {AVAILABLE_MODELS[provider]}"
                    )
        
        # Validar modelo local
        elif self.config.get('llm_provider') == 'local':
            model = self.config.get('local_model_name')
            if model and model not in AVAILABLE_MODELS.get('ollama', []):
                self.logger.info(
                    f"Modelo local '{model}' no está en la lista predefinida. "
                    "Asegúrate de tenerlo instalado en Ollama."
                )

    def _validate_api_keys(self) -> None:
        """Valida la presencia de API keys necesarias."""
        warnings = []
        
        # Validar según el proveedor de transcripción
        if self.config.get('transcription_provider') == 'api':
            if not self.config.get('whisper_api_key'):
                warnings.append("Transcripción configurada para API pero falta 'whisper_api_key'")
        
        # Validar según el proveedor de LLM
        if self.config.get('llm_provider') == 'api':
            if not self.config.get('api_key'):
                warnings.append("LLM configurado para API pero falta 'api_key'")
        
        # Mostrar advertencias
        for warning in warnings:
            self.logger.warning(warning)

    def get_config(self) -> Dict[str, Any]:
        """Obtiene la configuración completa."""
        return self.config.copy()

    def get(self, key: str, default: Any = None) -> Any:
        """Obtiene un valor específico de la configuración."""
        return self.config.get(key, default)

    def set(self, key: str, value: Any, save: bool = True) -> bool:
        """Establece un valor en la configuración."""
        try:
            # Navegación por claves anidadas (ej: "integrations.email.enabled")
            if '.' in key:
                keys = key.split('.')
                target = self.config
                
                for k in keys[:-1]:
                    if k not in target:
                        target[k] = {}
                    target = target[k]
                
                target[keys[-1]] = value
            else:
                self.config[key] = value
            
            # Validar después de cambiar
            self._validate_config()
            
            # Guardar si se solicita
            if save:
                return self._save_config()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error al establecer {key}={value}: {e}")
            return False

    def update(self, updates: Dict[str, Any], save: bool = True) -> bool:
        """Actualiza múltiples valores de configuración."""
        try:
            self._deep_update(self.config, updates)
            self._validate_config()
            
            if save:
                return self._save_config()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error al actualizar configuración: {e}")
            return False

    def reset_to_defaults(self, keys: Optional[list] = None) -> bool:
        """Resetea la configuración a valores por defecto."""
        try:
            if keys:
                # Resetear solo las claves especificadas
                for key in keys:
                    if key in DEFAULT_CONFIG:
                        self.config[key] = DEFAULT_CONFIG[key]
            else:
                # Resetear toda la configuración
                self.config = DEFAULT_CONFIG.copy()
            
            self._validate_config()
            return self._save_config()
            
        except Exception as e:
            self.logger.error(f"Error al resetear configuración: {e}")
            return False

    def export_config(self, export_path: str, include_sensitive: bool = False) -> bool:
        """Exporta la configuración a un archivo."""
        try:
            export_config = self.config.copy()
            
            # Remover información sensible si se solicita
            if not include_sensitive:
                sensitive_keys = [
                    'api_key', 'whisper_api_key', 'openrouter_api_key',
                    'integrations.email.smtp_password',
                    'integrations.slack.webhook_url'
                ]
                
                for key in sensitive_keys:
                    if '.' in key:
                        keys = key.split('.')
                        target = export_config
                        for k in keys[:-1]:
                            if k in target:
                                target = target[k]
                            else:
                                break
                        if keys[-1] in target:
                            target[keys[-1]] = "***REDACTED***"
                    elif key in export_config:
                        export_config[key] = "***REDACTED***"
            
            # Guardar configuración exportada
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(export_config, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Configuración exportada a: {export_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error al exportar configuración: {e}")
            return False

    def import_config(self, import_path: str) -> bool:
        """Importa configuración desde un archivo."""
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                imported_config = json.load(f)
            
            # Validar que es una configuración válida
            if not isinstance(imported_config, dict):
                raise ValueError("El archivo no contiene una configuración válida")
            
            # Hacer backup de la configuración actual
            backup_path = self.config_path.with_suffix('.json.pre_import')
            self.export_config(str(backup_path), include_sensitive=True)
            
            # Actualizar configuración
            self._deep_update(self.config, imported_config)
            self._validate_config()
            
            return self._save_config()
            
        except Exception as e:
            self.logger.error(f"Error al importar configuración: {e}")
            return False

    def get_api_headers(self) -> Dict[str, str]:
        """Obtiene los headers necesarios para las APIs configuradas."""
        headers = {}
        
        provider = self.config.get('api_provider')
        
        if provider == 'openrouter':
            headers['HTTP-Referer'] = self.config.get('openrouter_site_url', '')
            headers['X-Title'] = self.config.get('openrouter_app_name', '')
        
        return headers

    def is_valid(self) -> bool:
        """Verifica si la configuración actual es válida para operar."""
        # Verificar transcripción
        if self.config.get('transcription_provider') == 'api':
            if not self.config.get('whisper_api_key'):
                return False
        
        # Verificar LLM
        if self.config.get('llm_provider') == 'api':
            if not self.config.get('api_key'):
                return False
        
        return True

    def get_status(self) -> Dict[str, Any]:
        """Obtiene el estado actual de la configuración."""
        return {
            'config_file': str(self.config_path),
            'is_valid': self.is_valid(),
            'llm_provider': self.config.get('llm_provider'),
            'transcription_provider': self.config.get('transcription_provider'),
            'ui_mode': self.config.get('ui_mode'),
            'has_api_key': bool(self.config.get('api_key')),
            'has_whisper_key': bool(self.config.get('whisper_api_key')),
            'save_path': self.config.get('save_path'),
            'integrations': {
                'email': self.config.get('integrations', {}).get('email', {}).get('enabled', False),
                'slack': self.config.get('integrations', {}).get('slack', {}).get('enabled', False),
                'calendar': self.config.get('integrations', {}).get('calendar', {}).get('enabled', False)
            }
        }
