"""
Este arquivo contém os modelos Pydantic que definem a estrutura (o "schema")
dos dados que entram e, principalmente, saem da nossa API.

Eles são usados diretamente pelo FastAPI para:
1.  Validar Respostas: Garantir que o JSON retornado pelos endpoints
    (ex: /predict) siga exatamente o contrato definido aqui (ex: PredictionResponse).
2.  Documentação Automática: Gerar a documentação interativa
    (em /docs e /redoc) com exemplos claros dos schemas de resposta.
3.  Serialização: Converter tipos de dados complexos (como objetos Python)
    em JSON formatado para o cliente.
"""

from pydantic import BaseModel
from typing import Dict, Optional

class IntentPrediction(BaseModel):
    top_intent: str
    all_probs: Dict[str, float]

class Response(BaseModel):
    id: Optional[str] = None 
    text: str
    owner: str
    predictions: Dict[str, IntentPrediction]
    timestamp: int