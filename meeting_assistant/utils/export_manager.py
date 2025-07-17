import os
import json
from typing import Dict, List
from jinja2 import Environment, FileSystemLoader, Template
import matplotlib.pyplot as plt
from weasyprint import HTML  # Para PDF
from meeting_assistant.utils.file_manager import FileManager
from meeting_assistant.config.config_manager import ConfigManager

class ExportManager:
    def __init__(self, config_manager: ConfigManager, file_manager: FileManager):
        self.config = config_manager
        self.file_manager = file_manager
        self.templates_dir = os.path.join(os.path.dirname(__file__), '../../templates')
        self.env = Environment(loader=FileSystemLoader(self.templates_dir))

    def generate_graph(self, data: Dict, output_path: str):
        """Genera gráfico simple (ej: pie chart de métricas)."""
        # Ejemplo: Gráfico de sentimiento (positivo/negativo/neutral)
        sentiments = data.get('analysis', {}).get('sentiments', {'positivo': 0, 'negativo': 0, 'neutral': 0})
        labels = list(sentiments.keys())
        sizes = list(sentiments.values())
        plt.figure(figsize=(6, 4))
        plt.pie(sizes, labels=labels, autopct='%1.1f%%')
        plt.title('Análisis de Sentimiento')
        plt.savefig(output_path)
        plt.close()

    def render_template(self, template_name: str, data: Dict) -> str:
        """Renderiza plantilla HTML con datos."""
        template = self.env.get_template(template_name)
        return template.render(data=data)

    def export_to_html(self, meeting_id: str, template_name: str, output_path: str) -> str:
        """Exporta a HTML interactivo."""
        data = self.file_manager.load_meeting_data(meeting_id)  # Asume método en FileManager
        html_content = self.render_template(template_name, data)
        with open(output_path, 'w') as f:
            f.write(html_content)
        return output_path

    def export_to_pdf(self, meeting_id: str, template_name: str, output_path: str) -> str:
        """Exporta a PDF profesional."""
        data = self.file_manager.load_meeting_data(meeting_id)
        graph_path = os.path.join(os.path.dirname(output_path), f'{meeting_id}_graph.png')
        self.generate_graph(data, graph_path)
        data['graph_path'] = graph_path  # Para incluir en template
        html_content = self.render_template(template_name, data)
        HTML(string=html_content).write_pdf(output_path)
        return output_path

    def batch_export(self, meeting_ids: List[str], format: str, template_name: str, output_dir: str):
        """Exportación por lotes."""
        os.makedirs(output_dir, exist_ok=True)
        for mid in meeting_ids:
            if format == 'pdf':
                self.export_to_pdf(mid, template_name, os.path.join(output_dir, f'{mid}.pdf'))
            elif format == 'html':
                self.export_to_html(mid, template_name, os.path.join(output_dir, f'{mid}.html'))

# Ejemplo standalone
if __name__ == '__main__':
    config_mgr = ConfigManager()
    file_mgr = FileManager(config_mgr)
    exporter = ExportManager(config_mgr, file_mgr)
    # Prueba con un meeting_id ficticio
    exporter.export_to_pdf('test_meeting', 'pdf_report.html', 'test.pdf')