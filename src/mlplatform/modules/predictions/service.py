"""
service.py
==========

Lógica de negócio de predição: executa os modelos e registra o resultado.
"""

import logging
from datetime import datetime, timezone
from typing import Dict

from mlplatform.modules.intent_classifier import IntentClassifier
from mlplatform.modules.predictions.repository import log_prediction
from mlplatform.modules.predictions.schemas import IntentPrediction, Response

logger = logging.getLogger(__name__)


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

