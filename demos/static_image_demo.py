import argparse
import cv2
import numpy as np
from PIL import Image
import sys
from pathlib import Path

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

class StaticImageVerifier:
    def __init__(self):
        self.estimator = BetterAgeVerifyEstimator()
        self.logger = PrivacySafeLogger()
    
    def create_result_visualization(self, image: Image.Image, result: dict, 
                                   edge_cases: dict) -> np.ndarray:
        img_array = np.array(image)
        if len(img_array.shape) == 2:
            img_array = cv2.cvtColor(img_array, cv2.COLOR_GRAY2BGR)
        elif img_array.shape[2] == 4:
            img_array = cv2.cvtColor(img_array, cv2.COLOR_RGBA2BGR)
        else:
            img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        
        height, width = img_array.shape[:2]
        
        info_width = 500
        canvas = np.zeros((height, width + info_width, 3), dtype=np.uint8)
        canvas[:, :width] = img_array
        
        canvas[:, width:] = (30, 30, 30)
        
        x_offset = width + 20
        y_pos = 40
        
        cv2.putText(canvas, Config.PROJECT_NAME, (x_offset, y_pos), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        y_pos += 25
        cv2.putText(canvas, f"by {Config.CREATOR}", (x_offset, y_pos), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        y_pos += 40
        
        cv2.line(canvas, (x_offset, y_pos), (width + info_width - 20, y_pos), (100, 100, 100), 1)
        y_pos += 30
        
        if result.get("success"):
            age_text = f"Age: {result['predicted_age']} years"
            cv2.putText(canvas, age_text, (x_offset, y_pos), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
            y_pos += 50
            
            conf_text = f"Confidence: {result['confidence']:.1%}"
            conf_color = (0, 255, 0) if result['confidence'] > 0.85 else (0, 200, 255) if result['confidence'] > 0.70 else (0, 150, 255)
            cv2.putText(canvas, conf_text, (x_offset, y_pos), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, conf_color, 1)
            y_pos += 30
            
            cv2.putText(canvas, f"Level: {result['confidence_level']}", (x_offset, y_pos), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
            y_pos += 40
            
            uncertainty_text = f"Uncertainty: +/- {result['uncertainty']:.1f} yrs"
            cv2.putText(canvas, uncertainty_text, (x_offset, y_pos), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
            y_pos += 30
            
            agreement_text = f"Model Agreement: {result['model_agreement']:.1%}"
            cv2.putText(canvas, agreement_text, (x_offset, y_pos), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
            y_pos += 50
            
            cv2.line(canvas, (x_offset, y_pos), (width + info_width - 20, y_pos), (100, 100, 100), 1)
            y_pos += 30
            
            category = "CHILD" if result['is_child'] else "TEEN" if result['is_teen'] else "ADULT"
            category_color = (0, 150, 255) if result['is_child'] else (255, 200, 0) if result['is_teen'] else (0, 255, 0)
            
            cv2.putText(canvas, "Category:", (x_offset, y_pos), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
            y_pos += 30
            cv2.putText(canvas, category, (x_offset, y_pos), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, category_color, 2)
            y_pos += 50
            
            if result.get('should_retry'):
                cv2.putText(canvas, "Status: Retry Recommended", (x_offset, y_pos), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 150, 255), 1)
                y_pos += 30
            
            cv2.line(canvas, (x_offset, y_pos), (width + info_width - 20, y_pos), (100, 100, 100), 1)
            y_pos += 30
            
            cv2.putText(canvas, "Edge Cases:", (x_offset, y_pos), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
            y_pos += 30
            
            detected = [k.replace('_', ' ').title() for k, v in edge_cases.items() if v]
            if detected:
                for case in detected[:5]:
                    cv2.putText(canvas, f"- {case}", (x_offset, y_pos), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 200, 0), 1)
                    y_pos += 25
            else:
                cv2.putText(canvas, "None detected", (x_offset, y_pos), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                y_pos += 25
            
            y_pos += 30
            cv2.line(canvas, (x_offset, y_pos), (width + info_width - 20, y_pos), (100, 100, 100), 1)
            y_pos += 30
            
            cv2.putText(canvas, "Privacy:", (x_offset, y_pos), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
            y_pos += 30
            cv2.putText(canvas, "Data deleted", (x_offset, y_pos), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            y_pos += 25
            cv2.putText(canvas, "immediately", (x_offset, y_pos), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        else:
            cv2.putText(canvas, "VERIFICATION FAILED", (x_offset, y_pos), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            y_pos += 40
            error_msg = result.get('message', 'Unknown error')
            cv2.putText(canvas, error_msg, (x_offset, y_pos), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 200, 200), 1)
        
        return canvas
    
    def verify_image(self, image_path: str, show_visual: bool = True, 
                    save_output: bool = False, output_path: str = None):
        print(f"\n{Config.PROJECT_NAME} - Static Image Verification")
        print(f"Created by {Config.CREATOR}\n")
        
        image = ImageProcessor.load_image(image_path)
        
        if image is None:
            print(f"Error: Could not load image from {image_path}")
            return None
        
        print(f"Image loaded: {image_path}")
        print(f"Size: {image.size[0]}x{image.size[1]}")
        
        edge_cases = EdgeCaseDetector.analyze_image(image)
        detected_edge_cases = [k for k, v in edge_cases.items() if v]
        
        if detected_edge_cases:
            print(f"\n⚠️  Edge cases detected: {', '.join(detected_edge_cases)}")
        
        print("\nProcessing image...")
        result = self.estimator.estimate_age(image)
        
        print(ResultFormatter.format_cli_output(result))
        
        if result["success"]:
            self.logger.log_verification(result)
            for edge_case in detected_edge_cases:
                self.logger.log_edge_case(result, edge_case)
        
        if show_visual or save_output:
            visualization = self.create_result_visualization(image, result, edge_cases)
            
            if save_output:
                if output_path is None:
                    output_path = f"verification_result_{Path(image_path).stem}.png"
                cv2.imwrite(output_path, visualization)
                print(f"Visualization saved to: {output_path}")
            
            if show_visual:
                cv2.imshow(f'{Config.PROJECT_NAME} - Verification Result', visualization)
                print("\nPress any key to close visualization...")
                cv2.waitKey(0)
                cv2.destroyAllWindows()
        
        ImageProcessor.secure_delete(image)
        
        return result

def main():
    parser = argparse.ArgumentParser(
        description=f"{Config.PROJECT_NAME} Static Image Demo by {Config.CREATOR}"
    )
    parser.add_argument('--image', type=str, required=True, help='Path to input image')
    parser.add_argument('--no-visual', action='store_true', help='Disable visual output')
    parser.add_argument('--save', action='store_true', help='Save visualization to file')
    parser.add_argument('--output', type=str, help='Output file path for visualization')
    parser.add_argument('--skip-consent', action='store_true', help='Skip consent prompt')
    
    args = parser.parse_args()
    
    if not args.skip_consent and not ConsentManager.request_consent():
        print("Consent not provided. Exiting.")
        return 1
    
    verifier = StaticImageVerifier()
    result = verifier.verify_image(
        args.image,
        show_visual=not args.no_visual,
        save_output=args.save,
        output_path=args.output
    )
    
    if result is None or not result.get("success"):
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
