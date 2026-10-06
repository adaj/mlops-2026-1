"""
main.py
=======

Aplicação FastAPI que serve o modelo de classificação de intenções.

Comando para rodar:
    uvicorn mlplatform.main:app --host 0.0.0.0 --port 8000 --log-level debug
"""

import logging
import traceback
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

from mlplatform.modules.intent_classifier import clear_models, load_all_classifiers
from mlplatform.modules.predictions import router as predictions_router
from mlplatform.shared.config import get_env
from mlplatform.shared.logging import register_request_logging
from mlplatform.shared.observability import init_opentelemetry

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Código que será executado durante a inicialização do app.
    """
    logger.info("Carregando modelos do W&B durante a inicialização do app...")
    try:
        load_all_classifiers()
        logger.info("Modelos do W&B carregados com sucesso.")
    except Exception as e:
        logger.error(f"Falha crítica ao carregar modelos do W&B: {str(e)}")
        logger.error(traceback.format_exc())
        raise Exception(f"Falha crítica ao carregar modelos do W&B: {str(e)}")
    # This is the point where the app is ready to handle requests
    yield
    # Código para ser executado no shutdown (opcional)
    logger.info("Descarregando modelos e limpando recursos...")
    clear_models()


def create_app() -> FastAPI:
    # Initialize OpenTelemetry
    init_opentelemetry()

    # Read environment mode (defaults to dev for safety)
    env = get_env("ENV", "dev").lower()
    logger.info(f"Running in {env} mode")

    app = FastAPI(
        title="Basic ML App",
        description="A basic ML app",
        version="1.0.0",
        lifespan=lifespan,
    )

    # Controle de CORS (Cross-Origin Resource Sharing) para prevenir ataques de fontes não autorizadas.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],              # permite todos os métodos: GET, POST, etc
        allow_headers=["*"],              # permite todos os headers (Authorization, Content-Type...)
        # Durante o desenvolvimento: você pode usar allow_origins=["*"] para liberar tudo.
        # Em produção: evite "*" e especifique os domínios confiáveis.
    )

    # Instrument FastAPI metrics
    FastAPIInstrumentor().instrument_app(app)

    # Add request logging middleware
    register_request_logging(app)

    @app.get("/")
    async def root():
        return {"message": f"Basic ML App is running in {env} mode"}

    app.include_router(predictions_router)
    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
