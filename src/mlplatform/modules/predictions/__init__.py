"""Módulo predictions: rota /predict, serviço, repositório e schemas. API pública do módulo."""

from mlplatform.modules.predictions.api import router
from mlplatform.modules.predictions.schemas import IntentPrediction, Response
from mlplatform.modules.predictions.service import predict_and_log_intent

__all__ = ["router", "predict_and_log_intent", "IntentPrediction", "Response"]
