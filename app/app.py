"""
app.py
======

Módulo FastAPI responsável por servir o modelo de classificação de intenções.

Comando para rodar:
    uvicorn app.app:app --host 0.0.0.0 --port 8000 --log-level debug
"""


import os
import time
import traceback
from dotenv import load_dotenv
import logging
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

# Internal modules
from db.auth import conditional_auth
from app import services

# Import OpenTelemetry setup from observability module
from app.observability import init_opentelemetry
from opentelemetry import trace
from opentelemetry.metrics import get_meter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor 

# Initialize OpenTelemetry
init_opentelemetry()
logger = logging.getLogger(__name__)

# Get tracer and meter after initialization
tracer = trace.get_tracer(__name__)
meter = get_meter(__name__)

# Get custom metrics after initialization
prediction_count = meter.create_counter(
    "prediction_count",
    description="Number of predictions made"
)
prediction_latency = meter.create_histogram(
    "prediction_latency_seconds",
    description="Latency of model predictions in seconds",
    unit="s"
)


# Load environment variables from .env file
load_dotenv()

# Read environment mode (defaults to dev for safety)
ENV = os.getenv("ENV", "dev").lower()
logger.info(f"Running in {ENV} mode")

# Dicionário global para armazenar os modelos carregados.
MODELS = {}

def get_model_urls() -> str:
    """
    Busca a string de URLs de modelos da variável de ambiente WANDB_MODELS.
    Isolar essa lógica em uma função facilita o patching durante os testes.
    """
    models_env = os.getenv("WANDB_MODELS")
    assert models_env is not None, "Variável de ambiente WANDB_MODELS não definida."
    return models_env

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Código que será executado durante a inicialização do app.
    """

    global MODELS
    logger.info("Carregando modelos do W&B durante a inicialização do app...")
    try:
        model_urls_str = get_model_urls()
        MODELS = services.load_all_classifiers(model_urls_str)
        logger.info("Modelos do W&B carregados com sucesso.")
    except Exception as e:
        logger.error(f"Falha crítica ao carregar modelos do W&B: {str(e)}")
        logger.error(traceback.format_exc())
        raise Exception(f"Falha crítica ao carregar modelos do W&B: {str(e)}")
    # This is the point where the app is ready to handle requests
    yield
    # Código para ser executado no shutdown (opcional)
    logger.info("Descarregando modelos e limpando recursos...")
    MODELS.clear()


# Initialize FastAPI app with the lifespan manager
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


"""
Routes
"""
@app.get("/")
async def root():
    return {"message": f"Basic ML App is running in {ENV} mode"}

@app.post("/predict")
async def predict(text: str, owner: str = Depends(conditional_auth)):
    """
    Endpoint de predição.
    Este é um 'Controller' enxuto. 
    Ele apenas delega a lógica de negócio para o services.py.
    """
    start_time = time.time()
    try:
        # 1. O Controller delega TODA a lógica de negócio para o services.py
        results = services.predict_and_log_intent(
            text=text, 
            owner=owner, 
            models=MODELS
        )
        # Record custom metrics
        duration = time.time() - start_time
        predictions = results.get("predictions", {})
        for model_name, pred in predictions.items():
            top_intent = "unknown"
            if hasattr(pred, "top_intent"):
                top_intent = pred.top_intent
            elif isinstance(pred, dict) and "top_intent" in pred:
                top_intent = pred["top_intent"]
            
            prediction_latency.record(duration, {"model": model_name})
            prediction_count.add(1, {"model": model_name, "intent": top_intent})

        # 2. O Controller retorna a resposta (Lógica de View) no formato JSON
        return JSONResponse(content=results)
    except Exception as e:
        logger.error(f"Erro ao processar a predição: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Erro interno ao processar a predição: {str(e)}")



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)