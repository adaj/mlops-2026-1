"""
logging.py
==========

Logger compartilhado e middleware de log de requisições HTTP.
"""

import logging
import time

from fastapi import FastAPI, Request


def get_logger(name: str) -> logging.Logger:
    """Retorna um logger padrão da stdlib (a configuração fica em observability)."""
    return logging.getLogger(name)


logger = get_logger(__name__)


def register_request_logging(app: FastAPI) -> None:
    """Registra o middleware que loga requisições e respostas."""

    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        start_time = time.time()

        # Log incoming request
        logger.info(f"Incoming request: {request.method} {request.url}")
        if request.method == "POST":
            # Note: we can't log the body here easily without consuming it
            logger.info(f"Request headers: {dict(request.headers)}")

        response = await call_next(request)

        # Log response
        process_time = time.time() - start_time
        logger.info(f"Response: {response.status_code} - Time: {process_time:.3f}s")

        return response
