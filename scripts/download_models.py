import requests
import hashlib
from pathlib import Path
from tqdm import tqdm
import sys

sys.path.append(str(Path(__file__).parent.parent))

from src.config import BetterAgeVerifyConfig as Config

MODEL_URLS = {
    "wideresnet_age.pth": {
        "url": "https://example.com/models/wideresnet_age.pth",
        "sha256": "PLACEHOLDER_CHECKSUM_WIDERESNET",
        "size": 262144000
    },
    "dex_age.pth": {
        "url": "https://example.com/models/dex_age.pth",
        "sha256": "PLACEHOLDER_CHECKSUM_DEX",
        "size": 524288000
    },
    "vit_age_estimation.pth": {
        "url": "https://example.com/models/vit_age_estimation.pth",
        "sha256": "PLACEHOLDER_CHECKSUM_VIT",
        "size": 367001600
    }
}

def calculate_sha256(filepath):
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def download_file(url, destination, expected_size=None):
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    
    if expected_size and total_size != expected_size:
        print(f"Warning: Expected size {expected_size} but got {total_size}")
    
    block_size = 8192
    progress_bar = tqdm(total=total_size, unit='B', unit_scale=True, desc=destination.name)
    
    with open(destination, 'wb') as f:
        for chunk in response.iter_content(chunk_size=block_size):
            if chunk:
                f.write(chunk)
                progress_bar.update(len(chunk))
    
    progress_bar.close()

def verify_checksum(filepath, expected_checksum):
    if expected_checksum.startswith("PLACEHOLDER"):
        print(f"  ⚠️  Skipping checksum verification (placeholder checksum)")
        return True
    
    print(f"  Verifying checksum...")
    actual_checksum = calculate_sha256(filepath)
    
    if actual_checksum == expected_checksum:
        print(f"  ✓ Checksum verified")
        return True
    else:
        print(f"  ✗ Checksum mismatch!")
        print(f"    Expected: {expected_checksum}")
        print(f"    Got:      {actual_checksum}")
        return False

def download_models():
    print(f"\n{Config.PROJECT_NAME} - Model Weight Downloader")
    print(f"Created by {Config.CREATOR}\n")
    
    Config.MODELS_DIR.mkdir(parents=True, exist_ok=True)
    
    print(f"Downloading models to: {Config.MODELS_DIR}\n")
    
    for model_name, info in MODEL_URLS.items():
        model_path = Config.MODELS_DIR / model_name
        
        if model_path.exists():
            print(f"📦 {model_name}: Already exists")
            
            if verify_checksum(model_path, info["sha256"]):
                print(f"  ✓ Using existing file\n")
                continue
            else:
                print(f"  Removing corrupted file and re-downloading...\n")
                model_path.unlink()
        
        print(f"📥 Downloading {model_name}...")
        print(f"  URL: {info['url']}")
        print(f"  Size: {info['size'] / (1024**2):.1f} MB")
        
        try:
            download_file(info["url"], model_path, info["size"])
            
            if verify_checksum(model_path, info["sha256"]):
                print(f"  ✓ Download complete\n")
            else:
                print(f"  ✗ Download failed - checksum mismatch\n")
                model_path.unlink()
                return False
                
        except Exception as e:
            print(f"  ✗ Download failed: {e}\n")
            if model_path.exists():
                model_path.unlink()
            return False
    
    print("═" * 70)
    print("All models downloaded successfully!")
    print("═" * 70)
    print(f"\nYou can now run BetterAgeVerify demos:")
    print(f"  python demos/webcam_demo.py")
    print(f"  python demos/static_image_demo.py --image photo.jpg")
    print(f"  python demos/video_demo.py --video video.mp4\n")
    
    return True

def main():
    print("\n" + "═" * 70)
    print("IMPORTANT NOTICE")
    print("═" * 70)
    print("\nThis script contains PLACEHOLDER URLs and checksums.")
    print("In production, you must:")
    print("  1. Host your trained model weights on a reliable server")
    print("  2. Update MODEL_URLS with actual download URLs")
    print("  3. Generate and add real SHA256 checksums")
    print("\nFor development/testing without trained models:")
    print("  - BetterAgeVerify will initialize with random weights")
    print("  - Predictions will be inaccurate (for testing only)")
    print("  - See models/README.md for training instructions")
    print("═" * 70 + "\n")
    
    proceed = input("Proceed with download attempt? (yes/no): ").strip().lower()
    
    if proceed != "yes":
        print("Download cancelled.")
        return 1
    
    success = download_models()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
