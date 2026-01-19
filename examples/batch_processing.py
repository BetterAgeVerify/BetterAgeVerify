"""
BetterAgeVerify - Batch Processing Example
Created by luvaary

This example demonstrates how to process multiple images efficiently.
"""

import sys
from pathlib import Path
import time
import json

sys.path.append(str(Path(__file__).parent.parent))

from src.age_estimator import BetterAgeVerifyEstimator
from src.utils import ImageProcessor, EdgeCaseDetector
from src.config import BetterAgeVerifyConfig as Config

def process_batch(image_paths, output_file=None):
    print("\n" + "=" * 70)
    print("BetterAgeVerify - Batch Processing Example")
    print("Created by luvaary")
    print("=" * 70 + "\n")
    
    print(f"Processing {len(image_paths)} images...")
    print("Initializing estimator...\n")
    
    estimator = BetterAgeVerifyEstimator()
    
    results = []
    successful = 0
    failed = 0
    total_processing_time = 0
    
    start_time = time.time()
    
    for i, image_path in enumerate(image_paths, 1):
        print(f"[{i}/{len(image_paths)}] Processing: {Path(image_path).name}...", end=" ")
        
        image = ImageProcessor.load_image(image_path)
        
        if image is None:
            print("✗ Failed to load")
            failed += 1
            results.append({
                "filename": Path(image_path).name,
                "success": False,
                "error": "load_failed"
            })
            continue
        
        edge_cases = EdgeCaseDetector.analyze_image(image)
        result = estimator.estimate_age(image)
        
        ImageProcessor.secure_delete(image)
        
        if result["success"]:
            print(f"✓ Age: {result['predicted_age']:.1f} years ({result['confidence_level']})")
            successful += 1
            total_processing_time += result['processing_time']
            
            results.append({
                "filename": Path(image_path).name,
                "success": True,
                "predicted_age": result['predicted_age'],
                "confidence": result['confidence'],
                "confidence_level": result['confidence_level'],
                "uncertainty": result['uncertainty'],
                "age_category": "child" if result['is_child'] else "teen" if result['is_teen'] else "adult",
                "edge_cases": [k for k, v in edge_cases.items() if v],
                "processing_time": result['processing_time']
            })
        else:
            print(f"✗ {result['error']}")
            failed += 1
            
            results.append({
                "filename": Path(image_path).name,
                "success": False,
                "error": result.get('error', 'unknown'),
                "message": result.get('message', 'Unknown error')
            })
    
    total_time = time.time() - start_time
    
    print("\n" + "=" * 70)
    print("BATCH PROCESSING COMPLETE")
    print("=" * 70 + "\n")
    
    print(f"Total Images: {len(image_paths)}")
    print(f"Successful: {successful} ({successful/len(image_paths)*100:.1f}%)")
    print(f"Failed: {failed} ({failed/len(image_paths)*100:.1f}%)")
    print(f"\nTotal Time: {total_time:.2f}s")
    print(f"Average Time per Image: {total_time/len(image_paths):.3f}s")
    if successful > 0:
        print(f"Average Processing Time: {total_processing_time/successful:.3f}s")
    
    if successful > 0:
        ages = [r['predicted_age'] for r in results if r['success']]
        print(f"\nAge Statistics:")
        print(f"  Average Age: {sum(ages)/len(ages):.1f} years")
        print(f"  Min Age: {min(ages):.1f} years")
        print(f"  Max Age: {max(ages):.1f} years")
        
        children = sum(1 for r in results if r.get('age_category') == 'child')
        teens = sum(1 for r in results if r.get('age_category') == 'teen')
        adults = sum(1 for r in results if r.get('age_category') == 'adult')
        
        print(f"\nAge Categories:")
        print(f"  Children (< 13): {children}")
        print(f"  Teens (13-17): {teens}")
        print(f"  Adults (18+): {adults}")
    
    if output_file:
        with open(output_file, 'w') as f:
            json.dump({
                "summary": {
                    "total": len(image_paths),
                    "successful": successful,
                    "failed": failed,
                    "total_time": total_time,
                    "average_time": total_time / len(image_paths)
                },
                "results": results,
                "system": f"{Config.PROJECT_NAME} by {Config.CREATOR}"
            }, f, indent=2)
        
        print(f"\nResults saved to: {output_file}")
    
    print("\n" + "-" * 70)
    print("Privacy: All biometric data has been securely deleted")
    print("-" * 70 + "\n")
    
    return results

def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description=f"{Config.PROJECT_NAME} Batch Processing by {Config.CREATOR}"
    )
    parser.add_argument(
        'directory',
        type=str,
        help='Directory containing images to process'
    )
    parser.add_argument(
        '--output',
        type=str,
        help='Output JSON file for results'
    )
    parser.add_argument(
        '--pattern',
        type=str,
        default='*.jpg',
        help='File pattern to match (default: *.jpg)'
    )
    
    args = parser.parse_args()
    
    image_dir = Path(args.directory)
    
    if not image_dir.exists():
        print(f"Error: Directory not found: {image_dir}")
        return 1
    
    image_paths = list(image_dir.glob(args.pattern))
    
    if not image_paths:
        print(f"Error: No images found matching pattern: {args.pattern}")
        return 1
    
    process_batch([str(p) for p in image_paths], output_file=args.output)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
