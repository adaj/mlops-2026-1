"""
config.py
=========

Configuração (hiperparâmetros e metadados) do IntentClassifier.
"""

from dataclasses import dataclass
from typing import List, Optional, Union


@dataclass
class Config:
    """
    A dataclass to hold all configuration parameters for the IntentClassifier.

    This object stores settings related to the dataset, model architecture,
    training process, and logging.
    """
    dataset_name: str = "undefined"
    """Name of the dataset, used for logging and model naming."""
    codes : List[str] = None
    """A list of intent codes (class labels). Automatically populated from data if not provided."""
    architecture: str = "v0.1.5"
    """Version tag for the model architecture."""
    task: str = "undefined"
    """The current task being performed (e.g., 'train', 'predict')."""
    stop_words_file: Optional[str] = None
    """Path to a text file containing stopwords, one per line."""
    min_words: int = 1
    """The minimum number of words required in an utterance for processing. Shorter inputs are padded."""
    embedding_model: Union[str, List[str]] = 'https://www.kaggle.com/models/google/universal-sentence-encoder/tensorFlow2/multilingual/2'
    """URL or path to the TensorFlow Hub embedding model."""
    sent_hl_units: Union[int, List[int]] = 32
    """Number of units in the hidden layer."""
    sent_dropout: Union[float, List[float]] = 0.1
    """Dropout rate applied after the hidden layer."""
    l1_reg: float = 0.01
    """L1 regularization factor for the hidden layer kernel."""
    l2_reg: float = 0.01
    """L2 regularization factor for the hidden layer kernel."""
    epochs: int = 500
    """Maximum number of epochs for training."""
    callback_patience: int = 20
    """Number of epochs with no improvement to wait before early stopping."""
    learning_rate: Union[float, List[float]] = 5e-3
    """Initial learning rate for the optimizer."""
    validation_split: float = 0.2
    """Fraction of the training data to be used as validation data."""
