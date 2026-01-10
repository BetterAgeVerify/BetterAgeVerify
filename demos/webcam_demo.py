import cv2
import numpy as np
from PIL import Image
import time
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from src.age_estimator import BetterAgeVerifyEstimator
from src.utils import ConsentManager, EdgeCaseDetector, PrivacySafeLogger
from src.config import BetterAgeVerifyConfig as Config

class WebcamAgeVerifier:
    def __init__(self):
        self.estimator = BetterAgeVerifyEstimator()
        self.logger = PrivacySafeLogger()
        self.last_prediction_time = 0
        self.prediction_interval = 2.0
        self.current_result = None
        self.edge_cases = {}
        
    def draw_overlay(self, frame: np.ndarray, result: dict = None, edge_cases: dict = None) -> np.ndarray:
        overlay = frame.copy()
        height, width = frame.shape[:2]
        
        cv2.rectangle(overlay, (0, 0), (width, 120), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
        
        title = f"{Config.PROJECT_NAME} by {Config.CREATOR}"
        cv2.putText(frame, title, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)
        cv2.putText(frame, "Privacy-First Real-Time Age Verification", (20, 75), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
        cv2.putText(frame, "Press 'q' to quit | 's' to save result", (20, 105),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150, 150, 150), 1)
        
        if result and result.get("success"):
            box_y = height - 200
            cv2.rectangle(frame, (20, box_y), (width - 20, height - 20), (0, 0, 0), -1)
            cv2.rectangle(frame, (20, box_y), (width - 20, height - 20), (0, 255, 0), 2)
            
            age_text = f"Age: {result['predicted_age']} years"
            cv2.putText(frame, age_text, (40, box_y + 40), cv2.FONT_HERSHEY_SIMPLEX, 
                       1.2, (0, 255, 0), 2)
            
            conf_text = f"Confidence: {result['confidence']:.1%} ({result['confidence_level']})"
            cv2.putText(frame, conf_text, (40, box_y + 75), cv2.FONT_HERSHEY_SIMPLEX, 
                       0.7, (255, 255, 255), 1)
            
            category = "CHILD" if result['is_child'] else "TEEN" if result['is_teen'] else "ADULT"
            category_color = (0, 150, 255) if result['is_child'] else (255, 200, 0) if result['is_teen'] else (0, 255, 0)
            cv2.putText(frame, f"Category: {category}", (40, box_y + 110), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, category_color, 2)
            
            uncertainty_text = f"Uncertainty: +/- {result['uncertainty']:.1f} years"
            cv2.putText(frame, uncertainty_text, (40, box_y + 145), cv2.FONT_HERSHEY_SIMPLEX, 
                       0.6, (200, 200, 200), 1)
            
            if result.get('should_retry'):
                cv2.putText(frame, "Low confidence - adjusting...", (40, box_y + 175),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 150, 255), 1)
        
        if edge_cases:
            detected = [k.replace('_', ' ').title() for k, v in edge_cases.items() if v]
            if detected:
                y_pos = 150
                cv2.putText(frame, "Edge Cases Detected:", (20, y_pos), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 150, 255), 1)
                for i, case in enumerate(detected[:3]):
                    cv2.putText(frame, f"- {case}", (20, y_pos + 30 + i*25), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 200, 0), 1)
        
        privacy_text = "All biometric data deleted immediately"
        cv2.putText(frame, privacy_text, (width - 450, height - 10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        
        return frame
    
    def process_frame(self, frame: np.ndarray) -> tuple:
        current_time = time.time()
        
        if current_time - self.last_prediction_time < self.prediction_interval:
            return self.current_result, self.edge_cases
        
        pil_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        
        self.edge_cases = EdgeCaseDetector.analyze_image(pil_image)
        
        result = self.estimator.estimate_age(pil_image, attempt=1)
        
        if result.get("success"):
            self.current_result = result
            self.last_prediction_time = current_time
            self.logger.log_verification(result)
            
            detected_edge_cases = [k for k, v in self.edge_cases.items() if v]
            for edge_case in detected_edge_cases:
                self.logger.log_edge_case(result, edge_case)
        
        pil_image.close()
        del pil_image
        
        return self.current_result, self.edge_cases
    
    def run(self):
        print(f"\n{Config.PROJECT_NAME} - Webcam Demo")
        print(f"Created by {Config.CREATOR}\n")
        
        if not ConsentManager.request_consent():
            print("Consent not provided. Exiting.")
            return
        
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("Error: Could not open webcam")
            return
        
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        cap.set(cv2.CAP_PROP_FPS, 30)
        
        print("\nWebcam initialized. Processing...")
        print("Press 'q' to quit, 's' to save current result\n")
        
        frame_count = 0
        start_time = time.time()
        
        try:
            while True:
                ret, frame = cap.read()
                
                if not ret:
                    print("Error: Failed to capture frame")
                    break
                
                frame_count += 1
                
                result, edge_cases = self.process_frame(frame)
                
                display_frame = self.draw_overlay(frame, result, edge_cases)
                
                cv2.imshow(f'{Config.PROJECT_NAME} - Live Demo', display_frame)
                
                key = cv2.waitKey(1) & 0xFF
                
                if key == ord('q'):
                    break
                elif key == ord('s') and result:
                    timestamp = time.strftime("%Y%m%d_%H%M%S")
                    filename = f"verification_{timestamp}.png"
                    cv2.imwrite(filename, display_frame)
                    print(f"Saved result to {filename}")
                
                if frame_count % 30 == 0:
                    elapsed = time.time() - start_time
                    fps = frame_count / elapsed
                    print(f"FPS: {fps:.1f} | Frames: {frame_count}", end='\r')
        
        finally:
            cap.release()
            cv2.destroyAllWindows()
            
            elapsed = time.time() - start_time
            avg_fps = frame_count / elapsed if elapsed > 0 else 0
            print(f"\n\nSession complete:")
            print(f"Total frames: {frame_count}")
            print(f"Duration: {elapsed:.1f}s")
            print(f"Average FPS: {avg_fps:.1f}")
            print(f"\nAll biometric data has been securely deleted.")
            print(f"{Config.PROJECT_NAME} by {Config.CREATOR} - Privacy guaranteed.")

def main():
    verifier = WebcamAgeVerifier()
    verifier.run()

if __name__ == "__main__":
    main()
