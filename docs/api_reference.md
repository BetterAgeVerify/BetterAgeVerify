# BetterAgeVerify API Reference

**Created by luvaary**

Last Updated: January 11, 2026

---

## Overview

This document provides complete API reference documentation for BetterAgeVerify's Python API. All APIs maintain strict privacy compliance with the "No More Data!" license.

---

## Table of Contents

1. [Core Estimator API](#core-estimator-api)
2. [Configuration API](#configuration-api)
3. [Utility Functions](#utility-functions)
4. [Data Models](#data-models)
5. [Exception Handling](#exception-handling)
6. [Usage Examples](#usage-examples)

---

## Core Estimator API

### BetterAgeVerifyEstimator

Main class for age estimation with ensemble AI models.

```python
from src.age_estimator import BetterAgeVerifyEstimator
```

#### Constructor

```python
BetterAgeVerifyEstimator(config: BetterAgeVerifyConfig = Config)
```

**Parameters:**
- `config` (BetterAgeVerifyConfig, optional): Configuration object. Defaults to global Config.

**Returns:**
- Initialized estimator with loaded AI models

**Raises:**
- `RuntimeError`: If models fail to load
- `ImportError`: If required dependencies missing

**Example:**
```python
estimator = BetterAgeVerifyEstimator()
```

---

#### estimate_age()

Estimate age from a facial image with immediate biometric data deletion.

```python
estimate_age(image: Image.Image, attempt: int = 1) -> Dict
```

**Parameters:**
- `image` (PIL.Image.Image): RGB image containing a face
- `attempt` (int, optional): Attempt number for retry logic. Defaults to 1.

**Returns:**
- `Dict`: Result dictionary containing:
  - `success` (bool): Whether estimation succeeded
  - `predicted_age` (float): Estimated age in years (if success=True)
  - `confidence` (float): Confidence score 0.0-1.0 (if success=True)
  - `confidence_level` (str): "high", "medium", "low", or "very_low" (if success=True)
  - `uncertainty` (float): Uncertainty range in years (if success=True)
  - `model_agreement` (float): Agreement between ensemble models 0.0-1.0 (if success=True)
  - `age_bin` (int): Age bin index (if success=True)
  - `is_adult` (bool): Whether age >= 21 (if success=True)
  - `is_teen` (bool): Whether 13 <= age < 21 (if success=True)
  - `is_child` (bool): Whether age < 13 (if success=True)
  - `should_retry` (bool): Whether retry is recommended (if success=True)
  - `attempt` (int): Current attempt number (if success=True)
  - `processing_time` (float): Processing time in seconds
  - `timestamp` (float): Unix timestamp of estimation
  - `system` (str): "BetterAgeVerify by luvaary"
  - `error` (str): Error code (if success=False)
  - `message` (str): Error message (if success=False)

**Raises:**
- `RuntimeError`: If data deletion exceeds timeout (1 second)

**Privacy Guarantee:**
- All biometric data (image, face crop, tensors, embeddings) deleted within 1 second

**Example:**
```python
from PIL import Image

image = Image.open("photo.jpg")
result = estimator.estimate_age(image)

if result["success"]:
    print(f"Age: {result['predicted_age']} years")
    print(f"Confidence: {result['confidence']:.1%}")
else:
    print(f"Error: {result['message']}")
```

---

#### verify_age_threshold()

Verify if estimated age meets a minimum threshold.

```python
verify_age_threshold(image: Image.Image, threshold_age: int = 13) -> Dict
```

**Parameters:**
- `image` (PIL.Image.Image): RGB image containing a face
- `threshold_age` (int, optional): Minimum age threshold. Defaults to 13.

**Returns:**
- `Dict`: Same as `estimate_age()` plus:
  - `passes_threshold` (bool): Whether predicted_age >= threshold_age
  - `threshold_age` (int): The threshold used

**Example:**
```python
result = estimator.verify_age_threshold(image, threshold_age=18)

if result["success"]:
    if result["passes_threshold"]:
        print("✓ User is 18+")
    else:
        print("✗ User appears under 18")
```

---

#### detect_face()

Detect and extract face from image (internal method, but accessible).

```python
detect_face(image: Image.Image) -> Optional[Image.Image]
```

**Parameters:**
- `image` (PIL.Image.Image): Input image

**Returns:**
- `Image.Image`: Cropped face image, or None if no face detected

**Example:**
```python
face = estimator.detect_face(image)
if face:
    print(f"Face detected: {face.size}")
```

---

### Model Classes

Individual model architectures (advanced usage).

#### WideResNetAge

```python
from src.age_estimator import WideResNetAge

model = WideResNetAge(num_classes=101)
age_regression, age_classification = model(image_tensor)
```

#### DEXAge

```python
from src.age_estimator import DEXAge

model = DEXAge(num_classes=101)
age_regression, age_classification = model(image_tensor)
```

#### ViTAge

```python
from src.age_estimator import ViTAge

model = ViTAge(num_classes=101)
age_regression, age_classification = model(image_tensor)
```

---

## Configuration API

### BetterAgeVerifyConfig

Global configuration class with all system settings.

```python
from src.config import BetterAgeVerifyConfig as Config
```

#### Core Settings

**Project Information:**
- `PROJECT_NAME` (str): "BetterAgeVerify"
- `CREATOR` (str): "luvaary"
- `VERSION` (str): "1.0.0"

**Paths:**
- `BASE_DIR` (Path): Project root directory
- `MODELS_DIR` (Path): Model weights directory
- `CACHE_DIR` (Path): Cache directory

**Device:**
- `DEVICE` (str): "cuda" or "cpu" (auto-detected)

#### Model Settings

- `INPUT_SIZE` (int): 224 - Input image size
- `BATCH_SIZE` (int): 1 - Batch size for inference
- `ENSEMBLE_MODELS` (List[str]): ["wideresnet", "dex", "vit"]
- `ENSEMBLE_WEIGHTS` (Dict): Model voting weights

#### Age Settings

- `AGE_MIN` (int): 0
- `AGE_MAX` (int): 100
- `AGE_BINS` (List[int]): Age bin boundaries
- `AGE_THRESHOLDS` (Dict): {"child": 13, "teen": 18, "adult": 21}

#### Confidence Settings

- `CONFIDENCE_THRESHOLD_HIGH` (float): 0.85
- `CONFIDENCE_THRESHOLD_MEDIUM` (float): 0.70
- `CONFIDENCE_THRESHOLD_LOW` (float): 0.50
- `UNCERTAINTY_THRESHOLD` (float): 5.0
- `MAX_RETRY_ATTEMPTS` (int): 3

#### Privacy Settings

- `DELETE_DATA_TIMEOUT` (float): 1.0 - Maximum deletion time (seconds)
- `PRIVACY_MODE` (bool): True - Privacy mode enabled
- `OFFLINE_MODE` (bool): True - Offline processing preferred
- `LOG_EDGE_CASES` (bool): True - Log edge cases anonymously
- `ANONYMIZE_LOGS` (bool): True - Anonymize all logs

#### File Format Support

- `SUPPORTED_IMAGE_FORMATS` (List[str]): [".jpg", ".jpeg", ".png", ".bmp", ".webp"]
- `SUPPORTED_VIDEO_FORMATS` (List[str]): [".mp4", ".avi", ".mov", ".mkv"]

#### Helper Methods

```python
# Get age bin index for an age
bin_index = Config.get_age_bin(age=25)

# Get confidence level string
level = Config.get_confidence_level(confidence=0.87)

# Check if should retry
should_retry = Config.should_retry(confidence=0.65, attempt=1)

# Age category checks
is_adult = Config.is_adult(age=25)
is_teen = Config.is_teen(age=16)
is_child = Config.is_child(age=10)
```

---

## Utility Functions

### ImageProcessor

Image loading and processing utilities.

```python
from src.utils import ImageProcessor
```

#### load_image()

```python
ImageProcessor.load_image(image_path: str) -> Optional[Image.Image]
```

**Parameters:**
- `image_path` (str): Path to image file

**Returns:**
- `Image.Image`: Loaded RGB image, or None if failed

**Example:**
```python
image = ImageProcessor.load_image("photo.jpg")
if image:
    print(f"Loaded: {image.size}")
```

#### preprocess_image()

```python
ImageProcessor.preprocess_image(
    image: Image.Image, 
    target_size: int = 224
) -> Image.Image
```

**Parameters:**
- `image` (PIL.Image.Image): Input image
- `target_size` (int, optional): Target size. Defaults to 224.

**Returns:**
- `Image.Image`: Preprocessed square image

#### extract_video_frames()

```python
ImageProcessor.extract_video_frames(
    video_path: str, 
    num_frames: int = 10
) -> List[Image.Image]
```

**Parameters:**
- `video_path` (str): Path to video file
- `num_frames` (int, optional): Number of frames to extract. Defaults to 10.

**Returns:**
- `List[Image.Image]`: Extracted frames

**Example:**
```python
frames = ImageProcessor.extract_video_frames("video.mp4", num_frames=20)
print(f"Extracted {len(frames)} frames")
```

#### secure_delete()

```python
ImageProcessor.secure_delete(image: Image.Image)
```

**Parameters:**
- `image` (PIL.Image.Image): Image to delete

**Example:**
```python
ImageProcessor.secure_delete(image)
```

---

### EdgeCaseDetector

Detect challenging conditions in images.

```python
from src.utils import EdgeCaseDetector
```

#### analyze_image()

```python
EdgeCaseDetector.analyze_image(image: Image.Image) -> Dict[str, bool]
```

**Parameters:**
- `image` (PIL.Image.Image): Image to analyze

**Returns:**
- `Dict[str, bool]`: Edge case detection results:
  - `mask_detected`: Face mask present
  - `glasses_detected`: Eyewear present
  - `hat_detected`: Headwear present
  - `extreme_angle`: Face not centered/rotated
  - `low_light`: Insufficient lighting
  - `motion_blur`: Movement or camera shake

**Example:**
```python
edge_cases = EdgeCaseDetector.analyze_image(image)
if edge_cases["mask_detected"]:
    print("⚠️ Face mask detected")
```

---

### ConsentManager

User consent management.

```python
from src.utils import ConsentManager
```

#### request_consent()

```python
ConsentManager.request_consent() -> bool
```

**Returns:**
- `bool`: True if user consented, False otherwise

**Example:**
```python
if ConsentManager.request_consent():
    result = estimator.estimate_age(image)
else:
    print("Consent not provided")
```

#### get_consent_text()

```python
ConsentManager.get_consent_text() -> str
```

**Returns:**
- `str`: Consent text to display

---

### ResultFormatter

Format results for display.

```python
from src.utils import ResultFormatter
```

#### format_cli_output()

```python
ResultFormatter.format_cli_output(result: Dict) -> str
```

**Parameters:**
- `result` (Dict): Result from `estimate_age()`

**Returns:**
- `str`: Formatted text output

**Example:**
```python
result = estimator.estimate_age(image)
print(ResultFormatter.format_cli_output(result))
```

#### format_json_output()

```python
ResultFormatter.format_json_output(result: Dict) -> str
```

**Parameters:**
- `result` (Dict): Result from `estimate_age()`

**Returns:**
- `str`: JSON-formatted string

---

### PrivacySafeLogger

Anonymous privacy-safe logging.

```python
from src.utils import PrivacySafeLogger

logger = PrivacySafeLogger(log_dir=Path("logs"))
```

#### log_verification()

```python
logger.log_verification(result: Dict)
```

**Parameters:**
- `result` (Dict): Verification result (anonymized before logging)

#### log_edge_case()

```python
logger.log_edge_case(result: Dict, edge_case_type: str)
```

**Parameters:**
- `result` (Dict): Verification result
- `edge_case_type` (str): Type of edge case detected

---

## Data Models

### Result Dictionary

Standard result format from `estimate_age()`:

```python
{
    "success": bool,
    "predicted_age": float,           # if success
    "confidence": float,              # 0.0-1.0, if success
    "confidence_level": str,          # "high"|"medium"|"low"|"very_low", if success
    "uncertainty": float,             # in years, if success
    "model_agreement": float,         # 0.0-1.0, if success
    "age_bin": int,                   # if success
    "is_adult": bool,                 # if success
    "is_teen": bool,                  # if success
    "is_child": bool,                 # if success
    "should_retry": bool,             # if success
    "attempt": int,                   # if success
    "processing_time": float,         # in seconds
    "timestamp": float,               # unix timestamp
    "system": str,                    # "BetterAgeVerify by luvaary"
    "error": str,                     # if success=False
    "message": str                    # if success=False
}
```

### Edge Cases Dictionary

```python
{
    "mask_detected": bool,
    "glasses_detected": bool,
    "hat_detected": bool,
    "extreme_angle": bool,
    "low_light": bool,
    "motion_blur": bool
}
```

---

## Exception Handling

### Common Exceptions

#### RuntimeError

Raised when data deletion exceeds timeout:

```python
try:
    result = estimator.estimate_age(image)
except RuntimeError as e:
    print(f"Data deletion timeout: {e}")
```

#### ValueError

Raised for invalid inputs:

```python
try:
    image = Image.open("invalid.txt")
    result = estimator.estimate_age(image)
except ValueError as e:
    print(f"Invalid image: {e}")
```

### Best Practices

```python
from PIL import Image
from src.age_estimator import BetterAgeVerifyEstimator
from src.utils import ImageProcessor

estimator = BetterAgeVerifyEstimator()

try:
    # Load image
    image = ImageProcessor.load_image("photo.jpg")
    if image is None:
        print("Error: Could not load image")
        exit(1)
    
    # Estimate age
    result = estimator.estimate_age(image)
    
    # Check result
    if result["success"]:
        print(f"Age: {result['predicted_age']} years")
    else:
        print(f"Error: {result['message']}")
    
    # Clean up (automatic, but explicit is fine)
    ImageProcessor.secure_delete(image)
    
except RuntimeError as e:
    print(f"Runtime error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

---

## Usage Examples

### Basic Age Estimation

```python
from src.age_estimator import BetterAgeVerifyEstimator
from PIL import Image

estimator = BetterAgeVerifyEstimator()
image = Image.open("photo.jpg")

result = estimator.estimate_age(image)
print(f"Age: {result['predicted_age']} years")
print(f"Confidence: {result['confidence']:.1%}")
```

### Age Threshold Verification

```python
result = estimator.verify_age_threshold(image, threshold_age=18)

if result["passes_threshold"]:
    print("✓ User is 18+")
else:
    print("✗ User appears under 18")
```

### Batch Processing

```python
from pathlib import Path

for image_path in Path("images/").glob("*.jpg"):
    image = ImageProcessor.load_image(str(image_path))
    result = estimator.estimate_age(image)
    
    print(f"{image_path.name}: {result['predicted_age']} years")
    ImageProcessor.secure_delete(image)
```

### Video Processing

```python
frames = ImageProcessor.extract_video_frames("video.mp4", num_frames=30)

ages = []
for frame in frames:
    result = estimator.estimate_age(frame)
    if result["success"]:
        ages.append(result["predicted_age"])
    ImageProcessor.secure_delete(frame)

avg_age = sum(ages) / len(ages) if ages else 0
print(f"Average age: {avg_age:.1f} years")
```

### With Edge Case Detection

```python
from src.utils import EdgeCaseDetector

image = Image.open("photo.jpg")
edge_cases = EdgeCaseDetector.analyze_image(image)

if any(edge_cases.values()):
    print("⚠️ Edge cases detected:")
    for case, detected in edge_cases.items():
        if detected:
            print(f"  - {case}")

result = estimator.estimate_age(image)
```

### With Consent Management

```python
from src.utils import ConsentManager

if ConsentManager.request_consent():
    result = estimator.estimate_age(image)
else:
    print("User did not consent")
```

---

## Performance Optimization

### GPU Acceleration

```python
import torch

# Check GPU availability
if torch.cuda.is_available():
    print(f"Using GPU: {torch.cuda.get_device_name(0)}")
else:
    print("Using CPU")
```

### Batch Processing

```python
# Process multiple images efficiently
images = [ImageProcessor.load_image(f) for f in image_paths]
results = [estimator.estimate_age(img) for img in images]

# Clean up
for img in images:
    ImageProcessor.secure_delete(img)
```

### Model Caching

```python
# Initialize once
estimator = BetterAgeVerifyEstimator()

# Reuse for multiple predictions (models stay loaded)
for image_path in image_paths:
    image = ImageProcessor.load_image(image_path)
    result = estimator.estimate_age(image)
    ImageProcessor.secure_delete(image)
```

---

## Privacy Compliance

### Automatic Data Deletion

All biometric data is automatically deleted within 1 second:

```python
result = estimator.estimate_age(image)
# At this point, ALL biometric data has been deleted:
# - Original image
# - Face crop
# - Preprocessed tensors
# - Model embeddings
# - GPU cache
```

### Manual Cleanup

```python
# Automatic cleanup happens, but you can also explicitly clean up
ImageProcessor.secure_delete(image)
```

### Verify Privacy Compliance

```python
from src.config import BetterAgeVerifyConfig as Config

# Verify privacy settings
assert Config.PRIVACY_MODE == True
assert Config.DELETE_DATA_TIMEOUT <= 1.0
assert Config.ANONYMIZE_LOGS == True
print("✓ Privacy compliance verified")
```

---

## Version Compatibility

**Current Version**: 1.0.0

**Python**: 3.8+  
**PyTorch**: 2.0+  
**Dependencies**: See requirements.txt

---

## Support

For API questions:
- 📖 Documentation: `/docs/` folder
- 💬 Discussions: GitHub Discussions
- 🐛 Issues: GitHub Issues
- 📧 Email: See SECURITY.md

---

*API Reference created by luvaary for BetterAgeVerify*  
*Complete, accurate, and privacy-first*

---

**BetterAgeVerify by luvaary: Developer-friendly. Privacy-respecting. Production-ready.**



