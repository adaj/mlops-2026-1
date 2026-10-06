"""
service.py
==========

Regras de negócio de gerenciamento de tokens da API.
"""

import uuid
from datetime import datetime, timedelta

from mlplatform.modules.auth import repository


class TokenManager:
    """
    Gerencia tokens da API.
    """
    def create(self, owner: str, note: str = "", expires_in_days: int = 180):
        """
        Cria um novo token com tempo de expiração.

        Args:
            owner (str): Nome do dono do token.
            note (str): Descrição.
            expires_in_days (int): Validade do token em dias.
        """
        token = str(uuid.uuid4())

        now = datetime.utcnow()
        token_doc = {
            "token": token,
            "owner": owner,
            "note": note,
            "created_at": now,
            "expires_at": now + timedelta(days=expires_in_days),
            "active": True
        }

        repository.insert_token(token_doc)
        print(f"✅ Token criado (expira em {expires_in_days} dias): {token}")

    def read_all(self):
        """
        Lê e imprime todos os tokens armazenados no MongoDB.
        """
        for t in repository.list_tokens():
            print({
                "token": t.get("token"),
                "owner": t.get("owner"),
                "note": t.get("note"),
                "active": t.get("active"),
                "created_at": t.get("created_at")
            })

    def delete_expired(self):
        """
        Remove tokens expirados da base.
        """
        deleted = repository.delete_expired(datetime.utcnow())
        print(f"🧹 Tokens expirados removidos: {deleted}")
