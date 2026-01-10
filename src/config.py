import torch
from pathlib import Path

class BetterAgeVerifyConfig:
    PROJECT_NAME = "BetterAgeVerify"
    CREATOR = "luvaary"
    VERSION = "1.0.0"
    
    BASE_DIR = Path(__file__).parent.parent
    MODELS_DIR = BASE_DIR / "models"
    CACHE_DIR = BASE_DIR / ".cache"
    
    DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
    
    INPUT_SIZE = 224
    BATCH_SIZE = 1
    
    ENSEMBLE_MODELS = ["wideresnet", "dex", "vit"]
    
    WIDERESNET_WEIGHTS = "wideresnet_age.pth"
    DEX_WEIGHTS = "dex_age.pth"
    VIT_WEIGHTS = "vit_age_estimation.pth"
    
    AGE_MIN = 0
    AGE_MAX = 100
    AGE_BINS = [0, 2, 6, 12, 18, 25, 35, 45, 55, 65, 100]
    
    CONFIDENCE_THRESHOLD_HIGH = 0.85
    CONFIDENCE_THRESHOLD_MEDIUM = 0.70
    CONFIDENCE_THRESHOLD_LOW = 0.50
    
    UNCERTAINTY_THRESHOLD = 5.0
    
    MAX_RETRY_ATTEMPTS = 3
    
    ENSEMBLE_WEIGHTS = {
        "wideresnet": 0.40,
        "dex": 0.35,
        "vit": 0.25
    }
    
    FACE_DETECTION_CONFIDENCE = 0.90
    MIN_FACE_SIZE = 64
    
    AUGMENTATION_ENABLED = True
    AUGMENTATION_ITERATIONS = 5
    
    DELETE_DATA_TIMEOUT = 1.0
    
    PRIVACY_MODE = True
    OFFLINE_MODE = True
    LOG_EDGE_CASES = True
    ANONYMIZE_LOGS = True
    
    FALLBACK_VERIFICATION_ENABLED = True
    ID_VERIFICATION_ENABLED = True
    PARENTAL_APPROVAL_ENABLED = True
    
    DEMO_SAVE_RESULTS = False
    DEMO_SHOW_CONFIDENCE = True
    DEMO_SHOW_AGE_BIN = True
    
    AGE_THRESHOLDS = {
        "child": 13,
        "teen": 18,
        "adult": 21
    }
    
    EDGE_CASE_CONDITIONS = [
        "mask_detected",
        "glasses_detected",
        "hat_detected",
        "extreme_angle",
        "low_light",
        "multiple_faces",
        "partial_occlusion",
        "motion_blur"
    ]
    
    SUPPORTED_IMAGE_FORMATS = [".jpg", ".jpeg", ".png", ".bmp", ".webp"]
    SUPPORTED_VIDEO_FORMATS = [".mp4", ".avi", ".mov", ".mkv"]
    
    @classmethod
    def get_age_bin(cls, age):
        for i in range(len(cls.AGE_BINS) - 1):
            if cls.AGE_BINS[i] <= age < cls.AGE_BINS[i + 1]:
                return i
        return len(cls.AGE_BINS) - 2
    
    @classmethod
    def get_confidence_level(cls, confidence):
        if confidence >= cls.CONFIDENCE_THRESHOLD_HIGH:
            return "high"
        elif confidence >= cls.CONFIDENCE_THRESHOLD_MEDIUM:
            return "medium"
        elif confidence >= cls.CONFIDENCE_THRESHOLD_LOW:
            return "low"
        else:
            return "very_low"
    
    @classmethod
    def should_retry(cls, confidence, attempt):
        return confidence < cls.CONFIDENCE_THRESHOLD_MEDIUM and attempt < cls.MAX_RETRY_ATTEMPTS
    
    @classmethod
    def is_adult(cls, age):
        return age >= cls.AGE_THRESHOLDS["adult"]
    
    @classmethod
    def is_teen(cls, age):
        return cls.AGE_THRESHOLDS["child"] <= age < cls.AGE_THRESHOLDS["adult"]
    
    @classmethod
    def is_child(cls, age):
        return age < cls.AGE_THRESHOLDS["child"]
