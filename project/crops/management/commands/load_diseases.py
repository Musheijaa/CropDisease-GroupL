from django.core.management.base import BaseCommand
from crops.models import Disease, CropType


class Command(BaseCommand):
    help = 'Loads diseases into the database'

    def handle(self, *args, **kwargs):
        diseases_data = {
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

        for name, data in diseases_data.items():
            try:
                # Extract crop name before '___'
                crop_raw = name.split("___")[0].strip()
                crop_name = crop_raw.replace("(", "").replace(")", "").replace(",", "").replace("_", " ")

                # Get or create CropType
                crop_type, _ = CropType.objects.get_or_create(name=crop_name)

                # Get or create Disease with crop_type
                disease, created = Disease.objects.get_or_create(name=name, crop_type=crop_type)

                # Update treatment and prevention
                disease.treatment = data['treatment']
                disease.prevention = data['prevention']
                disease.save()

                if created:
                    self.stdout.write(self.style.SUCCESS(f"✅ Created: {name} (Crop: {crop_name})"))
                else:
                    self.stdout.write(self.style.WARNING(f"ℹ️  Already exists: {name} (Crop: {crop_name})"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ Failed to add {name}: {e}"))
