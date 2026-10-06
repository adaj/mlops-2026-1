"""
repository.py
=============

Acesso à coleção ``api_tokens`` no MongoDB.
"""

from datetime import datetime

from mlplatform.shared.db.mongo import get_collection

COLLECTION = "api_tokens"


def insert_token(token_doc: dict) -> None:
    get_collection(COLLECTION).insert_one(token_doc)


def list_tokens():
    return get_collection(COLLECTION).find()


def delete_expired(now: datetime) -> int:
    result = get_collection(COLLECTION).delete_many({"expires_at": {"$lt": now}})
    return result.deleted_count


def find_active_token(token: str):
    return get_collection(COLLECTION).find_one({"token": token, "active": True})
