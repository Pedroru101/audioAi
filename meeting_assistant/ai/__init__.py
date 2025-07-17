# ai/__init__.py
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
