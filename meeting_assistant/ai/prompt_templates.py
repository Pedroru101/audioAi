# Crear ai/prompt_templates.py

"""
Templates de prompts para el procesamiento con LLM.
Diseñados para ser modulares y personalizables.
"""

from typing import Dict, List, Optional
from datetime import datetime

class PromptTemplates:
    """Gestor de templates de prompts para diferentes casos de uso."""

    @staticmethod
    def get_prompt(template_name: str, **kwargs) -> str:
        """Obtiene un prompt formateado dado el nombre del template y el contexto."""
        try:
            template = getattr(PromptTemplates, template_name)
        except AttributeError:
            raise KeyError(f"Template {template_name} no encontrado")
        return template.format(**kwargs)
    
    # Template base para análisis completo
    ADVANCED_ANALYSIS_TEMPLATE = """Eres MIA (Meeting Intelligence Assistant), un asistente experto en análisis de reuniones.

CONTEXTO DE LA REUNIÓN:
- Título: {title}
- Fecha: {date}
- Duración: {duration}
- Participantes: {participants}
- Objetivo: {objective}

Tu tarea es analizar la siguiente transcripción y proporcionar un análisis completo y estructurado.

FORMATO DE SALIDA REQUERIDO:

## RESUMEN EJECUTIVO
[Resumen conciso de máximo 200 palabras con los puntos clave de la reunión]

## DECISIONES Y ACCIONES
| Acción | Responsable | Deadline | Prioridad | Estado |
|--------|-------------|----------|-----------|---------|
| [Descripción clara y específica] | [Nombre o "Por asignar"] | [DD/MM/YYYY o "Por definir"] | [Alta/Media/Baja] | [Pendiente] |

## ANÁLISIS ESTRATÉGICO

### 🚨 Riesgos Identificados
- **[Riesgo 1]**: [Descripción del riesgo y su impacto potencial]
- **[Riesgo 2]**: [Descripción del riesgo y su impacto potencial]

### 💡 Oportunidades Detectadas
- **[Oportunidad 1]**: [Descripción y beneficio potencial]
- **[Oportunidad 2]**: [Descripción y beneficio potencial]

### 📋 Recomendaciones Estratégicas
1. **[Área de mejora]**: [Recomendación específica y accionable]
2. **[Área de mejora]**: [Recomendación específica y accionable]

## MÉTRICAS DE LA REUNIÓN
- **Eficiencia**: [Alta/Media/Baja] - [Justificación breve]
- **Nivel de participación**: [Activa/Moderada/Pasiva]
- **Claridad de objetivos**: [Clara/Parcial/Confusa]
- **Tono general**: [Positivo/Neutral/Tenso/Constructivo]
- **Nivel de consenso**: [Alto/Medio/Bajo]

## TEMAS PRINCIPALES DISCUTIDOS
1. **[Tema 1]**: [Breve descripción y conclusiones]
2. **[Tema 2]**: [Breve descripción y conclusiones]
3. **[Tema 3]**: [Breve descripción y conclusiones]
4. **[Tema 4]**: [Breve descripción y conclusiones]
5. **[Tema 5]**: [Breve descripción y conclusiones]

## PRÓXIMOS PASOS RECOMENDADOS
1. **Inmediato (0-7 días)**: [Acción específica]
2. **Corto plazo (1-4 semanas)**: [Acción específica]
3. **Mediano plazo (1-3 meses)**: [Acción específica]

## INFORMACIÓN ADICIONAL
- **Temas pendientes para próxima reunión**: [Lista de temas]
- **Recursos necesarios identificados**: [Lista de recursos]
- **Decisiones que requieren escalamiento**: [Si aplica]

## CLASIFICACIÓN Y ETIQUETAS
- **Tipo de reunión**: [Brainstorming/Planificación/Revisión/Decisión/Informativa/Seguimiento]
- **Departamentos involucrados**: [Lista de departamentos]
- **Proyecto relacionado**: [Nombre del proyecto si aplica]
- **Tags**: #tag1 #tag2 #tag3 #tag4 #tag5

---JSON_OUTPUT_START---
{
  "metadata": {
    "meeting_id": "{meeting_id}",
    "processed_at": "{timestamp}",
    "meeting_type": "tipo_de_reunion",
    "efficiency_score": 0.0
  },
  "summary": {
    "executive_summary": "resumen ejecutivo aquí",
    "key_points": ["punto 1", "punto 2", "punto 3"],
    "meeting_outcome": "exitosa/parcial/no_concluyente"
  },
  "action_items": [
    {
      "id": "ACT001",
      "description": "descripción clara de la acción",
      "responsible": "nombre del responsable",
      "deadline": "YYYY-MM-DD",
      "priority": "Alta/Media/Baja",
      "status": "Pendiente",
      "dependencies": [],
      "estimated_effort": "horas/días"
    }
  ],
  "strategic_analysis": {
    "risks": [
      {
        "description": "descripción del riesgo",
        "impact": "Alto/Medio/Bajo",
        "probability": "Alta/Media/Baja",
        "mitigation": "estrategia de mitigación"
      }
    ],
    "opportunities": [
      {
        "description": "descripción de la oportunidad",
        "potential_value": "descripción del valor",
        "required_actions": ["acción 1", "acción 2"]
      }
    ],
    "recommendations": [
      {
        "area": "área de mejora",
        "recommendation": "recomendación específica",
        "priority": "Alta/Media/Baja",
        "expected_impact": "descripción del impacto"
      }
    ]
  },
  "metrics": {
    "efficiency": {
      "score": 0.0,
      "factors": ["factor 1", "factor 2"]
    },
    "participation": {
      "level": "Activa/Moderada/Pasiva",
      "speaker_distribution": {},
      "engagement_score": 0.0
    },
    "clarity": {
      "objectives": "Clara/Parcial/Confusa",
      "decisions": "Clara/Parcial/Confusa",
      "next_steps": "Clara/Parcial/Confusa"
    },
    "sentiment": {
      "overall": "Positivo/Neutral/Negativo",
      "progression": "Mejorando/Estable/Deteriorando",
      "highlights": ["momento positivo", "momento tenso"]
    },
    "consensus": {
      "level": "Alto/Medio/Bajo",
      "controversial_topics": ["tema 1", "tema 2"],
      "alignment_score": 0.0
    }
  },
  "topics": [
    {
      "title": "título del tema",
      "discussion_time_percentage": 0.0,
      "key_points": ["punto 1", "punto 2"],
      "decisions_made": ["decisión 1"],
      "open_items": ["item 1"]
    }
  ],
  "next_steps": [
    {
      "timeframe": "Inmediato/Corto plazo/Mediano plazo",
      "action": "descripción de la acción",
      "responsible": "responsable",
      "success_criteria": "criterio de éxito"
    }
  ],
  "follow_up": {
    "pending_topics": ["tema 1", "tema 2"],
    "required_resources": ["recurso 1", "recurso 2"],
    "escalation_needed": false,
    "next_meeting_suggested_date": "YYYY-MM-DD",
    "next_meeting_agenda": ["punto 1", "punto 2"]
  },
  "tags": ["tag1", "tag2", "tag3", "tag4", "tag5"],
  "departments": ["dept1", "dept2"],
  "project": "nombre_del_proyecto"
}
---JSON_OUTPUT_END---

IMPORTANTE:
- Sé preciso y objetivo en tu análisis
- Basa todas las conclusiones en la información presente en la transcripción
- Si no hay información suficiente para un campo, usa "No especificado" o valores neutros
- Prioriza la utilidad práctica sobre la exhaustividad
- Mantén un tono profesional pero accesible

TRANSCRIPCIÓN A ANALIZAR:
{transcription}
"""

    # Template para resumen rápido
    QUICK_SUMMARY_TEMPLATE = """Genera un resumen ejecutivo de esta transcripción de reunión.

INSTRUCCIONES:
- Máximo 150 palabras
- Solo los puntos más importantes
- Lenguaje claro y directo
- Formato: 2-3 párrafos cortos

TRANSCRIPCIÓN:
{transcription}

RESUMEN:"""

    # Template para extracción de acciones
    ACTION_EXTRACTION_TEMPLATE = """Identifica TODAS las acciones, tareas y compromisos mencionados en esta reunión.

FORMATO REQUERIDO:
Para cada acción encontrada, proporciona:
- Descripción clara y específica
- Responsable (si se mencionó)
- Fecha límite (si se mencionó)
- Contexto relevante

TRANSCRIPCIÓN:
{transcription}

ACCIONES IDENTIFICADAS:"""

    # Template para análisis de sentimiento
    SENTIMENT_ANALYSIS_TEMPLATE = """Analiza el tono y sentimiento de esta reunión.

ASPECTOS A EVALUAR:
1. Tono general (positivo/neutral/negativo/mixto)
2. Evolución del tono durante la reunión
3. Momentos de tensión o conflicto
4. Momentos de consenso o celebración
5. Nivel de energía y participación

TRANSCRIPCIÓN:
{transcription}

ANÁLISIS DE SENTIMIENTO:"""

    # Template para identificación de temas
    TOPIC_IDENTIFICATION_TEMPLATE = """Identifica y categoriza los principales temas discutidos en esta reunión.

INSTRUCCIONES:
- Lista los 5-7 temas más importantes
- Para cada tema indica:
  * Tiempo aproximado dedicado (%)
  * Puntos clave discutidos
  * Decisiones tomadas
  * Preguntas sin resolver

TRANSCRIPCIÓN:
{transcription}

TEMAS IDENTIFICADOS:"""

    # Template para seguimiento de decisiones
    DECISION_TRACKING_TEMPLATE = """Extrae todas las decisiones tomadas durante esta reunión.

PARA CADA DECISIÓN:
- Descripción clara de lo decidido
- Quién tomó la decisión
- Justificación o contexto
- Impacto esperado
- Acciones derivadas

TRANSCRIPCIÓN:
{transcription}

DECISIONES TOMADAS:"""

    # Template para análisis de participación
    PARTICIPATION_ANALYSIS_TEMPLATE = """Analiza los patrones de participación en esta reunión.

EVALÚA:
1. Distribución del tiempo de habla
2. Nivel de engagement de participantes
3. Balance en la participación
4. Participantes dominantes o silenciosos
5. Calidad de las intervenciones

NOTA: Si no puedes identificar speakers individuales, analiza el patrón general.

TRANSCRIPCIÓN:
{transcription}

ANÁLISIS DE PARTICIPACIÓN:"""

    # Template para identificación de riesgos
    RISK_IDENTIFICATION_TEMPLATE = """Identifica riesgos potenciales mencionados o implícitos en esta reunión.

CATEGORÍAS DE RIESGO:
- Técnicos
- De calendario/tiempo
- De recursos
- De alcance
- De comunicación
- Externos

Para cada riesgo indica impacto potencial y urgencia.

TRANSCRIPCIÓN:
{transcription}

RIESGOS IDENTIFICADOS:"""

    # Template para generación de agenda de seguimiento
    FOLLOW_UP_AGENDA_TEMPLATE = """Basándote en esta reunión, genera una agenda sugerida para la próxima reunión de seguimiento.

INCLUYE:
1. Revisión de acciones comprometidas
2. Temas pendientes no resueltos
3. Nuevos temas surgidos
4. Decisiones que requieren validación
5. Métricas o resultados a revisar

TRANSCRIPCIÓN:
{transcription}

AGENDA SUGERIDA PARA PRÓXIMA REUNIÓN:"""

    @classmethod
    def get_prompt(cls, template_name: str, **kwargs) -> str:
        """
        Obtiene un prompt formateado con los parámetros proporcionados.
        
        Args:
            template_name: Nombre del template a usar
            **kwargs: Parámetros para formatear el template
            
        Returns:
            Prompt formateado listo para usar
        """
        # Obtener el template
        template = getattr(cls, template_name, None)
        if not template:
            raise ValueError(f"Template '{template_name}' no encontrado")
        
        # Agregar valores por defecto para campos comunes
        defaults = {
            'title': 'Reunión sin título',
            'date': datetime.now().strftime('%Y-%m-%d'),
            'duration': 'No especificada',
            'participants': 'No especificados',
            'objective': 'No especificado',
            'meeting_id': datetime.now().strftime('%Y%m%d_%H%M%S'),
            'timestamp': datetime.now().isoformat()
        }
        
        # Combinar defaults con kwargs
        format_params = {**defaults, **kwargs}
        
        # Formatear y retornar
        return template.format(**format_params)
    
    @classmethod
    def get_custom_prompt(cls, base_template: str, custom_instructions: str, **kwargs) -> str:
        """
        Crea un prompt personalizado combinando un template base con instrucciones custom.
        
        Args:
            base_template: Nombre del template base
            custom_instructions: Instrucciones adicionales personalizadas
            **kwargs: Parámetros para formatear
            
        Returns:
            Prompt personalizado
        """
        base_prompt = cls.get_prompt(base_template, **kwargs)
        
        custom_section = f"\n\nINSTRUCCIONES ADICIONALES PERSONALIZADAS:\n{custom_instructions}\n"
        
        # Insertar las instrucciones custom antes de la transcripción
        if "TRANSCRIPCIÓN" in base_prompt:
            parts = base_prompt.split("TRANSCRIPCIÓN")
            return parts[0] + custom_section + "TRANSCRIPCIÓN" + "TRANSCRIPCIÓN".join(parts[1:])
        else:
            return base_prompt + custom_section

    @classmethod
    def combine_prompts(cls, template_names: List[str], **kwargs) -> str:
        """
        Combina múltiples templates en un solo prompt.
        
        Args:
            template_names: Lista de nombres de templates a combinar
            **kwargs: Parámetros para formatear
            
        Returns:
            Prompt combinado
        """
        combined_parts = []
        
        for template_name in template_names:
            prompt = cls.get_prompt(template_name, **kwargs)
            combined_parts.append(prompt)
        return "\n\n".join(combined_parts)