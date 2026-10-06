# MLOps 2026.1 - Serviço de Classificador de Texto

## Como instalar?

```bash
conda create -n intent-clf python=3.11
conda activate intent-clf
pip install -e .          # instala o pacote mlplatform (src-layout) e as dependências de requirements.txt
# opcional: pip install -e ".[dev]"  /  pip install -e ".[docs]"
```

## Como treinar um modelo?

Execute a partir da **raiz do repositório**. Os caminhos relativos são resolvidos a partir do
diretório atual (antes, os comandos eram executados dentro de `intent_classifier/`); os dados de
treino agora ficam em `src/mlplatform/modules/intent_classifier/`.

```bash
M=src/mlplatform/modules/intent_classifier

python -m mlplatform.modules.intent_classifier.cli train \
    --config="$M/reports/confusion/confusion_config.yml" \
    --training_data="$M/reports/confusion/confusion_intents.yml" \
    --save_model="$M/models/confusion.keras" \
    --wandb_project="mlops-2026-1"

python -m mlplatform.modules.intent_classifier.cli train \
    --config="$M/data/clair_intents/clair_intents_config.yml" \
    --training_data="$M/data/clair_intents/clair_intents.yml" \
    --save_model="$M/models/clair_intents.keras" \
    --wandb_project="mlops-2026-1"
```

## Como fazer uma predição local?

```bash
python -m mlplatform.modules.intent_classifier.cli predict \
    --load_model="$M/models/confusion.keras" \
    --input_text="teste teste" \
    --wandb_project="intent-classifier"
```

Modelos baixados do W&B são salvos em `src/mlplatform/modules/intent_classifier/models/`
(sobrescreva com a variável de ambiente `MODELS_DIR`).

## Como rodar a API?

Certifique-se de preencher o arquivo .env com as variáveis de ambiente.

```bash
# Na pasta raiz:
python -m uvicorn mlplatform.main:app --host 0.0.0.0 --port 8000 --log-level debug --reload
```

Ou com Docker: `docker compose up --build`.

## Como gerenciar tokens da API?

```bash
python -m mlplatform.modules.auth.cli create --owner="alguem" --expires_in_days=365
python -m mlplatform.modules.auth.cli read_all
```

## Arquitetura (monolito modular)

```
src/mlplatform/
  main.py                    # create_app(), lifespan, CORS, rota "/"
  shared/                    # config (.env), logging, observability, db/mongo
  modules/
    auth/                    # deps, service, repository, cli
    intent_classifier/       # ml/ (classifier, config, hub_layer, wandb_artifacts), service, cli,
                             # data/, reports/, models/
    predictions/             # api (/predict), service, repository, schemas
```

Regras de dependência:

- `main` pode importar tudo; `predictions` -> `intent_classifier`, `auth`, `shared`; `auth` -> `shared`;
  `intent_classifier` -> `shared.config`; `shared` nunca importa de `modules`.
- Um módulo só importa outro módulo pela sua API pública (`__init__.py`), nunca por submódulos.
- Sem dependências circulares.
