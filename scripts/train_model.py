import sys
import os
from pathlib import Path
import logging

# Add the parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

from app.services.model_trainer import model_trainer
from app.utils.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Train the fish identification model"""
    try:
        # Ensure training data directory exists
        if not Path(settings.TRAINING_DATA_DIR).exists():
            logger.error(f"Training data directory not found: {settings.TRAINING_DATA_DIR}")
            return
        
        # Create models directory if it doesn't exist
        models_dir = Path(settings.MODEL_PATH).parent
        models_dir.mkdir(parents=True, exist_ok=True)
        
        # Train the model
        logger.info("Starting model training...")
        model_trainer.train()
        
        # Evaluate the model
        logger.info("Evaluating model...")
        metrics = model_trainer.evaluate()
        
        logger.info("Training completed successfully!")
        logger.info(f"Model evaluation metrics: {metrics}")
        
    except Exception as e:
        logger.error(f"Error during model training: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 