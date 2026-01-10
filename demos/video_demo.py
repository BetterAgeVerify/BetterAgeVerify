import argparse
import cv2
import numpy as np
from PIL import Image
import sys
import time
from pathlib import Path
from collections import deque

sys.path.append(str(Path(__file__).parent.parent))

from src.age_estimator import BetterAgeVerifyEstimator
from src.utils import (
    ImageProcessor,
    EdgeCaseDetector,
    ConsentManager,
    PrivacySafeLogger,
    ResultFormatter
)
from src.config import BetterAgeVerifyConfig as Config

class VideoAgeVerifier:
    def __init__(self, frame_skip: int = 5, max_frames: int = 50):
        self.estimator = BetterAgeVerifyEstimator()
        self.logger = PrivacySafeLogger()
        self.frame_skip = frame_skip
        self.max_frames = max_frames
        self.results_history = deque(maxlen=100)
    
    def process_video(self, video_path: str, show_progress: bool = True) -> dict:
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            return {
                "success": False,
                "error": "video_open_failed",
                "message": f"Could not open video file: {video_path}"
            }
        
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        duration = total_frames / fps if fps > 0 else 0
        
        if show_progress:
            print(f"\nVideo Information:")
            print(f"Total frames: {total_frames}")
            print(f"FPS: {fps:.2f}")
            print(f"Duration: {duration:.2f}s")
            print(f"Processing every {self.frame_skip} frames...\n")
        
        frame_results = []
        edge_case_counts = {case: 0 for case in Config.EDGE_CASE_CONDITIONS}
        
        frame_idx = 0
        processed_count = 0
        
        start_time = time.time()
        
        try:
            while True:
                ret, frame = cap.read()
                
                if not ret:
                    break
                
                if frame_idx % self.frame_skip == 0 and processed_count < self.max_frames:
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    pil_image = Image.fromarray(frame_rgb)
                    
                    edge_cases = EdgeCaseDetector.analyze_image(pil_image)
                    for case, detected in edge_cases.items():
                        if detected:
                            edge_case_counts[case] += 1
                    
                    result = self.estimator.estimate_age(pil_image, attempt=1)
                    
                    if result.get("success"):
                        frame_results.append({
                            "frame_idx": frame_idx,
                            "timestamp": frame_idx / fps if fps > 0 else 0,
                            "predicted_age": result["predicted_age"],
                            "confidence": result["confidence"],
                            "uncertainty": result["uncertainty"],
                            "edge_cases": edge_cases
                        })
                        
                        processed_count += 1
                        
                        if show_progress and processed_count % 5 == 0:
                            print(f"Processed {processed_count} frames...", end='\r')
                    
                    pil_image.close()
                    del pil_image
                
                frame_idx += 1
                
                if processed_count >= self.max_frames:
                    break
        
        finally:
            cap.release()
        
        processing_time = time.time() - start_time
        
        if show_progress:
            print(f"\nProcessed {processed_count} frames in {processing_time:.2f}s")
        
        if not frame_results:
            return {
                "success": False,
                "error": "no_valid_frames",
                "message": "No faces detected in video frames"
            }
        
        ages = [r["predicted_age"] for r in frame_results]
        confidences = [r["confidence"] for r in frame_results]
        uncertainties = [r["uncertainty"] for r in frame_results]
        
        avg_age = np.mean(ages)
        median_age = np.median(ages)
        std_age = np.std(ages)
        
        high_conf_ages = [r["predicted_age"] for r in frame_results if r["confidence"] > Config.CONFIDENCE_THRESHOLD_HIGH]
        weighted_age = np.average(ages, weights=confidences) if confidences else avg_age
        
        final_age = weighted_age if len(high_conf_ages) > len(ages) * 0.3 else median_age
        
        avg_confidence = np.mean(confidences)
        avg_uncertainty = np.mean(uncertainties)
        
        consistency_score = 1.0 - min(std_age / max(final_age, 1.0), 1.0)
        
        final_result = {
            "success": True,
            "video_path": video_path,
            "predicted_age": round(final_age, 1),
            "median_age": round(median_age, 1),
            "age_range": f"{min(ages):.1f} - {max(ages):.1f}",
            "age_std_dev": round(std_age, 2),
            "confidence": round(avg_confidence, 3),
            "confidence_level": Config.get_confidence_level(avg_confidence),
            "uncertainty": round(avg_uncertainty, 2),
            "consistency_score": round(consistency_score, 3),
            "frames_analyzed": len(frame_results),
            "total_frames": total_frames,
            "video_duration": round(duration, 2),
            "processing_time": round(processing_time, 2),
            "is_adult": Config.is_adult(final_age),
            "is_teen": Config.is_teen(final_age),
            "is_child": Config.is_child(final_age),
            "edge_cases_detected": {k: v for k, v in edge_case_counts.items() if v > 0},
            "frame_results": frame_results,
            "system": f"{Config.PROJECT_NAME} by {Config.CREATOR}"
        }
        
        return final_result
    
    def generate_report(self, result: dict) -> str:
        if not result.get("success"):
            return f"Video verification failed: {result.get('message', 'Unknown error')}"
        
        report = f"""
{'=' * 70}
{Config.PROJECT_NAME} - Video Age Verification Report
Created by {Config.CREATOR}
{'=' * 70}

VIDEO INFORMATION:
  File: {result['video_path']}
  Duration: {result['video_duration']}s
  Total Frames: {result['total_frames']}
  Frames Analyzed: {result['frames_analyzed']}
  Processing Time: {result['processing_time']}s

AGE ESTIMATION RESULTS:
  Final Predicted Age: {result['predicted_age']} years
  Median Age: {result['median_age']} years
  Age Range: {result['age_range']} years
  Standard Deviation: ±{result['age_std_dev']} years
  
CONFIDENCE METRICS:
  Average Confidence: {result['confidence']:.1%} ({result['confidence_level']})
  Uncertainty: ±{result['uncertainty']} years
  Consistency Score: {result['consistency_score']:.1%}

AGE CATEGORY:
"""
        
        if result['is_child']:
            report += "  → CHILD (under 13)\n"
        elif result['is_teen']:
            report += "  → TEEN (13-17)\n"
        else:
            report += "  → ADULT (18+)\n"
        
        if result['edge_cases_detected']:
            report += f"\nEDGE CASES DETECTED:\n"
            for case, count in result['edge_cases_detected'].items():
                percentage = (count / result['frames_analyzed']) * 100
                report += f"  - {case.replace('_', ' ').title()}: {count} frames ({percentage:.1f}%)\n"
        else:
            report += f"\nEDGE CASES: None detected\n"
        
        report += f"""
{'=' * 70}
Privacy: All biometric data deleted immediately after processing
{'=' * 70}
"""
        
        return report

def main():
    parser = argparse.ArgumentParser(
        description=f"{Config.PROJECT_NAME} Video Verification Demo by {Config.CREATOR}"
    )
    parser.add_argument('--video', type=str, required=True, help='Path to video file')
    parser.add_argument('--frame-skip', type=int, default=5, help='Process every Nth frame (default: 5)')
    parser.add_argument('--max-frames', type=int, default=50, help='Maximum frames to process (default: 50)')
    parser.add_argument('--skip-consent', action='store_true', help='Skip consent prompt')
    parser.add_argument('--save-report', type=str, help='Save report to file')
    parser.add_argument('--json', action='store_true', help='Output results as JSON')
    
    args = parser.parse_args()
    
    print(f"\n{Config.PROJECT_NAME} - Video Age Verification")
    print(f"Created by {Config.CREATOR}\n")
    
    if not args.skip_consent and not ConsentManager.request_consent():
        print("Consent not provided. Exiting.")
        return 1
    
    video_path = Path(args.video)
    if not video_path.exists():
        print(f"Error: Video file not found: {args.video}")
        return 1
    
    if video_path.suffix.lower() not in Config.SUPPORTED_VIDEO_FORMATS:
        print(f"Error: Unsupported video format. Supported: {Config.SUPPORTED_VIDEO_FORMATS}")
        return 1
    
    verifier = VideoAgeVerifier(
        frame_skip=args.frame_skip,
        max_frames=args.max_frames
    )
    
    result = verifier.process_video(str(video_path), show_progress=True)
    
    if not result.get("success"):
        print(f"\nError: {result.get('message', 'Unknown error')}")
        return 1
    
    if result["success"]:
        logger = PrivacySafeLogger()
        logger.log_verification(result)
    
    if args.json:
        import json
        result_copy = result.copy()
        result_copy.pop('frame_results', None)
        print(json.dumps(result_copy, indent=2))
    else:
        report = verifier.generate_report(result)
        print(report)
    
    if args.save_report:
        report = verifier.generate_report(result)
        with open(args.save_report, 'w') as f:
            f.write(report)
        print(f"\nReport saved to: {args.save_report}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
