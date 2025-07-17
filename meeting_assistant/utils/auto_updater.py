import requests
import os
import json
import shutil
import zipfile
from typing import Optional
from meeting_assistant.config.config_manager import ConfigManager  # Import absoluto usando nombre de paquete
from meeting_assistant.utils.file_manager import FileManager
from plyer import notification  # Para notificaciones
from PyQt5.QtCore import QTimer  # Para scheduling (integra con Qt)

class AutoUpdater:
    def __init__(self, config_manager: ConfigManager, file_manager: FileManager):
        self.config = config_manager
        self.file_manager = file_manager
        self.github_repo = self.config.get('github_repo')  # Ahora se obtiene de la configuración
        if not self.github_repo:
            self.github_repo = "user/repo"  # Valor por defecto pero mostrará advertencia
            print(f"Warning: No GitHub repo configured in settings. Using default: {self.github_repo}")
        
        self.current_version = self.config.get('version', '1.0.0')
        self.update_url = f"https://api.github.com/repos/{self.github_repo}/releases/latest"
        self.download_dir = os.path.join(os.path.dirname(__file__), '../../updates')
        os.makedirs(self.download_dir, exist_ok=True)

    def schedule_update_check(self, interval_hours: int = 24):
        """Programa chequeos periódicos (integra con Qt QTimer)."""
        interval_ms = interval_hours * 60 * 60 * 1000
        self.timer = QTimer()
        self.timer.timeout.connect(lambda: self.check_for_updates(silent=True))
        self.timer.start(interval_ms)

    def check_for_updates(self, silent: bool = False) -> Optional[str]:
        """Verifica si hay nueva versión en GitHub (con opción silent)."""
        try:
            response = requests.get(self.update_url, timeout=10)
            
            if response.status_code == 404:
                if not silent:
                    print(f"Repo {self.github_repo} not found. Configure correct repo in settings.")
                return None
                
            response.raise_for_status()
            latest = response.json()
            latest_version = latest['tag_name']
            
            if latest_version > self.current_version:
                if not silent:
                    notification.notify(
                        title="Actualización disponible", 
                        message=f"Nueva versión {latest_version} lista."
                    )
                return latest_version
            return None
            
        except requests.exceptions.RequestException as e:
            if not silent:
                print(f"Error checking updates: {str(e)}")
            return None
        except Exception as e:
            print(f"Unexpected error checking updates: {str(e)}")
            return None

    def download_update(self, version: str, resume: bool = False) -> str:
        """Descarga incremental con resume."""
        download_url = f"https://github.com/{self.github_repo}/releases/download/{version}/MeetingAssistantPro_{version}_portable.zip"
        local_path = os.path.join(self.download_dir, f"update_{version}.zip")
        
        headers = {}
        if resume and os.path.exists(local_path):
            headers['Range'] = f"bytes={os.path.getsize(local_path)}-"
        
        with requests.get(download_url, headers=headers, stream=True) as r:
            r.raise_for_status()
            mode = 'ab' if resume else 'wb'
            with open(local_path, mode) as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        return local_path

    def install_update(self, zip_path: str, new_version: str) -> bool:
        """Instalación silenciosa (agrega new_version para actualizar config)."""
        try:
            backup_dir = os.path.join(self.download_dir, 'backup')
            os.makedirs(backup_dir, exist_ok=True)
            # Backup actual
            shutil.copytree(os.path.dirname(__file__), backup_dir, dirs_exist_ok=True)
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(os.path.dirname(__file__))
            
            self.config.set('version', new_version)  # Actualiza a nueva versión
            self.current_version = new_version  # Actualiza internamente
            notification.notify(title="Actualización completada", message="Reinicia la app para aplicar cambios.")
            return True
        except Exception as e:
            print(f"Error instalando: {e}")
            self.rollback(backup_dir)
            return False

    def rollback(self, backup_dir: str):
        """Rollback en caso de error."""
        try:
            shutil.copytree(backup_dir, os.path.dirname(__file__), dirs_exist_ok=True)
            shutil.rmtree(backup_dir)
            notification.notify(title="Rollback completado", message="Vuelta a versión anterior por error.")
        except Exception as e:
            print(f"Error en rollback: {e}")

# Ejemplo de uso (prueba standalone)
if __name__ == '__main__':
    config_mgr = ConfigManager()  # Asume init sin params; ajusta si necesita
    file_mgr = FileManager(config_mgr)  # Pasa config si es necesario
    updater = AutoUpdater(config_mgr, file_mgr)
    updater.schedule_update_check(24)  # Prueba scheduling
    new_version = updater.check_for_updates(silent=False)
    if new_version:
        zip_path = updater.download_update(new_version)
        updater.install_update(zip_path, new_version)