import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import transforms
import timm
import numpy as np
from facenet_pytorch import MTCNN
from PIL import Image
import time
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from src.config import BetterAgeVerifyConfig as Config

class WideResNetAge(nn.Module):
    def __init__(self, num_classes=101):
        super(WideResNetAge, self).__init__()
        self.backbone = timm.create_model('wide_resnet50_2', pretrained=True, num_classes=0)
        self.regression_head = nn.Linear(2048, 1)
        self.classification_head = nn.Linear(2048, num_classes)
    
    def forward(self, x):
        features = self.backbone(x)
        age_regression = self.regression_head(features)
        age_classification = self.classification_head(features)
        return age_regression, age_classification

class DEXAge(nn.Module):
    def __init__(self, num_classes=101):
        super(DEXAge, self).__init__()
        self.backbone = timm.create_model('vgg16', pretrained=True, num_classes=0)
        self.regression_head = nn.Linear(4096, 1)
        self.classification_head = nn.Linear(4096, num_classes)
    
    def forward(self, x):
        features = self.backbone(x)
        age_regression = self.regression_head(features)
        age_classification = self.classification_head(features)
        return age_regression, age_classification

class ViTAge(nn.Module):
    def __init__(self, num_classes=101):
        super(ViTAge, self).__init__()
        self.backbone = timm.create_model('vit_base_patch16_224', pretrained=True, num_classes=0)
        self.regression_head = nn.Linear(768, 1)
        self.classification_head = nn.Linear(768, num_classes)
    
    def forward(self, x):
        features = self.backbone(x)
        age_regression = self.regression_head(features)
        age_classification = self.classification_head(features)
        return age_regression, age_classification

class BetterAgeVerifyEstimator:
    def __init__(self, config: Config = Config):
        self.config = config
        self.device = torch.device(config.DEVICE)
        
        self.face_detector = MTCNN(
            keep_all=False,
            device=self.device,
            min_face_size=config.MIN_FACE_SIZE,
            thresholds=[0.6, 0.7, config.FACE_DETECTION_CONFIDENCE]
        )
        
        self.models = self._initialize_models()
        
        self.transform = transforms.Compose([
            transforms.Resize((config.INPUT_SIZE, config.INPUT_SIZE)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        
        self.augmentation = transforms.Compose([
            transforms.RandomHorizontalFlip(p=0.5),
            transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.1),
            transforms.RandomRotation(degrees=10)
        ])
    
    def _initialize_models(self) -> Dict[str, nn.Module]:
        models = {}
        
        if "wideresnet" in self.config.ENSEMBLE_MODELS:
            models["wideresnet"] = WideResNetAge().to(self.device)
            models["wideresnet"].eval()
        
        if "dex" in self.config.ENSEMBLE_MODELS:
            models["dex"] = DEXAge().to(self.device)
            models["dex"].eval()
        
        if "vit" in self.config.ENSEMBLE_MODELS:
            models["vit"] = ViTAge().to(self.device)
            models["vit"].eval()
        
        return models
    
    def detect_face(self, image: Image.Image) -> Optional[Image.Image]:
        image_array = np.array(image)
        
        boxes, probs = self.face_detector.detect(image_array)
        
        if boxes is None or len(boxes) == 0:
            return None
        
        box = boxes[0]
        x1, y1, x2, y2 = [int(coord) for coord in box]
        
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(image.width, x2), min(image.height, y2)
        
        face = image.crop((x1, y1, x2, y2))
        return face
    
    def predict_single_model(self, model_name: str, image_tensor: torch.Tensor) -> Tuple[float, np.ndarray, float]:
        model = self.models[model_name]
        
        with torch.no_grad():
            age_regression, age_classification = model(image_tensor)
        
        predicted_age = float(age_regression.squeeze().cpu().numpy())
        predicted_age = np.clip(predicted_age, self.config.AGE_MIN, self.config.AGE_MAX)
        
        age_probs = F.softmax(age_classification, dim=1).squeeze().cpu().numpy()
        
        expected_age = np.sum(age_probs * np.arange(len(age_probs)))
        variance = np.sum(age_probs * (np.arange(len(age_probs)) - expected_age) ** 2)
        uncertainty = float(np.sqrt(variance))
        
        return predicted_age, age_probs, uncertainty
    
    def ensemble_predict(self, image_tensor: torch.Tensor) -> Dict:
        predictions = {}
        
        for model_name in self.config.ENSEMBLE_MODELS:
            if model_name in self.models:
                age, probs, uncertainty = self.predict_single_model(model_name, image_tensor)
                predictions[model_name] = {
                    "age": age,
                    "probs": probs,
                    "uncertainty": uncertainty
                }
        
        weighted_age = sum(
            predictions[name]["age"] * self.config.ENSEMBLE_WEIGHTS.get(name, 0)
            for name in predictions
        )
        
        weighted_uncertainty = sum(
            predictions[name]["uncertainty"] * self.config.ENSEMBLE_WEIGHTS.get(name, 0)
            for name in predictions
        )
        
        age_stdev = np.std([p["age"] for p in predictions.values()])
        
        confidence = 1.0 / (1.0 + weighted_uncertainty + age_stdev)
        confidence = np.clip(confidence, 0.0, 1.0)
        
        return {
            "predicted_age": weighted_age,
            "confidence": confidence,
            "uncertainty": weighted_uncertainty,
            "model_agreement": 1.0 - (age_stdev / max(weighted_age, 1.0)),
            "individual_predictions": predictions
        }
    
    def estimate_age(self, image: Image.Image, attempt: int = 1) -> Dict:
        start_time = time.time()
        
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        face = self.detect_face(image)
        
        if face is None:
            return {
                "success": False,
                "error": "no_face_detected",
                "message": "No face detected in image",
                "processing_time": time.time() - start_time
            }
        
        if self.config.AUGMENTATION_ENABLED and attempt == 1:
            predictions_list = []
            
            for _ in range(self.config.AUGMENTATION_ITERATIONS):
                augmented_face = self.augmentation(face)
                image_tensor = self.transform(augmented_face).unsqueeze(0).to(self.device)
                pred = self.ensemble_predict(image_tensor)
                predictions_list.append(pred)
            
            final_age = np.mean([p["predicted_age"] for p in predictions_list])
            final_confidence = np.mean([p["confidence"] for p in predictions_list])
            final_uncertainty = np.mean([p["uncertainty"] for p in predictions_list])
            model_agreement = np.mean([p["model_agreement"] for p in predictions_list])
        else:
            image_tensor = self.transform(face).unsqueeze(0).to(self.device)
            prediction = self.ensemble_predict(image_tensor)
            final_age = prediction["predicted_age"]
            final_confidence = prediction["confidence"]
            final_uncertainty = prediction["uncertainty"]
            model_agreement = prediction["model_agreement"]
        
        age_bin = self.config.get_age_bin(final_age)
        confidence_level = self.config.get_confidence_level(final_confidence)
        
        should_retry = self.config.should_retry(final_confidence, attempt)
        
        processing_time = time.time() - start_time
        
        result = {
            "success": True,
            "predicted_age": round(final_age, 1),
            "age_bin": age_bin,
            "confidence": round(final_confidence, 3),
            "confidence_level": confidence_level,
            "uncertainty": round(final_uncertainty, 2),
            "model_agreement": round(model_agreement, 3),
            "is_adult": self.config.is_adult(final_age),
            "is_teen": self.config.is_teen(final_age),
            "is_child": self.config.is_child(final_age),
            "should_retry": should_retry,
            "attempt": attempt,
            "processing_time": round(processing_time, 3),
            "timestamp": time.time(),
            "system": f"{self.config.PROJECT_NAME} by {self.config.CREATOR}"
        }
        
        self._delete_biometric_data(image, face, image_tensor)
        
        return result
    
    def _delete_biometric_data(self, *data_objects):
        deletion_start = time.time()
        
        for obj in data_objects:
            if isinstance(obj, torch.Tensor):
                obj.cpu()
                del obj
            elif isinstance(obj, Image.Image):
                obj.close()
            else:
                del obj
        
        torch.cuda.empty_cache() if torch.cuda.is_available() else None
        
        deletion_time = time.time() - deletion_start
        
        if deletion_time > self.config.DELETE_DATA_TIMEOUT:
            raise RuntimeError(f"Data deletion exceeded timeout: {deletion_time}s > {self.config.DELETE_DATA_TIMEOUT}s")
    
    def verify_age_threshold(self, image: Image.Image, threshold_age: int = 13) -> Dict:
        result = self.estimate_age(image)
        
        if not result["success"]:
            return result
        
        result["passes_threshold"] = result["predicted_age"] >= threshold_age
        result["threshold_age"] = threshold_age
        
        return result
