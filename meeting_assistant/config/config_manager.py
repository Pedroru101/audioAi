# config/config_manager.py

import json
import os
from .settings import DEFAULT_CONFIG

class ConfigManager:
    def __init__(self, config_file='config.json'):
        self.config_file = config_file
        self.config = self._load_config()

    def _load_config(self):
        """Carga la configuración desde el archivo JSON, fusionándola con los valores por defecto."""
        # Empezamos con la configuración por defecto completa
        config = DEFAULT_CONFIG.copy()
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                # Fusionamos: la configuración del usuario sobrescribe los valores por defecto
                config.update(user_config)
            except (json.JSONDecodeError, TypeError):
                # Si el archivo está corrupto o mal formado, usamos los valores por defecto
                print("Advertencia: El archivo de configuración está corrupto. Se usarán los valores por defecto.")
                pass # Ya tenemos los defaults en 'config'
        
        return config

    def get_config(self):
        """Devuelve la configuración actual."""
        return self.config

    def save_config(self, new_config):
        """Guarda la configuración proporcionada en el archivo JSON."""
        self.config = new_config
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error al guardar la configuración: {e}")

    def get_setting(self, key):
        """Obtiene un valor específico de la configuración."""
        return self.config.get(key)