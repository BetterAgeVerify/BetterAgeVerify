# BetterAgeVerify Demo Instructions

**Created by luvaary**

Last Updated: January 11, 2026

---

## Welcome to BetterAgeVerify!

This guide will help you test and demonstrate the world's most accurate, privacy-first age verification system.

**Whether you're a developer, educator, parent, or just curious - these demos will show you why BetterAgeVerify is superior to proprietary systems like Roblox's vendor.**

---

## Table of Contents

1. [Installation](#installation)
2. [Demo Overview](#demo-overview)
3. [Webcam Demo](#webcam-demo)
4. [Static Image Demo](#static-image-demo)
5. [Video Demo](#video-demo)
6. [Command Line Interface](#command-line-interface)
7. [Understanding Results](#understanding-results)
8. [Troubleshooting](#troubleshooting)
9. [Privacy Notes](#privacy-notes)

---

## Installation

### Prerequisites

- **Python**: 3.8 or higher
- **Operating System**: Windows, macOS, or Linux
- **Webcam**: For real-time demos (optional)
- **GPU**: Recommended but not required

### Quick Install
```bash
# Clone the repository
git clone https://github.com/luvaary/BetterAgeVerify.git
cd BetterAgeVerify

# Install dependencies
pip install -r requirements.txt
```

### Verify Installation
```bash
# Check if everything works
python src/main.py --version
```

You should see:
```
BetterAgeVerify v1.0.0 by luvaary
```

---

## Demo Overview

BetterAgeVerify includes three main demonstration modes:

| Demo | Input | Best For |
|------|-------|----------|
| **Webcam** | Live camera feed | Real-time testing, presentations |
| **Static Image** | Photo files (JPG, PNG) | Detailed analysis, screenshots |
| **Video** | Video files (MP4, AVI) | Multi-frame averaging, recordings |

**All demos guarantee immediate data deletion and full privacy compliance.**

---

## Webcam Demo

### What It Does

- Opens your webcam
- Analyzes your face in real-time
- Shows age estimate, confidence, and edge cases
- Updates every 2 seconds

### Running the Demo
```bash
python demos/webcam_demo.py
```

### First Run

You'll see the consent prompt:
```
BetterAgeVerify - Age Verification Consent
Created by luvaary

By proceeding, you explicitly consent to:
1. Facial image processing for age estimation only
2. Immediate deletion of all biometric data after processing (within 1 second)
3. No long-term storage of your facial images or biometric data
4. Anonymous logging of edge cases for system improvement (no personal data)

Your privacy is protected by the "No More Data!" license.

Type 'I CONSENT' to proceed or 'NO' to cancel:
```

Type `I CONSENT` and press Enter.

### What You'll See
```
╔════════════════════════════════════════════════════════════════╗
║                    BetterAgeVerify v1.0.0                     ║
║          The World's Most Accurate Age Verification            ║
║              Privacy-First • Open-Source • Superior            ║
║                    Created by luvaary                          ║
╚════════════════════════════════════════════════════════════════╝

Live video feed with overlays showing:
- Your estimated age
- Confidence level (high/medium/low)
- Age category (CHILD/TEEN/ADULT)
- Uncertainty range
- Edge cases detected (if any)
- Privacy guarantee confirmation
```

### Controls

- **'q'**: Quit the demo
- **'s'**: Save current result as image
- The window shows real-time FPS and frame count

### Tips for Best Results

✓ **Good lighting**: Face the light source  
✓ **Clear view**: Remove glasses/masks if possible  
✓ **Neutral expression**: Works best with relaxed face  
✓ **Centered**: Keep face in center of frame  
✓ **Distance**: Sit 2-3 feet from camera  

### Common Edge Cases

The demo will automatically detect:
- 😷 **Mask Detected**: Lower half of face covered
- 👓 **Glasses Detected**: Eyewear present
- 🧢 **Hat Detected**: Headwear present
- 🔄 **Extreme Angle**: Face not centered/rotated
- 🌑 **Low Light**: Insufficient lighting
- 💨 **Motion Blur**: Movement or camera shake

**When edge cases are detected, you'll see warnings and confidence may be lower.**

---

## Static Image Demo

### What It Does

- Analyzes a single photo
- Shows detailed results with visualization
- Saves annotated results (optional)
- Perfect for testing specific images

### Running the Demo
```bash
# Basic usage
python demos/static_image_demo.py --image path/to/your/photo.jpg

# Skip consent (for repeated testing)
python demos/static_image_demo.py --image photo.jpg --skip-consent

# Save visualization
python demos/static_image_demo.py --image photo.jpg --save --output result.png

# No visual display (CLI only)
python demos/static_image_demo.py --image photo.jpg --no-visual
```

### Sample Commands
```bash
# Test with a selfie
python demos/static_image_demo.py --image selfie.jpg

# Test multiple images
python demos/static_image_demo.py --image photo1.jpg --skip-consent
python demos/static_image_demo.py --image photo2.jpg --skip-consent
python demos/static_image_demo.py --image photo3.jpg --skip-consent

# Save all results
python demos/static_image_demo.py --image photo.jpg --save
```

### Understanding the Visualization

The demo creates a side-by-side display:

**Left Side**: Your original image  
**Right Side**: Detailed results panel
```
┌─────────────────────────────────────────────┐
│ BetterAgeVerify                             │
│ by luvaary                                  │
├─────────────────────────────────────────────┤
│ Age: 25.3 years                             │
│ Confidence: 87.6% (high)                    │
│ Level: high                                 │
│                                             │
│ Uncertainty: ± 2.8 yrs                      │
│ Model Agreement: 91.2%                      │
├─────────────────────────────────────────────┤
│ Category:                                   │
│ ADULT                                       │
├─────────────────────────────────────────────┤
│ Edge Cases:                                 │
│ - Glasses Detected                          │
│ - Low Light                                 │
├─────────────────────────────────────────────┤
│ Privacy:                                    │
│ Data deleted                                │
│ immediately                                 │
└─────────────────────────────────────────────┘
```

### Supported Image Formats

- JPG / JPEG
- PNG
- BMP
- WebP

---

## Video Demo

### What It Does

- Processes video files frame-by-frame
- Averages predictions across multiple frames
- More accurate than single images
- Shows consistency score

### Running the Demo
```bash
# Basic usage
python demos/video_demo.py --video path/to/video.mp4

# Process more frames (slower but more accurate)
python demos/video_demo.py --video video.mp4 --max-frames 100

# Skip every 10th frame (faster)
python demos/video_demo.py --video video.mp4 --frame-skip 10

# Save report to file
python demos/video_demo.py --video video.mp4 --save-report report.txt

# JSON output
python demos/video_demo.py --video video.mp4 --json
```

### Sample Output
```
BetterAgeVerify - Video Age Verification
Created by luvaary

Video Information:
Total frames: 450
FPS: 30.00
Duration: 15.00s
Processing every 5 frames...

Processed 50 frames in 12.34s

════════════════════════════════════════════════════════════════════
BetterAgeVerify - Video Age Verification Report
Created by luvaary
════════════════════════════════════════════════════════════════════

VIDEO INFORMATION:
  File: video.mp4
  Duration: 15.0s
  Total Frames: 450
  Frames Analyzed: 50
  Processing Time: 12.34s

AGE ESTIMATION RESULTS:
  Final Predicted Age: 24.7 years
  Median Age: 24.5 years
  Age Range: 22.3 - 27.1 years
  Standard Deviation: ±1.9 years
  
CONFIDENCE METRICS:
  Average Confidence: 88.5% (high)
  Uncertainty: ±2.4 years
  Consistency Score: 92.1%

AGE CATEGORY:
  → ADULT (18+)

EDGE CASES DETECTED:
  - Glasses Detected: 12 frames (24.0%)
  - Motion Blur: 5 frames (10.0%)

════════════════════════════════════════════════════════════════════
Privacy: All biometric data deleted immediately after processing
════════════════════════════════════════════════════════════════════
```

### Video Tips

✓ **Better than photos**: Multiple frames = higher accuracy  
✓ **Keep face visible**: Ensure face is in frame most of the time  
✓ **Steady video**: Less motion = better results  
✓ **Good lighting**: Consistent lighting throughout  

---

## Command Line Interface

### Basic Commands
```bash
# Verify single image
python src/main.py --image photo.jpg

# Verify video
python src/main.py --video video.mp4

# Check if someone is 13+
python src/main.py --image photo.jpg --threshold 13

# Check if someone is 18+
python src/main.py --image photo.jpg --threshold 18

# JSON output for automation
python src/main.py --image photo.jpg --json
```

### Threshold Verification

Perfect for quick yes/no checks:
```bash
# Is this person 13 or older?
python src/main.py --image kid.jpg --threshold 13

# Output:
════════════════════════════════════════════════════════════════
BetterAgeVerify - Age Threshold Verification
Created by luvaary
════════════════════════════════════════════════════════════════

Predicted Age: 11.8 years
Threshold: 13 years
Result: FAIL ✗
Confidence: 89.2%

════════════════════════════════════════════════════════════════
```

### Automation Example
```bash
# Process multiple images and save results
for image in images/*.jpg; do
    python src/main.py --image "$image" --json --skip-consent >> results.jsonl
done
```

---

## Understanding Results

### Result Components

Every BetterAgeVerify result includes:

#### 1. Predicted Age
```
Predicted Age: 25.3 years
```
- Most likely age based on facial features
- Rounded to 1 decimal place
- Range: 0-100 years

#### 2. Confidence Level
```
Confidence: 87.6% (high)
```
- **High** (85-100%): Very reliable
- **Medium** (70-85%): Reliable with caveats
- **Low** (50-70%): Consider retry
- **Very Low** (< 50%): Retry recommended

#### 3. Uncertainty
```
Uncertainty: ± 2.8 years
```
- Estimated error range
- Lower = more precise
- Typical range: ±2-5 years

#### 4. Model Agreement
```
Model Agreement: 91.2%
```
- How much AI models agree
- Higher = more consistent
- > 90% is excellent

#### 5. Age Category
```
Category: ADULT
```
- **CHILD**: Under 13
- **TEEN**: 13-17
- **ADULT**: 18+

### When to Retry

**BetterAgeVerify automatically suggests retry when:**
- Confidence < 70%
- Edge cases detected
- High uncertainty (> 5 years)
- Model disagreement (< 80%)

**Retry tips:**
- Try better lighting
- Remove glasses/masks
- Face camera directly
- Use multiple photos
- Try video mode

---

## Troubleshooting

### Common Issues

#### "Could not open webcam"

**Solution**:
```bash
# Check webcam permissions
# Windows: Settings > Privacy > Camera
# macOS: System Preferences > Security & Privacy > Camera
# Linux: Check /dev/video0 permissions
```

#### "No face detected"

**Causes**:
- Face too far from camera
- Poor lighting
- Face partially obscured
- Extreme angle

**Solutions**:
- Move closer to camera
- Improve lighting
- Remove obstructions
- Face camera directly

#### "Error: Could not load image"

**Solutions**:
- Check file path is correct
- Verify file format (JPG, PNG, BMP, WebP)
- Ensure file isn't corrupted
- Try absolute path instead of relative

#### Slow Performance

**Solutions**:
```bash
# Use GPU acceleration (if available)
# Check CUDA is installed for NVIDIA GPUs

# Reduce video frame processing
python demos/video_demo.py --video video.mp4 --frame-skip 10 --max-frames 20

# Use smaller images
python demos/static_image_demo.py --image large_image.jpg
# (automatic resizing to 224x224)
```

#### Low Confidence Results

**Common causes**:
- Edge cases present (masks, glasses, hats)
- Poor image quality
- Extreme lighting
- Unusual facial features
- Very young or very old subjects

**Solutions**:
- Remove obstructions
- Try better lighting
- Use multiple images
- Try video mode for averaging

---

## Privacy Notes

### What Happens to Your Data

**During Processing**:
1. Your image is loaded into memory
2. Face is detected and cropped
3. AI models estimate age
4. Result is generated
5. **ALL data is deleted** (< 1 second)

**After Processing**:
- ✓ No images stored
- ✓ No biometric data retained
- ✓ No tracking or profiling
- ✓ Only anonymous statistics logged

### What Gets Logged (Anonymously)

✓ Age category (child/teen/adult) - NOT specific age  
✓ Confidence level  
✓ Edge cases detected  
✓ Processing time  

✗ NOT logged: images, faces, names, locations, devices

### Verification

You can verify privacy guarantees:
```bash
# Check the source code
cat src/age_estimator.py | grep -A 20 "_delete_biometric_data"

# Monitor network traffic (should be zero in offline mode)
# Use Wireshark, tcpdump, or similar tools
```

**BetterAgeVerify is open-source. Don't trust us - verify yourself.**

---

## Advanced Usage

### Custom Configuration

Edit `src/config.py` to customize:
```python
# Adjust confidence thresholds
CONFIDENCE_THRESHOLD_HIGH = 0.85  # Default: 0.85
CONFIDENCE_THRESHOLD_MEDIUM = 0.70  # Default: 0.70

# Change processing speed
AUGMENTATION_ITERATIONS = 5  # Default: 5, lower = faster

# Adjust age bins
AGE_BINS = [0, 2, 6, 12, 18, 25, 35, 45, 55, 65, 100]
```

### Batch Processing
```python
from src.age_estimator import BetterAgeVerifyEstimator
from src.utils import ImageProcessor
from pathlib import Path

estimator = BetterAgeVerifyEstimator()

for image_path in Path("images/").glob("*.jpg"):
    image = ImageProcessor.load_image(str(image_path))
    result = estimator.estimate_age(image)
    print(f"{image_path.name}: {result['predicted_age']} years")
    ImageProcessor.secure_delete(image)
```

---

## Demo Scenarios

### For Parents/Educators

"Is this platform safe for my child?"

```bash
# Take photo of child
# Run verification
python src/main.py --image child.jpg --threshold 13

# If result is FAIL ✗ → child is under 13
# If result is PASS ✓ → child appears 13+
```

### For Developers

"How do I integrate this?"

```python
from src.age_estimator import BetterAgeVerifyEstimator
from PIL import Image

estimator = BetterAgeVerifyEstimator()
image = Image.open("user_photo.jpg")
result = estimator.verify_age_threshold(image, threshold_age=18)

if result["passes_threshold"]:
    print("User is 18+")
else:
    print("User appears under 18")
```

### For Media/Press

"Show me it works better than Roblox"

```bash
# Run benchmarks
python benchmarks/benchmark_accuracy.py
python benchmarks/benchmark_edge_cases.py

# See results demonstrating superiority
cat benchmarks/results/accuracy_report_*.txt
```

---

## Getting Help

### Resources

- **Documentation**: `/docs/` folder
- **Source Code**: `/src/` folder
- **Tests**: `/tests/` folder
- **Issues**: GitHub Issues (when repository is public)

### Reporting Bugs

Found a bug? Great! We want to know.

1. Check if it's already reported
2. Include error messages
3. Describe steps to reproduce
4. Include system information

### Feature Requests

Have an idea? Submit it!

1. Describe the use case
2. Explain why it's needed
3. Suggest implementation (optional)

---

## Next Steps

### After Testing

1. **Review the code**: See how it works
2. **Check benchmarks**: Verify superior performance
3. **Read privacy policy**: Understand guarantees
4. **Share feedback**: Help improve BetterAgeVerify

### For Production Use

1. Test with your specific use case
2. Measure performance in your environment
3. Review compliance with your regulations
4. Consider fallback mechanisms
5. Monitor and log (privacy-safe)

---

## Conclusion

**You've now seen BetterAgeVerify in action.**

- ✅ More accurate than proprietary systems
- ✅ Complete privacy protection
- ✅ Open-source and transparent
- ✅ Free to use
- ✅ Easy to integrate

**This is how age verification should work.**

---

*Demo instructions created by luvaary for BetterAgeVerify*  
*The privacy-first, superior alternative to proprietary systems*

**Questions? Check the docs. Want to contribute? Read the code. Ready to deploy? You're all set.**

**BetterAgeVerify: Better than Roblox's vendor. Better for users. Better for the world.**
```
