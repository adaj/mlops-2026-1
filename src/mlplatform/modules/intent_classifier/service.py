"""
service.py
==========

Registro dos classificadores carregados em memória e carregamento a partir do W&B.
"""

import logging
from typing import Dict, Optional

from mlplatform.modules.intent_classifier.ml.classifier import IntentClassifier
from mlplatform.shared.config import get_env

logger = logging.getLogger(__name__)

# Registro global dos modelos carregados (nome -> IntentClassifier).
MODELS: Dict[str, IntentClassifier] = {}


def get_model_urls() -> str:
    """
    Busca a string de URLs de modelos da variável de ambiente WANDB_MODELS.
    Isolar essa lógica em uma função facilita o patching durante os testes.
    """
    models_env = get_env("WANDB_MODELS")
    assert models_env is not None, "Variável de ambiente WANDB_MODELS não definida."
    return models_env


def get_models() -> Dict[str, IntentClassifier]:
    """Retorna o registro de modelos carregados."""
    return MODELS


def clear_models() -> None:
    """Descarrega os modelos do registro."""
    MODELS.clear()


def load_all_classifiers(models_to_load_str: Optional[str] = None) -> Dict[str, IntentClassifier]:
    """
    Carrega todos os modelos de ML especificados (por padrão, na variável de ambiente
    WANDB_MODELS) a partir do registro do Weights & Biases e os registra em MODELS.
    """
    if models_to_load_str is None:
        models_to_load_str = get_model_urls()
    loaded = {}
    model_urls = [url.strip() for url in models_to_load_str.split(',') if url.strip()]
    logger.info(f"Carregando {len(model_urls)} modelo(s) do W&B...")
    for url in model_urls:
        try:
            # Extrair o nome do modelo da URL
            model_name = url.split('/')[-1].split(':')[0]
            # Carregar o modelo usando o IntentClassifier
            logger.info(f"Carregando modelo: '{model_name}'")
            loaded[model_name] = IntentClassifier(load_model=url)
            logger.info(f"Modelo '{model_name}' carregado com sucesso.")
        except Exception as e:
            logger.error(f"Falha ao carregar o modelo de '{url}': {e}")
            # Parar a inicialização do app se falhar ao carregar um modelo.
            raise Exception(f"Falha ao carregar o modelo de '{url}': {e}")
    MODELS.clear()
    MODELS.update(loaded)
    return MODELS
