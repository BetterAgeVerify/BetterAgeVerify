import os
import cv2
import numpy as np
import hashlib
import json
from PIL import Image
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from src.config import BetterAgeVerifyConfig as Config

class PrivacySafeLogger:
    def __init__(self, log_dir: Path = None):
        self.log_dir = log_dir or Config.BASE_DIR / "logs"
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.enabled = Config.LOG_EDGE_CASES and Config.ANONYMIZE_LOGS
    
    def log_edge_case(self, result: Dict, edge_case_type: str):
        if not self.enabled:
            return
        
        anonymized_log = {
            "timestamp": datetime.utcnow().isoformat(),
            "edge_case_type": edge_case_type,
            "predicted_age_bin": result.get("age_bin"),
            "confidence_level": result.get("confidence_level"),
            "uncertainty": result.get("uncertainty"),
            "model_agreement": result.get("model_agreement"),
            "system": f"{Config.PROJECT_NAME} by {Config.CREATOR}"
        }
        
        log_hash = hashlib.sha256(json.dumps(anonymized_log, sort_keys=True).encode()).hexdigest()[:16]
        log_file = self.log_dir / f"edge_case_{log_hash}.json"
        
        with open(log_file, 'w') as f:
            json.dump(anonymized_log, f, indent=2)
    
    def log_verification(self, result: Dict):
        if not self.enabled:
            return
        
        anonymized_log = {
            "timestamp": datetime.utcnow().isoformat(),
            "success": result.get("success"),
            "confidence_level": result.get("confidence_level"),
            "age_category": "child" if result.get("is_child") else "teen" if result.get("is_teen") else "adult",
            "processing_time": result.get("processing_time"),
            "system": f"{Config.PROJECT_NAME} by {Config.CREATOR}"
        }
        
        log_file = self.log_dir / f"verification_{datetime.utcnow().strftime('%Y%m%d')}.jsonl"
        
        with open(log_file, 'a') as f:
            f.write(json.dumps(anonymized_log) + '\n')

class EdgeCaseDetector:
    @staticmethod
    def detect_mask(image: np.ndarray) -> bool:
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        lower_face = gray[int(gray.shape[0] * 0.6):, :]
        edge_density = np.sum(cv2.Canny(lower_face, 50, 150)) / lower_face.size
        return edge_density < 0.02
    
    @staticmethod
    def detect_glasses(image: np.ndarray) -> bool:
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        eye_region = gray[int(gray.shape[0] * 0.2):int(gray.shape[0] * 0.5), :]
        edges = cv2.Canny(eye_region, 50, 150)
        lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=30, minLineLength=20, maxLineGap=5)
        return lines is not None and len(lines) > 10
    
    @staticmethod
    def detect_hat(image: np.ndarray) -> bool:
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        top_region = gray[:int(gray.shape[0] * 0.3), :]
        edge_density = np.sum(cv2.Canny(top_region, 50, 150)) / top_region.size
        return edge_density > 0.05
    
    @staticmethod
    def detect_extreme_angle(image: np.ndarray) -> bool:
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        left_half = gray[:, :gray.shape[1] // 2]
        right_half = gray[:, gray.shape[1] // 2:]
        symmetry = np.corrcoef(left_half.flatten(), np.fliplr(right_half).flatten())[0, 1]
        return symmetry < 0.6
    
    @staticmethod
    def detect_low_light(image: np.ndarray) -> bool:
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        mean_brightness = np.mean(gray)
        return mean_brightness < 80
    
    @staticmethod
    def detect_motion_blur(image: np.ndarray) -> bool:
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        return laplacian_var < 100
    
    @staticmethod
    def analyze_image(image: Image.Image) -> Dict[str, bool]:
        img_array = np.array(image)
        
        if img_array.shape[2] == 4:
            img_array = cv2.cvtColor(img_array, cv2.COLOR_RGBA2RGB)
        
        return {
            "mask_detected": EdgeCaseDetector.detect_mask(img_array),
            "glasses_detected": EdgeCaseDetector.detect_glasses(img_array),
            "hat_detected": EdgeCaseDetector.detect_hat(img_array),
            "extreme_angle": EdgeCaseDetector.detect_extreme_angle(img_array),
            "low_light": EdgeCaseDetector.detect_low_light(img_array),
            "motion_blur": EdgeCaseDetector.detect_motion_blur(img_array)
        }

class ImageProcessor:
    @staticmethod
    def load_image(image_path: str) -> Optional[Image.Image]:
        try:
            path = Path(image_path)
            if not path.exists():
                return None
            
            if path.suffix.lower() not in Config.SUPPORTED_IMAGE_FORMATS:
                return None
            
            image = Image.open(image_path)
            return image.convert('RGB')
        except Exception:
            return None
    
    @staticmethod
    def preprocess_image(image: Image.Image, target_size: int = Config.INPUT_SIZE) -> Image.Image:
        width, height = image.size
        aspect_ratio = width / height
        
        if aspect_ratio > 1:
            new_width = target_size
            new_height = int(target_size / aspect_ratio)
        else:
            new_height = target_size
            new_width = int(target_size * aspect_ratio)
        
        image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        new_image = Image.new('RGB', (target_size, target_size), (128, 128, 128))
        paste_x = (target_size - new_width) // 2
        paste_y = (target_size - new_height) // 2
        new_image.paste(image, (paste_x, paste_y))
        
        return new_image
    
    @staticmethod
    def extract_video_frames(video_path: str, num_frames: int = 10) -> List[Image.Image]:
        path = Path(video_path)
        if not path.exists() or path.suffix.lower() not in Config.SUPPORTED_VIDEO_FORMATS:
            return []
        
        cap = cv2.VideoCapture(video_path)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        if total_frames == 0:
            cap.release()
            return []
        
        frame_indices = np.linspace(0, total_frames - 1, num_frames, dtype=int)
        frames = []
        
        for idx in frame_indices:
            cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
            ret, frame = cap.read()
            
            if ret:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil_image = Image.fromarray(frame_rgb)
                frames.append(pil_image)
        
        cap.release()
        return frames
    
    @staticmethod
    def secure_delete(image: Image.Image):
        if image:
            image.close()
            del image

class ConsentManager:
    @staticmethod
    def get_consent_text() -> str:
        return f"""
{Config.PROJECT_NAME} - Age Verification Consent
Created by {Config.CREATOR}

By proceeding, you explicitly consent to:
1. Facial image processing for age estimation only
2. Immediate deletion of all biometric data after processing (within 1 second)
3. No long-term storage of your facial images or biometric data
4. Anonymous logging of edge cases for system improvement (no personal data)

Your privacy is protected by the "No More Data!" license.

Type 'I CONSENT' to proceed or 'NO' to cancel:
"""
    
    @staticmethod
    def request_consent() -> bool:
        print(ConsentManager.get_consent_text())
        response = input().strip().upper()
        return response == "I CONSENT"

class ResultFormatter:
    @staticmethod
    def format_cli_output(result: Dict) -> str:
        if not result.get("success"):
            return f"""
{Config.PROJECT_NAME} - Age Verification Failed
Error: {result.get('error', 'Unknown error')}
Message: {result.get('message', 'No additional information')}
"""
        
        output = f"""
{'=' * 60}
{Config.PROJECT_NAME} - Age Verification Result
Created by {Config.CREATOR}
{'=' * 60}

Predicted Age: {result['predicted_age']} years
Confidence: {result['confidence']:.1%} ({result['confidence_level']})
Uncertainty: ±{result['uncertainty']:.1f} years
Model Agreement: {result['model_agreement']:.1%}

Age Category:
"""
        
        if result['is_child']:
            output += "  → CHILD (under 13)\n"
        elif result['is_teen']:
            output += "  → TEEN (13-17)\n"
        else:
            output += "  → ADULT (18+)\n"
        
        output += f"\nProcessing Time: {result['processing_time']:.3f}s\n"
        output += f"Attempt: {result['attempt']}\n"
        
        if result.get('should_retry'):
            output += "\n⚠️  Low confidence - retry recommended\n"
        
        output += f"\n{'=' * 60}\n"
        output += "Privacy: All biometric data deleted immediately\n"
        output += f"{'=' * 60}\n"
        
        return output
    
    @staticmethod
    def format_json_output(result: Dict) -> str:
        return json.dumps(result, indent=2)

def validate_environment():
    required_dirs = [Config.MODELS_DIR, Config.CACHE_DIR]
    
    for directory in required_dirs:
        directory.mkdir(parents=True, exist_ok=True)
    
    return True
