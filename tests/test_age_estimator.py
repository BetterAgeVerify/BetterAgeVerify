import pytest
import torch
import numpy as np
from PIL import Image
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))

from src.age_estimator import BetterAgeVerifyEstimator, WideResNetAge, DEXAge, ViTAge
from src.config import BetterAgeVerifyConfig as Config

class TestModelArchitectures:
    
    def test_wideresnet_initialization(self):
        model = WideResNetAge(num_classes=101)
        assert model is not None
        assert hasattr(model, 'regression_head')
        assert hasattr(model, 'classification_head')
    
    def test_dex_initialization(self):
        model = DEXAge(num_classes=101)
        assert model is not None
        assert hasattr(model, 'regression_head')
        assert hasattr(model, 'classification_head')
    
    def test_vit_initialization(self):
        model = ViTAge(num_classes=101)
        assert model is not None
        assert hasattr(model, 'regression_head')
        assert hasattr(model, 'classification_head')
    
    def test_wideresnet_forward_pass(self):
        model = WideResNetAge(num_classes=101)
        model.eval()
        
        dummy_input = torch.randn(1, 3, Config.INPUT_SIZE, Config.INPUT_SIZE)
        
        with torch.no_grad():
            age_reg, age_cls = model(dummy_input)
        
        assert age_reg.shape == (1, 1)
        assert age_cls.shape == (1, 101)
    
    def test_dex_forward_pass(self):
        model = DEXAge(num_classes=101)
        model.eval()
        
        dummy_input = torch.randn(1, 3, Config.INPUT_SIZE, Config.INPUT_SIZE)
        
        with torch.no_grad():
            age_reg, age_cls = model(dummy_input)
        
        assert age_reg.shape == (1, 1)
        assert age_cls.shape == (1, 101)
    
    def test_vit_forward_pass(self):
        model = ViTAge(num_classes=101)
        model.eval()
        
        dummy_input = torch.randn(1, 3, Config.INPUT_SIZE, Config.INPUT_SIZE)
        
        with torch.no_grad():
            age_reg, age_cls = model(dummy_input)
        
        assert age_reg.shape == (1, 1)
        assert age_cls.shape == (1, 101)

class TestBetterAgeVerifyEstimator:
    
    @pytest.fixture
    def estimator(self):
        return BetterAgeVerifyEstimator()
    
    @pytest.fixture
    def sample_image(self):
        img = Image.new('RGB', (640, 480), color=(128, 128, 128))
        return img
    
    def test_estimator_initialization(self, estimator):
        assert estimator is not None
        assert hasattr(estimator, 'models')
        assert hasattr(estimator, 'face_detector')
        assert hasattr(estimator, 'transform')
        assert len(estimator.models) > 0
    
    def test_models_loaded(self, estimator):
        assert 'wideresnet' in estimator.models
        assert 'dex' in estimator.models
        assert 'vit' in estimator.models
    
    def test_device_configuration(self, estimator):
        assert estimator.device.type in ['cpu', 'cuda']
    
    def test_predict_single_model_output_format(self, estimator):
        dummy_tensor = torch.randn(1, 3, Config.INPUT_SIZE, Config.INPUT_SIZE).to(estimator.device)
        
        age, probs, uncertainty = estimator.predict_single_model('wideresnet', dummy_tensor)
        
        assert isinstance(age, float)
        assert isinstance(probs, np.ndarray)
        assert isinstance(uncertainty, float)
        assert Config.AGE_MIN <= age <= Config.AGE_MAX
        assert len(probs) == 101
        assert np.isclose(np.sum(probs), 1.0, atol=0.01)
    
    def test_ensemble_predict_output_format(self, estimator):
        dummy_tensor = torch.randn(1, 3, Config.INPUT_SIZE, Config.INPUT_SIZE).to(estimator.device)
        
        result = estimator.ensemble_predict(dummy_tensor)
        
        assert 'predicted_age' in result
        assert 'confidence' in result
        assert 'uncertainty' in result
        assert 'model_agreement' in result
        assert 'individual_predictions' in result
        
        assert isinstance(result['predicted_age'], (int, float))
        assert 0.0 <= result['confidence'] <= 1.0
        assert result['uncertainty'] >= 0
        assert 0.0 <= result['model_agreement'] <= 1.0
    
    def test_estimate_age_result_structure(self, estimator, sample_image):
        result = estimator.estimate_age(sample_image)
        
        assert 'success' in result
        assert 'processing_time' in result
        
        if result['success']:
            assert 'predicted_age' in result
            assert 'confidence' in result
            assert 'confidence_level' in result
            assert 'uncertainty' in result
            assert 'age_bin' in result
            assert 'is_adult' in result
            assert 'is_teen' in result
            assert 'is_child' in result
            assert 'timestamp' in result
            assert 'system' in result
    
    def test_age_bin_calculation(self):
        assert Config.get_age_bin(5) == 1
        assert Config.get_age_bin(15) == 3
        assert Config.get_age_bin(25) == 4
        assert Config.get_age_bin(50) == 6
    
    def test_confidence_level_calculation(self):
        assert Config.get_confidence_level(0.90) == "high"
        assert Config.get_confidence_level(0.75) == "medium"
        assert Config.get_confidence_level(0.60) == "low"
        assert Config.get_confidence_level(0.40) == "very_low"
    
    def test_age_category_checks(self):
        assert Config.is_child(10) == True
        assert Config.is_child(15) == False
        
        assert Config.is_teen(15) == True
        assert Config.is_teen(10) == False
        assert Config.is_teen(20) == False
        
        assert Config.is_adult(25) == True
        assert Config.is_adult(15) == False
    
    def test_should_retry_logic(self):
        assert Config.should_retry(0.60, 1) == True
        assert Config.should_retry(0.90, 1) == False
        assert Config.should_retry(0.60, 5) == False
    
    def test_verify_age_threshold(self, estimator, sample_image):
        result = estimator.verify_age_threshold(sample_image, threshold_age=13)
        
        if result.get('success'):
            assert 'passes_threshold' in result
            assert 'threshold_age' in result
            assert result['threshold_age'] == 13
            assert isinstance(result['passes_threshold'], bool)
    
    def test_data_deletion_timeout(self, estimator):
        with pytest.raises(RuntimeError):
            test_objects = [torch.randn(1000, 1000, 1000) for _ in range(100)]
            estimator._delete_biometric_data(*test_objects)
    
    def test_ensemble_weights_sum(self):
        total_weight = sum(Config.ENSEMBLE_WEIGHTS.values())
        assert np.isclose(total_weight, 1.0, atol=0.01)
    
    def test_privacy_settings(self):
        assert Config.PRIVACY_MODE == True
        assert Config.DELETE_DATA_TIMEOUT == 1.0
        assert Config.ANONYMIZE_LOGS == True

class TestEdgeCases:
    
    @pytest.fixture
    def estimator(self):
        return BetterAgeVerifyEstimator()
    
    def test_no_face_detected(self, estimator):
        blank_image = Image.new('RGB', (640, 480), color=(0, 0, 0))
        result = estimator.estimate_age(blank_image)
        
        assert result['success'] == False
        assert result['error'] == 'no_face_detected'
    
    def test_grayscale_image_conversion(self, estimator):
        gray_image = Image.new('L', (640, 480), color=128)
        result = estimator.estimate_age(gray_image)
        
        assert 'success' in result
    
    def test_rgba_image_conversion(self, estimator):
        rgba_image = Image.new('RGBA', (640, 480), color=(128, 128, 128, 255))
        result = estimator.estimate_age(rgba_image)
        
        assert 'success' in result
    
    def test_small_image_handling(self, estimator):
        small_image = Image.new('RGB', (64, 64), color=(128, 128, 128))
        result = estimator.estimate_age(small_image)
        
        assert 'success' in result
    
    def test_large_image_handling(self, estimator):
        large_image = Image.new('RGB', (4000, 3000), color=(128, 128, 128))
        result = estimator.estimate_age(large_image)
        
        assert 'success' in result

class TestSystemMetadata:
    
    def test_project_branding(self):
        assert Config.PROJECT_NAME == "BetterAgeVerify"
        assert Config.CREATOR == "luvaary"
        assert Config.VERSION == "1.0.0"
    
    def test_result_includes_branding(self):
        estimator = BetterAgeVerifyEstimator()
        sample_image = Image.new('RGB', (640, 480), color=(128, 128, 128))
        result = estimator.estimate_age(sample_image)
        
        if result.get('success'):
            assert Config.PROJECT_NAME in result['system']
            assert Config.CREATOR in result['system']

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
