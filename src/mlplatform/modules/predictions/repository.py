"""
repository.py
=============

Persistência dos logs de predição no MongoDB.
"""

from mlplatform.shared.config import get_env
from mlplatform.shared.db.mongo import get_collection


def log_prediction(prediction_data) -> dict:
    """
    Insere um log de predição no banco de dados e retorna o
    documento inserido com o ID formatado para resposta JSON.
    """
    env = get_env("ENV", "prod").lower()
    collection = get_collection(f"{env.upper()}_intent_logs")
    
    # Converte o modelo Pydantic para um dicionário antes de inserir
    prediction_dict = prediction_data.model_dump()

    # Log the prediction to the database
    try:
        # O Pymongo modifica o dicionário `prediction_dict`, adicionando um campo `_id`.
        result = collection.insert_one(prediction_dict)
        
        # Adicionamos o ID gerado como uma string para a resposta JSON
        # e removemos o campo `_id` (do tipo ObjectId) que não é serializável.
        prediction_dict["id"] = str(result.inserted_id)
        prediction_dict.pop("_id", None)

    except Exception as e:
        # If insert_one fails, log the error and continue
        raise Exception(f"Failed to log prediction to database. Error: {e}")

    return prediction_dict

