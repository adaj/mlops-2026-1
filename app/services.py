"""
services.py
===========

Módulo responsável pela lógica de negócios da aplicação, como carregar os classificadores e processar predições.
"""

from typing import Dict
from datetime import datetime, timezone
import logging

from mlplatform.modules.intent_classifier import IntentClassifier
from mlplatform.modules.predictions.repository import log_prediction
from mlplatform.modules.predictions.schemas import IntentPrediction, Response

logger = logging.getLogger(__name__)


def load_all_classifiers(models_to_load_str) -> dict:
    """
    Carrega todos os modelos de ML especificados na variável de ambiente
    WANDB_MODELS a partir do registro do Weights & Biases.
    """
    MODELS = {}
    model_urls = [url.strip() for url in models_to_load_str.split(',') if url.strip()]
    logger.info(f"Carregando {len(model_urls)} modelo(s) do W&B...")
    for url in model_urls:
        try:
            # 2. Extrair o nome do modelo da URL
            model_name = url.split('/')[-1].split(':')[0]
            # 3. Carregar o modelo usando o IntentClassifier
            logger.info(f"Carregando modelo: '{model_name}'")
            MODELS[model_name] = IntentClassifier(load_model=url)
            logger.info(f"Modelo '{model_name}' carregado com sucesso.")
        except Exception as e:
            logger.error(f"Falha ao carregar o modelo de '{url}': {e}")
            # Parar a inicialização do app se falhar ao carregar um modelo.
            raise Exception(f"Falha ao carregar o modelo de '{url}': {e}")
    return MODELS


def predict_and_log_intent(
    text: str, 
    owner: str, 
    models: Dict[str, IntentClassifier]
) -> Dict:
    """
    Executes predictions, records metrics, and logs to DB.
    """
    # 1. Execute Predictions (ML Logic)
    predictions = {}
    for model_name, model in models.items():
        top_intent, all_probs = model.predict(text)
        
        predictions[model_name] = IntentPrediction(top_intent=top_intent, 
                                                   all_probs=all_probs)

    # 2. Format Prediction and Save to DB (Infrastructure Logic) (Data Logic)
    log_document = Response(
        text=text, 
        owner=owner, 
        predictions=predictions, 
        timestamp=int(datetime.now(timezone.utc).timestamp())
    )
    result_to_return = log_document.model_dump()
    
    try:
        saved_record = log_prediction(log_document)
        result_to_return = saved_record
    except Exception as e:
        logger.error(f"Failed to log prediction to DB: {e}")

    return result_to_return

