"""
BetterAgeVerify - Simple Example
Created by luvaary

This example demonstrates the simplest possible usage of BetterAgeVerify.
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from src.age_estimator import BetterAgeVerifyEstimator
from PIL import Image

def main():
    print("\n" + "=" * 60)
    print("BetterAgeVerify - Simple Example")
    print("Created by luvaary")
    print("=" * 60 + "\n")
    
    print("Initializing BetterAgeVerify...")
    estimator = BetterAgeVerifyEstimator()
    print("✓ Initialized\n")
    
    image_path = input("Enter path to image file: ").strip()
    
    try:
        print(f"\nLoading image: {image_path}")
        image = Image.open(image_path)
        print("✓ Image loaded\n")
        
        print("Processing (this may take a few seconds)...")
        result = estimator.estimate_age(image)
        
        print("\n" + "=" * 60)
        print("RESULT")
        print("=" * 60 + "\n")
        
        if result["success"]:
            print(f"✓ Age Estimation Successful")
            print(f"\nPredicted Age: {result['predicted_age']} years")
            print(f"Confidence: {result['confidence']:.1%} ({result['confidence_level']})")
            print(f"Uncertainty: ±{result['uncertainty']} years")
            
            print(f"\nAge Category: ", end="")
            if result['is_child']:
                print("CHILD (under 13)")
            elif result['is_teen']:
                print("TEEN (13-17)")
            else:
                print("ADULT (18+)")
            
            if result['should_retry']:
                print("\n⚠️  Low confidence - consider retrying with better image")
        else:
            print(f"✗ Estimation Failed")
            print(f"\nError: {result['error']}")
            print(f"Message: {result['message']}")
        
        print(f"\nProcessing Time: {result['processing_time']:.3f}s")
        print(f"\n{'-' * 60}")
        print("Privacy: All biometric data has been deleted")
        print("-" * 60 + "\n")
        
    except FileNotFoundError:
        print(f"\n✗ Error: File not found: {image_path}")
    except Exception as e:
        print(f"\n✗ Error: {e}")

if __name__ == "__main__":
    main()
