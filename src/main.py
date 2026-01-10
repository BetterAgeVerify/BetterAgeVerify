import argparse
import sys
from pathlib import Path
from PIL import Image
from src.age_estimator import BetterAgeVerifyEstimator
from src.utils import (
    ImageProcessor,
    EdgeCaseDetector,
    ConsentManager,
    ResultFormatter,
    PrivacySafeLogger,
    validate_environment
)
from src.config import BetterAgeVerifyConfig as Config

def print_banner():
    banner = f"""
    ╔════════════════════════════════════════════════════════════════╗
    ║                                                                ║
    ║                    BetterAgeVerify v{Config.VERSION}                    ║
    ║                                                                ║
    ║          The World's Most Accurate Age Verification            ║
    ║              Privacy-First • Open-Source • Superior            ║
    ║                                                                ║
    ║                    Created by {Config.CREATOR}                         ║
    ║                                                                ║
    ╚════════════════════════════════════════════════════════════════╝
    """
    print(banner)

def verify_image(image_path: str, estimator: BetterAgeVerifyEstimator, logger: PrivacySafeLogger, 
                 skip_consent: bool = False, json_output: bool = False) -> int:
    
    if not skip_consent and not ConsentManager.request_consent():
        print("Consent not provided. Exiting.")
        return 1
    
    image = ImageProcessor.load_image(image_path)
    
    if image is None:
        print(f"Error: Could not load image from {image_path}")
        return 1
    
    edge_cases = EdgeCaseDetector.analyze_image(image)
    
    detected_edge_cases = [k for k, v in edge_cases.items() if v]
    if detected_edge_cases:
        print(f"\n⚠️  Edge cases detected: {', '.join(detected_edge_cases)}")
        print("This may affect accuracy. Consider retaking the image.\n")
    
    result = estimator.estimate_age(image)
    
    if result["success"] and detected_edge_cases:
        for edge_case in detected_edge_cases:
            logger.log_edge_case(result, edge_case)
    
    logger.log_verification(result)
    
    ImageProcessor.secure_delete(image)
    
    if json_output:
        print(ResultFormatter.format_json_output(result))
    else:
        print(ResultFormatter.format_cli_output(result))
    
    return 0 if result["success"] else 1

def verify_video(video_path: str, estimator: BetterAgeVerifyEstimator, logger: PrivacySafeLogger,
                 skip_consent: bool = False, json_output: bool = False) -> int:
    
    if not skip_consent and not ConsentManager.request_consent():
        print("Consent not provided. Exiting.")
        return 1
    
    print(f"\nExtracting frames from video: {video_path}")
    frames = ImageProcessor.extract_video_frames(video_path, num_frames=10)
    
    if not frames:
        print("Error: Could not extract frames from video")
        return 1
    
    print(f"Extracted {len(frames)} frames. Processing...\n")
    
    results = []
    for i, frame in enumerate(frames):
        print(f"Processing frame {i+1}/{len(frames)}...", end='\r')
        result = estimator.estimate_age(frame, attempt=1)
        
        if result["success"]:
            results.append(result)
        
        ImageProcessor.secure_delete(frame)
    
    print("\n")
    
    if not results:
        print("Error: No successful age predictions from video frames")
        return 1
    
    avg_age = sum(r["predicted_age"] for r in results) / len(results)
    avg_confidence = sum(r["confidence"] for r in results) / len(results)
    avg_uncertainty = sum(r["uncertainty"] for r in results) / len(results)
    
    final_result = {
        "success": True,
        "predicted_age": round(avg_age, 1),
        "confidence": round(avg_confidence, 3),
        "confidence_level": Config.get_confidence_level(avg_confidence),
        "uncertainty": round(avg_uncertainty, 2),
        "frames_processed": len(results),
        "is_adult": Config.is_adult(avg_age),
        "is_teen": Config.is_teen(avg_age),
        "is_child": Config.is_child(avg_age),
        "system": f"{Config.PROJECT_NAME} by {Config.CREATOR}"
    }
    
    logger.log_verification(final_result)
    
    if json_output:
        print(ResultFormatter.format_json_output(final_result))
    else:
        print(ResultFormatter.format_cli_output(final_result))
    
    return 0

def verify_threshold(image_path: str, threshold: int, estimator: BetterAgeVerifyEstimator,
                     skip_consent: bool = False) -> int:
    
    if not skip_consent and not ConsentManager.request_consent():
        print("Consent not provided. Exiting.")
        return 1
    
    image = ImageProcessor.load_image(image_path)
    
    if image is None:
        print(f"Error: Could not load image from {image_path}")
        return 1
    
    result = estimator.verify_age_threshold(image, threshold_age=threshold)
    
    ImageProcessor.secure_delete(image)
    
    if not result["success"]:
        print(f"Verification failed: {result.get('message', 'Unknown error')}")
        return 1
    
    print(f"\n{'=' * 60}")
    print(f"{Config.PROJECT_NAME} - Age Threshold Verification")
    print(f"Created by {Config.CREATOR}")
    print(f"{'=' * 60}\n")
    print(f"Predicted Age: {result['predicted_age']} years")
    print(f"Threshold: {threshold} years")
    print(f"Result: {'PASS ✓' if result['passes_threshold'] else 'FAIL ✗'}")
    print(f"Confidence: {result['confidence']:.1%}")
    print(f"\n{'=' * 60}\n")
    
    return 0 if result['passes_threshold'] else 1

def main():
    parser = argparse.ArgumentParser(
        description=f"{Config.PROJECT_NAME} - Privacy-first age verification by {Config.CREATOR}",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--image', type=str, help='Path to image file for age verification')
    parser.add_argument('--video', type=str, help='Path to video file for age verification')
    parser.add_argument('--threshold', type=int, help='Verify age against threshold (e.g., 13, 18, 21)')
    parser.add_argument('--skip-consent', action='store_true', help='Skip consent prompt (use with caution)')
    parser.add_argument('--json', action='store_true', help='Output results as JSON')
    parser.add_argument('--version', action='version', version=f'{Config.PROJECT_NAME} v{Config.VERSION} by {Config.CREATOR}')
    
    args = parser.parse_args()
    
    print_banner()
    
    if not validate_environment():
        print("Error: Failed to validate environment")
        return 1
    
    estimator = BetterAgeVerifyEstimator()
    logger = PrivacySafeLogger()
    
    if args.image and args.threshold:
        return verify_threshold(args.image, args.threshold, estimator, args.skip_consent)
    elif args.image:
        return verify_image(args.image, estimator, logger, args.skip_consent, args.json)
    elif args.video:
        return verify_video(args.video, estimator, logger, args.skip_consent, args.json)
    else:
        parser.print_help()
        print(f"\nExample usage:")
        print(f"  python src/main.py --image photo.jpg")
        print(f"  python src/main.py --video video.mp4")
        print(f"  python src/main.py --image photo.jpg --threshold 13")
        print(f"  python src/main.py --image photo.jpg --json")
        return 1

if __name__ == "__main__":
    sys.exit(main())
