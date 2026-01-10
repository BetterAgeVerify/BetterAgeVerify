import pytest
import numpy as np
import json
from PIL import Image
from pathlib import Path
import sys
import tempfile
import shutil

sys.path.append(str(Path(__file__).parent.parent))

from src.utils import (
    PrivacySafeLogger,
    EdgeCaseDetector,
    ImageProcessor,
    ConsentManager,
    ResultFormatter,
    validate_environment
)
from src.config import BetterAgeVerifyConfig as Config

class TestPrivacySafeLogger:
    
    @pytest.fixture
    def temp_log_dir(self):
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def logger(self, temp_log_dir):
        return PrivacySafeLogger(log_dir=temp_log_dir)
    
    def test_logger_initialization(self, logger):
        assert logger is not None
        assert logger.log_dir.exists()
        assert logger.enabled == (Config.LOG_EDGE_CASES and Config.ANONYMIZE_LOGS)
    
    def test_log_edge_case_creates_file(self, logger, temp_log_dir):
        if not logger.enabled:
            pytest.skip("Logging disabled in config")
        
        result = {
            "age_bin": 3,
            "confidence_level": "medium",
            "uncertainty": 3.5,
            "model_agreement": 0.85
        }
        
        logger.log_edge_case(result, "mask_detected")
        
        log_files = list(temp_log_dir.glob("edge_case_*.json"))
        assert len(log_files) > 0
    
    def test_log_edge_case_anonymization(self, logger, temp_log_dir):
        if not logger.enabled:
            pytest.skip("Logging disabled in config")
        
        result = {
            "predicted_age": 25.5,
            "age_bin": 4,
            "confidence_level": "high",
            "uncertainty": 2.1,
            "model_agreement": 0.92
        }
        
        logger.log_edge_case(result, "glasses_detected")
        
        log_files = list(temp_log_dir.glob("edge_case_*.json"))
        assert len(log_files) > 0
        
        with open(log_files[0], 'r') as f:
            log_data = json.load(f)
        
        assert "predicted_age" not in log_data
        assert "age_bin" in log_data
        assert "timestamp" in log_data
        assert "system" in log_data
        assert Config.PROJECT_NAME in log_data["system"]
        assert Config.CREATOR in log_data["system"]
    
    def test_log_verification_creates_file(self, logger, temp_log_dir):
        if not logger.enabled:
            pytest.skip("Logging disabled in config")
        
        result = {
            "success": True,
            "confidence_level": "high",
            "is_child": False,
            "is_teen": True,
            "is_adult": False,
            "processing_time": 0.234
        }
        
        logger.log_verification(result)
        
        log_files = list(temp_log_dir.glob("verification_*.jsonl"))
        assert len(log_files) > 0
    
    def test_log_verification_anonymization(self, logger, temp_log_dir):
        if not logger.enabled:
            pytest.skip("Logging disabled in config")
        
        result = {
            "success": True,
            "predicted_age": 16.5,
            "confidence_level": "medium",
            "is_child": False,
            "is_teen": True,
            "is_adult": False,
            "processing_time": 0.567
        }
        
        logger.log_verification(result)
        
        log_files = list(temp_log_dir.glob("verification_*.jsonl"))
        with open(log_files[0], 'r') as f:
            log_line = f.readline()
            log_data = json.loads(log_line)
        
        assert "predicted_age" not in log_data
        assert "age_category" in log_data
        assert log_data["age_category"] == "teen"

class TestEdgeCaseDetector:
    
    @pytest.fixture
    def sample_image(self):
        return Image.new('RGB', (640, 480), color=(128, 128, 128))
    
    def test_analyze_image_returns_dict(self, sample_image):
        result = EdgeCaseDetector.analyze_image(sample_image)
        
        assert isinstance(result, dict)
        assert "mask_detected" in result
        assert "glasses_detected" in result
        assert "hat_detected" in result
        assert "extreme_angle" in result
        assert "low_light" in result
        assert "motion_blur" in result
    
    def test_analyze_image_all_boolean(self, sample_image):
        result = EdgeCaseDetector.analyze_image(sample_image)
        
        for key, value in result.items():
            assert isinstance(value, (bool, np.bool_))
    
    def test_detect_low_light_dark_image(self):
        dark_image = Image.new('RGB', (640, 480), color=(20, 20, 20))
        img_array = np.array(dark_image)
        
        is_low_light = EdgeCaseDetector.detect_low_light(img_array)
        assert is_low_light == True
    
    def test_detect_low_light_bright_image(self):
        bright_image = Image.new('RGB', (640, 480), color=(200, 200, 200))
        img_array = np.array(bright_image)
        
        is_low_light = EdgeCaseDetector.detect_low_light(img_array)
        assert is_low_light == False
    
    def test_rgba_image_handling(self):
        rgba_image = Image.new('RGBA', (640, 480), color=(128, 128, 128, 255))
        result = EdgeCaseDetector.analyze_image(rgba_image)
        
        assert isinstance(result, dict)
        assert len(result) > 0

class TestImageProcessor:
    
    @pytest.fixture
    def temp_image_dir(self):
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    def test_load_image_valid_jpg(self, temp_image_dir):
        image_path = temp_image_dir / "test.jpg"
        img = Image.new('RGB', (640, 480), color=(128, 128, 128))
        img.save(image_path)
        
        loaded = ImageProcessor.load_image(str(image_path))
        
        assert loaded is not None
        assert loaded.mode == 'RGB'
    
    def test_load_image_valid_png(self, temp_image_dir):
        image_path = temp_image_dir / "test.png"
        img = Image.new('RGB', (640, 480), color=(128, 128, 128))
        img.save(image_path)
        
        loaded = ImageProcessor.load_image(str(image_path))
        
        assert loaded is not None
        assert loaded.mode == 'RGB'
    
    def test_load_image_nonexistent(self):
        loaded = ImageProcessor.load_image("nonexistent_file.jpg")
        assert loaded is None
    
    def test_load_image_unsupported_format(self, temp_image_dir):
        file_path = temp_image_dir / "test.txt"
        file_path.write_text("not an image")
        
        loaded = ImageProcessor.load_image(str(file_path))
        assert loaded is None
    
    def test_preprocess_image_landscape(self):
        img = Image.new('RGB', (800, 600))
        processed = ImageProcessor.preprocess_image(img, target_size=224)
        
        assert processed.size == (224, 224)
        assert processed.mode == 'RGB'
    
    def test_preprocess_image_portrait(self):
        img = Image.new('RGB', (600, 800))
        processed = ImageProcessor.preprocess_image(img, target_size=224)
        
        assert processed.size == (224, 224)
        assert processed.mode == 'RGB'
    
    def test_preprocess_image_square(self):
        img = Image.new('RGB', (500, 500))
        processed = ImageProcessor.preprocess_image(img, target_size=224)
        
        assert processed.size == (224, 224)
        assert processed.mode == 'RGB'
    
    def test_secure_delete(self):
        img = Image.new('RGB', (640, 480))
        ImageProcessor.secure_delete(img)
        
        with pytest.raises(ValueError):
            img.size

class TestConsentManager:
    
    def test_get_consent_text_contains_branding(self):
        text = ConsentManager.get_consent_text()
        
        assert Config.PROJECT_NAME in text
        assert Config.CREATOR in text
        assert "I CONSENT" in text
    
    def test_get_consent_text_contains_privacy_info(self):
        text = ConsentManager.get_consent_text()
        
        assert "delete" in text.lower() or "deletion" in text.lower()
        assert "biometric" in text.lower()
        assert "consent" in text.lower()

class TestResultFormatter:
    
    @pytest.fixture
    def success_result(self):
        return {
            "success": True,
            "predicted_age": 25.5,
            "confidence": 0.876,
            "confidence_level": "high",
            "uncertainty": 3.2,
            "model_agreement": 0.91,
            "age_bin": 4,
            "is_child": False,
            "is_teen": False,
            "is_adult": True,
            "processing_time": 0.234,
            "attempt": 1,
            "should_retry": False
        }
    
    @pytest.fixture
    def failure_result(self):
        return {
            "success": False,
            "error": "no_face_detected",
            "message": "No face detected in image"
        }
    
    def test_format_cli_output_success(self, success_result):
        output = ResultFormatter.format_cli_output(success_result)
        
        assert Config.PROJECT_NAME in output
        assert Config.CREATOR in output
        assert "25.5" in output
        assert "87.6%" in output or "87%" in output
        assert "ADULT" in output
        assert "Privacy" in output
    
    def test_format_cli_output_failure(self, failure_result):
        output = ResultFormatter.format_cli_output(failure_result)
        
        assert "Failed" in output
        assert "no_face_detected" in output
    
    def test_format_json_output(self, success_result):
        output = ResultFormatter.format_json_output(success_result)
        
        parsed = json.loads(output)
        assert parsed["predicted_age"] == 25.5
        assert parsed["success"] == True
    
    def test_format_cli_output_child(self):
        result = {
            "success": True,
            "predicted_age": 10.5,
            "confidence": 0.92,
            "confidence_level": "high",
            "uncertainty": 2.1,
            "model_agreement": 0.95,
            "is_child": True,
            "is_teen": False,
            "is_adult": False,
            "processing_time": 0.156,
            "attempt": 1,
            "should_retry": False
        }
        
        output = ResultFormatter.format_cli_output(result)
        assert "CHILD" in output
    
    def test_format_cli_output_teen(self):
        result = {
            "success": True,
            "predicted_age": 15.8,
            "confidence": 0.85,
            "confidence_level": "high",
            "uncertainty": 2.8,
            "model_agreement": 0.88,
            "is_child": False,
            "is_teen": True,
            "is_adult": False,
            "processing_time": 0.198,
            "attempt": 1,
            "should_retry": False
        }
        
        output = ResultFormatter.format_cli_output(result)
        assert "TEEN" in output
    
    def test_format_cli_output_retry_warning(self):
        result = {
            "success": True,
            "predicted_age": 18.5,
            "confidence": 0.62,
            "confidence_level": "low",
            "uncertainty": 5.4,
            "model_agreement": 0.71,
            "is_child": False,
            "is_teen": False,
            "is_adult": True,
            "processing_time": 0.245,
            "attempt": 1,
            "should_retry": True
        }
        
        output = ResultFormatter.format_cli_output(result)
        assert "retry" in output.lower() or "Retry" in output

class TestValidateEnvironment:
    
    def test_validate_environment_creates_directories(self):
        result = validate_environment()
        
        assert result == True
        assert Config.MODELS_DIR.exists()
        assert Config.CACHE_DIR.exists()
    
    def test_validate_environment_idempotent(self):
        result1 = validate_environment()
        result2 = validate_environment()
        
        assert result1 == True
        assert result2 == True

class TestPrivacyCompliance:
    
    def test_privacy_mode_enabled(self):
        assert Config.PRIVACY_MODE == True
    
    def test_deletion_timeout_reasonable(self):
        assert Config.DELETE_DATA_TIMEOUT <= 1.0
        assert Config.DELETE_DATA_TIMEOUT > 0
    
    def test_anonymized_logging_enabled(self):
        assert Config.ANONYMIZE_LOGS == True
    
    def test_offline_mode_supported(self):
        assert Config.OFFLINE_MODE == True

class TestBrandingConsistency:
    
    def test_project_name_in_config(self):
        assert Config.PROJECT_NAME == "BetterAgeVerify"
    
    def test_creator_in_config(self):
        assert Config.CREATOR == "luvaary"
    
    def test_consent_text_branding(self):
        text = ConsentManager.get_consent_text()
        assert "BetterAgeVerify" in text
        assert "luvaary" in text
    
    def test_logger_includes_branding(self, temp_log_dir=None):
        if temp_log_dir is None:
            temp_log_dir = Path(tempfile.mkdtemp())
        
        logger = PrivacySafeLogger(log_dir=temp_log_dir)
        
        if logger.enabled:
            result = {
                "age_bin": 3,
                "confidence_level": "high",
                "uncertainty": 2.5,
                "model_agreement": 0.90
            }
            
            logger.log_edge_case(result, "test_case")
            
            log_files = list(temp_log_dir.glob("edge_case_*.json"))
            if log_files:
                with open(log_files[0], 'r') as f:
                    log_data = json.load(f)
                
                assert "BetterAgeVerify" in log_data.get("system", "")
                assert "luvaary" in log_data.get("system", "")
        
        if temp_log_dir != Config.BASE_DIR / "logs":
            shutil.rmtree(temp_log_dir)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
