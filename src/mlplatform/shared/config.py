"""
config.py
=========

Carregamento do ``.env`` e leitura de variáveis de ambiente sob demanda.
"""

import os

from dotenv import find_dotenv, load_dotenv

_loaded = False


def load_env() -> None:
    """Carrega o arquivo ``.env`` (se existir). Idempotente."""
    global _loaded
    if _loaded:
        return
    load_dotenv(find_dotenv() or find_dotenv(usecwd=True))
    _loaded = True


def get_env(name: str, default=None):
    """Lê uma variável de ambiente (carregando o ``.env`` antes, se necessário)."""
    load_env()
    return os.getenv(name, default)
