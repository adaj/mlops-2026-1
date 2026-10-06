"""
deps.py
=======

Dependências FastAPI de autenticação.
"""

from datetime import datetime

from fastapi import HTTPException, Request

from mlplatform.modules.auth import repository
from mlplatform.shared.config import get_env


def verify_token(request: Request):
    token = request.headers.get("Authorization")
    if not token:
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    token = token.replace("Bearer ", "")
    token_entry = repository.find_active_token(token)

    if not token_entry:
        raise HTTPException(status_code=403, detail="Invalid or inactive token")

    if datetime.utcnow() > token_entry["expires_at"]:
        raise HTTPException(status_code=403, detail="Token expired")

    return token_entry["owner"]


async def conditional_auth(request: Request):
    """
    Retorna o 'owner' baseado no modo do ambiente (dev ou prod).
    Esta função é o 'Depends' principal para as rotas.
    """
    if get_env("ENV", "prod").lower() == "dev":
        return "dev_user"
    else:
        try:
            return verify_token(request)
        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(status_code=401, detail="Authentication failed")
