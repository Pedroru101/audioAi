# utils/file_manager.py
import os
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List, Tuple
import hashlib
import zipfile
import logging

class FileManager:
    """Gestor centralizado de archivos para Meeting Assistant Pro."""
    
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.logger = logging.getLogger(__name__)
        
        # Obtener rutas base desde la configuración
        self.base_path = Path(self.config_manager.get('save_path', 
                              os.path.join(os.path.expanduser("~"), "MeetingAssistant_Recordings")))
        self.temp_path = Path(self.config_manager.get('temp_path',
                              os.path.join(os.path.expanduser("~"), ".meeting_assistant", "temp")))
        
        # Crear directorios base si no existen
        self._ensure_directories()
        
        self.logger.info(f"FileManager inicializado. Base: {self.base_path}")

    def _ensure_directories(self):
        """Asegura que existan todos los directorios necesarios."""
        directories = [
            self.base_path,
            self.temp_path,
            self.base_path / "meetings",
            self.base_path / "exports",
            self.base_path / "backups",
            self.base_path / "templates"
        ]
        
        for directory in directories:
            try:
                directory.mkdir(parents=True, exist_ok=True)
                self.logger.debug(f"Directorio asegurado: {directory}")
            except Exception as e:
                self.logger.error(f"Error creando directorio {directory}: {e}")

    def create_meeting_folder(self, custom_name: Optional[str] = None) -> str:
        """
        Crea una carpeta para una nueva reunión.
        
        Args:
            custom_name: Nombre personalizado para la carpeta (opcional)
            
        Returns:
            Ruta completa de la carpeta creada
        """
        # Generar nombre de carpeta
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        
        if custom_name:
            # Sanitizar el nombre personalizado
            safe_name = self._sanitize_filename(custom_name)
            folder_name = f"{timestamp}_{safe_name}"
        else:
            folder_name = timestamp
        
        # Crear la carpeta
        meeting_path = self.base_path / "meetings" / folder_name
        
        try:
            meeting_path.mkdir(parents=True, exist_ok=True)
            
            # Crear subcarpetas estándar
            (meeting_path / "audio").mkdir(exist_ok=True)
            (meeting_path / "transcriptions").mkdir(exist_ok=True)
            (meeting_path / "analysis").mkdir(exist_ok=True)
            (meeting_path / "exports").mkdir(exist_ok=True)
            
            # Crear archivo de metadatos
            metadata = {
                "created": datetime.now().isoformat(),
                "folder_name": folder_name,
                "custom_name": custom_name,
                "status": "in_progress",
                "version": "1.0"
            }
            
            self.save_json_file(str(meeting_path), "metadata.json", metadata)
            
            self.logger.info(f"Carpeta de reunión creada: {meeting_path}")
            return str(meeting_path)
            
        except Exception as e:
            self.logger.error(f"Error creando carpeta de reunión: {e}")
            raise

    def _sanitize_filename(self, filename: str) -> str:
        """
        Sanitiza un nombre de archivo para que sea seguro en todos los sistemas.
        
        Args:
            filename: Nombre a sanitizar
            
        Returns:
            Nombre sanitizado
        """
        # Caracteres no permitidos en nombres de archivo
        invalid_chars = '<>:"|?*\/
'
        
        # Reemplazar caracteres inválidos
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        # Limitar longitud
        filename = filename[:100]
        
        # Remover espacios al inicio y final
        filename = filename.strip()
        
        # Si queda vacío, usar un nombre por defecto
        if not filename:
            filename = "untitled"
        
        return filename

    def save_text_file(self, folder_path: str, filename: str, content: str) -> bool:
        """
        Guarda contenido de texto en un archivo.
        
        Args:
            folder_path: Ruta de la carpeta destino
            filename: Nombre del archivo
            content: Contenido a guardar
            
        Returns:
            True si se guardó exitosamente
        """
        try:
            file_path = Path(folder_path) / filename
            
            # Crear directorio si no existe
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Guardar archivo
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.logger.debug(f"Archivo de texto guardado: {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error guardando archivo de texto: {e}")
            return False

    def save_json_file(self, folder_path: str, filename: str, data: Dict[str, Any]) -> bool:
        """
        Guarda datos en formato JSON.
        
        Args:
            folder_path: Ruta de la carpeta destino
            filename: Nombre del archivo
            data: Datos a guardar
            
        Returns:
            True si se guardó exitosamente
        """
        try:
            file_path = Path(folder_path) / filename
            
            # Crear directorio si no existe
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Guardar archivo
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            self.logger.debug(f"Archivo JSON guardado: {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error guardando archivo JSON: {e}")
            return False

    def load_json_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Carga datos desde un archivo JSON.
        
        Args:
            file_path: Ruta del archivo a cargar
            
        Returns:
            Datos cargados o None si hay error
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Error cargando archivo JSON: {e}")
            return None

    def list_meetings(self, 
                     filter_date: Optional[datetime] = None,
                     filter_status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Lista todas las reuniones guardadas.
        
        Args:
            filter_date: Filtrar por fecha (opcional)
            filter_status: Filtrar por estado (opcional)
            
        Returns:
            Lista de diccionarios con información de cada reunión
        """
        meetings = []
        meetings_path = self.base_path / "meetings"
        
        if not meetings_path.exists():
            return meetings
        
        for folder in sorted(meetings_path.iterdir(), reverse=True):
            if not folder.is_dir():
                continue
            
            # Cargar metadatos
            metadata_path = folder / "metadata.json"
            if metadata_path.exists():
                metadata = self.load_json_file(str(metadata_path))
                if metadata:
                    # Añadir información adicional
                    metadata['folder_path'] = str(folder)
                    metadata['folder_name'] = folder.name
                    
                    # Calcular tamaño
                    metadata['size_mb'] = self._get_folder_size(folder) / (1024 * 1024)
                    
                    # Verificar archivos existentes
                    metadata['has_audio'] = (folder / "audio" / "audio.wav").exists()
                    metadata['has_transcription'] = (folder / "transcripcion.txt").exists()
                    metadata['has_summary'] = (folder / "resumen.md").exists()
                    
                    # Aplicar filtros
                    if filter_date:
                        meeting_date = datetime.fromisoformat(metadata.get('created', ''))
                        if meeting_date.date() != filter_date.date():
                            continue
                    
                    if filter_status and metadata.get('status') != filter_status:
                        continue
                    
                    meetings.append(metadata)
        
        return meetings

    def _get_folder_size(self, folder_path: Path) -> int:
        """Calcula el tamaño total de una carpeta en bytes."""
        total_size = 0
        
        for file_path in folder_path.rglob('*'):
            if file_path.is_file():
                total_size += file_path.stat().st_size
        
        return total_size

    def get_meeting_data(self, meeting_path: str) -> Dict[str, Any]:
        """
        Obtiene todos los datos de una reunión.
        
        Args:
            meeting_path: Ruta de la carpeta de la reunión
            
        Returns:
            Diccionario con todos los datos de la reunión
        """
        meeting_data = {}
        meeting_folder = Path(meeting_path)
        
        if not meeting_folder.exists():
            self.logger.error(f"La carpeta de reunión no existe: {meeting_path}")
            return meeting_data
        
        # Cargar metadatos
        metadata_path = meeting_folder / "metadata.json"
        if metadata_path.exists():
            meeting_data['metadata'] = self.load_json_file(str(metadata_path))
        
        # Cargar transcripción
        transcription_path = meeting_folder / "transcripcion.txt"
        if transcription_path.exists():
            with open(transcription_path, 'r', encoding='utf-8') as f:
                meeting_data['transcription'] = f.read()
        
        # Cargar resumen
        summary_path = meeting_folder / "resumen.md"
        if summary_path.exists():
            with open(summary_path, 'r', encoding='utf-8') as f:
                meeting_data['summary'] = f.read()
        
        # Cargar acciones
        actions_path = meeting_folder / "acciones.json"
        if actions_path.exists():
            meeting_data['actions'] = self.load_json_file(str(actions_path))
        
        # Cargar análisis
        analytics_path = meeting_folder / "analytics.json"
        if analytics_path.exists():
            meeting_data['analytics'] = self.load_json_file(str(analytics_path))
        
        # Información de archivos
        meeting_data['files'] = {
            'audio': str(meeting_folder / "audio" / "audio.wav") if (meeting_folder / "audio" / "audio.wav").exists() else None,
            'transcription': str(transcription_path) if transcription_path.exists() else None,
            'summary': str(summary_path) if summary_path.exists() else None,
            'folder': str(meeting_folder)
        }
        
        return meeting_data

    def export_meeting(self, 
                      meeting_path: str,
                      export_format: str = 'zip',
                      include_audio: bool = True) -> Optional[str]:
        """
        Exporta una reunión en el formato especificado.
        
        Args:
            meeting_path: Ruta de la carpeta de la reunión
            export_format: Formato de exportación ('zip', 'pdf', 'markdown')
            include_audio: Si incluir el archivo de audio en la exportación
            
        Returns:
            Ruta del archivo exportado o None si hay error
        """
        meeting_folder = Path(meeting_path)
        
        if not meeting_folder.exists():
            self.logger.error(f"La carpeta de reunión no existe: {meeting_path}")
            return None
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        export_name = f"{meeting_folder.name}_export_{timestamp}"
        
        if export_format == 'zip':
            return self._export_as_zip(meeting_folder, export_name, include_audio)
        elif export_format == 'markdown':
            return self._export_as_markdown(meeting_folder, export_name)
        else:
            self.logger.error(f"Formato de exportación no soportado: {export_format}")
            return None

    def _export_as_zip(self, 
                      meeting_folder: Path,
                      export_name: str,
                      include_audio: bool) -> Optional[str]:
        """Exporta la reunión como archivo ZIP."""
        export_path = self.base_path / "exports" / f"{export_name}.zip"
        
        try:
            with zipfile.ZipFile(export_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Añadir todos los archivos excepto audio si no se solicita
                for file_path in meeting_folder.rglob('*'):
                    if file_path.is_file():
                        # Saltar archivos de audio si no se incluyen
                        if not include_audio and file_path.suffix in ['.wav', '.mp3', '.m4a']:
                            continue
                        
                        # Añadir archivo al ZIP
                        arcname = file_path.relative_to(meeting_folder.parent)
                        zipf.write(file_path, arcname)
            
            self.logger.info(f"Reunión exportada como ZIP: {export_path}")
            return str(export_path)
            
        except Exception as e:
            self.logger.error(f"Error exportando como ZIP: {e}")
            return None

    def _export_as_markdown(self, meeting_folder: Path, export_name: str) -> Optional[str]:
        """Exporta la reunión como un único archivo Markdown."""
        export_path = self.base_path / "exports" / f"{export_name}.md"
        
        try:
            meeting_data = self.get_meeting_data(str(meeting_folder))
            
            # Construir el documento Markdown
            content = []
            
            # Título y metadatos
            metadata = meeting_data.get('metadata', {})
            content.append(f"# Reunión: {metadata.get('custom_name', 'Sin título')}")
            content.append(f"**Fecha:** {metadata.get('created', 'Desconocida')}")
            content.append("")
            
            # Resumen
            if 'summary' in meeting_data:
                content.append("## Resumen")
                content.append(meeting_data['summary'])
                content.append("")
            
            # Acciones
            if 'actions' in meeting_data and meeting_data['actions']:
                content.append("## Acciones y Tareas")
                content.append("| Acción | Responsable | Deadline | Prioridad |")
                content.append("|--------|-------------|----------|-----------|")
                
                for action in meeting_data['actions']:
                    content.append(
                        f"| {action.get('action', '')} | "
                        f"{action.get('responsible', '')} | "
                        f"{action.get('deadline', '')} | "
                        f"{action.get('priority', '')} |"
                    )
                content.append("")
            
            # Transcripción
            if 'transcription' in meeting_data:
                content.append("## Transcripción Completa")
                content.append("```")
                content.append(meeting_data['transcription'])
                content.append("```")
            
            # Guardar archivo
            with open(export_path, 'w', encoding='utf-8') as f:
                f.write('
'.join(content))
            
            self.logger.info(f"Reunión exportada como Markdown: {export_path}")
            return str(export_path)
            
        except Exception as e:
            self.logger.error(f"Error exportando como Markdown: {e}")
            return None

    def delete_meeting(self, meeting_path: str, confirm: bool = True) -> bool:
        """
        Elimina una carpeta de reunión.
        
        Args:
            meeting_path: Ruta de la carpeta a eliminar
            confirm: Si se requiere confirmación (por seguridad)
            
        Returns:
            True si se eliminó exitosamente
        """
        meeting_folder = Path(meeting_path)
        
        if not meeting_folder.exists():
            self.logger.warning(f"La carpeta no existe: {meeting_path}")
            return False
        
        if not confirm:
            self.logger.warning("Eliminación cancelada: se requiere confirmación")
            return False
        
        try:
            # Hacer backup antes de eliminar
            backup_name = f"{meeting_folder.name}_deleted_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            backup_path = self.base_path / "backups" / backup_name
            
            shutil.copytree(meeting_folder, backup_path)
            self.logger.info(f"Backup creado antes de eliminar: {backup_path}")
            
            # Eliminar la carpeta original
            shutil.rmtree(meeting_folder)
            self.logger.info(f"Reunión eliminada: {meeting_path}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error eliminando reunión: {e}")
            return False

    def cleanup_old_meetings(self, days: int = 30) -> int:
        """
        Limpia reuniones antiguas según la política de retención.
        
        Args:
            days: Número de días a mantener las reuniones
            
        Returns:
            Número de reuniones eliminadas
        """
        if not self.config_manager.get('auto_delete_recordings', False):
            self.logger.info("Limpieza automática deshabilitada")
            return 0
        
        retention_days = self.config_manager.get('retention_days', days)
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        deleted_count = 0
        
        meetings = self.list_meetings()
        
        for meeting in meetings:
            try:
                created_date = datetime.fromisoformat(meeting.get('created', ''))
                
                if created_date < cutoff_date:
                    if self.delete_meeting(meeting['folder_path'], confirm=True):
                        deleted_count += 1
                        self.logger.info(f"Reunión antigua eliminada: {meeting['folder_name']}")
                        
            except Exception as e:
                self.logger.error(f"Error procesando reunión para limpieza: {e}")
        
        return deleted_count

    def get_storage_info(self) -> Dict[str, Any]:
        """
        Obtiene información sobre el uso de almacenamiento.
        
        Returns:
            Diccionario con información de almacenamiento
        """
        total_size = 0
        file_count = 0
        meeting_count = len(self.list_meetings())
        
        # Calcular tamaño total
        for file_path in self.base_path.rglob('*'):
            if file_path.is_file():
                total_size += file_path.stat().st_size
                file_count += 1
        
        # Obtener espacio libre en el disco
        stat = os.statvfs(self.base_path)
        free_space = stat.f_bavail * stat.f_frsize
        
        return {
            'total_size_mb': total_size / (1024 * 1024),
            'total_size_gb': total_size / (1024 * 1024 * 1024),
            'file_count': file_count,
            'meeting_count': meeting_count,
            'free_space_gb': free_space / (1024 * 1024 * 1024),
            'base_path': str(self.base_path),
            'largest_meetings': self._get_largest_meetings(5)
        }

    def _get_largest_meetings(self, count: int = 5) -> List[Dict[str, Any]]:
        """Obtiene las reuniones más grandes por tamaño."""
        meetings = self.list_meetings()
        
        # Ordenar por tamaño
        meetings.sort(key=lambda x: x.get('size_mb', 0), reverse=True)
        
        return meetings[:count]

    def verify_integrity(self, meeting_path: str) -> Dict[str, bool]:
        """
        Verifica la integridad de los archivos de una reunión.
        
        Args:
            meeting_path: Ruta de la carpeta de la reunión
            
        Returns:
            Diccionario con el estado de cada archivo esperado
        """
        meeting_folder = Path(meeting_path)
        
        expected_files = {
            'metadata': meeting_folder / "metadata.json",
            'audio': meeting_folder / "audio" / "audio.wav",
            'transcription': meeting_folder / "transcripcion.txt",
            'summary': meeting_folder / "resumen.md",
            'actions': meeting_folder / "acciones.json"
        }
        
        integrity = {}
        
        for file_type, file_path in expected_files.items():
            integrity[file_type] = file_path.exists()
        
        return integrity
