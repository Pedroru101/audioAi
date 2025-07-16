"""
Gestión de archivos de reuniones y grabaciones
"""
import os
from pathlib import Path

class FileManager:
    @staticmethod
    def get_meetings_folder():
        return Path("data/meetings")

    @staticmethod
    def list_meetings():
        folder = FileManager.get_meetings_folder()
        if not folder.exists():
            return []
        return [f for f in folder.iterdir() if f.suffix == '.wav']

    @staticmethod
    def save_transcript(meeting_id, text):
        folder = FileManager.get_meetings_folder()
        folder.mkdir(parents=True, exist_ok=True)
        with open(folder / f"{meeting_id}.txt", 'w', encoding='utf-8') as f:
            f.write(text)

    @staticmethod
    def save_summary(meeting_id, summary):
        folder = FileManager.get_meetings_folder()
        folder.mkdir(parents=True, exist_ok=True)
        with open(folder / f"{meeting_id}_summary.txt", 'w', encoding='utf-8') as f:
            f.write(summary)
