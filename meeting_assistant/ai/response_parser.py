# Crear ai/response_parser.py

"""
Parser para estructurar y validar las respuestas de los LLMs.
Convierte el texto en estructuras de datos utilizables.
"""

import json
import re
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict


@dataclass
class ActionItem:
    """Representa una acción o tarea identificada."""
    id: str
    description: str
    responsible: str = "Por asignar"
    deadline: str = "Por definir"
    priority: str = "Media"
    status: str = "Pendiente"
    dependencies: List[str] = None
    estimated_effort: str = "Por definir"
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    def validate(self) -> List[str]:
        """Valida los datos y retorna lista de advertencias."""
        warnings = []
        
        if not self.description or len(self.description) < 5:
            warnings.append(f"Acción {self.id}: Descripción muy corta o vacía")
        
        if self.priority not in ["Alta", "Media", "Baja"]:
            warnings.append(f"Acción {self.id}: Prioridad inválida '{self.priority}'")
        
        # Validar formato de fecha si no es "Por definir"
        if self.deadline != "Por definir":
            try:
                datetime.strptime(self.deadline, "%Y-%m-%d")
            except ValueError:
                warnings.append(f"Acción {self.id}: Formato de fecha inválido '{self.deadline}'")
        
        return warnings


@dataclass
class MeetingInsights:
    """Representa los insights estratégicos de la reunión."""
    risks: List[Dict[str, str]]
    opportunities: List[Dict[str, str]]
    recommendations: List[Dict[str, str]]
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class MeetingMetrics:
    """Métricas y estadísticas de la reunión."""
    efficiency_score: float = 0.0
    participation_level: str = "Moderada"
    clarity_score: float = 0.0
    sentiment: str = "Neutral"
    consensus_level: str = "Medio"
    estimated_duration: str = "No especificado"
    participants_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ResponseParser:
    """Parser principal para procesar respuestas de LLM."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def parse_llm_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parsea la respuesta completa del LLM.
        
        Args:
            response: Respuesta del LLMProcessor
            
        Returns:
            Diccionario estructurado con todos los datos parseados
        """
        if not response.get('success', False):
            return {
                'success': False,
                'error': response.get('error', 'Unknown error'),
                'parsed_at': datetime.now().isoformat()
            }
        
        parsed_result = {
            'success': True,
            'parsed_at': datetime.now().isoformat(),
            'template_used': response.get('template_used'),
            'processing_metadata': response.get('metadata', {})
        }
        
        # Si hay datos estructurados JSON, usarlos directamente
        if 'structured_data' in response:
            parsed_result['structured_data'] = response['structured_data']
            parsed_result['markdown_content'] = response.get('markdown_content', '')
        else:
            # Parsear del texto raw
            raw_text = response.get('raw_response', '')
            parsed_result['markdown_content'] = raw_text
            
            # Intentar extraer diferentes secciones
            parsed_result['summary'] = self._extract_summary(raw_text)
            parsed_result['action_items'] = self._extract_action_items(raw_text)
            parsed_result['insights'] = self._extract_insights(raw_text)
            parsed_result['metrics'] = self._extract_metrics(raw_text)
            parsed_result['topics'] = self._extract_topics(raw_text)
            parsed_result['next_steps'] = self._extract_next_steps(raw_text)
            parsed_result['tags'] = self._extract_tags(raw_text)
        
        # Validar y enriquecer datos
        parsed_result = self._validate_and_enrich(parsed_result)
        
        return parsed_result
    
    def _extract_summary(self, text: str) -> str:
        """Extrae el resumen ejecutivo del texto."""
        patterns = [
            r"## RESUMEN EJECUTIVO\n(.*?)(?=##|\Z)",
            r"RESUMEN:?\n(.*?)(?=##|\n\n|\Z)",
            r"Resumen ejecutivo:?\n(.*?)(?=##|\n\n|\Z)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
            if match:
                summary = match.group(1).strip()
                # Limpiar y limitar longitud
                summary = re.sub(r'\n+', ' ', summary)
                return summary[:1000]  # Limitar a 1000 caracteres
        
        # Si no encuentra patrón, tomar primeros párrafos
        paragraphs = text.split('\n\n')
        if paragraphs:
            return paragraphs[0][:500]
        
        return "No se pudo extraer resumen"
    
    def _extract_action_items(self, text: str) -> List[Dict[str, Any]]:
        """Extrae las acciones de la respuesta."""
        actions = []
        
        # Buscar tabla de acciones
        table_pattern = r"\| Acción \|.*?\n\|[-\s|]+\n((?:\|.*?\n)+)"
        table_match = re.search(table_pattern, text, re.DOTALL)
        
        if table_match:
            rows = table_match.group(1).strip().split('\n')
            for i, row in enumerate(rows):
                if row.strip():
                    cols = [col.strip() for col in row.split('|') if col.strip()]
                    if len(cols) >= 4:
                        action = ActionItem(
                            id=f"ACT{i+1:03d}",
                            description=cols[0],
                            responsible=cols[1] if len(cols) > 1 else "Por asignar",
                            deadline=cols[2] if len(cols) > 2 else "Por definir",
                            priority=cols[3] if len(cols) > 3 else "Media"
                        )
                        actions.append(action.to_dict())
        
        # Buscar formato de lista
        if not actions:
            list_pattern = r"(?:ACCIONES|Acciones|Action Items):\s*\n((?:[-*•]\s*.*\n)+)"
            list_match = re.search(list_pattern, text, re.MULTILINE)
            
            if list_match:
                items = re.findall(r"[-*•]\s*(.*)", list_match.group(1))
                for i, item in enumerate(items):
                    action = ActionItem(
                        id=f"ACT{i+1:03d}",
                        description=item.strip()
                    )
                    actions.append(action.to_dict())
        
        return actions
    
    def _extract_insights(self, text: str) -> Dict[str, List[Dict[str, str]]]:
        """Extrae insights estratégicos."""
        insights = {
            'risks': [],
            'opportunities': [],
            'recommendations': []
        }
        
        # Patrones para cada tipo de insight
        patterns = {
            'risks': [
                r"### 🚨 Riesgos.*?\n((?:[-*•].*\n)+)",
                r"Riesgos identificados:?\n((?:[-*•].*\n)+)"
            ],
            'opportunities': [
                r"### 💡 Oportunidades.*?\n((?:[-*•].*\n)+)",
                r"Oportunidades detectadas:?\n((?:[-*•].*\n)+)"
            ],
            'recommendations': [
                r"### 📋 Recomendaciones.*?\n((?:[-*•].*\n)+)",
                r"Recomendaciones:?\n((?:[-*•].*\n)+)"
            ]
        }
        
        for insight_type, pattern_list in patterns.items():
            for pattern in pattern_list:
                match = re.search(pattern, text, re.MULTILINE | re.IGNORECASE)
                if match:
                    items = re.findall(r"[-*•]\s*\*?\*?(.+?)\*?\*?:?\s*(.*)", match.group(1))
                    for title, description in items:
                        insights[insight_type].append({
                            'title': title.strip(),
                            'description': description.strip() if description else ''
                        })
                    break
        
        return insights
    
    def _extract_metrics(self, text: str) -> Dict[str, Any]:
        """Extrae métricas de la reunión."""
        metrics = MeetingMetrics()
        
        # Buscar sección de métricas
        metrics_section = re.search(
            r"## MÉTRICAS.*?\n(.*?)(?=##|\Z)",
            text,
            re.DOTALL | re.IGNORECASE
        )
        
        if metrics_section:
            content = metrics_section.group(1)
            
            # Extraer valores específicos
            efficiency_match = re.search(r"Eficiencia:\s*\[?(Alta|Media|Baja)", content, re.IGNORECASE)
            if efficiency_match:
                efficiency_map = {'Alta': 0.8, 'Media': 0.5, 'Baja': 0.3}
                metrics.efficiency_score = efficiency_map.get(efficiency_match.group(1), 0.5)
            
            participation_match = re.search(r"participación:\s*\[?(Activa|Moderada|Pasiva)", content, re.IGNORECASE)
            if participation_match:
                metrics.participation_level = participation_match.group(1)
            
            sentiment_match = re.search(r"Tono general:\s*\[?(Positivo|Neutral|Negativo|Mixto)", content, re.IGNORECASE)
            if sentiment_match:
                metrics.sentiment = sentiment_match.group(1)
            
            consensus_match = re.search(r"consenso:\s*\[?(Alto|Medio|Bajo)", content, re.IGNORECASE)
            if consensus_match:
                metrics.consensus_level = consensus_match.group(1)
        
        return metrics.to_dict()
    
    def _extract_topics(self, text: str) -> List[Dict[str, Any]]:
        """Extrae los temas principales discutidos."""
        topics = []
        
        # Buscar sección de temas
        topics_section = re.search(
            r"## TEMAS PRINCIPALES.*?\n((?:\d+\..*\n)+)",
            text,
            re.MULTILINE | re.IGNORECASE
        )
        
        if topics_section:
            items = re.findall(r"\d+\.\s*\*?\*?(.+?)\*?\*?:?\s*(.*)", topics_section.group(1))
            for i, (title, description) in enumerate(items):
                topics.append({
                    'id': f"TOPIC{i+1:03d}",
                    'title': title.strip(),
                    'description': description.strip() if description else '',
                    'order': i + 1
                })
        
        return topics
    
    def _extract_next_steps(self, text: str) -> List[Dict[str, str]]:
        """Extrae los próximos pasos sugeridos."""
        next_steps = []
        
        patterns = [
            r"## PRÓXIMOS PASOS.*?\n((?:\d+\..*\n)+)",
            r"Próximos pasos:?\n((?:[-*•].*\n)+)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.MULTILINE | re.IGNORECASE)
            if match:
                items = re.findall(r"(?:\d+\.|-|\*|•)\s*(.+)", match.group(1))
                for i, step in enumerate(items):
                    # Intentar extraer timeframe
                    timeframe_match = re.match(r"\*?\*?(.+?)\s*$$(.+?)$$", step)
                    if timeframe_match:
                        next_steps.append({
                            'step': timeframe_match.group(1).strip(),
                            'timeframe': timeframe_match.group(2).strip(),
                            'order': i + 1
                        })
                    else:
                        next_steps.append({
                            'step': step.strip(),
                            'timeframe': 'Por definir',
                            'order': i + 1
                        })
                break
        
        return next_steps
    
    def _extract_tags(self, text: str) -> List[str]:
        """Extrae tags o etiquetas."""
        tags = []
        
        # Buscar línea de tags
        tags_match = re.search(r"(?:Tags?|Etiquetas?):\s*(.+)", text, re.IGNORECASE)
        if tags_match:
            # Extraer hashtags
            tags = re.findall(r"#(\w+)", tags_match.group(1))
        
        # Buscar hashtags en todo el texto si no se encontraron
        if not tags:
            tags = re.findall(r"#(\w+)", text)
            # Limitar a los primeros 10 únicos
            tags = list(dict.fromkeys(tags))[:10]
        
        return tags
    
    def _validate_and_enrich(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Valida y enriquece los datos parseados."""
        warnings = []
        
        # Validar acciones
        if 'action_items' in parsed_data:
            for action in parsed_data['action_items']:
                action_obj = ActionItem(**action)
                action_warnings = action_obj.validate()
                warnings.extend(action_warnings)
        
        # Enriquecer con estadísticas
        parsed_data['statistics'] = {
            'total_actions': len(parsed_data.get('action_items', [])),
            'high_priority_actions': sum(
                1 for a in parsed_data.get('action_items', [])
                if a.get('priority') == 'Alta'
            ),
            'total_risks': len(parsed_data.get('insights', {}).get('risks', [])),
            'total_opportunities': len(parsed_data.get('insights', {}).get('opportunities', [])),
            'total_topics': len(parsed_data.get('topics', [])),
            'has_next_steps': len(parsed_data.get('next_steps', [])) > 0
        }
        
        # Agregar advertencias si las hay
        if warnings:
            parsed_data['validation_warnings'] = warnings
        
        # Calcular score de calidad
        parsed_data['quality_score'] = self._calculate_quality_score(parsed_data)
        
        return parsed_data
    
    def _calculate_quality_score(self, data: Dict[str, Any]) -> float:
        """Calcula un score de calidad del análisis."""
        score = 0.0
        max_score = 10.0
        
        # Criterios de calidad
        if data.get('summary') and len(data['summary']) > 50:
            score += 2.0
        
        if data.get('statistics', {}).get('total_actions', 0) > 0:
            score += 2.0
        
        if data.get('insights'):
            if data['insights'].get('risks'):
                score += 1.0
            if data['insights'].get('opportunities'):
                score += 1.0
            if data['insights'].get('recommendations'):
                score += 1.0
        
        if data.get('topics') and len(data['topics']) >= 3:
            score += 1.5
        
        if data.get('next_steps'):
            score += 1.5
        
        return round(score / max_score, 2)
    
    def format_for_export(self, parsed_data: Dict[str, Any], format_type: str = 'markdown') -> str:
        """
        Formatea los datos parseados para exportación.
        
        Args:
            parsed_data: Datos parseados
            format_type: 'markdown', 'html', 'plain'
            
        Returns:
            Texto formateado
        """
        if format_type == 'markdown':
            return self._format_markdown(parsed_data)
        elif format_type == 'html':
            return self._format_html(parsed_data)
        elif format_type == 'plain':
            return self._format_plain(parsed_data)
        else:
            return parsed_data.get('markdown_content', '')
    
    def _format_markdown(self, data: Dict[str, Any]) -> str:
        """Formatea a Markdown."""
        # Si ya hay contenido markdown, usarlo como base
        if 'markdown_content' in data:
            return data['markdown_content']
        
        # Construir markdown desde los datos estructurados
        sections = []
        
        # Resumen
        if data.get('summary'):
            sections.append(f"## Resumen Ejecutivo\n\n{data['summary']}")
        
        # Acciones
        if data.get('action_items'):
            actions_md = "## Acciones y Tareas\n\n"
            actions_md += "| Acción | Responsable | Deadline | Prioridad |\n"
            actions_md += "|--------|-------------|----------|-----------|\\n"
            for action in data['action_items']:
                actions_md += f"| {action['description']} | {action['responsible']} | {action['deadline']} | {action['priority']} |\\n"
            sections.append(actions_md)
        
        # Insights
        if data.get('insights'):
            insights_md = "## Análisis Estratégico\n"
            
            if data['insights'].get('risks'):
                insights_md += "\n### 🚨 Riesgos Identificados\n"
                for risk in data['insights']['risks']:
                    insights_md += f"- **{risk['title']}**: {risk['description']}\\n"
            
            if data['insights'].get('opportunities'):
                insights_md += "\n### 💡 Oportunidades\n"
                for opp in data['insights']['opportunities']:
                    insights_md += f"- **{opp['title']}**: {opp['description']}\n"
                    if data['insights'].get('recommendations'):
                        insights_md += "\n### 📋 Recomendaciones\n"
                        for rec in data['insights']['recommendations']:
                            insights_md += f"- **{rec['area']}**: {rec['recommendation']}\n"
                    sections.append(insights_md)

        return "\n\n".join(sections)