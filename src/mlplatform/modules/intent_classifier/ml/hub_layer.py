"""
hub_layer.py
============

Camada Keras customizada que carrega um módulo do TensorFlow Hub.
"""

import tensorflow as tf
import tensorflow_text  # noqa: F401  (registra ops necessárias ao embedding)
import tensorflow_hub as hub
from tensorflow.keras.saving import register_keras_serializable


@register_keras_serializable()
class HubLayer(tf.keras.layers.Layer):
    """
    A custom Keras layer to load and use a TensorFlow Hub module.

    This layer loads a pre-trained model from a TensorFlow Hub URL
    and integrates it into a Keras model. It can be set to be
    trainable or frozen.

    :param hub_url: The URL of the TensorFlow Hub module to load.
    :type hub_url: str
    :param trainable: Whether the loaded Hub module should be trainable.
    :type trainable: bool, optional
    """
    def __init__(self, hub_url, trainable=False, **kwargs):
        """
        Initializes the HubLayer.
        """
        super(HubLayer, self).__init__(**kwargs)
        self.hub_module = hub.load(hub_url)
        self.hub_module.trainable = trainable

    def call(self, inputs: tf.Tensor) -> tf.Tensor:
        """
        Executes the forward pass of the layer.

        :param inputs: The input tensor(s) to the Hub module.
        :type inputs: tf.Tensor
        :return: The output tensor(s) from the Hub module.
        :rtype: tf.Tensor
        """
        return self.hub_module(inputs)
