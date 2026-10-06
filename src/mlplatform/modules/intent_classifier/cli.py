"""
cli.py
======

CLI de treino e predição. Execute a partir da raiz do repositório. Os caminhos
relativos são resolvidos a partir do diretório atual::

    M=src/mlplatform/modules/intent_classifier

    python -m mlplatform.modules.intent_classifier.cli train \\
        --config="$M/data/clair_intents/clair_intents_config.yml" \\
        --training_data="$M/data/clair_intents/clair_intents.yml" \\
        --save_model="$M/models/clair_intents.keras" \\
        --wandb_project="mlops-2026-1"

    python -m mlplatform.modules.intent_classifier.cli predict \\
        --load_model="$M/models/confusion.keras" \\
        --input_text="teste teste" \\
        --wandb_project="intent-classifier"
"""

from mlplatform.modules.intent_classifier.ml.classifier import IntentClassifier

# This script works as a module and as a CLI tool
if __name__ == "__main__":
    import fire
    # Instead of fire.Fire(IntentClassifier),
    # Define the functions to be used by Fire CLI so that 
    #  it's not cluttered with all the functions in the IntentClassifier class
    def train(config: str, training_data: str, save_model: str = None, wandb_project: str = None):
        """
        Train the model with the given configuration and examples.

        :param config: Path to the YAML configuration file.
        :type config: str
        :param training_data: Path to the YAML file with training examples.
        :type training_data: str
        :param save_model: Path to save the trained model (e.g., "model.keras").
        :type save_model: str   
        :param wandb_project: Name of the Weights & Biases project to log to.
        :type wandb_project: str
        """
        classifier = IntentClassifier(config=config, training_data=training_data, wandb_project=wandb_project)
        classifier.train(save_model=save_model)
        print("Training completed successfully!")

    def predict(load_model: str, input_text: str, wandb_project: str = None):
        """
        Make predictions using a trained model.

        :param load_model: Path to the saved Keras model file or W&B URL.
        :type load_model: str
        :param input_text: The input text string to classify.
        :type input_text: str
        :param wandb_project: Name of the Weights & Biases project to log to.
        :type wandb_project: str
        """
        classifier = IntentClassifier(load_model=load_model, wandb_project=wandb_project)
        predictions = classifier.predict(input_text)
        print(f"Predictions: {predictions}")

    fire.Fire({
        'train': train,
        'predict': predict
    }, serialize=False)
