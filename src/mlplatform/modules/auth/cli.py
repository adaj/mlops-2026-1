"""
cli.py
======

Criar um novo token:
    python -m mlplatform.modules.auth.cli create --owner="alguem" --expires_in_days=365

Ler todos os tokens:
    python -m mlplatform.modules.auth.cli read_all
"""

import fire

from mlplatform.modules.auth.service import TokenManager

if __name__ == "__main__":
    fire.Fire(TokenManager)
