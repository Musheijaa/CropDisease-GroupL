import os
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout, BatchNormalization
from tensorflow.keras.optimizers import Adam
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.utils import class_weight
import plotly.express as px
import plotly.io as pio
from pathlib import Path
from PIL import Image
import logging
import json
import sys

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('training.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Set Plotly renderer to PNG
try:
    pio.renderers.default = 'png'
except Exception as e:
    logger.error(f"Failed to set Plotly renderer: {e}")
    sys.exit(1)

# Enable GPU memory growth
try:
    physical_devices = tf.config.list_physical_devices('GPU')
    if physical_devices:
        tf.config.experimental.set_memory_growth(physical_devices[0], True)
        logger.info(f"GPU detected: {physical_devices}")
    else:
        logger.info("No GPU detected, using CPU.")
except Exception as e:
    logger.error(f"Error configuring GPU: {e}")

# Set random seed for reproducibility
tf.random.set_seed(42)
np.random.seed(42)

# Define paths
base_dir = './dataset/New Plant Diseases Dataset(Augmented)/New Plant Diseases Dataset(Augmented)'
train_dir = os.path.join(base_dir, 'train')
valid_dir = os.path.join(base_dir, 'valid')
test_dir = './dataset/test/test'

# Data Exploration (Task 1, 2)
def explore_dataset():
    logger.info("Starting dataset exploration...")
    try:
        for dir_path in [train_dir, valid_dir, test_dir]:
            if not os.path.exists(dir_path):
                logger.error(f"Directory not found: {dir_path}")
                raise FileNotFoundError(f"Directory not found: {dir_path}")

        classes = [d for d in os.listdir(train_dir) if os.path.isdir(os.path.join(train_dir, d))]
        if not classes:
            logger.error("No classes found in training directory")
            raise ValueError("No classes found in training directory")

        class_counts = {}
        corrupted_files = []
        
        for class_name in classes:
            class_path = os.path.join(train_dir, class_name)
            image_count = 0
            for img in os.listdir(class_path):
                img_path = os.path.join(class_path, img)
                try:
                    with Image.open(img_path) as img_file:
                        img_file.verify()
                    image_count += 1
                except Exception as e:
                    logger.warning(f"Corrupted image: {img_path}, error: {e}")
                    corrupted_files.append(img_path)
            class_counts[class_name] = image_count
        
        if not class_counts:
            logger.error("No valid images found in training directory")
            raise ValueError("No valid images found in training directory")

        df_counts = pd.DataFrame(list(class_counts.items()), columns=['Class', 'Count'])
        logger.info("Training Dataset Class Distribution:")
        logger.info(df_counts.to_string())
        
        # Visualize class distribution (Task 8)
        try:
            fig = px.bar(df_counts, x='Class', y='Count', title='Class Distribution in Training Set')
            fig.update_layout(xaxis_tickangle=45)
            fig.write_image('class_distribution.png')
            logger.info("Saved class distribution plot as class_distribution.png")
        except Exception as e:
            logger.warning(f"Error saving Plotly figure: {e}. Falling back to Matplotlib.")
            plt.figure(figsize=(12, 6))
            plt.bar(df_counts['Class'], df_counts['Count'])
            plt.title('Class Distribution in Training Set')
            plt.xlabel('Class')
            plt.ylabel('Count')
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.savefig('class_distribution.png')
            plt.close()
            logger.info("Saved class distribution plot as class_distribution.png (Matplotlib fallback)")
        
        logger.info(f"Corrupted or invalid files: {len(corrupted_files)}")
        if corrupted_files:
            logger.info(f"Corrupted files (first 5): {corrupted_files[:5]}")
        
        valid_classes = [d for d in os.listdir(valid_dir) if os.path.isdir(os.path.join(valid_dir, d))]
        test_classes = [d for d in os.listdir(test_dir) if os.path.isdir(os.path.join(test_dir, d))]
        test_files = []
        for root, _, files in os.walk(test_dir):
            test_files.extend([os.path.join(root, f) for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg'))])
        
        logger.info(f"Number of classes in validation set: {len(valid_classes)}")
        logger.info(f"Number of classes in test set: {len(test_classes)}")
        logger.info(f"Number of test images: {len(test_files)}")
        
        if set(classes) != set(valid_classes):
            logger.warning("Class mismatch between training and validation sets!")
        
        if not test_files:
            logger.warning("No valid test images found. Evaluation may fail.")
        
        if test_classes and set(test_classes) != set(classes):
            logger.warning("Class mismatch between training and test sets!")
        
        return class_counts
    except Exception as e:
        logger.error(f"Dataset exploration failed: {e}")
        raise

# Data Preprocessing (Task 5)
def create_data_generators(class_counts):
    try:
        train_datagen = ImageDataGenerator(
            rescale=1./255,
            rotation_range=20,
            width_shift_range=0.2,
            height_shift_range=0.2,
            shear_range=0.2,
            zoom_range=0.2,
            horizontal_flip=True,
            fill_mode='nearest'
        )
        
        valid_datagen = ImageDataGenerator(rescale=1./255)
        
        batch_size = 32
        while True:
            try:
                train_generator = train_datagen.flow_from_directory(
                    train_dir,
                    target_size=(224, 224),
                    batch_size=batch_size,
                    class_mode='categorical'
                )
                valid_generator = valid_datagen.flow_from_directory(
                    valid_dir,
                    target_size=(224, 224),
                    batch_size=batch_size,
                    class_mode='categorical'
                )
                test_generator = valid_datagen.flow_from_directory(
                    test_dir,
                    target_size=(224, 224),
                    batch_size=1,
                    class_mode='categorical',
                    shuffle=False
                )
                
                # Validate class consistency
                if train_generator.num_classes != valid_generator.num_classes:
                    logger.error("Number of classes in train and validation generators do not match")
                    raise ValueError("Class mismatch between train and validation")
                
                if test_generator.num_classes == 0:
                    logger.warning("No classes found in test generator. Using validation set for evaluation.")
                    test_generator = valid_generator
                elif test_generator.num_classes != train_generator.num_classes:
                    logger.warning("Test generator classes do not match training classes")
                
                return train_generator, valid_generator, test_generator
            except Exception as e:
                logger.warning(f"Data generator failed with batch_size={batch_size}: {e}")
                batch_size //= 2
                if batch_size < 4:
                    logger.error("Unable to create data generators even with reduced batch size")
                    raise ValueError("Failed to create data generators")
                logger.info(f"Retrying with reduced batch_size={batch_size}")
    except Exception as e:
        logger.error(f"Data preprocessing failed: {e}")
        raise

# Build CNN Model
def build_cnn_model(num_classes):
    try:
        if num_classes <= 0:
            logger.error("Invalid number of classes: %d", num_classes)
            raise ValueError("Number of classes must be positive")
        
        model = Sequential([
            Conv2D(32, (3, 3), activation='relu', input_shape=(224, 224, 3)),
            BatchNormalization(),
            MaxPooling2D((2, 2)),
            Conv2D(64, (3, 3), activation='relu'),
            BatchNormalization(),
            MaxPooling2D((2, 2)),
            Conv2D(128, (3, 3), activation='relu'),
            BatchNormalization(),
            MaxPooling2D((2, 2)),
            Conv2D(128, (3, 3), activation='relu'),
            BatchNormalization(),
            MaxPooling2D((2, 2)),
            Flatten(),
            Dense(512, activation='relu'),
            Dropout(0.5),
            Dense(256, activation='relu'),
            Dropout(0.3),
            Dense(num_classes, activation='softmax')
        ])
        
        model.compile(
            optimizer=Adam(learning_rate=0.001),
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        
        logger.info("CNN model built successfully")
        model.summary()
        return model
    except Exception as e:
        logger.error(f"Model building failed: {e}")
        raise

# Train and Evaluate Model (Task 10, 11)
def train_model(train_generator, valid_generator, num_classes):
    try:
        model = build_cnn_model(num_classes)
        
        # Compute class weights for imbalanced datasets
        class_weights = class_weight.compute_class_weight(
            'balanced',
            classes=np.unique(train_generator.classes),
            y=train_generator.classes
        )
        class_weights = dict(enumerate(class_weights))
        logger.info("Computed class weights for training")
        
        history = model.fit(
            train_generator,
            epochs=15,
            validation_data=valid_generator,
            class_weight=class_weights,
            callbacks=[
                tf.keras.callbacks.EarlyStopping(
                    monitor='val_loss',
                    patience=5,
                    restore_best_weights=True
                ),
                tf.keras.callbacks.ModelCheckpoint(
                    'best_model.keras',
                    save_best_only=True,
                    monitor='val_loss'
                )
            ]
        )
        
        # Check write permissions before saving
        if not os.access('.', os.W_OK):
            logger.error("No write permissions in current directory")
            raise PermissionError("Cannot save model files")
        
        model.save('trained_cnn_model.keras')
        logger.info("Model saved as trained_cnn_model.keras")
        return model, history
    except Exception as e:
        logger.error(f"Model training failed: {e}")
        raise

# Evaluate and Visualize Results (Task 8, 9)
def evaluate_model(model, test_generator, history):
    try:
        test_loss, test_accuracy = model.evaluate(test_generator)
        logger.info(f"Test Loss: {test_loss:.4f}, Test Accuracy: {test_accuracy:.4f}")
        
        test_generator.reset()
        y_pred = model.predict(test_generator)
        y_pred_classes = np.argmax(y_pred, axis=1)
        y_true = test_generator.classes
        
        class_names = list(test_generator.class_indices.keys())
        if len(class_names) != test_generator.num_classes:
            logger.warning("Class names length does not match number of classes")
        
        logger.info("\nClassification Report:")
        logger.info(classification_report(y_true, y_pred_classes, target_names=class_names))
        
        cm = confusion_matrix(y_true, y_pred_classes)
        plt.figure(figsize=(12, 10))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=class_names, yticklabels=class_names)
        plt.title('Confusion Matrix')
        plt.xlabel('Predicted')
        plt.ylabel('True')
        plt.xticks(rotation=45)
        plt.yticks(rotation=0)
        plt.savefig('./confusion_matrix.png')
        plt.close()
        logger.info("Saved confusion matrix as confusion_matrix.png")
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
        ax1.plot(history.history['accuracy'], label='Training Accuracy')
        ax1.plot(history.history['val_accuracy'], label='Validation Accuracy')
        ax1.set_title('Model Accuracy')
        ax1.set_xlabel('Epoch')
        ax1.set_ylabel('Accuracy')
        ax1.legend()
        
        ax2.plot(history.history['loss'], label='Training Loss')
        ax2.plot(history.history['val_loss'], label='Validation Loss')
        ax2.set_title('Model Loss')
        ax2.set_xlabel('Epoch')
        ax2.set_ylabel('Loss')
        ax2.legend()
        
        plt.tight_layout()
        plt.savefig('./training_history.png')
        plt.close()
        logger.info("Saved training history as training_history.png")
    except Exception as e:
        logger.error(f"Model evaluation failed: {e}")
        raise

# Main execution
def main():
    try:
        # Explore dataset
        logger.info("Starting main execution")
        class_counts = explore_dataset()
        num_classes = len(class_counts)
        if num_classes <= 0:
            logger.error("No classes found in dataset")
            raise ValueError("No classes found in dataset")
        
        # Save class indices for Django integration
        train_generator, valid_generator, test_generator = create_data_generators(class_counts)
        try:
            with open('./class_indices.txt', 'w') as f:
                json.dump(test_generator.class_indices, f)
            logger.info("Saved class indices as class_indices.txt")
        except Exception as e:
            logger.error(f"Failed to save class_indices.txt: {e}")
            raise
        
        # Train model
        model, history = train_model(train_generator, valid_generator, num_classes)
        
        # Evaluate and visualize
        try:
            evaluate_model(model, test_generator, history)
        except Exception as e:
            logger.warning(f"Evaluation on test set failed: {e}. Falling back to validation set.")
            evaluate_model(model, valid_generator, history)
            logger.info("Evaluation completed using validation set as fallback.")
        
        logger.info("Model training complete. Saved as 'trained_cnn_model.keras' and 'best_model.keras'")
        logger.info("Class indices saved as 'class_indices.txt' for Django integration")
    except Exception as e:
        logger.error(f"Main execution failed: {e}")
        raise

if __name__ == '__main__':
    main()