"""
api.py
======

Rota de predição (camada HTTP enxuta; a lógica fica em service.py).
"""

import logging
import time
import traceback

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse

from mlplatform.modules.auth import conditional_auth
from mlplatform.modules.intent_classifier import get_models
from mlplatform.modules.predictions import service
from mlplatform.shared import observability

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/predict")
async def predict(text: str, owner: str = Depends(conditional_auth)):
    """
    Endpoint de predição.
    Este é um 'Controller' enxuto.
    Ele apenas delega a lógica de negócio para o service.py.
    """
    start_time = time.time()
    try:
        # 1. O Controller delega TODA a lógica de negócio para o service.py
        results = service.predict_and_log_intent(
            text=text,
            owner=owner,
            models=get_models()
        )
        # Record custom metrics
        duration = time.time() - start_time
        predictions = results.get("predictions", {})
        for model_name, pred in predictions.items():
            top_intent = "unknown"
            if hasattr(pred, "top_intent"):
                top_intent = pred.top_intent
            elif isinstance(pred, dict) and "top_intent" in pred:
                top_intent = pred["top_intent"]

            observability.prediction_latency.record(duration, {"model": model_name})
            observability.prediction_count.add(1, {"model": model_name, "intent": top_intent})

        # 2. O Controller retorna a resposta (Lógica de View) no formato JSON
        return JSONResponse(content=results)
    except Exception as e:
        logger.error(f"Erro ao processar a predição: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Erro interno ao processar a predição: {str(e)}")
