import tensorflow as tf
import tensorflow_hub as hub
import numpy as np
from pathlib import Path
import os

def create_model(num_classes: int = 3) -> tf.keras.Model:
    """
    Create a fish identification model based on MobileNetV2
    Args:
        num_classes: Number of fish species to classify
    Returns:
        Compiled Keras model
    """
    # Load pre-trained MobileNetV2
    base_model = tf.keras.applications.MobileNetV2(
        input_shape=(224, 224, 3),
        include_top=False,
        weights='imagenet'
    )
    
    # Freeze the base model
    base_model.trainable = False
    
    # Create model
    model = tf.keras.Sequential([
        base_model,
        tf.keras.layers.GlobalAveragePooling2D(),
        tf.keras.layers.Dropout(0.2),
        tf.keras.layers.Dense(128, activation='relu'),
        tf.keras.layers.Dropout(0.2),
        tf.keras.layers.Dense(num_classes, activation='softmax')
    ])
    
    # Compile model
    model.compile(
        optimizer='adam',
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    
    return model

def save_model(model: tf.keras.Model, model_path: str):
    """
    Save the model to disk
    """
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    
    # Save model
    model.save(model_path)
    print(f"Model saved to {model_path}")

def main():
    # Create and save initial model
    model = create_model()
    
    # Get model path from settings
    from ..utils.config import settings
    model_path = settings.MODEL_PATH
    
    # Save model
    save_model(model, model_path)
    
    # Test model with random input
    test_input = np.random.random((1, 224, 224, 3))
    prediction = model.predict(test_input)
    print("\nModel test successful!")
    print(f"Input shape: {test_input.shape}")
    print(f"Output shape: {prediction.shape}")
    print(f"Output sample: {prediction[0]}")

if __name__ == "__main__":
    main() 