"""
wandb_artifacts.py
==================

Download de artefatos de modelo do Weights & Biases.
"""

import os
from pathlib import Path
from typing import Tuple

import wandb

from mlplatform.shared.config import get_env


def get_models_dir() -> Path:
    """Diretório local de modelos (override via variável de ambiente MODELS_DIR)."""
    override = get_env("MODELS_DIR")
    if override:
        return Path(override)
    return Path(__file__).resolve().parents[1] / "models"


MODELS_DIR = get_models_dir()


def fetch_artifact_from_wandb(model_full_name: str) -> Tuple[str, str]:
    """
    Download a model artifact from W&B and return the paths to the model and config files.

    :param model_full_name: The W&B artifact full name (e.g., "adaj/intent-classifier-2025-2/confusion-clf:v1").
                           Must have format: "entity/project/artifact_name:version"
    :type model_full_name: str
    :return: A tuple containing the local file path to the Keras model file and the config file.
    :rtype: tuple[str, str]
    :raises ValueError: If format is invalid or files are not found in the artifact.
    """
    # Validate format
    parts = model_full_name.split("/")
    if len(parts) != 3 or ":" not in parts[2]:
        raise ValueError(
            f"Invalid model_full_name format: '{model_full_name}'. "
            f"Expected format: 'entity/project/artifact_name:version' (e.g., 'adaj/intent-classifier-2025-2/confusion-clf:v1')"
        )
    
    # Download artifact from W&B
    try:
        api = wandb.Api()
        artifact = api.artifact(model_full_name, type='model')
    except wandb.errors.CommError as e:
        raise ValueError(f"Could not fetch artifact '{model_full_name}' from W&B. Ensure the path is correct and you are logged in. Original error: {e}")

    # Create a target directory for the download
    models_dir = MODELS_DIR
    models_dir.mkdir(exist_ok=True)
    
    # Download artifact content. The path returned is the directory where files are.
    download_path = artifact.download(root=models_dir)
    
    model_file, config_file = None, None
    # Iterate over the files *in the artifact manifest* to find the correct ones.
    # This prevents accidentally loading unrelated files from the same directory.
    for f in artifact.files():
        if f.name.endswith((".keras", ".h5")):
            model_file = os.path.join(download_path, f.name)
        elif f.name.endswith("_config.yml"):
            config_file = os.path.join(download_path, f.name)
            
    if not model_file:
        raise ValueError(f"Model file (.keras or .h5) not found in W&B artifact '{model_full_name}'.")
    if not config_file:
        raise ValueError(f"Config file (_config.yml) not found in W&B artifact '{model_full_name}'.")
        
    return model_file, config_file
