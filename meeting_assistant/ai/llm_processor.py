# ai/llm_processor.py
"""
Procesador principal para interactuar con diferentes LLMs.
Soporta OpenAI, Ollama y otros proveedores vía OpenRouter.
"""

import json
import logging
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
import requests
from abc import ABC, abstractmethod
import time

# Intentar importar librerías opcionales
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("⚠️ OpenAI no instalado. Instala con: pip install openai")

try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    print("⚠️ Ollama no instalado. Instala con: pip install ollama")


class LLMProvider(ABC):
    """Clase base abstracta para proveedores de LLM."""
    
    @abstractmethod
    def process(self, prompt: str, **kwargs) -> Tuple[str, Dict[str, Any]]:
        """Procesa un prompt y retorna la respuesta y metadata."""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Verifica si el proveedor está disponible."""
        pass
    
    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """Retorna información sobre el modelo actual."""
        pass


class OpenAIProvider(LLMProvider):
    """Proveedor para modelos de OpenAI."""
    
    def __init__(self, api_key: str, model: str = "gpt-4o", **kwargs):
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI library not available")
        
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model
        self.temperature = kwargs.get('temperature', 0.7)
        self.max_tokens = kwargs.get('max_tokens', 2000)
        self.logger = logging.getLogger(__name__)
    
    def process(self, prompt: str, **kwargs) -> Tuple[str, Dict[str, Any]]:
        """Procesa el prompt usando OpenAI API."""
        try:
            start_time = time.time()
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are MIA, an expert meeting analysis assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=kwargs.get('temperature', self.temperature),
                max_tokens=kwargs.get('max_tokens', self.max_tokens),
                response_format={"type": "text"}
            )
            
            processing_time = time.time() - start_time
            
            metadata = {
                'model': self.model,
                'provider': 'openai',
                'processing_time': processing_time,
                'tokens_used': response.usage.total_tokens if response.usage else None,
                'finish_reason': response.choices[0].finish_reason
            }
            
            return response.choices[0].message.content, metadata
            
        except Exception as e:
            self.logger.error(f"Error en OpenAI API: {str(e)}")
            raise
    
    def is_available(self) -> bool:
        """Verifica disponibilidad del servicio."""
        try:
            # Hacer una llamada simple para verificar
            self.client.models.list()
            return True
        except:
            return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """Retorna información del modelo."""
        return {
            'provider': 'OpenAI',
            'model': self.model,
            'temperature': self.temperature,
            'max_tokens': self.max_tokens,
            'available': self.is_available()
        }


class OllamaProvider(LLMProvider):
    """Proveedor para modelos locales con Ollama."""
    
    def __init__(self, model: str = "llama3", host: str = "http://localhost", port: str = "11434", **kwargs):
        if not OLLAMA_AVAILABLE:
            raise ImportError("Ollama library not available")
        
        self.model = model
        self.host = host
        self.port = port
        self.base_url = f"{host}:{port}"
        self.temperature = kwargs.get('temperature', 0.7)
        self.max_tokens = kwargs.get('max_tokens', 2000)
        self.logger = logging.getLogger(__name__)
        
        # Configurar cliente Ollama
        self.client = ollama.Client(host=self.base_url)
    
    def process(self, prompt: str, **kwargs) -> Tuple[str, Dict[str, Any]]:
        """Procesa el prompt usando Ollama."""
        try:
            start_time = time.time()
            
            response = self.client.chat(
                model=self.model,
                messages=[
                    {
                        'role': 'system',
                        'content': 'You are MIA, an expert meeting analysis assistant.'
                    },
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                options={
                    'temperature': kwargs.get('temperature', self.temperature),
                    'num_predict': kwargs.get('max_tokens', self.max_tokens)
                }
            )
            
            processing_time = time.time() - start_time
            
            metadata = {
                'model': self.model,
                'provider': 'ollama',
                'processing_time': processing_time,
                'local': True
            }
            
            return response['message']['content'], metadata
            
        except Exception as e:
            self.logger.error(f"Error en Ollama: {str(e)}")
            raise
    
    def is_available(self) -> bool:
        """Verifica si Ollama está corriendo."""
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            return response.status_code == 200
        except:
            return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """Retorna información del modelo."""
        return {
            'provider': 'Ollama',
            'model': self.model,
            'host': self.base_url,
            'temperature': self.temperature,
            'max_tokens': self.max_tokens,
            'available': self.is_available(),
            'local': True
        }


class OpenRouterProvider(LLMProvider):
    """Proveedor para acceder a múltiples modelos vía OpenRouter."""
    
    def __init__(self, api_key: str, model: str = "openai/gpt-4", **kwargs):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://openrouter.ai/api/v1"
        self.temperature = kwargs.get('temperature', 0.7)
        self.max_tokens = kwargs.get('max_tokens', 2000)
        self.site_url = kwargs.get('site_url', 'http://localhost:3000')
        self.app_name = kwargs.get('app_name', 'Meeting Assistant Pro')
        self.logger = logging.getLogger(__name__)
    
    def process(self, prompt: str, **kwargs) -> Tuple[str, Dict[str, Any]]:
        """Procesa el prompt usando OpenRouter API."""
        try:
            start_time = time.time()
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "HTTP-Referer": self.site_url,
                "X-Title": self.app_name,
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": "You are MIA, an expert meeting analysis assistant."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": kwargs.get('temperature', self.temperature),
                "max_tokens": kwargs.get('max_tokens', self.max_tokens)
            }
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data
            )
            
            response.raise_for_status()
            result = response.json()
            
            processing_time = time.time() - start_time
            
            metadata = {
                'model': self.model,
                'provider': 'openrouter',
                'processing_time': processing_time,
                'tokens_used': result.get('usage', {}).get('total_tokens'),
                'finish_reason': result['choices'][0].get('finish_reason')
            }
            
            return result['choices'][0]['message']['content'], metadata
            
        except Exception as e:
            self.logger.error(f"Error en OpenRouter API: {str(e)}")
            raise
    
    def is_available(self) -> bool:
        """Verifica disponibilidad del servicio."""
        try:
            headers = {"Authorization": f"Bearer {self.api_key}"}
            response = requests.get(f"{self.base_url}/models", headers=headers)
            return response.status_code == 200
        except:
            return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """Retorna información del modelo."""
        return {
            'provider': 'OpenRouter',
            'model': self.model,
            'temperature': self.temperature,
            'max_tokens': self.max_tokens,
            'available': self.is_available()
        }


class LLMProcessor:
    """
    Procesador principal que gestiona diferentes proveedores de LLM.
    Actúa como fachada para simplificar el uso de diferentes APIs.
    """
    
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.logger = logging.getLogger(__name__)
        self.provider = None
        self._initialize_provider()
    
    def _initialize_provider(self):
        """Inicializa el proveedor de LLM según la configuración."""
        config = self.config_manager.get_config()
        llm_provider = config.get('llm_provider', 'local')
        
        try:
            if llm_provider == 'api':
                api_provider = config.get('api_provider', 'openai')
                api_key = config.get('api_key', '')
                
                if not api_key:
                    raise ValueError("API key no configurada")
                
                if api_provider == 'openai':
                    self.provider = OpenAIProvider(
                        api_key=api_key,
                        model=config.get('api_model_name', 'gpt-4o'),
                        temperature=config.get('api_temperature', 0.7),
                        max_tokens=config.get('api_max_tokens', 2000)
                    )
                elif api_provider == 'openrouter':
                    self.provider = OpenRouterProvider(
                        api_key=api_key,
                        model=config.get('api_model_name', 'openai/gpt-4'),
                        temperature=config.get('api_temperature', 0.7),
                        max_tokens=config.get('api_max_tokens', 2000),
                        site_url=config.get('openrouter_site_url'),
                        app_name=config.get('openrouter_app_name')
                    )
                else:
                    raise ValueError(f"Proveedor API no soportado: {api_provider}")
                    
            elif llm_provider == 'local':
                self.provider = OllamaProvider(
                    model=config.get('local_model_name', 'llama3'),
                    host=config.get('ollama_host', 'http://localhost'),
                    port=config.get('ollama_port', '11434'),
                    temperature=config.get('local_temperature', 0.7),
                    max_tokens=config.get('local_max_tokens', 2000)
                )
            else:
                raise ValueError(f"Proveedor LLM no soportado: {llm_provider}")
            
            # Verificar disponibilidad
            if not self.provider.is_available():
                raise ConnectionError(f"El proveedor {llm_provider} no está disponible")
            
            self.logger.info(f"LLM Provider inicializado: {self.provider.get_model_info()}")
            
        except Exception as e:
            self.logger.error(f"Error al inicializar LLM provider: {str(e)}")
            self.provider = None
            raise
    
    def process_transcription(self, 
                            transcription: str, 
                            template_name: str = 'ADVANCED_ANALYSIS_TEMPLATE',
                            meeting_context: Optional[Dict[str, Any]] = None,
                            **kwargs) -> Dict[str, Any]:
        """
        Procesa una transcripción usando el template especificado.
        
        Args:
            transcription: Texto de la transcripción
            template_name: Nombre del template a usar
            meeting_context: Contexto adicional de la reunión
            **kwargs: Parámetros adicionales para el prompt
            
        Returns:
            Diccionario con el resultado procesado
        """
        if not self.provider:
            raise RuntimeError("No hay proveedor LLM configurado")
        
        # Importar PromptTemplates
        from .prompt_templates import PromptTemplates
        
        # Preparar contexto
        context = meeting_context or {}
        context['transcription'] = transcription
        
        # Obtener prompt
        try:
            prompt = PromptTemplates.get_prompt(template_name, **context)
        except Exception as e:
            self.logger.error(f"Error al generar prompt: {str(e)}")
            raise
        
        # Procesar con LLM
        try:
            self.logger.info(f"Procesando transcripción con {self.provider.get_model_info()['provider']}")
            response_text, metadata = self.provider.process(prompt, **kwargs)
            
            # Estructurar respuesta
            result = {
                'raw_response': response_text,
                'metadata': metadata,
                'template_used': template_name,
                'processed_at': datetime.now().isoformat(),
                'success': True
            }
            
            # Intentar parsear JSON si está presente
            if '---JSON_OUTPUT_START---' in response_text and '---JSON_OUTPUT_END---' in response_text:
                try:
                    json_start = response_text.find('---JSON_OUTPUT_START---') + len('---JSON_OUTPUT_START---')
                    json_end = response_text.find('---JSON_OUTPUT_END---')
                    json_str = response_text[json_start:json_end].strip()
                    result['structured_data'] = json.loads(json_str)
                    result['markdown_content'] = response_text[:response_text.find('---JSON_OUTPUT_START---')].strip()
                except Exception as e:
                    self.logger.warning(f"No se pudo parsear JSON de la respuesta: {str(e)}")
                    result['markdown_content'] = response_text
            else:
                result['markdown_content'] = response_text
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error al procesar con LLM: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'template_used': template_name,
                'processed_at': datetime.now().isoformat()
            }
    
    def process_multiple_templates(self,
                                 transcription: str,
                                 template_names: List[str],
                                 meeting_context: Optional[Dict[str, Any]] = None,
                                 **kwargs) -> Dict[str, Dict[str, Any]]:
        """
        Procesa una transcripción con múltiples templates.
        
        Args:
            transcription: Texto de la transcripción
            template_names: Lista de templates a aplicar
            meeting_context: Contexto de la reunión
            **kwargs: Parámetros adicionales
            
        Returns:
            Diccionario con resultados por template
        """
        results = {}
        
        for template_name in template_names:
            self.logger.info(f"Procesando con template: {template_name}")
            try:
                result = self.process_transcription(
                    transcription=transcription,
                    template_name=template_name,
                    meeting_context=meeting_context,
                    **kwargs
                )
                results[template_name] = result
            except Exception as e:
                self.logger.error(f"Error con template {template_name}: {str(e)}")
                results[template_name] = {
                    'success': False,
                    'error': str(e)
                }
        
        return results
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Retorna información sobre el proveedor actual."""
        if self.provider:
            return self.provider.get_model_info()
        return {'error': 'No provider configured'}
    
    def switch_provider(self, provider_type: str, **kwargs):
        """
        Cambia dinámicamente el proveedor de LLM.
        
        Args:
            provider_type: 'local' o 'api'
            **kwargs: Configuración adicional para el proveedor
        """
        # Actualizar configuración
        self.config_manager.set('llm_provider', provider_type, save=False)
        
        # Aplicar configuración adicional
        for key, value in kwargs.items():
            self.config_manager.set(key, value, save=False)
        
        # Guardar cambios
        self.config_manager._save_config()
        
        # Reinicializar proveedor
        self._initialize_provider()
    
    def test_connection(self) -> Tuple[bool, str]:
        """Prueba la conexión con el proveedor actual."""
        if not self.provider:
            return False, "No hay proveedor configurado"
        
        try:
            # Hacer una llamada simple de prueba
            test_prompt = "Responde solo con 'OK' si recibes este mensaje."
            response, _ = self.provider.process(test_prompt, max_tokens=10)
            
            if response:
                return True, f"Conexión exitosa con {self.provider.get_model_info()['provider']}"
            else:
                return False, "Respuesta vacía del proveedor"
                
        except Exception as e:
            return False, f"Error de conexión: {str(e)}"
    
    def estimate_cost(self, text_length: int) -> Optional[Dict[str, float]]:
        """
        Estima el costo de procesar un texto de cierta longitud.
        
        Args:
            text_length: Longitud del texto en caracteres
            
        Returns:
            Estimación de costo si aplica
        """
        # Estimación aproximada de tokens (1 token ≈ 4 caracteres)
        estimated_tokens = text_length / 4
        
        # Costos aproximados por millón de tokens (actualizar según sea necesario)
        cost_per_million = {
            'gpt-4o': {'input': 5.0, 'output': 15.0},
            'gpt-4': {'input': 30.0, 'output': 60.0},
            'gpt-3.5-turbo': {'input': 0.5, 'output': 1.5},
            'claude-3-opus': {'input': 15.0, 'output': 75.0},
            'llama3': {'input': 0.0, 'output': 0.0}  # Local, sin costo
        }
        
        if self.provider:
            model_info = self.provider.get_model_info()
            model = model_info.get('model', '')
            
            # Buscar costo del modelo
            for model_key, costs in cost_per_million.items():
                if model_key in model.lower():
                    input_cost = (estimated_tokens / 1_000_000) * costs['input']
                    # Asumimos que la salida será ~50% del input
                    output_cost = (estimated_tokens * 0.5 / 1_000_000) * costs['output']
                    
                    return {
                        'estimated_input_tokens': int(estimated_tokens),
                        'estimated_output_tokens': int(estimated_tokens * 0.5),
                        'estimated_cost_usd': round(input_cost + output_cost, 4),
                        'model': model
                    }
        
        return None

    def generate_summary(self, transcription: str, **kwargs) -> str:
        config = self.config_manager.get_config()
        prompt_template = config.get("summary_prompt", "")
        prompt = prompt_template + transcription
        self.logger.info("Generando resumen con prompt personalizado")
        response_text, metadata = self.provider.process(prompt, **kwargs)
        return response_text.strip()

    def generate_actions(self, transcription: str, **kwargs) -> str:
        config = self.config_manager.get_config()
        prompt_template = config.get("action_items_prompt", "")
        prompt = prompt_template + transcription
        self.logger.info("Generando propuestas de acción con prompt personalizado")
        response_text, metadata = self.provider.process(prompt, **kwargs)
        return response_text.strip()
