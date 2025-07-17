# Crear ai/__init__.py para completar el módulo
ai_init_code = '''# ai/__init__.py
"""
Módulo de Inteligencia Artificial para Meeting Assistant Pro.
Gestiona el procesamiento con LLMs, análisis y generación de insights.
"""

from .prompt_templates import PromptTemplates
from .llm_processor import LLMProcessor
from .response_parser import ResponseParser
from .analytics_engine import AnalyticsEngine

__all__ = [
    'PromptTemplates',
    'LLMProcessor',
    'ResponseParser',
    'AnalyticsEngine'
]

# Versión del módulo
__version__ = '1.0.0'
'''

# Guardar el archivo
with open('ai_init.py', 'w', encoding='utf-8') as f:
    f.write(ai_init_code)

print("✅ ai/__init__.py creado exitosamente")

# Crear un ejemplo de integración completa
integration_example = '''# ai/meeting_processor.py
"""
Procesador integrado que combina todos los componentes del módulo AI.
Este es el punto de entrada principal para procesar reuniones.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import json
import os

from .prompt_templates import PromptTemplates
from .llm_processor import LLMProcessor
from .response_parser import ResponseParser
from .analytics_engine import AnalyticsEngine


class MeetingProcessor:
    """
    Procesador principal que orquesta todo el flujo de análisis de reuniones.
    """
    
    def __init__(self, config_manager, file_manager):
        self.config_manager = config_manager
        self.file_manager = file_manager
        self.logger = logging.getLogger(__name__)
        
        # Inicializar componentes
        self.llm_processor = LLMProcessor(config_manager)
        self.response_parser = ResponseParser()
        self.analytics_engine = AnalyticsEngine()
        
        self.logger.info("MeetingProcessor inicializado")
    
    def process_meeting(self,
                       transcription_path: str,
                       meeting_context: Optional[Dict[str, Any]] = None,
                       output_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Procesa una reunión completa desde la transcripción hasta el análisis final.
        
        Args:
            transcription_path: Ruta al archivo de transcripción
            meeting_context: Contexto adicional de la reunión
            output_path: Ruta donde guardar los resultados
            
        Returns:
            Diccionario con todos los resultados del procesamiento
        """
        try:
            self.logger.info(f"Iniciando procesamiento de: {transcription_path}")
            
            # 1. Cargar transcripción
            transcription = self._load_transcription(transcription_path)
            
            # 2. Preparar contexto
            context = self._prepare_context(meeting_context)
            
            # 3. Procesar con LLM
            llm_result = self._process_with_llm(transcription, context)
            
            # 4. Parsear respuesta
            parsed_result = self._parse_response(llm_result)
            
            # 5. Análisis avanzado
            analytics_result = self._analyze_meeting(transcription, parsed_result, context)
            
            # 6. Compilar resultados
            final_result = self._compile_results(
                transcription, context, llm_result, parsed_result, analytics_result
            )
            
            # 7. Guardar resultados
            if output_path:
                self._save_results(final_result, output_path)
            else:
                output_path = self._save_results(final_result)
            
            final_result['output_path'] = output_path
            
            self.logger.info(f"Procesamiento completado. Resultados en: {output_path}")
            return final_result
            
        except Exception as e:
            self.logger.error(f"Error en procesamiento: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _load_transcription(self, path: str) -> str:
        """Carga el archivo de transcripción."""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            raise Exception(f"Error al cargar transcripción: {str(e)}")
    
    def _prepare_context(self, meeting_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Prepara el contexto de la reunión."""
        default_context = {
            'title': 'Reunión sin título',
            'date': datetime.now().strftime('%Y-%m-%d'),
            'participants': [],
            'objective': '',
            'tags': []
        }
        
        if meeting_context:
            default_context.update(meeting_context)
        
        # Agregar información del sistema
        default_context['processed_by'] = 'Meeting Assistant Pro - MIA'
        default_context['version'] = '1.0.0'
        
        return default_context
    
    def _process_with_llm(self, transcription: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Procesa la transcripción con el LLM."""
        config = self.config_manager.get_config()
        
        # Determinar qué templates usar
        templates_to_use = []
        
        if config.get('generate_summary', True):
            templates_to_use.append('ADVANCED_ANALYSIS_TEMPLATE')
        
        if config.get('generate_actions', True) and 'ADVANCED_ANALYSIS_TEMPLATE' not in templates_to_use:
            templates_to_use.append('ACTION_EXTRACTION_TEMPLATE')
        
        if not templates_to_use:
            templates_to_use = ['ADVANCED_ANALYSIS_TEMPLATE']  # Default
        
        # Procesar con el template principal
        primary_template = templates_to_use[0]
        result = self.llm_processor.process_transcription(
            transcription=transcription,
            template_name=primary_template,
            meeting_context=context
        )
        
        # Si hay templates adicionales, procesarlos
        if len(templates_to_use) > 1:
            additional_results = self.llm_processor.process_multiple_templates(
                transcription=transcription,
                template_names=templates_to_use[1:],
                meeting_context=context
            )
            result['additional_analyses'] = additional_results
        
        return result
    
    def _parse_response(self, llm_result: Dict[str, Any]) -> Dict[str, Any]:
        """Parsea la respuesta del LLM."""
        return self.response_parser.parse_llm_response(llm_result)
    
    def _analyze_meeting(self, 
                        transcription: str, 
                        parsed_result: Dict[str, Any],
                        context: Dict[str, Any]) -> Dict[str, Any]:
        """Realiza análisis avanzado de la reunión."""
        return self.analytics_engine.analyze_meeting(
            transcription=transcription,
            parsed_data=parsed_result,
            meeting_context=context
        )
    
    def _compile_results(self, 
                        transcription: str,
                        context: Dict[str, Any],
                        llm_result: Dict[str, Any],
                        parsed_result: Dict[str, Any],
                        analytics_result: Dict[str, Any]) -> Dict[str, Any]:
        """Compila todos los resultados en una estructura unificada."""
        return {
            'success': True,
            'timestamp': datetime.now().isoformat(),
            'meeting_info': {
                'title': context.get('title'),
                'date': context.get('date'),
                'participants': context.get('participants'),
                'objective': context.get('objective'),
                'transcription_length': len(transcription)
            },
            'processing_info': {
                'llm_provider': self.llm_processor.get_provider_info(),
                'template_used': llm_result.get('template_used'),
                'processing_time': llm_result.get('metadata', {}).get('processing_time'),
                'quality_score': parsed_result.get('quality_score')
            },
            'content': {
                'summary': parsed_result.get('summary') or parsed_result.get('structured_data', {}).get('summary', {}).get('executive_summary'),
                'action_items': parsed_result.get('action_items') or parsed_result.get('structured_data', {}).get('action_items', []),
                'insights': parsed_result.get('insights') or parsed_result.get('structured_data', {}).get('strategic_analysis', {}),
                'topics': parsed_result.get('topics') or parsed_result.get('structured_data', {}).get('topics', []),
                'next_steps': parsed_result.get('next_steps') or parsed_result.get('structured_data', {}).get('next_steps', []),
                'tags': parsed_result.get('tags') or parsed_result.get('structured_data', {}).get('tags', [])
            },
            'analytics': analytics_result,
            'raw_outputs': {
                'markdown': parsed_result.get('markdown_content', ''),
                'structured_data': parsed_result.get('structured_data', {})
            }
        }
    
    def _save_results(self, results: Dict[str, Any], output_path: Optional[str] = None) -> str:
        """Guarda los resultados en diferentes formatos."""
        if not output_path:
            # Crear carpeta de salida basada en timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = self.file_manager.create_output_folder(f"analysis_{timestamp}")
        
        # Asegurar que el directorio existe
        os.makedirs(output_path, exist_ok=True)
        
        # 1. Guardar JSON completo
        json_path = os.path.join(output_path, 'analysis_complete.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        # 2. Guardar resumen en Markdown
        md_path = os.path.join(output_path, 'summary.md')
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(self._generate_markdown_summary(results))
        
        # 3. Guardar acciones en formato CSV
        if results['content']['action_items']:
            csv_path = os.path.join(output_path, 'action_items.csv')
            self._save_actions_csv(results['content']['action_items'], csv_path)
        
        # 4. Guardar reporte de analytics
        analytics_path = os.path.join(output_path, 'analytics_report.md')
        with open(analytics_path, 'w', encoding='utf-8') as f:
            f.write(self.analytics_engine.generate_analytics_report(results['analytics']))
        
        # 5. Guardar versión de texto plano
        txt_path = os.path.join(output_path, 'summary.txt')
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(self.response_parser.format_for_export(
                {'markdown_content': results['raw_outputs']['markdown']}, 
                'plain'
            ))
        
        self.logger.info(f"Resultados guardados en: {output_path}")
        return output_path
    
    def _generate_markdown_summary(self, results: Dict[str, Any]) -> str:
        """Genera un resumen en formato Markdown."""
        md = f"""# Análisis de Reunión: {results['meeting_info']['title']}

**Fecha**: {results['meeting_info']['date']}  
**Participantes**: {', '.join(results['meeting_info']['participants']) if results['meeting_info']['participants'] else 'No especificados'}  
**Score de calidad**: {results['processing_info']['quality_score']}/1.0  
**Score general**: {results['analytics']['overall_score']}/1.0

## Resumen Ejecutivo

{results['content']['summary']}

## Acciones y Tareas

"""
        
        if results['content']['action_items']:
            md += "| # | Acción | Responsable | Deadline | Prioridad |\n"
            md += "|---|--------|-------------|----------|-----------|\\n"
            for i, action in enumerate(results['content']['action_items'], 1):
                md += f"| {i} | {action['description']} | {action['responsible']} | {action['deadline']} | {action['priority']} |\\n"
        else:
            md += "*No se identificaron acciones específicas*\n"
        
        # Insights
        if results['content']['insights']:
            md += "\n## Análisis Estratégico\n"
            
            if results['content']['insights'].get('risks'):
                md += "\n### 🚨 Riesgos\n"
                for risk in results['content']['insights']['risks']:
                    md += f"- {risk.get('title', risk.get('description', 'Riesgo'))}\n"
            
            if results['content']['insights'].get('opportunities'):
                md += "\n### 💡 Oportunidades\n"
                for opp in results['content']['insights']['opportunities']:
                    md += f"- {opp.get('title', opp.get('description', 'Oportunidad'))}\n"
        
        # Próximos pasos
        if results['content']['next_steps']:
            md += "\n## Próximos Pasos\n"
            for step in results['content']['next_steps']:
                md += f"- {step.get('step', step.get('action', 'Paso'))} ({step.get('timeframe', 'Por definir')})\n"
        
        # Tags
        if results['content']['tags']:
            md += f"\n## Tags\n{' '.join(['#' + tag for tag in results['content']['tags']])}\n"
        
        # Métricas clave
        md += f"""
## Métricas Clave

- **Duración estimada**: {results['analytics']['basic_metrics']['estimated_duration_formatted']}
- **Eficiencia**: {results['analytics']['efficiency_metrics']['efficiency_score']}/1.0
- **Sentimiento**: {results['analytics']['sentiment_analysis']['dominant']} ({results['analytics']['sentiment_analysis']['score']})
- **Consenso**: {results['analytics']['interaction_patterns']['consensus_indicator']:.0%}

---
*Análisis generado por Meeting Assistant Pro - {datetime.now().strftime('%Y-%m-%d %H:%M')}*
"""
        
        return md
    
    def _save_actions_csv(self, actions: List[Dict[str, Any]], path: str):
        """Guarda las acciones en formato CSV."""
        import csv
        
        with open(path, 'w', newline='', encoding='utf-8') as f:
            if actions:
                fieldnames = ['id', 'description', 'responsible', 'deadline', 'priority', 'status']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                
                writer.writeheader()
                for action in actions:
                    writer.writerow({
                        'id': action.get('id', ''),
                        'description': action.get('description', ''),
                        'responsible': action.get('responsible', ''),
                        'deadline': action.get('deadline', ''),
                        'priority': action.get('priority', ''),
                        'status': action.get('status', 'Pendiente')
                    })
    
    def batch_process_meetings(self, 
                             transcription_paths: List[str],
                             output_base_path: str) -> Dict[str, Any]:
        """
        Procesa múltiples reuniones en lote.
        
        Args:
            transcription_paths: Lista de rutas a transcripciones
            output_base_path: Carpeta base para guardar resultados
            
        Returns:
            Resumen del procesamiento en lote
        """
        results = {
            'total': len(transcription_paths),
            'successful': 0,
            'failed': 0,
            'results': []
        }
        
        for i, path in enumerate(transcription_paths, 1):
            self.logger.info(f"Procesando {i}/{len(transcription_paths)}: {path}")
            
            try:
                # Crear subcarpeta para esta reunión
                meeting_name = os.path.splitext(os.path.basename(path))[0]
                output_path = os.path.join(output_base_path, meeting_name)
                
                # Procesar
                result = self.process_meeting(path, output_path=output_path)
                
                if result.get('success'):
                    results['successful'] += 1
                else:
                    results['failed'] += 1
                
                results['results'].append({
                    'file': path,
                    'success': result.get('success'),
                    'output': result.get('output_path'),
                    'score': result.get('analytics', {}).get('overall_score')
                })
                
            except Exception as e:
                self.logger.error(f"Error procesando {path}: {str(e)}")
                results['failed'] += 1
                results['results'].append({
                    'file': path,
                    'success': False,
                    'error': str(e)
                })
        
        # Guardar resumen del lote
        summary_path = os.path.join(output_base_path, 'batch_summary.json')
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
        
        return results
    
    def reprocess_with_different_template(self,
                                        original_results_path: str,
                                        new_template: str) -> Dict[str, Any]:
        """
        Reprocesa una reunión con un template diferente.
        
        Args:
            original_results_path: Ruta a los resultados originales
            new_template: Nombre del nuevo template a usar
            
        Returns:
            Nuevos resultados
        """
        # Cargar resultados originales
        with open(os.path.join(original_results_path, 'analysis_complete.json'), 'r', encoding='utf-8') as f:
            original = json.load(f)
        
        # Extraer información necesaria
        transcription = original['raw_outputs'].get('transcription', '')
        context = original['meeting_info']
        
        # Reprocesar con nuevo template
        new_result = self.llm_processor.process_transcription(
            transcription=transcription,
            template_name=new_template,
            meeting_context=context
        )
        
        # Parsear y analizar
        parsed = self.response_parser.parse_llm_response(new_result)
        analytics = self.analytics_engine.analyze_meeting(transcription, parsed, context)
        
        # Compilar y guardar
        final_result = self._compile_results(transcription, context, new_result, parsed, analytics)
        
        # Guardar en subcarpeta
        new_output_path = os.path.join(original_results_path, f'reprocess_{new_template.lower()}')
        self._save_results(final_result, new_output_path)
        
        return final_result
'''

# Guardar el archivo de integración
with open('meeting_processor.py', 'w', encoding='utf-8') as f:
    f.write(integration_example)

print("✅ ai/meeting_processor.py creado exitosamente")
print("\n🎉 FASE 3 COMPLETADA!")
print("\nComponentes creados:")
print("1. ✓ prompt_templates.py - Templates modulares y personalizables")
print("2. ✓ llm_processor.py - Procesador multi-proveedor (OpenAI, Ollama, OpenRouter)")
print("3. ✓ response_parser.py - Parser inteligente de respuestas")
print("4. ✓ analytics_engine.py - Motor de análisis avanzado")
print("5. ✓ meeting_processor.py - Integrador principal")
print("6. ✓ __init__.py - Inicializador del módulo")