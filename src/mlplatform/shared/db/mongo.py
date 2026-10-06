"""
mongo.py
========

Conexão com o MongoDB. O cliente é criado de forma lazy e reutilizado.
"""

from functools import lru_cache

from pymongo import MongoClient

from mlplatform.shared.config import get_env


@lru_cache(maxsize=1)
def get_client() -> MongoClient:
    """Retorna o MongoClient (criado na primeira chamada e reutilizado)."""
    mongo_uri = get_env("MONGO_URI", None)
    if mongo_uri is None or get_env("MONGO_DB", None) is None:
        raise ValueError("MONGO_URI and MONGO_DB must be set")
    return MongoClient(mongo_uri)


def get_db():
    """Retorna o banco definido em MONGO_DB."""
    client = get_client()
    return client[get_env("MONGO_DB", None)]


def get_collection(collection_name: str):
    """Retorna uma coleção do banco configurado."""
    return get_db()[collection_name]
