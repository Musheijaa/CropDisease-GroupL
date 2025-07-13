import os
import json
import logging
import tempfile
import numpy as np
import tensorflow as tf
from django.conf import settings
from PIL import Image

logger = logging.getLogger(__name__)

class DiseasePredictor:
    def __init__(self):
        """Initialize model, class names, and treatments"""
        self.model = None
        self.class_names = []
        self.input_size = (224, 224)  # Matches config.json input shape
        self.treatments = {
            "Apple___Apple_scab": {
                "treatment": "Apply sulfur or myclobutanil-based fungicides",
                "prevention": "Remove fallen leaves, improve air circulation"
            },
            "Apple___Black_rot": {
                "treatment": "Apply captan or sulfur-based fungicides",
                "prevention": "Prune infected branches, sanitize tools"
            },
            "Apple___Cedar_apple_rust": {
                "treatment": "Apply myclobutanil or sulfur fungicides",
                "prevention": "Remove nearby cedar trees, improve air flow"
            },
            "Apple___healthy": {
                "treatment": "No treatment needed",
                "prevention": "Maintain good growing conditions"
            },
            "Blueberry___healthy": {
                "treatment": "No treatment needed",
                "prevention": "Maintain good growing conditions"
            },
            "Cherry_(including_sour)___Powdery_mildew": {
                "treatment": "Apply sulfur or potassium bicarbonate",
                "prevention": "Improve air circulation, avoid overhead watering"
            },
            "Cherry_(including_sour)___healthy": {
                "treatment": "No treatment needed",
                "prevention": "Maintain good growing conditions"
            },
            "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot": {
                "treatment": "Apply azoxystrobin or propiconazole fungicides",
                "prevention": "Rotate crops, remove crop debris"
            },
            "Corn_(maize)___Common_rust_": {
                "treatment": "Apply triazole or strobilurin fungicides",
                "prevention": "Plant resistant varieties, monitor early"
            },
            "Corn_(maize)___Northern_Leaf_Blight": {
                "treatment": "Apply fungicides like mancozeb",
                "prevention": "Rotate crops, use resistant hybrids"
            },
            "Corn_(maize)___healthy": {
                "treatment": "No treatment needed",
                "prevention": "Maintain good growing conditions"
            },
            "Grape___Black_rot": {
                "treatment": "Apply myclobutanil or captan",
                "prevention": "Remove infected berries, improve air circulation"
            },
            "Grape___Esca_(Black_Measles)": {
                "treatment": "No effective chemical treatment; prune infected vines",
                "prevention": "Use clean planting material, manage irrigation"
            },
            "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)": {
                "treatment": "Apply fungicides like captan",
                "prevention": "Improve canopy ventilation, remove debris"
            },
            "Grape___healthy": {
                "treatment": "No treatment needed",
                "prevention": "Maintain good growing conditions"
            },
            "Orange___Haunglongbing_(Citrus_greening)": {
                "treatment": "No cure; remove infected trees",
                "prevention": "Control psyllid vectors, use certified stock"
            },
            "Peach___Bacterial_spot": {
                "treatment": "Apply copper-based bactericides",
                "prevention": "Plant resistant varieties, avoid overhead irrigation"
            },
            "Peach___healthy": {
                "treatment": "No treatment needed",
                "prevention": "Maintain good growing conditions"
            },
            "Pepper,_bell___Bacterial_spot": {
                "treatment": "Apply copper-based bactericides",
                "prevention": "Use disease-free seeds, rotate crops"
            },
            "Pepper,_bell___healthy": {
                "treatment": "No treatment needed",
                "prevention": "Maintain good growing conditions"
            },
            "Potato___Early_blight": {
                "treatment": "Apply chlorothalonil or mancozeb",
                "prevention": "Rotate crops, remove plant debris"
            },
            "Potato___Late_blight": {
                "treatment": "Apply copper-based fungicide",
                "prevention": "Remove infected plants, improve air circulation"
            },
            "Potato___healthy": {
                "treatment": "No treatment needed",
                "prevention": "Maintain good growing conditions"
            },
            "Raspberry___healthy": {
                "treatment": "No treatment needed",
                "prevention": "Maintain good growing conditions"
            },
            "Soybean___healthy": {
                "treatment": "No treatment needed",
                "prevention": "Maintain good growing conditions"
            },
            "Squash___Powdery_mildew": {
                "treatment": "Apply sulfur or myclobutanil",
                "prevention": "Improve air circulation, avoid overhead watering"
            },
            "Strawberry___Leaf_scorch": {
                "treatment": "Apply captan or sulfur fungicides",
                "prevention": "Remove infected leaves, improve ventilation"
            },
            "Strawberry___healthy": {
                "treatment": "No treatment needed",
                "prevention": "Maintain good growing conditions"
            },
            "Tomato___Bacterial_spot": {
                "treatment": "Apply copper-based bactericides",
                "prevention": "Use disease-free seeds, rotate crops"
            },
            "Tomato___Early_blight": {
                "treatment": "Apply chlorothalonil or mancozeb",
                "prevention": "Rotate crops, remove plant debris"
            },
            "Tomato___Late_blight": {
                "treatment": "Apply copper-based fungicide",
                "prevention": "Remove infected plants, improve air circulation"
            },
            "Tomato___Leaf_Mold": {
                "treatment": "Apply chlorothalonil or copper fungicides",
                "prevention": "Increase air circulation, reduce humidity"
            },
            "Tomato___Septoria_leaf_spot": {
                "treatment": "Apply chlorothalonil or azoxystrobin",
                "prevention": "Remove infected leaves, avoid overhead watering"
            },
            "Tomato___Spider_mites Two-spotted_spider_mite": {
                "treatment": "Apply miticides like abamectin",
                "prevention": "Monitor for pests, maintain plant health"
            },
            "Tomato___Target_Spot": {
                "treatment": "Apply azoxystrobin or chlorothalonil",
                "prevention": "Remove infected leaves, improve air circulation"
            },
            "Tomato___Tomato_Yellow_Leaf_Curl_Virus": {
                "treatment": "No cure; remove infected plants",
                "prevention": "Control whitefly vectors, use resistant varieties"
            },
            "Tomato___Tomato_mosaic_virus": {
                "treatment": "No cure; remove infected plants",
                "prevention": "Use virus-free seeds, sanitize tools"
            },
            "Tomato___healthy": {
                "treatment": "No treatment needed",
                "prevention": "Maintain good growing conditions"
            }
        }
        self.load_class_names()

    def load_class_names(self):
        """Load class names from JSON file"""
        try:
            class_names_path = os.path.join(settings.BASE_DIR, 'ml_models', 'class_indices.txt')
            if not os.path.exists(class_names_path):
                raise FileNotFoundError(f"Class names file not found at: {class_names_path}")
            with open(class_names_path, 'r') as f:
                class_indices = json.load(f)
                self.class_names = [key for key in class_indices.keys()]
            logger.info(f"✅ Loaded {len(self.class_names)} class names")
        except Exception as e:
            logger.error(f"❌ Error loading class names: {str(e)}")
            raise

    def load_model(self):
        """Load the trained model architecture from config.json and weights from model.weights.h5"""
        if self.model is not None:
            return  # Model already loaded
        
        try:
            config_path = os.path.join(
                settings.BASE_DIR, 
                'ml_models', 
                'trained_cnn_model.keras', 
                'config.json'
            )
            weights_path = os.path.join(
                settings.BASE_DIR, 
                'ml_models', 
                'trained_cnn_model.keras', 
                'model.weights.h5'
            )
            
            if not os.path.exists(config_path):
                raise FileNotFoundError(f"Config file not found at: {config_path}")
            if not os.path.exists(weights_path):
                raise FileNotFoundError(f"Weights file not found at: {weights_path}")
            
            # Load model architecture from config.json
            with open(config_path, 'r') as f:
                model_config = json.load(f)
            
            # Rebuild model from config
            self.model = tf.keras.models.model_from_json(json.dumps(model_config))
            
            # Load weights into the model
            self.model.load_weights(weights_path)
            
            logger.info(f"✅ Model architecture loaded from {config_path}")
            logger.info(f"✅ Model weights loaded from {weights_path}")
            logger.info(f"Model input shape: {self.model.input_shape}")
            
            if len(self.model.input_shape) >= 3:
                self.input_size = self.model.input_shape[1:3]
                
        except Exception as e:
            logger.error(f"❌ Error loading model: {str(e)}")
            raise

    def preprocess_image(self, image_path: str) -> np.ndarray:
        """Preprocess the input image for model prediction"""
        try:
            img = Image.open(image_path).convert('RGB')
            img = img.resize(self.input_size, Image.Resampling.LANCZOS)
            img_array = np.array(img) / 255.0
            img_array = np.expand_dims(img_array, axis=0)
            return img_array
        except Exception as e:
            logger.error(f"❌ Error preprocessing image: {str(e)}")
            raise

    def predict_disease(self, image_path: str) -> dict:
        """Make prediction and return results"""
        try:
            # Load model if not already loaded
            if self.model is None:
                self.load_model()
            
            # Preprocess image
            image_array = self.preprocess_image(image_path)
            
            # Get prediction
            predictions = self.model.predict(image_array)
            predicted_index = int(np.argmax(predictions[0]))
            confidence = float(np.max(predictions[0]))
            
            if predicted_index >= len(self.class_names):
                raise ValueError(
                    f"Model predicted invalid class index {predicted_index}. "
                    f"Only {len(self.class_names)} classes available."
                )
            
            predicted_label = self.class_names[predicted_index]
            treatment_info = self.treatments.get(
                predicted_label,
                {
                    "treatment": "Consult agricultural expert",
                    "prevention": "Practice crop rotation"
                }
            )
            
            # Add detailed logging to debug recommendations
            logger.info(f"🔍 Predicted: {predicted_label} ({confidence:.2%} confidence)")
            logger.info(f"🔍 Recommendations for {predicted_label}: {treatment_info}")
            
            return {
                'status': 'success',
                'predicted_disease': predicted_label,
                'confidence': round(confidence * 100, 2),
                'recommendations': treatment_info
            }
            
        except Exception as e:
            logger.error(f"❌ Prediction failed: {str(e)}")
            return {
                'status': 'error',
                'error': str(e)
            }

def get_predictor():
    """Return a singleton instance of DiseasePredictor"""
    global _predictor
    if _predictor is None:
        _predictor = DiseasePredictor()
    return _predictor

_predictor = None