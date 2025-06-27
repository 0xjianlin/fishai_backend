import os
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models, applications
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from pathlib import Path
import logging
from typing import Tuple, Dict, List
from ..utils.config import settings
from .species_service import species_service

logger = logging.getLogger(__name__)

class ModelTrainer:
    def __init__(self):
        self.model = None
        self.class_mapping: Dict[str, int] = {}
        self.reverse_class_mapping: Dict[int, str] = {}
        self.training_data_dir = Path(settings.TRAINING_DATA_DIR)
        
    def _create_model(self, num_classes: int) -> tf.keras.Model:
        """Create a CNN model for fish identification"""
        # Use MobileNetV2 as the base model
        base_model = applications.MobileNetV2(
            input_shape=settings.MODEL_INPUT_SIZE + (3,),
            include_top=False,
            weights='imagenet'
        )
        
        # Freeze the base model
        base_model.trainable = False
        
        # Create the model
        model = models.Sequential([
            base_model,
            layers.GlobalAveragePooling2D(),
            layers.Dropout(0.2),
            layers.Dense(512, activation='relu'),
            layers.Dropout(0.2),
            layers.Dense(num_classes, activation='softmax')
        ])
        
        # Compile the model
        model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=settings.LEARNING_RATE),
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        
        return model
    
    def _create_data_generators(self) -> Tuple[ImageDataGenerator, ImageDataGenerator]:
        """Create data generators for training and validation"""
        # Data augmentation for training
        train_datagen = ImageDataGenerator(
            rescale=1./255,
            rotation_range=20,
            width_shift_range=0.2,
            height_shift_range=0.2,
            shear_range=0.2,
            zoom_range=0.2,
            horizontal_flip=True,
            fill_mode='nearest',
            validation_split=settings.VALIDATION_SPLIT
        )
        
        # Only rescaling for validation
        val_datagen = ImageDataGenerator(
            rescale=1./255,
            validation_split=settings.VALIDATION_SPLIT
        )
        
        return train_datagen, val_datagen
    
    def _create_class_mapping(self) -> None:
        """Create mapping between species directories and class indices"""
        # Get all species directories
        species_dirs = [d for d in self.training_data_dir.iterdir() if d.is_dir()]
        species_dirs.sort()  # Sort for consistent mapping
        
        # Create mapping
        for idx, species_dir in enumerate(species_dirs):
            species_id = species_dir.name
            self.class_mapping[species_id] = idx
            self.reverse_class_mapping[idx] = species_id
            
        logger.info(f"Created class mapping for {len(self.class_mapping)} species")
    
    def _save_class_mapping(self) -> None:
        """Save class mapping to a file"""
        mapping_file = Path(settings.MODEL_PATH).parent / "class_mapping.json"
        import json
        
        with open(mapping_file, 'w') as f:
            json.dump({
                'class_mapping': self.class_mapping,
                'reverse_mapping': self.reverse_class_mapping
            }, f, indent=2)
        
        logger.info(f"Saved class mapping to {mapping_file}")
    
    def train(self) -> None:
        """Train the fish identification model"""
        try:
            # Create class mapping
            self._create_class_mapping()
            
            # Create data generators
            train_datagen, val_datagen = self._create_data_generators()
            
            # Create data generators for training and validation
            train_generator = train_datagen.flow_from_directory(
                str(self.training_data_dir),
                target_size=settings.MODEL_INPUT_SIZE,
                batch_size=settings.BATCH_SIZE,
                class_mode='categorical',
                subset='training',
                shuffle=True
            )
            
            validation_generator = val_datagen.flow_from_directory(
                str(self.training_data_dir),
                target_size=settings.MODEL_INPUT_SIZE,
                batch_size=settings.BATCH_SIZE,
                class_mode='categorical',
                subset='validation',
                shuffle=False
            )
            
            # Create and compile model
            num_classes = len(self.class_mapping)
            self.model = self._create_model(num_classes)
            
            # Create callbacks
            callbacks = [
                tf.keras.callbacks.EarlyStopping(
                    monitor='val_loss',
                    patience=5,
                    restore_best_weights=True
                ),
                tf.keras.callbacks.ReduceLROnPlateau(
                    monitor='val_loss',
                    factor=0.2,
                    patience=3
                ),
                tf.keras.callbacks.ModelCheckpoint(
                    filepath=str(Path(settings.MODEL_PATH)),
                    monitor='val_accuracy',
                    save_best_only=True
                )
            ]
            
            # Train the model
            logger.info("Starting model training...")
            history = self.model.fit(
                train_generator,
                epochs=settings.EPOCHS,
                validation_data=validation_generator,
                callbacks=callbacks
            )
            
            # Save class mapping
            self._save_class_mapping()
            
            logger.info("Model training completed successfully")
            
        except Exception as e:
            logger.error(f"Error during model training: {e}")
            raise
    
    def evaluate(self, test_data_dir: str = None) -> Dict[str, float]:
        """Evaluate the trained model"""
        if not self.model:
            raise ValueError("Model not trained yet")
            
        try:
            # Use validation data for evaluation if no test data provided
            if test_data_dir is None:
                test_data_dir = self.training_data_dir
                
            # Create data generator for evaluation
            test_datagen = ImageDataGenerator(rescale=1./255)
            test_generator = test_datagen.flow_from_directory(
                test_data_dir,
                target_size=settings.MODEL_INPUT_SIZE,
                batch_size=settings.BATCH_SIZE,
                class_mode='categorical',
                shuffle=False
            )
            
            # Evaluate model
            results = self.model.evaluate(test_generator)
            
            metrics = {
                'loss': results[0],
                'accuracy': results[1]
            }
            
            logger.info(f"Model evaluation results: {metrics}")
            return metrics
            
        except Exception as e:
            logger.error(f"Error during model evaluation: {e}")
            raise

# Create singleton instance
model_trainer = ModelTrainer() 