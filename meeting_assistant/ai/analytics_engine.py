# ai/analytics_engine.py
"""
Motor de análisis avanzado para extraer métricas y estadísticas
de las transcripciones y resultados del procesamiento.
"""

import re
import json
import logging
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime, timedelta
from collections import Counter, defaultdict
import statistics


class AnalyticsEngine:
    """Motor principal para análisis avanzado de reuniones."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Palabras clave para diferentes análisis
        self.sentiment_keywords = {
            'positive': [
                'excelente', 'perfecto', 'genial', 'fantástico', 'bueno', 'bien',
                'acuerdo', 'sí', 'correcto', 'adelante', 'éxito', 'logro',
                'feliz', 'contento', 'satisfecho', 'positivo', 'mejor'
            ],
            'negative': [
                'problema', 'mal', 'difícil', 'complicado', 'no', 'imposible',
                'error', 'fallo', 'preocupación', 'riesgo', 'retraso', 'bloqueo',
                'frustrado', 'molesto', 'negativo', 'peor', 'crítico'
            ],
            'neutral': [
                'quizás', 'tal vez', 'posiblemente', 'depende', 'veremos',
                'considerar', 'evaluar', 'analizar', 'revisar', 'pendiente'
            ]
        }
        
        self.action_keywords = [
            'hacer', 'realizar', 'completar', 'enviar', 'crear', 'desarrollar',
            'implementar', 'revisar', 'aprobar', 'contactar', 'preparar',
            'organizar', 'definir', 'establecer', 'configurar', 'actualizar'
        ]
        
        self.decision_keywords = [
            'decidimos', 'acordamos', 'aprobado', 'confirmado', 'establecido',
            'definido', 'resuelto', 'determinado', 'concluido', 'finalizado'
        ]
        
        self.question_patterns = [
            r'\?(?:\s|$)',
            r'(?:qué|cómo|cuándo|dónde|por qué|quién|cuál)\s',
            r'(?:what|how|when|where|why|who|which)\s'
        ]
    
    def analyze_meeting(self, 
                       transcription: str,
                       parsed_data: Dict[str, Any],
                       meeting_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Realiza un análisis completo de la reunión.
        
        Args:
            transcription: Transcripción original
            parsed_data: Datos ya parseados del LLM
            meeting_context: Contexto adicional de la reunión
            
        Returns:
            Diccionario con análisis completo
        """
        analysis = {
            'timestamp': datetime.now().isoformat(),
            'basic_metrics': self._calculate_basic_metrics(transcription),
            'sentiment_analysis': self._analyze_sentiment(transcription),
            'participation_metrics': self._analyze_participation(transcription),
            'content_analysis': self._analyze_content(transcription),
            'interaction_patterns': self._analyze_interactions(transcription),
            'efficiency_metrics': self._calculate_efficiency(transcription, parsed_data),
            'quality_indicators': self._assess_quality(transcription, parsed_data),
            'trends': self._identify_trends(transcription),
            'recommendations': self._generate_recommendations(parsed_data)
        }
        
        # Agregar contexto si está disponible
        if meeting_context:
            analysis['context_analysis'] = self._analyze_context(meeting_context, analysis)
        
        # Calcular score general
        analysis['overall_score'] = self._calculate_overall_score(analysis)
        
        return analysis
    
    def _calculate_basic_metrics(self, text: str) -> Dict[str, Any]:
        """Calcula métricas básicas del texto."""
        words = text.split()
        sentences = re.split(r'[.!?]+', text)
        paragraphs = text.split('\n\n')
        
        # Calcular velocidad de habla estimada (palabras por minuto)
        # Asumiendo velocidad promedio de habla de 150 palabras/minuto
        estimated_duration_minutes = len(words) / 150
        
        return {
            'total_words': len(words),
            'total_sentences': len([s for s in sentences if s.strip()]),
            'total_paragraphs': len([p for p in paragraphs if p.strip()]),
            'average_sentence_length': statistics.mean([len(s.split()) for s in sentences if s.strip()]) if sentences else 0,
            'estimated_duration_minutes': round(estimated_duration_minutes, 1),
            'estimated_duration_formatted': self._format_duration(estimated_duration_minutes),
            'lexical_diversity': len(set(words)) / len(words) if words else 0,
            'questions_count': len(re.findall(r'\?', text)),
            'exclamations_count': len(re.findall(r'!', text))
        }
    
    def _analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analiza el sentimiento general del texto."""
        text_lower = text.lower()
        words = text_lower.split()
        
        # Contar palabras por sentimiento
        sentiment_counts = {
            'positive': 0,
            'negative': 0,
            'neutral': 0
        }
        
        for word in words:
            for sentiment, keywords in self.sentiment_keywords.items():
                if word in keywords:
                    sentiment_counts[sentiment] += 1
        
        total_sentiment_words = sum(sentiment_counts.values())
        
        # Calcular porcentajes
        sentiment_percentages = {}
        if total_sentiment_words > 0:
            for sentiment, count in sentiment_counts.items():
                sentiment_percentages[sentiment] = round(count / total_sentiment_words * 100, 1)
        else:
            sentiment_percentages = {'positive': 33.3, 'negative': 33.3, 'neutral': 33.4}
        
        # Determinar sentimiento dominante
        dominant_sentiment = max(sentiment_counts, key=sentiment_counts.get)
        
        # Analizar progresión del sentimiento
        sentiment_progression = self._analyze_sentiment_progression(text)
        
        return {
            'counts': sentiment_counts,
            'percentages': sentiment_percentages,
            'dominant': dominant_sentiment,
            'score': self._calculate_sentiment_score(sentiment_counts),
            'progression': sentiment_progression,
            'intensity': self._calculate_sentiment_intensity(text)
        }
    
    def _analyze_participation(self, text: str) -> Dict[str, Any]:
        """Analiza patrones de participación."""
        # Intentar identificar cambios de hablante
        speaker_patterns = [
            r'^([A-Z][a-z]+):',  # Nombre:
            r'^([A-Z]{2,}):',    # INICIALES:
            r'^\[([^\]]+)\]',    # [Nombre]
            r'^-\s*([A-Z][a-z]+):', # - Nombre:
        ]
        
        speakers = []
        for pattern in speaker_patterns:
            matches = re.findall(pattern, text, re.MULTILINE)
            speakers.extend(matches)
        
        speaker_counts = Counter(speakers)
        
        # Análisis de distribución
        participation_data = {
            'identified_speakers': len(set(speakers)),
            'total_interventions': len(speakers),
            'speaker_distribution': dict(speaker_counts),
            'participation_balance': self._calculate_participation_balance(speaker_counts),
            'dominant_speaker': speaker_counts.most_common(1)[0] if speaker_counts else None,
            'silent_periods': self._identify_silent_periods(text)
        }
        
        # Si no se identificaron speakers, usar análisis alternativo
        if not speakers:
            participation_data['note'] = "No se pudieron identificar hablantes individuales"
            participation_data['interaction_density'] = self._calculate_interaction_density(text)
        
        return participation_data
    
    def _analyze_content(self, text: str) -> Dict[str, Any]:
        """Analiza el contenido temático."""
        words = text.lower().split()
        
        # Filtrar palabras comunes (stopwords básicas)
        stopwords = {
            'el', 'la', 'de', 'que', 'y', 'a', 'en', 'un', 'ser', 'se',
            'no', 'haber', 'por', 'con', 'su', 'para', 'como', 'estar',
            'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have',
            'i', 'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you'
        }
        
        filtered_words = [w for w in words if len(w) > 3 and w not in stopwords]
        
        # Análisis de frecuencia
        word_freq = Counter(filtered_words)
        
        # Detectar temas por n-gramas
        bigrams = self._extract_ngrams(text, 2)
        trigrams = self._extract_ngrams(text, 3)
        
        # Categorizar contenido
        content_categories = self._categorize_content(text)
        
        return {
            'top_words': word_freq.most_common(10),
            'top_bigrams': Counter(bigrams).most_common(5),
            'top_trigrams': Counter(trigrams).most_common(5),
            'content_categories': content_categories,
            'technical_terms': self._extract_technical_terms(text),
            'action_items_detected': len(re.findall('|'.join(self.action_keywords), text.lower())),
            'decisions_detected': len(re.findall('|'.join(self.decision_keywords), text.lower())),
            'questions_topics': self._analyze_questions(text)
        }
    
    def _analyze_interactions(self, text: str) -> Dict[str, Any]:
        """Analiza patrones de interacción."""
        lines = text.split('\n')
        
        # Detectar patrones de conversación
        question_responses = 0
        agreements = 0
        disagreements = 0
        clarifications = 0
        
        agreement_words = ['sí', 'correcto', 'exacto', 'acuerdo', 'definitivamente', 'absolutamente']
        disagreement_words = ['no', 'pero', 'sin embargo', 'aunque', 'discrepo', 'diferente']
        clarification_words = ['es decir', 'o sea', 'me refiero', 'quiero decir', 'aclarar']
        
        for i, line in enumerate(lines):
            line_lower = line.lower()
            
            # Contar tipos de interacciones
            if '?' in line and i < len(lines) - 1:
                question_responses += 1
            
            if any(word in line_lower for word in agreement_words):
                agreements += 1
            
            if any(word in line_lower for word in disagreement_words):
                disagreements += 1
            
            if any(word in line_lower for word in clarification_words):
                clarifications += 1
        
        return {
            'question_response_pairs': question_responses,
            'agreements': agreements,
            'disagreements': disagreements,
            'clarifications': clarifications,
            'interaction_ratio': (agreements + disagreements + clarifications) / len(lines) if lines else 0,
            'consensus_indicator': agreements / (agreements + disagreements) if (agreements + disagreements) > 0 else 0.5,
            'discussion_depth': self._calculate_discussion_depth(text)
        }
    
    def _calculate_efficiency(self, text: str, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calcula métricas de eficiencia de la reunión."""
        basic_metrics = self._calculate_basic_metrics(text)
        
        # Factores de eficiencia
        factors = {
            'action_ratio': len(parsed_data.get('action_items', [])) / (basic_metrics['estimated_duration_minutes'] / 30),
            'decision_ratio': len(re.findall('|'.join(self.decision_keywords), text.lower())) / basic_metrics['total_sentences'],
            'focus_score': 1 - (basic_metrics['questions_count'] / basic_metrics['total_sentences']),
            'clarity_score': parsed_data.get('quality_score', 0.5)
        }
        
        # Calcular score de eficiencia ponderado
        weights = {'action_ratio': 0.3, 'decision_ratio': 0.3, 'focus_score': 0.2, 'clarity_score': 0.2}
        efficiency_score = sum(factors[k] * weights[k] for k in factors) / sum(weights.values())
        
        return {
            'efficiency_score': round(min(efficiency_score, 1.0), 2),
            'factors': factors,
            'time_per_action': basic_metrics['estimated_duration_minutes'] / len(parsed_data.get('action_items', [])) if parsed_data.get('action_items') else None,
            'meeting_velocity': len(parsed_data.get('topics', [])) / basic_metrics['estimated_duration_minutes'] if basic_metrics['estimated_duration_minutes'] > 0 else 0,
            'productivity_index': self._calculate_productivity_index(text, parsed_data)
        }
    
    def _assess_quality(self, text: str, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Evalúa indicadores de calidad de la reunión."""
        quality_indicators = {
            'structure_score': self._assess_structure(text),
            'clarity_score': self._assess_clarity(text),
            'completeness_score': self._assess_completeness(parsed_data),
            'actionability_score': self._assess_actionability(parsed_data),
            'follow_up_readiness': self._assess_follow_up_readiness(parsed_data)
        }
        
        # Score general de calidad
        quality_score = statistics.mean(quality_indicators.values())
        
        return {
            'overall_quality': round(quality_score, 2),
            'indicators': quality_indicators,
            'strengths': [k for k, v in quality_indicators.items() if v >= 0.7],
            'areas_for_improvement': [k for k, v in quality_indicators.items() if v < 0.5],
            'recommendations': self._generate_quality_recommendations(quality_indicators)
        }
    
    def _identify_trends(self, text: str) -> Dict[str, Any]:
        """Identifica tendencias y patrones en la reunión."""
        # Dividir texto en segmentos temporales
        segments = self._divide_into_segments(text, 5)  # 5 segmentos
        
        trends = {
            'energy_progression': [],
            'topic_evolution': [],
            'participation_changes': []
        }
        
        for i, segment in enumerate(segments):
            # Analizar energía (basado en signos de exclamación, longitud de oraciones)
            energy = len(re.findall(r'[!?]', segment)) / len(segment.split('.')) if segment else 0
            trends['energy_progression'].append(round(energy, 2))
            
            # Evolución de temas
            words = segment.lower().split()
            top_words = Counter(words).most_common(3)
            trends['topic_evolution'].append([w[0] for w in top_words])
        
        return {
            'trends': trends,
            'meeting_flow': self._determine_meeting_flow(trends),
            'momentum_shifts': self._identify_momentum_shifts(text),
            'critical_moments': self._identify_critical_moments(text)
        }
    
    def _generate_recommendations(self, parsed_data: Dict[str, Any]) -> List[Dict[str, str]]:
        """Genera recomendaciones basadas en el análisis."""
        recommendations = []
        
        # Analizar datos para generar recomendaciones
        stats = parsed_data.get('statistics', {})
        
        if stats.get('total_actions', 0) == 0:
            recommendations.append({
                'type': 'process',
                'priority': 'high',
                'recommendation': 'Definir acciones concretas con responsables y fechas',
                'impact': 'Mejorará el seguimiento y la ejecución post-reunión'
            })
        
        if stats.get('total_actions', 0) > 10:
            recommendations.append({
                'type': 'focus',
                'priority': 'medium',
                'recommendation': 'Considerar dividir los temas en múltiples reuniones más enfocadas',
                'impact': 'Aumentará la profundidad del análisis y la calidad de las decisiones'
            })
        
        if not stats.get('has_next_steps', False):
            recommendations.append({
                'type': 'planning',
                'priority': 'high',
                'recommendation': 'Establecer próximos pasos claros y fecha de seguimiento',
                'impact': 'Asegurará continuidad y progreso en los temas tratados'
            })
        
        return recommendations
    
    # Métodos auxiliares
    
    def _format_duration(self, minutes: float) -> str:
        """Formatea duración en formato legible."""
        if minutes < 60:
            return f"{int(minutes)} minutos"
        else:
            hours = int(minutes // 60)
            mins = int(minutes % 60)
            return f"{hours}h {mins}m"
    
    def _calculate_sentiment_score(self, counts: Dict[str, int]) -> float:
        """Calcula score de sentimiento (-1 a 1)."""
        total = sum(counts.values())
        if total == 0:
            return 0.0
        
        score = (counts['positive'] - counts['negative']) / total
        return round(score, 2)
    
    def _analyze_sentiment_progression(self, text: str) -> str:
        """Analiza cómo progresa el sentimiento durante la reunión."""
        segments = self._divide_into_segments(text, 3)
        progression = []
        
        for segment in segments:
            sentiment = self._analyze_sentiment(segment)
            progression.append(sentiment['dominant'])
        
        if progression[0] == 'negative' and progression[-1] == 'positive':
            return 'improving'
        elif progression[0] == 'positive' and progression[-1] == 'negative':
            return 'deteriorating'
        else:
            return 'stable'
    
    def _calculate_sentiment_intensity(self, text: str) -> str:
        """Calcula la intensidad del sentimiento."""
        intensifiers = ['muy', 'mucho', 'bastante', 'extremadamente', 'totalmente', 'completamente']
        intensity_count = sum(1 for word in text.lower().split() if word in intensifiers)
        
        ratio = intensity_count / len(text.split())
        
        if ratio > 0.02:
            return 'high'
        elif ratio > 0.01:
            return 'medium'
        else:
            return 'low'
    
    def _calculate_participation_balance(self, speaker_counts: Counter) -> float:
        """Calcula el balance de participación (0-1, 1 = perfectamente balanceado)."""
        if not speaker_counts:
            return 0.5
        
        total = sum(speaker_counts.values())
        expected = total / len(speaker_counts)
        
        variance = sum((count - expected) ** 2 for count in speaker_counts.values())
        std_dev = (variance / len(speaker_counts)) ** 0.5
        
        # Normalizar a 0-1 (inverso del coeficiente de variación)
        cv = std_dev / expected if expected > 0 else 1
        balance = 1 / (1 + cv)
        
        return round(balance, 2)
    
    def _identify_silent_periods(self, text: str) -> int:
        """Identifica períodos de silencio o poca actividad."""
        # Buscar múltiples líneas vacías o secciones muy cortas
        silent_pattern = r'\n\n\n+|\.\.\.|---'
        return len(re.findall(silent_pattern, text))
    
    def _calculate_interaction_density(self, text: str) -> float:
        """Calcula la densidad de interacción cuando no hay speakers identificados."""
        lines = [l for l in text.split('\n') if l.strip()]
        if not lines:
            return 0.0
        
        # Contar cambios de tema o dirección
        changes = 0
        for i in range(1, len(lines)):
            if len(lines[i]) < len(lines[i-1]) * 0.5 or len(lines[i]) > len(lines[i-1]) * 2:
                changes += 1
        
        return round(changes / len(lines), 2)
    
    def _extract_ngrams(self, text: str, n: int) -> List[Tuple[str, ...]]:
        """Extrae n-gramas del texto."""
        words = text.lower().split()
        return [tuple(words[i:i+n]) for i in range(len(words)-n+1)]
    
    def _categorize_content(self, text: str) -> Dict[str, int]:
        """Categoriza el contenido por tipo."""
        categories = {
            'technical': ['sistema', 'código', 'desarrollo', 'implementar', 'técnico', 'software', 'hardware'],
            'business': ['cliente', 'venta', 'mercado', 'estrategia', 'objetivo', 'meta', 'revenue'],
            'process': ['proceso', 'procedimiento', 'flujo', 'etapa', 'fase', 'metodología'],
            'people': ['equipo', 'persona', 'recurso', 'colaborador', 'responsable', 'líder'],
            'planning': ['plan', 'proyecto', 'timeline', 'fecha', 'deadline', 'milestone']
        }
        
        text_lower = text.lower()
        category_counts = {}
        
        for category, keywords in categories.items():
            count = sum(1 for keyword in keywords if keyword in text_lower)
            category_counts[category] = count
        
        return category_counts
    
    def _extract_technical_terms(self, text: str) -> List[str]:
        """Extrae términos técnicos o especializados."""
        # Patrones para términos técnicos
        patterns = [
            r'\b[A-Z]{2,}\b',  # Siglas
            r'\b\w+\.\w+\b',   # Términos con punto (ej: config.json)
            r'\b\w+_\w+\b',    # Términos con guión bajo
            r'\b\w+-\w+\b',    # Términos con guión
        ]
        
        technical_terms = set()
        for pattern in patterns:
            matches = re.findall(pattern, text)
            technical_terms.update(matches)
        
        return list(technical_terms)[:20]  # Limitar a 20 términos
    
    def _analyze_questions(self, text: str) -> Dict[str, Any]:
        """Analiza las preguntas realizadas."""
        questions = []
        
        for pattern in self.question_patterns:
            matches = re.findall(f'([^.!?]*{pattern})', text, re.IGNORECASE)
            questions.extend(matches)
        
        # Categorizar preguntas
        question_types = {
            'clarification': 0,
            'strategic': 0,
            'technical': 0,
            'procedural': 0
        }
        
        for question in questions:
            q_lower = question.lower()
            if any(word in q_lower for word in ['qué significa', 'puedes explicar', 'no entiendo']):
                question_types['clarification'] += 1
            elif any(word in q_lower for word in ['estrategia', 'objetivo', 'meta', 'visión']):
                question_types['strategic'] += 1
            elif any(word in q_lower for word in ['técnico', 'sistema', 'código', 'error']):
                question_types['technical'] += 1
            else:
                question_types['procedural'] += 1
        
        return {
            'total_questions': len(questions),
            'question_types': question_types,
            'unanswered_questions': self._identify_unanswered_questions(text, questions)
        }
    
    def _identify_unanswered_questions(self, text: str, questions: List[str]) -> int:
        """Identifica preguntas sin respuesta."""
        unanswered = 0
        lines = text.split('\n')
        
        for question in questions:
            # Buscar la pregunta en el texto
            for i, line in enumerate(lines):
                if question in line:
                    # Verificar si hay respuesta en las siguientes líneas
                    if i < len(lines) - 1:
                        next_lines = ' '.join(lines[i+1:i+4])  # Siguientes 3 líneas
                        if len(next_lines.strip()) < 20:  # Respuesta muy corta o vacía
                            unanswered += 1
                    break
        
        return unanswered
    
    def _calculate_discussion_depth(self, text: str) -> float:
        """Calcula la profundidad de la discusión."""
        # Buscar conectores lógicos
        logical_connectors = [
            'primero', 'segundo', 'tercero', 'finalmente',
            'por lo tanto', 'en consecuencia', 'además',
            'sin embargo', 'por otro lado', 'en resumen'
        ]
        
        text_lower = text.lower()
        connector_count = sum(1 for connector in logical_connectors if connector in text_lower)
        
        # Normalizar por longitud del texto
        words = text.split()
        depth_ratio = depth_count / (len(words) / 100) if words else 0
        
        return round(min(depth_ratio, 1.0), 2)
    
    def _calculate_productivity_index(self, text: str, parsed_data: Dict[str, Any]) -> float:
        """Calcula índice de productividad de la reunión."""
        factors = {
            'actions_generated': min(len(parsed_data.get('action_items', [])) / 5, 1.0),
            'decisions_made': min(len(re.findall('|'.join(self.decision_keywords), text.lower())) / 3, 1.0),
            'topics_covered': min(len(parsed_data.get('topics', [])) / 5, 1.0),
            'next_steps_defined': 1.0 if parsed_data.get('next_steps') else 0.0
        }
        
        return round(statistics.mean(factors.values()), 2)
    
    def _assess_structure(self, text: str) -> float:
        """Evalúa la estructura del contenido."""
        indicators = {
            'has_sections': bool(re.search(r'^#+\s', text, re.MULTILINE)),
            'has_lists': bool(re.search(r'^[\*\-\d]+\.?\s', text, re.MULTILINE)),
            'has_paragraphs': len(text.split('\n\n')) > 3,
            'logical_flow': self._check_logical_flow(text)
        }
        
        return sum(indicators.values()) / len(indicators)
    
    def _assess_clarity(self, text: str) -> float:
        """Evalúa la claridad del contenido."""
        sentences = [s for s in re.split(r'[.!?]+', text) if s.strip()]
        if not sentences:
            return 0.5
        
        # Factores de claridad
        avg_sentence_length = statistics.mean([len(s.split()) for s in sentences])
        clarity_factors = {
            'sentence_length': 1.0 if 10 <= avg_sentence_length <= 20 else 0.5,
            'technical_density': 1.0 - min(len(self._extract_technical_terms(text)) / 50, 1.0),
            'ambiguity_level': 1.0 - (text.lower().count('tal vez') + text.lower().count('quizás')) / len(sentences)
        }
        
        return statistics.mean(clarity_factors.values())
    
    def _assess_completeness(self, parsed_data: Dict[str, Any]) -> float:
        """Evalúa la completitud del análisis."""
        required_elements = [
            'summary',
            'action_items',
            'insights',
            'topics',
            'next_steps'
        ]
        
        present_elements = sum(1 for elem in required_elements if parsed_data.get(elem))
        return present_elements / len(required_elements)
    
    def _assess_actionability(self, parsed_data: Dict[str, Any]) -> float:
        """Evalúa qué tan accionable es el resultado."""
        score = 0.0
        
        # Verificar acciones
        actions = parsed_data.get('action_items', [])
        if actions:
            # Acciones con responsable asignado
            with_responsible = sum(1 for a in actions if a.get('responsible') != 'Por asignar')
            score += (with_responsible / len(actions)) * 0.5
            
            # Acciones con deadline
            with_deadline = sum(1 for a in actions if a.get('deadline') != 'Por definir')
            score += (with_deadline / len(actions)) * 0.5
        
        return score
    
    def _assess_follow_up_readiness(self, parsed_data: Dict[str, Any]) -> float:
        """Evalúa qué tan lista está la reunión para seguimiento."""
        readiness_factors = {
            'has_actions': bool(parsed_data.get('action_items')),
            'has_next_steps': bool(parsed_data.get('next_steps')),
            'has_deadlines': any(a.get('deadline') != 'Por definir' for a in parsed_data.get('action_items', [])),
            'has_responsible': any(a.get('responsible') != 'Por asignar' for a in parsed_data.get('action_items', []))
        }
        
        return sum(readiness_factors.values()) / len(readiness_factors)
    
    def _generate_quality_recommendations(self, indicators: Dict[str, float]) -> List[str]:
        """Genera recomendaciones basadas en indicadores de calidad."""
        recommendations = []
        
        if indicators.get('structure_score', 0) < 0.5:
            recommendations.append("Mejorar la estructura usando secciones claras y listas")
        
        if indicators.get('clarity_score', 0) < 0.5:
            recommendations.append("Simplificar el lenguaje y reducir la ambigüedad")
        
        if indicators.get('actionability_score', 0) < 0.5:
            recommendations.append("Asignar responsables y fechas específicas a las acciones")
        
        return recommendations
    
    def _divide_into_segments(self, text: str, num_segments: int) -> List[str]:
        """Divide el texto en segmentos temporales."""
        lines = text.split('\n')
        segment_size = len(lines) // num_segments
        
        segments = []
        for i in range(num_segments):
            start = i * segment_size
            end = start + segment_size if i < num_segments - 1 else len(lines)
            segments.append('\n'.join(lines[start:end]))
        
        return segments
    
    def _check_logical_flow(self, text: str) -> bool:
        """Verifica si hay un flujo lógico en el contenido."""
        # Buscar conectores lógicos
        logical_connectors = [
            'primero', 'segundo', 'tercero', 'finalmente',
            'por lo tanto', 'en consecuencia', 'además',
            'sin embargo', 'por otro lado', 'en resumen'
        ]
        
        text_lower = text.lower()
        connector_count = sum(1 for connector in logical_connectors if connector in text_lower)
        
        return connector_count >= 3
    
    def _determine_meeting_flow(self, trends: Dict[str, List]) -> str:
        """Determina el flujo general de la reunión."""
        energy_progression = trends.get('energy_progression', [])
        
        if not energy_progression:
            return 'undefined'
        
        # Analizar tendencia
        if energy_progression[-1] > energy_progression[0] * 1.2:
            return 'crescendo'
        elif energy_progression[-1] < energy_progression[0] * 0.8:
            return 'diminuendo'
        else:
            return 'steady'
    
    def _identify_momentum_shifts(self, text: str) -> List[Dict[str, Any]]:
        """Identifica cambios de momentum en la reunión."""
        shifts = []
        
        # Buscar patrones que indican cambios
        shift_patterns = [
            (r'pero|sin embargo|no obstante', 'contrast'),
            (r'excelente|perfecto|genial', 'positive_peak'),
            (r'problema|dificultad|bloqueo', 'challenge'),
            (r'acuerdo|decidido|aprobado', 'resolution')
        ]
        
        for pattern, shift_type in shift_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                shifts.append({
                    'position': match.start(),
                    'type': shift_type,
                    'context': text[max(0, match.start()-50):match.end()+50]
                })
        
        return sorted(shifts, key=lambda x: x['position'])[:10]  # Top 10 shifts
    
    def _identify_critical_moments(self, text: str) -> List[str]:
        """Identifica momentos críticos de la reunión."""
        critical_patterns = [
            r'decisión importante:?\s*([^.!?]+)',
            r'punto clave:?\s*([^.!?]+)',
            r'crítico:?\s*([^.!?]+)',
            r'fundamental:?\s*([^.!?]+)'
        ]
        
        critical_moments = []
        for pattern in critical_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            critical_moments.extend(matches)
        
        return critical_moments[:5]  # Top 5 momentos críticos
    
    def _analyze_context(self, context: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Analiza el contexto de la reunión."""
        context_analysis = {
            'objective_achievement': self._assess_objective_achievement(context, analysis),
            'participant_engagement': self._assess_participant_engagement(context, analysis),
            'time_efficiency': self._assess_time_efficiency(context, analysis),
            'context_relevance': self._assess_context_relevance(context, analysis)
        }
        
        return context_analysis
    
    def _assess_objective_achievement(self, context: Dict[str, Any], analysis: Dict[str, Any]) -> float:
        """Evalúa el logro de objetivos."""
        objective = context.get('objective', '').lower()
        if not objective:
            return 0.5
        
        # Buscar palabras clave del objetivo en el contenido
        content_analysis = analysis.get('content_analysis', {})
        top_words = [w[0] for w in content_analysis.get('top_words', [])]
        
        objective_words = objective.split()
        matches = sum(1 for word in objective_words if word in top_words)
        
        return min(matches / len(objective_words), 1.0) if objective_words else 0.5
    
    def _assess_participant_engagement(self, context: Dict[str, Any], analysis: Dict[str, Any]) -> float:
        """Evalúa el engagement de participantes."""
        expected_participants = len(context.get('participants', []))
        identified_speakers = analysis.get('participation_metrics', {}).get('identified_speakers', 0)
        
        if expected_participants == 0:
            return 0.5
        
        return min(identified_speakers / expected_participants, 1.0)
    
    def _assess_time_efficiency(self, context: Dict[str, Any], analysis: Dict[str, Any]) -> float:
        """Evalúa la eficiencia del tiempo."""
        # Comparar duración estimada con duración esperada
        estimated_duration = analysis.get('basic_metrics', {}).get('estimated_duration_minutes', 30)
        
        # Asumir reunión estándar de 30-60 minutos
        if 25 <= estimated_duration <= 65:
            return 1.0
        elif estimated_duration < 25:
            return 0.7  # Muy corta
        else:
            return max(0.3, 1.0 - (estimated_duration - 60) / 60)  # Penalizar por exceso
    
    def _assess_context_relevance(self, context: Dict[str, Any], analysis: Dict[str, Any]) -> float:
        """Evalúa la relevancia del contenido al contexto."""
        tags = context.get('tags', [])
        identified_tags = analysis.get('tags', [])
        
        if not tags:
            return 0.5
        
        matches = sum(1 for tag in tags if tag in identified_tags)
        return min(matches / len(tags), 1.0)
    
    def _calculate_overall_score(self, analysis: Dict[str, Any]) -> float:
        """Calcula un score general de la reunión."""
        scores = {
            'sentiment': (analysis['sentiment_analysis']['score'] + 1) / 2,  # Normalizar -1 a 1 -> 0 a 1
            'efficiency': analysis['efficiency_metrics']['efficiency_score'],
            'quality': analysis['quality_indicators']['overall_quality'],
            'participation': analysis['participation_metrics']['participation_balance'],
            'actionability': analysis['quality_indicators']['indicators']['actionability_score']
        }
        
        # Ponderación
        weights = {
            'sentiment': 0.15,
            'efficiency': 0.25,
            'quality': 0.25,
            'participation': 0.15,
            'actionability': 0.20
        }
        
        overall = sum(scores[k] * weights[k] for k in scores)
        return round(overall, 2)
    
    def generate_analytics_report(self, analysis: Dict[str, Any]) -> str:
        """Genera un reporte de analytics en formato markdown."""
        report = f"""# Reporte de Analytics - Reunión\n\n**Fecha de análisis**: {analysis['timestamp']}\n**Score general**: {analysis['overall_score']}/1.0\n\n## Métricas Básicas\n- **Duración estimada**: {analysis['basic_metrics']['estimated_duration_formatted']}\n- **Total de palabras**: {analysis['basic_metrics']['total_words']:,}\n- **Diversidad léxica**: {analysis['basic_metrics']['lexical_diversity']:.2%}\n\n## Análisis de Sentimiento\n- **Sentimiento dominante**: {analysis['sentiment_analysis']['dominant']}\n- **Score de sentimiento**: {analysis['sentiment_analysis']['score']}\n- **Progresión**: {analysis['sentiment_analysis']['progression']}\n\n## Eficiencia de la Reunión\n- **Score de eficiencia**: {analysis['efficiency_metrics']['efficiency_score']}\n- **Índice de productividad**: {analysis['efficiency_metrics']['productivity_index']}\n- **Velocidad de reunión**: {analysis['efficiency_metrics']['meeting_velocity']:.2f} temas/minuto\n\n## Calidad del Contenido\n- **Calidad general**: {analysis['quality_indicators']['overall_quality']}\n- **Fortalezas**: {', '.join(analysis['quality_indicators']['strengths'])}\n- **Áreas de mejora**: {', '.join(analysis['quality_indicators']['areas_for_improvement'])}\n\n## Patrones de Interacción\n- **Consenso**: {analysis['interaction_patterns']['consensus_indicator']:.2%}\n- **Profundidad de discusión**: {analysis['interaction_patterns']['discussion_depth']}\n\n## Recomendaciones\n"""
        
        for rec in analysis['recommendations']:
            report += f"\n### {rec['priority'].upper()} - {rec['type']}\n"
            report += f"**Recomendación**: {rec['recommendation']}\n"
            report += f"**Impacto esperado**: {rec['impact']}\n"
        
        return report
